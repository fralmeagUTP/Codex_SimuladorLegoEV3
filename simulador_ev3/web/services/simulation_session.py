"""Per-user web simulation session wrapper."""

from __future__ import annotations

import json
import re
import tempfile
import threading
from collections import deque
from pathlib import Path
from typing import Any

from simulador_ev3.application.simulation_service import SimulationService
from simulador_ev3.application.world_editor_service import WorldEditorService
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.domain.editor.world_editor_model import (
    ASSET_CATALOG,
    CELL_SIZE_MM,
    GRID_SIZE_PX,
    MAX_WORLD_MM,
    get_asset_spec,
)
from simulador_ev3.persistence.world_repository import WorldRepository
from simulador_ev3.runtime.execution_policy import ExecutionPolicy
from simulador_ev3.web.errors import InvalidPayload, InvalidSessionState
from simulador_ev3.web.services.world_dto import world_to_dict


class SimulationSession:
    """Isolated state and callbacks for one browser/user session."""

    def __init__(
        self,
        *,
        session_id: str,
        config: dict[str, Any],
        max_runtime_s: float,
    ) -> None:
        self.session_id = session_id
        self._config = config
        self._lock = threading.RLock()
        self._events: deque[dict[str, Any]] = deque(maxlen=300)
        self._sequence = 0
        self._source_code: str | None = None
        self._latest_snapshot: dict[str, Any] | None = None
        self._latest_error: dict[str, Any] | None = None
        self._latest_debug: dict[str, Any] | None = None
        self._debug_breakpoints: set[int] = set()
        self._status = "created"
        self._loaded_world_name: str | None = None
        self._editor = WorldEditorService()
        self._service = SimulationService(
            config=SimEngineConfig(
                world_width_mm=MAX_WORLD_MM,
                world_height_mm=MAX_WORLD_MM,
            ),
            policy=ExecutionPolicy(max_runtime_s=max_runtime_s)
        )
        self._wire_callbacks()

    @property
    def status(self) -> str:
        with self._lock:
            return self._status

    def load_script(self, source: str) -> dict[str, Any]:
        if not isinstance(source, str):
            raise InvalidPayload("El campo source debe ser texto.")
        max_size = int(self._config.get("MAX_SCRIPT_SIZE_BYTES", 128 * 1024))
        if len(source.encode("utf-8")) > max_size:
            raise InvalidPayload("El script excede el tamano maximo permitido.")
        with self._lock:
            self._source_code = source
            self._service.load_script(source)
            if self._status in {"created", "stopped", "error"}:
                self._status = "ready"
            self._latest_error = None
            self._push_event("status", {"status": self._status})
            return self.summary()

    def start(self, *, debug: bool = False, step_mode: bool = False) -> dict[str, Any]:
        with self._lock:
            if not self._source_code:
                raise InvalidSessionState("No hay script cargado para ejecutar.")
            if debug:
                self._service.set_debug_breakpoints(self._debug_breakpoints)
            self._service.start(debug=debug, step_mode=step_mode)
            self._status = "running"
            self._push_event("status", {"status": self._status})
            return self.summary()

    def pause(self) -> dict[str, Any]:
        with self._lock:
            self._service.pause()
            self._status = "paused"
            self._push_event("status", {"status": self._status})
            return self.summary()

    def resume(self) -> dict[str, Any]:
        with self._lock:
            self._service.resume()
            self._status = "running"
            self._push_event("status", {"status": self._status})
            return self.summary()

    def stop(self) -> dict[str, Any]:
        with self._lock:
            self._service.stop()
            self._status = "stopped"
            self._push_event("status", {"status": self._status})
            return self.summary()

    def reset(self) -> dict[str, Any]:
        with self._lock:
            self._service.reset()
            self._wire_callbacks()
            self._source_code = None
            self._latest_snapshot = None
            self._latest_error = None
            self._latest_debug = None
            self._debug_breakpoints = set()
            self._status = "created"
            self._push_event("status", {"status": self._status})
            return self.summary()

    def set_debug_breakpoints(self, breakpoints: set[int]) -> dict[str, Any]:
        with self._lock:
            self._debug_breakpoints = {int(line) for line in breakpoints if int(line) > 0}
            self._service.set_debug_breakpoints(self._debug_breakpoints)
            payload = {"breakpoints": sorted(self._debug_breakpoints)}
            self._push_event("debug", {"type": "breakpoints", **payload})
            return payload

    def debug_continue(self) -> dict[str, Any]:
        with self._lock:
            self._service.debug_continue()
            payload = {"status": self._status, "action": "continue"}
            self._push_event("debug", {"type": "command", **payload})
            return payload

    def debug_step(self) -> dict[str, Any]:
        with self._lock:
            self._service.debug_step()
            payload = {"status": self._status, "action": "step"}
            self._push_event("debug", {"type": "command", **payload})
            return payload

    def set_robot_start(
        self,
        x_mm: float,
        y_mm: float,
        theta_deg: float | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            self._service.set_robot_start(float(x_mm), float(y_mm), theta_deg)
            return self.summary()

    def load_world_name(self, name: str) -> dict[str, Any]:
        if not name or any(part in name for part in ("..", "/", "\\")):
            raise InvalidPayload("Nombre de mundo invalido.")
        path = Path(self._config["WORLDS_DIR"]) / name
        if path.suffix.lower() != ".json" or not path.exists():
            raise InvalidPayload("Mundo no encontrado.")
        with self._lock:
            self._service.load_world_file(path)
            self._loaded_world_name = name
            self._status = "ready" if self._status == "created" else self._status
            self._push_event("world", self.current_world())
            return self.summary() | {"world": self.current_world()}

    def upload_world_json(self, data: dict[str, Any]) -> dict[str, Any]:
        raw = json.dumps(data, ensure_ascii=False)
        max_size = int(self._config.get("MAX_WORLD_JSON_SIZE_BYTES", 2 * 1024 * 1024))
        if len(raw.encode("utf-8")) > max_size:
            raise InvalidPayload("El mundo excede el tamano maximo permitido.")
        with tempfile.NamedTemporaryFile(
            "w",
            suffix=".json",
            delete=False,
            encoding="utf-8",
            dir=Path(tempfile.gettempdir()),
        ) as fh:
            fh.write(raw)
            tmp_path = Path(fh.name)
        with self._lock:
            self._service.load_world_file(tmp_path)
            self._loaded_world_name = None
            self._push_event("world", self.current_world())
            return self.summary() | {"world": self.current_world()}

    def snapshot_response(self) -> dict[str, Any]:
        with self._lock:
            snapshot = self._latest_snapshot
            if snapshot is None:
                dto = self._service.get_snapshot()
                snapshot = dto.to_dict() if dto else None
                self._latest_snapshot = snapshot
            return {
                "session_id": self.session_id,
                "status": self._status,
                "snapshot": snapshot,
                "error": self._latest_error,
                "debug": self._latest_debug,
            }

    def create_editor_world(self, width_cells: int = 20, height_cells: int = 20) -> dict[str, Any]:
        with self._lock:
            try:
                self._editor.reset_formal_world(int(width_cells), int(height_cells))
            except (TypeError, ValueError) as exc:
                raise InvalidPayload("Dimensiones de mundo invalidas.") from exc
            return self.editor_response()

    def load_editor_world(self, data: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise InvalidPayload("El mundo del editor debe ser un objeto JSON.")
        with self._lock:
            try:
                world = self._editor.load(json.dumps(data, ensure_ascii=False))
            except Exception as exc:  # noqa: BLE001
                raise InvalidPayload(f"Mundo del editor invalido: {exc}") from exc
            self._editor._formal_world = world
            self._editor._rebuild_legacy_from_formal()
            self._push_event("editor_world", world.to_dict())
            return self.editor_response()

    def save_editor_world(self, name: str) -> dict[str, Any]:
        safe_name = _safe_world_filename(name)
        worlds_dir = Path(self._config["WORLDS_DIR"])
        worlds_dir.mkdir(parents=True, exist_ok=True)
        out = worlds_dir / safe_name
        with self._lock:
            validation = self._validation_dict()
            if not validation["valid"]:
                raise InvalidPayload("No se puede guardar un mundo con errores de validacion.")
            self._editor.save_json(out)
            self._loaded_world_name = safe_name
            return {
                "status": "saved",
                "name": safe_name,
                "path": str(out),
                "validation": validation,
            }

    def place_asset(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            try:
                placement = self._editor.place_asset_current(
                    str(payload.get("asset_key", "")),
                    int(payload.get("x", payload.get("x_px", 0))),
                    int(payload.get("y", payload.get("y_px", 0))),
                    int(payload.get("rotation", 0)),
                )
            except (TypeError, ValueError) as exc:
                raise InvalidPayload("No se pudo colocar el asset.") from exc
            return self.editor_response(extra={"placement": placement.to_dict()})

    def move_asset(self, payload: dict[str, Any]) -> dict[str, Any]:
        asset_id = str(payload.get("id", payload.get("asset_id", "")))
        with self._lock:
            try:
                moved = self._editor.move_asset_current(
                    asset_id,
                    int(payload.get("x", payload.get("x_px", 0))),
                    int(payload.get("y", payload.get("y_px", 0))),
                )
            except (TypeError, ValueError) as exc:
                raise InvalidPayload("Coordenadas de asset invalidas.") from exc
            if not moved:
                raise InvalidPayload("No se pudo mover el asset.")
            return self.editor_response()

    def rotate_asset(self, payload: dict[str, Any]) -> dict[str, Any]:
        asset_id = str(payload.get("id", payload.get("asset_id", "")))
        with self._lock:
            try:
                delta = int(payload.get("delta_deg", 90))
            except (TypeError, ValueError) as exc:
                raise InvalidPayload("Rotacion de asset invalida.") from exc
            if not self._editor.rotate_asset_current(asset_id, delta):
                raise InvalidPayload("No se pudo rotar el asset.")
            return self.editor_response()

    def update_asset(self, payload: dict[str, Any]) -> dict[str, Any]:
        asset_id = str(payload.get("id", payload.get("asset_id", "")))
        if not asset_id:
            raise InvalidPayload("Debe indicar el asset.")
        with self._lock:
            try:
                x_px = payload.get("x", payload.get("x_px"))
                y_px = payload.get("y", payload.get("y_px"))
                changed = self._editor.update_asset_current(
                    asset_id,
                    asset_key=str(payload["asset_key"]) if "asset_key" in payload else None,
                    x_px=int(x_px) if x_px is not None else None,
                    y_px=int(y_px) if y_px is not None else None,
                    rotation=int(payload["rotation"]) if "rotation" in payload else None,
                )
            except (TypeError, ValueError) as exc:
                raise InvalidPayload("Propiedades de asset invalidas.") from exc
            if not changed:
                raise InvalidPayload("No se pudo actualizar el asset.")
            placement = self._editor.get_placement(asset_id)
            return self.editor_response(extra={"placement": placement.to_dict() if placement else None})

    def duplicate_asset(self, payload: dict[str, Any]) -> dict[str, Any]:
        asset_id = str(payload.get("id", payload.get("asset_id", "")))
        with self._lock:
            source = self._editor.get_placement(asset_id)
            if source is None:
                raise InvalidPayload("No se pudo duplicar el asset.")
            try:
                dx_px = int(payload["dx_px"]) if "dx_px" in payload else None
                dy_px = int(payload["dy_px"]) if "dy_px" in payload else None
            except (TypeError, ValueError) as exc:
                raise InvalidPayload("Desplazamiento de duplicado invalido.") from exc
            if dx_px is None and dy_px is None:
                spec = get_asset_spec(source.asset_key)
                width_cells = spec.width_cells if spec else 1
                height_cells = spec.height_cells if spec else 1
                if source.rotation % 180 == 90:
                    width_cells, height_cells = height_cells, width_cells
                dx_px = max(1, width_cells) * GRID_SIZE_PX
                dy_px = 0
            placement = self._editor.duplicate_asset_current(
                asset_id,
                dx_px=dx_px if dx_px is not None else 0,
                dy_px=dy_px if dy_px is not None else 0,
            )
            if placement is None:
                raise InvalidPayload("No se pudo duplicar el asset.")
            return self.editor_response(extra={"placement": placement.to_dict()})

    def remove_asset(self, asset_id: str) -> dict[str, Any]:
        with self._lock:
            if not self._editor.remove_asset_current(asset_id):
                raise InvalidPayload("No se pudo eliminar el asset.")
            return self.editor_response()

    def validate_editor_world(self) -> dict[str, Any]:
        with self._lock:
            return self._validation_dict()

    def apply_editor_world(self) -> dict[str, Any]:
        with self._lock:
            validation = self._validation_dict()
            if not validation["valid"]:
                raise InvalidPayload("El mundo tiene errores de validacion.")
            world = self._editor.to_world_model()
            robot_start = self._robot_start_from_editor_world()
            if robot_start is not None:
                x_mm, y_mm, theta_deg = robot_start
                self._service.set_robot_start(x_mm, y_mm, theta_deg)
            self._service._loaded_world = world
            self._service.engine.set_world(world)
            self._push_event("world", self.current_world())
            return self.summary() | {"world": self.current_world()}

    def editor_response(self, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        world = self._editor.current_formal_world().to_dict()
        response = {"world": world, "validation": self._validation_dict()}
        if extra:
            response.update(extra)
        return response

    def current_world(self) -> dict[str, Any] | None:
        if self._service.engine is None:
            return None
        return world_to_dict(
            self._service.engine.world,
            editor_spec=self._editor.current_formal_world().to_dict(),
        )

    def events_since(self, sequence: int = 0) -> list[dict[str, Any]]:
        with self._lock:
            return [event for event in self._events if event["sequence"] > sequence]

    def summary(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "status": self._status,
            "loaded_world": self._loaded_world_name,
            "has_script": self._source_code is not None,
            "error": self._latest_error,
            "debug": self._latest_debug,
            "breakpoints": sorted(self._debug_breakpoints),
        }

    def close(self) -> None:
        with self._lock:
            self._service.stop(reason="session_close")
            self._status = "expired"
            self._push_event("status", {"status": self._status})

    def _wire_callbacks(self) -> None:
        self._service.set_snapshot_callback(self._on_snapshot)
        self._service.set_error_callback(self._on_error)
        self._service.set_status_callback(self._on_status)
        self._service.set_debug_callback(self._on_debug)

    def _on_snapshot(self, dto) -> None:
        data = dto.to_dict()
        with self._lock:
            self._latest_snapshot = data
            self._push_event("snapshot", data)

    def _on_error(self, payload: dict[str, Any]) -> None:
        with self._lock:
            self._latest_error = dict(payload)
            self._status = "error"
            self._push_event("error", self._latest_error)

    def _on_status(self, status: str) -> None:
        mapped = {
            "started": "running",
            "paused": "paused",
            "resumed": "running",
            "stopped": "stopped",
            "reset": "created",
            "error": "error",
            "world_loaded": self._status if self._status != "created" else "ready",
        }.get(status, status)
        with self._lock:
            self._status = mapped
            self._push_event("status", {"status": mapped, "raw_status": status})

    def _on_debug(self, payload: dict[str, Any]) -> None:
        with self._lock:
            self._latest_debug = dict(payload)
            self._push_event("debug", self._latest_debug)

    def _push_event(self, event_type: str, payload: dict[str, Any] | None) -> None:
        self._sequence += 1
        self._events.append(
            {
                "sequence": self._sequence,
                "type": event_type,
                "session_id": self.session_id,
                "payload": payload or {},
            }
        )

    def _validation_dict(self) -> dict[str, Any]:
        report = self._editor._validator.validate(self._editor.current_formal_world())
        return {
            "valid": not report.has_errors,
            "errors": [_issue_dict(issue) for issue in report.errors],
            "warnings": [_issue_dict(issue) for issue in report.warnings],
        }

    def _robot_start_from_editor_world(self) -> tuple[float, float, float] | None:
        world = self._editor.current_formal_world()
        mm_per_px = CELL_SIZE_MM / float(world.grid_size_px or GRID_SIZE_PX)
        for placement in world.placements:
            spec = get_asset_spec(placement.asset_key)
            if spec is None or spec.asset_type != "robot":
                continue
            width_cells = spec.width_cells
            height_cells = spec.height_cells
            if placement.rotation % 180 == 90:
                width_cells, height_cells = height_cells, width_cells
            x_mm = placement.x_px * mm_per_px + (width_cells * CELL_SIZE_MM) / 2.0
            y_mm = placement.y_px * mm_per_px + (height_cells * CELL_SIZE_MM) / 2.0
            return float(x_mm), float(y_mm), float(placement.rotation % 360)
        return None


def asset_catalog_dict() -> dict[str, Any]:
    return {
        "grid_size_px": 32,
        "cell_size_mm": 100.0,
        "assets": [
            {
                "key": spec.key,
                "type": spec.asset_type,
                "layer": spec.layer,
                "width_cells": spec.width_cells,
                "height_cells": spec.height_cells,
                "connectors": sorted(spec.connectors),
            }
            for spec in ASSET_CATALOG.values()
        ],
    }


def _issue_dict(issue) -> dict[str, Any]:
    return {
        "code": issue.code,
        "message": issue.message,
        "severity": issue.severity,
        "placement_id": issue.placement_id,
        "cell": list(issue.cell) if issue.cell else None,
    }


def _safe_world_filename(name: str) -> str:
    raw = str(name or "").strip()
    if not raw:
        raise InvalidPayload("El nombre del mundo es requerido.")
    if any(part in raw for part in ("..", "/", "\\")):
        raise InvalidPayload("Nombre de mundo invalido.")
    if raw.lower().endswith(".json"):
        raw = raw[:-5]
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", raw):
        raise InvalidPayload("Use solo letras, numeros, guion y guion bajo.")
    return f"{raw}.json"
