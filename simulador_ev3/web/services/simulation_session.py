"""Per-user web simulation session wrapper."""

from __future__ import annotations

import json
import re
import tempfile
import threading
import time
from datetime import datetime, timezone
from collections import deque
from pathlib import Path
from typing import Any

from simulador_ev3.application.simulation_service import SimulationService
from simulador_ev3.application.world_editor_service import WorldEditorService
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.domain.editor.world_editor_model import (
    ASSET_CATALOG,
    CELL_SIZE_MM,
    DEFAULT_WORLD_CELLS,
    DEFAULT_WORLD_MM,
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
        self._latest_debug_context: dict[str, Any] | None = None
        self._last_snapshot_event_at = 0.0
        snapshot_hz = float(self._config.get("WEB_SNAPSHOT_MAX_HZ", 12.0))
        self._snapshot_event_interval_s = 0.0 if snapshot_hz <= 0 else 1.0 / snapshot_hz
        self._debug_breakpoints: set[int] = set()
        self._debug_watches: list[str] = []
        self._debugstate_v2_enabled = bool(self._config.get("DEBUGSTATE_V2_ENABLED", True))
        self._start_idempotency: dict[str, tuple[float, dict[str, Any]]] = {}
        self._start_idempotency_ttl_s = float(self._config.get("START_IDEMPOTENCY_TTL_S", 20.0))
        self._status = "created"
        self._loaded_world_name: str | None = None
        self._editor = WorldEditorService()
        self._world_has_editor_spec = False
        self._service = SimulationService(
            config=SimEngineConfig(
                world_width_mm=DEFAULT_WORLD_MM,
                world_height_mm=DEFAULT_WORLD_MM,
            ),
            policy=ExecutionPolicy(max_runtime_s=max_runtime_s)
        )
        self._wire_callbacks()
        self._latest_debug = self._build_debug_state("idle")

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
            self._set_debug_state("idle")
            self._push_event("status", {"status": self._status})
            return self.summary()

    def start(self, *, debug: bool = False, step_mode: bool = False) -> dict[str, Any]:
        with self._lock:
            if not self._source_code:
                raise InvalidSessionState("No hay script cargado para ejecutar.")
            if debug:
                self._service.set_debug_breakpoints(self._debug_breakpoints)
                self._service.set_debug_watches(self._debug_watches)
            self._service.start(debug=debug, step_mode=step_mode)
            self._status = "running"
            self._set_debug_state("running")
            self._push_event("status", {"status": self._status})
            return self.summary()

    def get_start_idempotency(self, request_id: str | None) -> dict[str, Any] | None:
        normalized = str(request_id or "").strip()
        if not normalized:
            return None
        now = time.monotonic()
        with self._lock:
            self._prune_start_idempotency(now)
            cached = self._start_idempotency.get(normalized)
            if cached is None:
                return None
            return dict(cached[1])

    def remember_start_idempotency(self, request_id: str | None, payload: dict[str, Any]) -> None:
        normalized = str(request_id or "").strip()
        if not normalized:
            return
        now = time.monotonic()
        with self._lock:
            self._prune_start_idempotency(now)
            self._start_idempotency[normalized] = (now, dict(payload))

    def pause(self) -> dict[str, Any]:
        with self._lock:
            self._service.pause()
            self._status = "paused"
            self._set_debug_state("paused_manual", reason="manual")
            self._push_event("status", {"status": self._status})
            return self.summary()

    def resume(self) -> dict[str, Any]:
        with self._lock:
            self._service.resume()
            self._status = "running"
            self._set_debug_state("running")
            self._push_event("status", {"status": self._status})
            return self.summary()

    def stop(self) -> dict[str, Any]:
        with self._lock:
            self._status = "stopped"
            self._set_debug_state("stopped")
            self._service.stop()
            self._push_event("status", {"status": self._status})
            return self.summary()

    def reset(self) -> dict[str, Any]:
        with self._lock:
            self._service.reset()
            self._wire_callbacks()
            self._source_code = None
            self._latest_snapshot = None
            self._latest_error = None
            self._latest_debug_context = None
            self._debug_breakpoints = set()
            self._debug_watches = []
            self._start_idempotency.clear()
            self._status = "created"
            self._set_debug_state("idle")
            self._push_event("status", {"status": self._status})
            return self.summary()

    def set_debug_breakpoints(self, breakpoints: set[int]) -> dict[str, Any]:
        with self._lock:
            self._debug_breakpoints = {int(line) for line in breakpoints if int(line) > 0}
            self._service.set_debug_breakpoints(self._debug_breakpoints)
            payload = {"breakpoints": sorted(self._debug_breakpoints)}
            self._set_debug_state(
                self._latest_debug.get("debug_state", "idle") if isinstance(self._latest_debug, dict) else "idle",
                legacy={"type": "breakpoints", **payload},
            )
            return payload

    def set_debug_watches(self, watches: list[str]) -> dict[str, Any]:
        with self._lock:
            cleaned: list[str] = []
            for raw in watches[:20]:
                expr = str(raw).strip()
                if expr:
                    cleaned.append(expr)
            self._debug_watches = cleaned
            self._service.set_debug_watches(self._debug_watches)
            payload = {"watches": list(self._debug_watches)}
            self._set_debug_state(
                self._latest_debug.get("debug_state", "idle") if isinstance(self._latest_debug, dict) else "idle",
                legacy={"type": "watches", **payload},
            )
            return payload

    def debug_continue(self) -> dict[str, Any]:
        with self._lock:
            self._service.debug_continue()
            payload = {"type": "command", "status": self._status, "action": "continue"}
            self._set_debug_state("running", legacy=payload)
            return payload

    def debug_step(self) -> dict[str, Any]:
        with self._lock:
            self._service.debug_step()
            payload = {"type": "command", "status": self._status, "action": "step"}
            self._set_debug_state("running", legacy=payload)
            return payload

    def set_robot_start(
        self,
        x_mm: float,
        y_mm: float,
        theta_deg: float | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            self._service.set_robot_start(float(x_mm), float(y_mm), theta_deg)
            self._latest_snapshot = None
            return self.summary()

    def load_world_name(self, name: str) -> dict[str, Any]:
        if not name or any(part in name for part in ("..", "/", "\\")):
            raise InvalidPayload("Nombre de mundo invalido.")
        path = Path(self._config["WORLDS_DIR"]) / name
        if path.suffix.lower() != ".json" or not path.exists():
            raise InvalidPayload("Mundo no encontrado.")
        with self._lock:
            self._service.load_world_file(path)
            self._sync_editor_from_world_file(path)
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
            self._sync_editor_from_world_file(tmp_path)
            self._loaded_world_name = None
            self._push_event("world", self.current_world())
            return self.summary() | {"world": self.current_world()}

    def load_blank_world(
        self,
        width_cells: int = DEFAULT_WORLD_CELLS,
        height_cells: int = DEFAULT_WORLD_CELLS,
    ) -> dict[str, Any]:
        with self._lock:
            try:
                w_cells = int(width_cells)
                h_cells = int(height_cells)
            except (TypeError, ValueError) as exc:
                raise InvalidPayload("Dimensiones de mundo invalidas.") from exc

            w_mm = float(w_cells * CELL_SIZE_MM)
            h_mm = float(h_cells * CELL_SIZE_MM)
            self._service.load_blank_world(width_mm=w_mm, height_mm=h_mm)
            self._editor.reset_formal_world(w_cells, h_cells)
            self._world_has_editor_spec = True
            self._loaded_world_name = None
            self._status = "ready" if self._status == "created" else self._status
            self._push_event("world", self.current_world())
            return self.summary() | {"world": self.current_world()}

    def _sync_editor_from_world_file(self, path: Path) -> None:
        """Keep editor_spec aligned with the currently loaded simulation world file."""
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            # Si el archivo no se puede parsear, al menos limpiar estado visual.
            self._editor.reset_formal_world(DEFAULT_WORLD_CELLS, DEFAULT_WORLD_CELLS)
            self._world_has_editor_spec = False
            return

        try:
            # 1) Mundo de editor "formal" puro.
            if isinstance(raw, dict) and all(
                key in raw for key in ("schema_version", "world_width_cells", "world_height_cells", "placements")
            ):
                world = self._editor.load(json.dumps(raw, ensure_ascii=False))
                self._editor._formal_world = world
                self._editor._rebuild_legacy_from_formal()
                self._world_has_editor_spec = True
                return

            # 2) Mundo de simulacion envuelto con editor_spec.
            editor_spec = raw.get("editor_spec") if isinstance(raw, dict) else None
            if isinstance(editor_spec, dict):
                self._editor.load_json(path)
                self._world_has_editor_spec = True
                return

            # 3) Mundo de simulacion puro (sin editor_spec): limpiar overlays previos.
            world_data = raw.get("world") if isinstance(raw, dict) else None
            if isinstance(world_data, dict):
                width_mm = float(world_data.get("width_mm", DEFAULT_WORLD_MM))
                height_mm = float(world_data.get("height_mm", DEFAULT_WORLD_MM))
                width_cells = max(1, int(round(width_mm / CELL_SIZE_MM)))
                height_cells = max(1, int(round(height_mm / CELL_SIZE_MM)))
                self._editor.reset_formal_world(width_cells, height_cells)
                self._world_has_editor_spec = False
                return
        except Exception:  # noqa: BLE001
            # Fallback defensivo: estado limpio por defecto.
            self._editor.reset_formal_world(DEFAULT_WORLD_CELLS, DEFAULT_WORLD_CELLS)
            self._world_has_editor_spec = False
            return

        # Si no reconoce formato, dejar estado visual limpio.
        self._editor.reset_formal_world(DEFAULT_WORLD_CELLS, DEFAULT_WORLD_CELLS)
        self._world_has_editor_spec = False

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
                "debug_context": self._latest_debug_context,
            }

    def create_editor_world(
        self,
        width_cells: int = DEFAULT_WORLD_CELLS,
        height_cells: int = DEFAULT_WORLD_CELLS,
    ) -> dict[str, Any]:
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

    def import_editor_world_payload(self, data: dict[str, Any]) -> dict[str, Any]:
        """Accept both pure editor_spec and wrapped world JSON payloads."""
        if not isinstance(data, dict):
            raise InvalidPayload("El mundo del editor debe ser un objeto JSON.")

        formal_payload = data
        if "schema_version" not in formal_payload or "placements" not in formal_payload:
            wrapped_spec = data.get("editor_spec")
            if isinstance(wrapped_spec, dict):
                formal_payload = wrapped_spec

        if isinstance(formal_payload, dict) and "schema_version" in formal_payload and "placements" in formal_payload:
            return self.load_editor_world(formal_payload)

        legacy_payload = data.get("editor_objects") if isinstance(data.get("editor_objects"), dict) else None
        if legacy_payload is None and all(key in data for key in ("world", "walls", "lines", "zones")):
            legacy_payload = data

        if legacy_payload is not None:
            with self._lock:
                try:
                    self._editor.from_editor_dict(legacy_payload)
                except Exception as exc:  # noqa: BLE001
                    raise InvalidPayload(f"Mundo del editor invalido: {exc}") from exc
                self._world_has_editor_spec = True
                self._push_event("editor_world", self._editor.current_formal_world().to_dict())
                return self.editor_response()

        # Formato de mundo de simulacion (WorldRepository): {"version": 1, "world": {...}}
        if isinstance(data.get("world"), dict) and "version" in data:
            with self._lock:
                try:
                    world = WorldRepository.from_dict(data)
                    self._editor._from_world_model(world)
                except Exception as exc:  # noqa: BLE001
                    raise InvalidPayload(f"Mundo de simulacion invalido: {exc}") from exc
                self._world_has_editor_spec = True
                self._push_event("editor_world", self._editor.current_formal_world().to_dict())
                return self.editor_response()

        raise InvalidPayload(
            "Formato de mundo no soportado. Se esperaba editor_spec o editor_objects."
        )

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
            self._world_has_editor_spec = True
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
        editor_spec = self._editor.current_formal_world().to_dict() if self._world_has_editor_spec else None
        return world_to_dict(
            self._service.engine.world,
            editor_spec=editor_spec,
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
            "debug_context": self._latest_debug_context,
            "breakpoints": sorted(self._debug_breakpoints),
            "watches": list(self._debug_watches),
        }

    def runtime_checkpoint(self) -> dict[str, Any]:
        with self._lock:
            world_snapshot = self.current_world()
            world_wrapper = {"version": 1, "world": world_snapshot} if world_snapshot else None
            editor_world = (
                self._editor.current_formal_world().to_dict() if self._world_has_editor_spec else None
            )
            return {
                "source_code": self._source_code,
                "loaded_world_name": self._loaded_world_name,
                "status": self._status,
                "debug_breakpoints": sorted(self._debug_breakpoints),
                "debug_watches": list(self._debug_watches),
                "world_has_editor_spec": self._world_has_editor_spec,
                "world_wrapper": world_wrapper,
                "editor_world": editor_world,
            }

    def restore_runtime_checkpoint(self, checkpoint: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(checkpoint, dict):
            raise InvalidPayload("Checkpoint de sesion invalido.")

        with self._lock:
            source_code = checkpoint.get("source_code")
            if isinstance(source_code, str) and source_code.strip():
                self.load_script(source_code)

            restored_world = False
            world_wrapper = checkpoint.get("world_wrapper")
            if isinstance(world_wrapper, dict) and world_wrapper:
                try:
                    self.upload_world_json(world_wrapper)
                    restored_world = True
                except Exception:  # noqa: BLE001
                    restored_world = False

            if not restored_world and bool(checkpoint.get("world_has_editor_spec", False)):
                editor_world = checkpoint.get("editor_world")
                if isinstance(editor_world, dict) and editor_world:
                    try:
                        self.load_editor_world(editor_world)
                        self.apply_editor_world()
                        restored_world = True
                    except Exception:  # noqa: BLE001
                        restored_world = False

            loaded_world_name = checkpoint.get("loaded_world_name")
            if isinstance(loaded_world_name, str) and loaded_world_name:
                self._loaded_world_name = loaded_world_name

            raw_breakpoints = checkpoint.get("debug_breakpoints")
            if isinstance(raw_breakpoints, list):
                try:
                    breakpoints = {int(line) for line in raw_breakpoints if int(line) > 0}
                    self.set_debug_breakpoints(breakpoints)
                except (TypeError, ValueError):
                    pass

            raw_watches = checkpoint.get("debug_watches")
            if isinstance(raw_watches, list):
                watches: list[str] = []
                for item in raw_watches[:20]:
                    if isinstance(item, str) and item.strip():
                        watches.append(item.strip())
                self.set_debug_watches(watches)

            raw_status = str(checkpoint.get("status", "")).strip().lower()
            if raw_status in {"running", "paused"}:
                self._status = "ready" if self._source_code else "created"
                self._set_debug_state("idle", reason="recovered")
                self._push_event("status", {"status": self._status, "raw_status": "recovered"})

            return self.summary() | {"restored_world": restored_world}

    def close(self) -> None:
        with self._lock:
            self._service.stop(reason="session_close")
            self._status = "expired"
            self._set_debug_state("stopped")
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
            now = time.monotonic()
            if now - self._last_snapshot_event_at >= self._snapshot_event_interval_s:
                self._last_snapshot_event_at = now
                self._push_event("snapshot", data)

    def _on_error(self, payload: dict[str, Any]) -> None:
        with self._lock:
            if self._status in {"stopped", "created", "expired"}:
                return
            self._latest_error = dict(payload)
            self._status = "error"
            error_reason = "timeout" if "tiempo m" in str(payload.get("error", "")).lower() else "error"
            self._set_debug_state("error", reason=error_reason)
            self._push_event("error", self._latest_error)

    def _on_status(self, status: str) -> None:
        if status == "error" and self._status in {"stopped", "created", "expired"}:
            return
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
            if status == "started":
                self._set_debug_state("running")
            elif status == "paused":
                self._set_debug_state("paused_manual", reason="manual")
            elif status == "resumed":
                self._set_debug_state("running")
            elif status == "stopped":
                self._set_debug_state("stopped")
            elif status == "reset":
                self._set_debug_state("idle")
            elif status == "error":
                self._set_debug_state("error", reason="error")
            self._push_event("status", {"status": mapped, "raw_status": status})

    def _on_debug(self, payload: dict[str, Any]) -> None:
        with self._lock:
            normalized = dict(payload)
            debug_context = {
                "line": normalized.get("line"),
                "stack": normalized.get("stack"),
                "locals": normalized.get("locals"),
                "watches": normalized.get("watches"),
            }
            if any(debug_context.get(key) is not None for key in ("stack", "locals", "watches")):
                self._latest_debug_context = debug_context
                if self._debugstate_v2_enabled:
                    self._push_event("debug_context", self._latest_debug_context)
            event_type = str(normalized.get("type", ""))
            if self._status in {"stopped", "created", "expired", "error"} and event_type in {"line", "paused"}:
                return
            line = normalized.get("line")
            function_name = normalized.get("function")
            reason = normalized.get("reason")
            if event_type == "paused":
                debug_state = "paused_breakpoint" if reason == "breakpoint" else "paused_step"
                self._set_debug_state(
                    debug_state,
                    line=line,
                    function=function_name,
                    reason=reason or "step",
                    legacy=normalized,
                )
                return
            if event_type == "line":
                self._set_debug_state(
                    "running",
                    line=line,
                    function=function_name,
                    legacy=normalized,
                )
                return
            self._set_debug_state(
                self._latest_debug.get("debug_state", "idle") if isinstance(self._latest_debug, dict) else "idle",
                line=line,
                function=function_name,
                reason=reason,
                legacy=normalized,
            )

    @staticmethod
    def _utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    @staticmethod
    def _debug_capabilities(debug_state: str) -> tuple[bool, bool]:
        can_continue = debug_state in {"paused_breakpoint", "paused_step", "paused_manual"}
        can_step = debug_state in {"paused_breakpoint", "paused_step", "paused_manual"}
        return can_continue, can_step

    def _build_debug_state(
        self,
        debug_state: str,
        *,
        line: int | None = None,
        function: str | None = None,
        reason: str | None = None,
        legacy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "debug_state": debug_state,
            "breakpoints": sorted(self._debug_breakpoints),
            "watches": list(self._debug_watches),
            "timestamp": self._utc_now_iso(),
        }
        can_continue, can_step = self._debug_capabilities(debug_state)
        payload["can_continue"] = can_continue
        payload["can_step"] = can_step

        if line is not None:
            try:
                payload["line"] = int(line)
            except (TypeError, ValueError):
                pass
        elif isinstance(self._latest_debug, dict) and isinstance(self._latest_debug.get("line"), int):
            if debug_state.startswith("paused_"):
                payload["line"] = int(self._latest_debug["line"])

        if function:
            payload["function"] = str(function)
        elif isinstance(self._latest_debug, dict) and self._latest_debug.get("function") and debug_state.startswith("paused_"):
            payload["function"] = str(self._latest_debug["function"])

        if reason:
            payload["reason"] = str(reason)

        if legacy:
            for key, value in legacy.items():
                if key == "watches":
                    continue
                payload[key] = value
        return payload

    def _set_debug_state(
        self,
        debug_state: str,
        *,
        line: int | None = None,
        function: str | None = None,
        reason: str | None = None,
        legacy: dict[str, Any] | None = None,
    ) -> None:
        self._latest_debug = self._build_debug_state(
            debug_state,
            line=line,
            function=function,
            reason=reason,
            legacy=legacy,
        )
        self._push_event("debug", self._latest_debug)
        if self._debugstate_v2_enabled:
            self._push_event("debug_state", self._latest_debug)

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

    def _prune_start_idempotency(self, now: float | None = None) -> None:
        if self._start_idempotency_ttl_s <= 0:
            self._start_idempotency.clear()
            return
        now_value = time.monotonic() if now is None else now
        expired = [
            key
            for key, (created_at, _) in self._start_idempotency.items()
            if now_value - created_at > self._start_idempotency_ttl_s
        ]
        for key in expired:
            self._start_idempotency.pop(key, None)

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
