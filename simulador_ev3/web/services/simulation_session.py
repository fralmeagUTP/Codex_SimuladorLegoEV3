"""Per-user web simulation session wrapper."""

from __future__ import annotations

import json
import re
import tempfile
import threading
import time
from collections import deque
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from simulador_ev3.application.interface_ports import (
    LearningPort,
    LearningState,
    ObservabilityPort,
    ObservabilitySnapshot,
    PresentationPort,
    PresentationState,
)
from simulador_ev3.application.session_contract import SessionEvent
from simulador_ev3.application.simulation_service import SimulationService
from simulador_ev3.application.simulation_session_port import SimulationSessionPort
from simulador_ev3.application.snapshot_dto import SnapshotDTO
from simulador_ev3.application.world_editor_service import WorldEditorService
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.domain.assessment import MissionDefinition
from simulador_ev3.domain.editor.world_editor_model import (
    CELL_SIZE_MM,
    DEFAULT_WORLD_CELLS,
    DEFAULT_WORLD_MM,
    GRID_SIZE_PX,
    get_asset_spec,
)
from simulador_ev3.persistence.world_repository import WorldRepository
from simulador_ev3.runtime.execution_policy import ExecutionPolicy
from simulador_ev3.runtime.isolated_worker import IsolatedRuntimeWorker, worker_isolation_enabled
from simulador_ev3.shared.asset_catalog import editor_asset_manifest
from simulador_ev3.shared.debug_configuration import normalize_breakpoints, normalize_watches
from simulador_ev3.shared.interface_catalog import controls_for_status, is_supported_runtime_limit, message_for_status
from simulador_ev3.shared.learning_catalog import initial_learning_route
from simulador_ev3.shared.session_status import SessionStatus, can_transition
from simulador_ev3.web.errors import InvalidPayload, InvalidSessionState
from simulador_ev3.web.services.world_dto import world_to_dict


class SimulationSession(SimulationSessionPort, PresentationPort, LearningPort, ObservabilityPort):
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
        self._max_runtime_s = float(max_runtime_s)
        self._lock = threading.RLock()
        self._events_ready = threading.Condition(self._lock)
        self._events: deque[dict[str, Any]] = deque(maxlen=300)
        self._sequence = 0
        self._source_code: str | None = None
        self._latest_snapshot: dict[str, Any] | None = None
        self._snapshot_generation = 0
        self._latest_error: dict[str, Any] | None = None
        self._latest_debug: dict[str, Any] | None = None
        self._latest_debug_context: dict[str, Any] | None = None
        self._last_snapshot_event_at = 0.0
        snapshot_hz = float(self._config.get("WEB_SNAPSHOT_MAX_HZ", 30.0))
        self._snapshot_event_interval_s = 0.0 if snapshot_hz <= 0 else 1.0 / snapshot_hz
        self._debug_breakpoints: set[int] = set()
        self._debug_watches: list[str] = []
        self._debugstate_v2_enabled = bool(self._config.get("DEBUGSTATE_V2_ENABLED", True))
        self._start_idempotency: dict[str, tuple[float, dict[str, Any]]] = {}
        self._start_idempotency_ttl_s = float(self._config.get("START_IDEMPOTENCY_TTL_S", 20.0))
        self._status = SessionStatus.CREATED.value
        self._loaded_world_name: str | None = None
        self._active_mission: MissionDefinition | None = None
        self._latest_mission_result: dict[str, Any] | None = None
        self._editor = WorldEditorService()
        self._world_has_editor_spec = False
        self._service = SimulationService(
            config=SimEngineConfig(
                world_width_mm=DEFAULT_WORLD_MM,
                world_height_mm=DEFAULT_WORLD_MM,
            ),
            policy=ExecutionPolicy(max_runtime_s=max_runtime_s),
        )
        self._worker_shadow: IsolatedRuntimeWorker | None = None
        self._worker_shadow_last_sequence = 0
        self._worker_shadow_snapshot: dict[str, Any] | None = None
        self._worker_shadow_status: str | None = None
        self._reset_in_progress = False
        self._worker_diagnostics: dict[str, int | float | str] = {}
        self._last_command_id: str | None = None
        if worker_isolation_enabled():
            self._worker_shadow = IsolatedRuntimeWorker(f"web-shadow-{session_id}")
            self._worker_shadow.start()
            self._worker_shadow.receive()
            self._mirror_worker(
                "initialize",
                {
                    "execution_policy": {
                        "max_runtime_s": max(1.0, float(max_runtime_s)),
                        "max_memory_mb": 256,
                        "max_cpu_s": max(1.0, float(max_runtime_s)),
                    },
                    "engine_config": asdict(self._service.engine_config),
                    "snapshot_hz": snapshot_hz,
                },
            )
        self._wire_callbacks()
        if self._worker_shadow is not None:
            # La primera vista de una sesión aislada también debe proceder del
            # worker. Sin este snapshot, ``GET /snapshot`` construía un tick
            # local y el primer paso manual devolvía el mismo tick del worker.
            with self._lock:
                self._mirror_worker("snapshot")
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
            if self._status in {"created", "stopped", "finished", "error", "timed_out"}:
                self._transition(SessionStatus.READY)
            self._mirror_worker("load_script", {"source": source})
            # Sin este snapshot inicial, el primer ``step_tick`` del worker
            # podía coincidir con el snapshot local previo y el navegador no
            # observaba ningún incremento de tick.
            self._mirror_worker("snapshot")
            self._latest_error = None
            self._set_debug_state("idle")
            self._push_event("status", {"status": self._status})
            return self.summary()

    @property
    def _worker_executes(self) -> bool:
        """El worker es la unica ruta de ejecucion cuando el aislamiento esta activo."""
        return self._worker_shadow is not None

    def start(
        self,
        *,
        debug: bool = False,
        step_mode: bool = False,
        source: str | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            if source is not None:
                if not isinstance(source, str):
                    raise InvalidPayload("El campo source debe ser texto.")
                max_size = int(self._config.get("MAX_SCRIPT_SIZE_BYTES", 128 * 1024))
                if len(source.encode("utf-8")) > max_size:
                    raise InvalidPayload("El script excede el tamano maximo permitido.")
                # Ruta de baja latencia usada por la Web: el mismo comando IPC
                # carga y ejecuta el programa. Antes se esperaban por separado
                # ``load_script`` y ``start``, lo que retrasaba visualmente los
                # programas cortos aunque el motor ya tuviera capacidad libre.
                self._source_code = source
                self._service.load_script(source)
                if self._status in {"created", "stopped", "finished", "error", "timed_out"}:
                    self._transition(SessionStatus.READY)
            if not self._source_code:
                raise InvalidSessionState("No hay script cargado para ejecutar.")
            if debug:
                self._service.set_debug_breakpoints(self._debug_breakpoints)
                self._service.set_debug_watches(self._debug_watches)
            # El worker puede alcanzar un breakpoint inmediatamente al arrancar.
            # La transición debe ocurrir antes de enviar el comando: de otro
            # modo ``ready -> paused`` se descarta y la pausa queda oculta.
            self._transition(SessionStatus.RUNNING)
            self._set_debug_state("running")
            if not self._worker_executes:
                self._service.start(debug=debug, step_mode=step_mode)
            worker_payload: dict[str, Any] = {"debug": debug, "step_mode": step_mode}
            if source is not None:
                worker_payload["source"] = source
            self._mirror_worker("start", worker_payload)
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
            if not self._worker_executes:
                self._service.pause()
            self._mirror_worker("pause")
            self._transition(SessionStatus.PAUSED)
            self._set_debug_state("paused_manual", reason="manual")
            # El resumen de telemetría depende exclusivamente del snapshot.
            # Publicarlo tras la transición evita que la barra diga "paused"
            # mientras el panel conserva el estado anterior "running".
            self._publish_current_snapshot()
            self._push_event("status", {"status": self._status})
            return self.summary()

    def resume(self) -> dict[str, Any]:
        with self._lock:
            if not self._worker_executes:
                self._service.resume()
            self._mirror_worker("resume")
            self._transition(SessionStatus.RUNNING)
            self._set_debug_state("running")
            self._publish_current_snapshot()
            self._push_event("status", {"status": self._status})
            return self.summary()

    def stop(self) -> dict[str, Any]:
        with self._lock:
            self._transition(SessionStatus.STOPPED)
            self._set_debug_state("stopped")
            if not self._worker_executes:
                self._service.stop()
            self._mirror_worker("stop")
            # El estado stopped no puede adelantar al último snapshot visible:
            # canvas, telemetría y LCD deben conservar la misma pose terminal.
            self._publish_current_snapshot()
            self._push_event("status", {"status": self._status})
            self._complete_mission("cancelled")
            return self.summary()

    def reset(self) -> dict[str, Any]:
        with self._lock:
            self._reset_in_progress = True
            try:
                self._transition(SessionStatus.RESETTING)
                # Descartar el espejo antes de crear una nueva generación: ningún
                # snapshot de la ejecución anterior debe poder restaurar la UI.
                self._drain_shadow_worker()
                self._snapshot_generation += 1
                self._worker_shadow_snapshot = None
                self._worker_shadow_status = None
                self._last_snapshot_event_at = 0.0
                self._service.reset()
                self._mirror_worker("reset", discard_unrelated_events=True, wait_for_status="reset")
                # El comando reset genera primero las notificaciones de parada del
                # runtime. Su snapshot final pertenece a la ejecución cancelada,
                # por lo que no puede ser el estado visible posterior al reinicio.
                self._worker_shadow_snapshot = None
                self._worker_shadow_status = None
                self._wire_callbacks()
                self._source_code = None
                self._active_mission = None
                self._latest_mission_result = None
                self._latest_error = None
                self._latest_debug_context = None
                self._debug_breakpoints = set()
                self._debug_watches = []
                self._start_idempotency.clear()
                self._transition(SessionStatus.CREATED)
                self._set_debug_state("idle")
                # Se decora tras la transición para que telemetría, canvas y el
                # resumen de sesión reciban el mismo estado terminal: ``created``.
                # ``get_snapshot`` avanza el motor un tick para compatibilidad
                # con pruebas antiguas. Tras reiniciar necesitamos una lectura
                # pura: el canvas, LCD y telemetrÃ­a deben volver al tick 0.
                initial_dto = self._service.current_snapshot()
                initial = self._decorate_snapshot(initial_dto.to_dict() if initial_dto is not None else None)
                self._latest_snapshot = initial
                if initial is not None:
                    self._push_event("snapshot", initial)
                self._push_event("status", {"status": self._status})
                return self.summary()
            finally:
                self._reset_in_progress = False

    def select_mission(self, mission: MissionDefinition) -> dict[str, Any]:
        """Activa la evaluación de la misión cargada por la interfaz."""
        with self._lock:
            self._active_mission = mission
            self._latest_mission_result = None
            self._service.activate_mission(mission)
            self._push_event(
                "mission",
                {
                    "event_version": 1,
                    "mission": {"id": mission.identifier, "title": mission.title, "version": mission.version},
                },
            )
            return self.summary()

    def _complete_mission(self, outcome: str) -> dict[str, Any] | None:
        if self._active_mission is None or self._latest_mission_result is not None:
            return None
        payload = self._service.complete_active_mission(outcome)
        if payload is None:
            return None
        payload = dict(payload)
        payload["snapshot_generation"] = self._snapshot_generation
        self._latest_mission_result = payload
        self._push_event("mission_result", payload)
        return payload

    def set_max_runtime_s(self, max_runtime_s: float) -> dict[str, Any]:
        """Configura el watchdog de la sesion antes de iniciar una ejecucion."""
        value = float(max_runtime_s)
        if not is_supported_runtime_limit(value):
            raise InvalidPayload("El tiempo maximo debe ser 30, 60, 120, 300 o 0 (sin limite).")
        with self._lock:
            if self._status in {SessionStatus.RUNNING.value, SessionStatus.PAUSED.value}:
                raise InvalidSessionState("No se puede cambiar el tiempo maximo durante una simulacion activa.")
            self._service.set_max_runtime_s(value)
            self._mirror_worker("set_max_runtime", {"max_runtime_s": value})
            self._max_runtime_s = value
            payload = {"max_runtime_s": value, "label": "Sin limite" if value == 0 else f"{value:.0f} s"}
            self._push_event("runtime_limit", payload)
            return self.summary() | payload

    def set_debug_breakpoints(self, breakpoints: set[int]) -> dict[str, Any]:
        with self._lock:
            self._debug_breakpoints = normalize_breakpoints(breakpoints)
            self._service.set_debug_breakpoints(self._debug_breakpoints)
            self._mirror_worker(
                "set_debug", {"breakpoints": sorted(self._debug_breakpoints), "watches": list(self._debug_watches)}
            )
            payload = {"breakpoints": sorted(self._debug_breakpoints)}
            self._set_debug_state(
                self._latest_debug.get("debug_state", "idle") if isinstance(self._latest_debug, dict) else "idle",
                legacy={"type": "breakpoints", **payload},
            )
            return payload

    def set_debug_watches(self, watches: list[str]) -> dict[str, Any]:
        with self._lock:
            self._debug_watches = normalize_watches(watches)
            self._service.set_debug_watches(self._debug_watches)
            self._mirror_worker(
                "set_debug", {"breakpoints": sorted(self._debug_breakpoints), "watches": list(self._debug_watches)}
            )
            payload = {"watches": list(self._debug_watches)}
            self._set_debug_state(
                self._latest_debug.get("debug_state", "idle") if isinstance(self._latest_debug, dict) else "idle",
                legacy={"type": "watches", **payload},
            )
            return payload

    def set_simulation_profile(self, profile: str, calibration: dict[str, float] | None = None) -> dict[str, Any]:
        with self._lock:
            if self._status in {SessionStatus.RUNNING.value, SessionStatus.PAUSED.value}:
                raise InvalidSessionState("No se puede cambiar el perfil durante una simulacion activa.")
            self._service.set_simulation_profile(profile, calibration)
            self._mirror_worker("set_simulation_profile", {"profile": profile, "calibration": calibration or {}})
            self._latest_snapshot = None
            payload = {
                "profile": self._service.engine_config.simulation_profile,
                "calibration": self._service.engine_config.calibration,
            }
            self._push_event("profile", payload)
            return payload

    def step_tick(self) -> dict[str, Any]:
        with self._lock:
            if self._status in {SessionStatus.RUNNING.value, SessionStatus.PAUSED.value}:
                raise InvalidSessionState("El paso de tick requiere una simulacion detenida.")
            if self._worker_executes:
                # El worker aislado es la fuente de verdad para snapshots. El
                # avance local dejaba visible el snapshot previo del worker.
                self._mirror_worker("step_tick")
                snapshot = self._worker_shadow_snapshot
            else:
                snapshot = self._decorate_snapshot(self._service.step_tick().to_dict())
            if snapshot is None:
                raise RuntimeError("No fue posible generar el snapshot de la sesión.")
            self._latest_snapshot = snapshot
            self._push_event("snapshot", snapshot)
            return snapshot

    def start_trace(self) -> None:
        with self._lock:
            self._service.start_trace()

    def stop_trace(self) -> None:
        with self._lock:
            self._service.stop_trace()

    def export_trace(self, format: str = "json") -> str:
        with self._lock:
            return self._service.export_trace(format)

    def debug_continue(self) -> dict[str, Any]:
        with self._lock:
            if not self._worker_executes:
                self._service.debug_continue()
                self._service.resume()
            self._mirror_worker("debug_continue")
            changed = self._transition(SessionStatus.RUNNING)
            payload = {"type": "command", "status": self._status, "action": "continue"}
            self._set_debug_state("running", legacy=payload)
            if changed:
                self._publish_current_snapshot()
                self._push_event("status", {"status": self._status, "raw_status": "debug_continue"})
            return payload

    def debug_step(self) -> dict[str, Any]:
        with self._lock:
            if not self._worker_executes:
                self._service.debug_step()
                self._service.resume()
            self._mirror_worker("debug_step")
            changed = self._transition(SessionStatus.RUNNING)
            payload = {"type": "command", "status": self._status, "action": "step"}
            self._set_debug_state("running", legacy=payload)
            if changed:
                self._publish_current_snapshot()
                self._push_event("status", {"status": self._status, "raw_status": "debug_step"})
            return payload

    def set_robot_start(
        self,
        x_mm: float,
        y_mm: float,
        theta_deg: float | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            self._service.set_robot_start(float(x_mm), float(y_mm), theta_deg)
            self._mirror_worker("set_robot_start", {"x_mm": x_mm, "y_mm": y_mm, "theta_deg": theta_deg})
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
            # Una carga de mundo inicia una nueva representacion visual. El
            # worker puede conservar snapshots encolados de una ejecucion
            # anterior; no pueden ganar prioridad sobre la pose inicial del
            # robot que acaba de definir el mundo.
            self._replace_visible_snapshot_for_loaded_world()
            self._mirror_worker(
                "load_world",
                {"source": path.read_text(encoding="utf-8")},
                discard_unrelated_events=True,
            )
            self._sync_editor_from_world_file(path)
            self._loaded_world_name = name
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
            self._replace_visible_snapshot_for_loaded_world()
            self._mirror_worker("load_world", {"source": raw}, discard_unrelated_events=True)
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
            self._replace_visible_snapshot_for_loaded_world()
            self._mirror_worker(
                "load_blank_world",
                {"width_mm": w_mm, "height_mm": h_mm},
                discard_unrelated_events=True,
            )
            self._editor.reset_formal_world(w_cells, h_cells)
            self._world_has_editor_spec = True
            self._loaded_world_name = None
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
            self._drain_shadow_worker()
            snapshot = self._worker_shadow_snapshot or self._latest_snapshot
            if snapshot is None:
                dto = self._service.get_snapshot()
                snapshot = dto.to_dict() if dto else None
            # La copia del worker puede haberse producido en el último tick de
            # ejecución, antes del evento terminal. Nunca debe devolver
            # ``running`` cuando el estado autoritativo de sesión ya es
            # ``finished``/``error``/etc.; telemetría, LCD y canvas consumen
            # este mismo DTO.
            snapshot = self._decorate_snapshot(snapshot)
            self._latest_snapshot = snapshot
            if self._worker_shadow_snapshot is not None:
                self._worker_shadow_snapshot = snapshot
            return {
                "session_id": self.session_id,
                "status": self._status,
                "sequence": self._sequence,
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

        raise InvalidPayload("Formato de mundo no soportado. Se esperaba editor_spec o editor_objects.")

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
            self._service.apply_world_model(world)
            self._replace_visible_snapshot_for_loaded_world()
            worker_source = json.dumps(
                {"version": 1, "editor_spec": self._editor.current_formal_world().to_dict()},
                ensure_ascii=False,
            )
            self._mirror_worker("load_world", {"source": worker_source}, discard_unrelated_events=True)
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
        world = self._service.current_world_model
        if world is None:
            return None
        editor_spec = self._editor.current_formal_world().to_dict() if self._world_has_editor_spec else None
        return world_to_dict(
            world,
            editor_spec=editor_spec,
        )

    def events_since(self, sequence: int = 0) -> list[dict[str, Any]]:
        with self._lock:
            self._drain_shadow_worker()
            return [event for event in self._events if event["sequence"] > sequence]

    def wait_for_events_since(
        self,
        sequence: int = 0,
        *,
        timeout_s: float = 0.0,
    ) -> list[dict[str, Any]]:
        timeout = max(0.0, float(timeout_s))
        with self._events_ready:
            self._drain_shadow_worker()
            if self._sequence <= sequence and timeout > 0:
                self._events_ready.wait(timeout=timeout)
            self._drain_shadow_worker()
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
            "simulation_profile": self._service.engine_config.simulation_profile,
            "active_mission": (
                {"id": self._active_mission.identifier, "title": self._active_mission.title}
                if self._active_mission is not None
                else None
            ),
            "mission_result": self._latest_mission_result,
        }

    def presentation_state(self) -> PresentationState:
        """DTO estable para que una UI no tenga que inspeccionar el runtime."""
        status = self.status
        return PresentationState(
            session_id=self.session_id,
            status=status,
            controls=controls_for_status(status),
            message=str((self._latest_error or {}).get("message", "")) or message_for_status(status),
        )

    def learning_state(self) -> LearningState:
        mission = self._active_mission
        result = self._latest_mission_result or {}
        route = initial_learning_route()
        completed = bool(result.get("result", {}).get("passed")) or (
            mission is None and self.status == SessionStatus.FINISHED.value
        )
        return LearningState(
            session_id=self.session_id,
            activity_id=mission.identifier if mission is not None else route.identifier,
            objective=mission.title if mission is not None else route.objective,
            next_step=route.practice,
            result="Actividad completada." if completed else None,
            progress_current=1 if completed else 0,
            progress_total=1,
        )

    def observability_snapshot(self) -> ObservabilitySnapshot:
        response = self.snapshot_response()
        snapshot = response.get("snapshot") or {}
        error = response.get("error") or {}
        return ObservabilitySnapshot(
            session_id=self.session_id,
            command_id=self._last_command_id,
            worker_id=f"web-shadow-{self.session_id}" if self._worker_shadow is not None else None,
            status=self.status,
            tick=int(snapshot["tick"]) if snapshot.get("tick") is not None else None,
            simulation_time_s=float(snapshot["sim_time_s"]) if snapshot.get("sim_time_s") is not None else None,
            error_code=str(error.get("code")) if error.get("code") else None,
        )

    def runtime_checkpoint(self) -> dict[str, Any]:
        with self._lock:
            world_snapshot = self.current_world()
            world_wrapper = {"version": 1, "world": world_snapshot} if world_snapshot else None
            editor_world = self._editor.current_formal_world().to_dict() if self._world_has_editor_spec else None
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
                self._transition(SessionStatus.READY if self._source_code else SessionStatus.CREATED)
                self._set_debug_state("idle", reason="recovered")
                self._push_event("status", {"status": self._status, "raw_status": "recovered"})

            return self.summary() | {"restored_world": restored_world}

    def close(self) -> None:
        with self._lock:
            if self._worker_shadow is not None:
                self._worker_shadow.close()
            self._service.stop(reason="session_close")
            self._transition(SessionStatus.EXPIRED)
            self._set_debug_state("stopped")
            self._push_event("status", {"status": self._status})

    def _mirror_worker(
        self,
        command: str,
        payload: dict[str, Any] | None = None,
        *,
        discard_unrelated_events: bool = False,
        wait_for_status: str | None = None,
    ) -> str | None:
        """Espeja un comando en el worker sin publicar sus eventos en la sesión visible."""
        if self._worker_shadow is None:
            return None
        command_id = self._worker_shadow.send(command, payload)
        self._last_command_id = command_id
        for _ in range(20):
            try:
                event = self._worker_shadow.receive(0.2)
            except TimeoutError:
                continue
            if discard_unrelated_events and event.get("command_id") != command_id:
                continue
            self._consume_shadow_event(event)
            if event.get("command_id") != command_id:
                continue
            if wait_for_status is None:
                return command_id
            if event.get("type") == "status" and event.get("payload", {}).get("status") == wait_for_status:
                return command_id
        raise TimeoutError(f"El worker sombra no confirmó {command}")

    def _drain_shadow_worker(self) -> None:
        if self._worker_shadow is None:
            return
        for event in self._worker_shadow.drain_events():
            self._consume_shadow_event(event)

    def worker_diagnostics(self) -> dict[str, int | float | str]:
        """Diagnostico público y no bloqueante del worker asociado a la sesión."""
        with self._lock:
            if self._worker_shadow is not None:
                try:
                    self._worker_shadow.send("heartbeat")
                except RuntimeError:
                    self._worker_diagnostics["worker_alive"] = 0
                self._drain_shadow_worker()
            return {"worker_alive": int(self._worker_shadow is not None), **self._worker_diagnostics}

    def recover_worker(self) -> dict[str, Any]:
        """Recrea un worker caído y repone el contrato mínimo de ejecución."""
        with self._lock:
            if self._worker_shadow is None:
                raise InvalidSessionState("La sesión no usa worker aislado.")
            self._worker_shadow.close()
            self._worker_shadow = IsolatedRuntimeWorker(f"web-recovered-{self.session_id}")
            # La secuencia IPC pertenece al proceso del worker, no a la
            # sesion. Un worker recuperado comienza en 1; conservar la ultima
            # secuencia del proceso anterior descartaria su inicializacion,
            # politica y snapshots como si fueran eventos atrasados.
            self._worker_shadow_last_sequence = 0
            self._worker_shadow_snapshot = None
            self._worker_shadow_status = None
            self._worker_shadow.start()
            self._consume_shadow_event(self._worker_shadow.receive())
            self._mirror_worker(
                "initialize",
                {
                    "execution_policy": {
                        # La recuperacion debe respetar el limite que el usuario
                        # eligio para *esta* sesion, no volver al valor global de
                        # configuracion. Esto mantiene el mismo contrato que la
                        # aplicacion de escritorio al reconstruir el worker.
                        "max_runtime_s": max(1.0, self._max_runtime_s),
                        "max_memory_mb": 256,
                        "max_cpu_s": max(1.0, self._max_runtime_s),
                    },
                    "engine_config": asdict(self._service.engine_config),
                },
            )
            if self._source_code:
                self._mirror_worker("load_script", {"source": self._source_code})
            self._mirror_worker(
                "set_debug",
                {"breakpoints": sorted(self._debug_breakpoints), "watches": list(self._debug_watches)},
            )
            self._worker_shadow_status = SessionStatus.READY.value if self._source_code else SessionStatus.CREATED.value
            self._transition(self._worker_shadow_status)
            self._push_event("status", {"status": self._status, "raw_status": "worker_recovered"})
            return self.summary()

    def _consume_shadow_event(self, event: dict[str, Any]) -> None:
        event = SessionEvent.from_dict(event).to_dict()
        worker_sequence = int(event.get("sequence", 0))
        # El pipe del worker puede entregar snapshots que estaban encolados
        # antes del reset. Nunca pueden reescribir una generación ya aplicada.
        if worker_sequence <= self._worker_shadow_last_sequence:
            return
        self._worker_shadow_last_sequence = worker_sequence
        if event.get("type") == "snapshot" and isinstance(event.get("payload"), dict):
            if self._reset_in_progress:
                return
            snapshot = self._decorate_snapshot(event["payload"])
            self._worker_shadow_snapshot = snapshot
            self._latest_snapshot = snapshot
            self._service.record_external_snapshot(SnapshotDTO(event["payload"]))
            if snapshot is not None:
                self._worker_diagnostics["last_tick"] = int(snapshot.get("tick", 0))
            now = time.monotonic()
            if now - self._last_snapshot_event_at >= self._snapshot_event_interval_s:
                self._last_snapshot_event_at = now
                self._push_event("snapshot", snapshot)
        if event.get("type") == "world_loaded" and isinstance(event.get("payload"), dict):
            # ``load_world`` responde con un evento propio, no con el evento
            # ``snapshot`` habitual. Consumir su snapshot evita que el canvas
            # conserve la pose de la mision o mundo anterior mientras el
            # nombre del mundo ya cambio en la interfaz.
            world_snapshot = event["payload"].get("snapshot")
            if isinstance(world_snapshot, dict):
                snapshot = self._decorate_snapshot(world_snapshot)
                self._worker_shadow_snapshot = snapshot
                self._latest_snapshot = snapshot
                self._service.record_external_snapshot(SnapshotDTO(world_snapshot))
                if snapshot is not None:
                    self._worker_diagnostics["last_tick"] = int(snapshot.get("tick", 0))
                    self._push_event("snapshot", snapshot)
            self._worker_shadow_status = SessionStatus.READY.value
            self._on_status("world_loaded")
        if event.get("type") == "status" and isinstance(event.get("payload"), dict):
            policy = event["payload"].get("execution_policy")
            if isinstance(policy, dict) and isinstance(policy.get("max_runtime_s"), (int, float)):
                self._worker_diagnostics["max_runtime_s"] = float(policy["max_runtime_s"])
            candidate = event["payload"].get("status")
            if candidate in {status.value for status in SessionStatus}:
                self._worker_shadow_status = candidate
                self._on_status(str(candidate))
        if event.get("type") == "heartbeat" and isinstance(event.get("payload"), dict):
            self._worker_diagnostics.update({
                key: value for key, value in event["payload"].items() if isinstance(value, (int, float, str))
            })
        if event.get("type") == "error" and isinstance(event.get("payload"), dict):
            self._on_error(event["payload"])
        if event.get("type") == "debug" and isinstance(event.get("payload"), dict):
            self._on_debug(event["payload"])

    def _wire_callbacks(self) -> None:
        self._service.set_snapshot_callback(self._on_snapshot)
        self._service.set_error_callback(self._on_error)
        self._service.set_status_callback(self._on_status)
        self._service.set_debug_callback(self._on_debug)

    def _on_snapshot(self, dto) -> None:
        data = self._decorate_snapshot(dto.to_dict())
        with self._lock:
            if self._reset_in_progress:
                return
            # RuntimeController puede finalizar el último callback justo al
            # detenerse. Tras reset ya no hay código cargado: conservar el
            # snapshot inicial evita que ese callback tardío restaure ticks,
            # LCD o telemetría de la misión anterior en modo local.
            if (
                self._status == SessionStatus.CREATED.value
                and self._source_code is None
                and self._latest_snapshot is not None
            ):
                return
            self._latest_snapshot = data
            now = time.monotonic()
            if now - self._last_snapshot_event_at >= self._snapshot_event_interval_s:
                self._last_snapshot_event_at = now
                self._push_event("snapshot", data)

    def _decorate_snapshot(self, snapshot: dict[str, Any] | None) -> dict[str, Any] | None:
        """Añade metadatos de sesión sin alterar el contrato del motor."""
        if snapshot is None:
            return None
        data = dict(snapshot)
        data["snapshot_generation"] = self._snapshot_generation
        # La telemetría se renderiza exclusivamente desde este DTO, por lo que
        # el estado de sesión se incorpora al mismo snapshot que canvas y LCD.
        data["status"] = self._status
        return data

    def _publish_current_snapshot(self) -> None:
        """Publica sin throttling el snapshot que corresponde al estado actual."""
        snapshot = self._worker_shadow_snapshot or self._latest_snapshot
        if snapshot is None:
            dto = self._service.get_snapshot()
            snapshot = dto.to_dict() if dto is not None else None
        snapshot = self._decorate_snapshot(snapshot)
        if snapshot is None:
            return
        self._latest_snapshot = snapshot
        self._push_event("snapshot", snapshot)

    def _replace_visible_snapshot_for_loaded_world(self) -> None:
        """Publica la pose inicial del mundo y descarta el snapshot anterior.

        La aplicacion web usa el worker aislado como fuente normal de eventos.
        Un script que acaba de finalizar puede dejar un snapshot terminal en
        su cola. Al seleccionar otro mundo, ese estado no pertenece a la nueva
        escena y no puede usarse para dibujar robot, LCD o telemetria.
        """
        self._snapshot_generation += 1
        self._worker_shadow_snapshot = None
        self._worker_shadow_status = None
        self._last_snapshot_event_at = 0.0
        self._latest_error = None
        self._latest_mission_result = None
        self._latest_debug_context = None
        self._transition(SessionStatus.READY)
        self._set_debug_state("idle")

        initial_dto = self._service.current_snapshot()
        initial = self._decorate_snapshot(initial_dto.to_dict() if initial_dto is not None else None)
        self._latest_snapshot = initial
        if initial is not None:
            self._push_event("snapshot", initial)
        self._push_event("status", {"status": self._status, "raw_status": "world_loaded"})

    def _on_error(self, payload: dict[str, Any]) -> None:
        with self._lock:
            if self._status in {"stopped", "created", "expired"}:
                return
            self._latest_error = dict(payload)
            error_reason = "timeout" if "tiempo m" in str(payload.get("error", "")).lower() else "error"
            target = SessionStatus.TIMED_OUT if error_reason == "timeout" else SessionStatus.ERROR
            if not self._transition(target):
                return
            self._set_debug_state(self._status, reason=error_reason)
            self._publish_current_snapshot()
            self._push_event("error", self._latest_error)

    def _on_status(self, status: str) -> None:
        if self._reset_in_progress:
            return
        if status == "error" and self._status in {"stopped", "created", "expired"}:
            return
        mapped = {
            "started": "running",
            "paused": "paused",
            "resumed": "running",
            "stopped": "stopped",
            "finished": "finished",
            "timed_out": "timed_out",
            "reset": "created",
            "error": "error",
            # Cargar un mundo siempre deja la sesion lista para una nueva
            # ejecucion; conservar ``finished`` aqui desincronizaba el canvas
            # de la pose inicial que ya habia cargado el motor.
            "world_loaded": "ready",
        }.get(status, status)
        with self._lock:
            # El worker confirma ``running`` después de iniciar el hilo de
            # script. Si el breakpoint ya pausó ese hilo, esa confirmación es
            # atrasada y no puede reanudar la sesión por sí sola. ``resumed``
            # conserva el camino explícito de Reanudar/Continuar.
            if (
                status == "running"
                and self._status == SessionStatus.PAUSED.value
                and isinstance(self._latest_debug, dict)
                and str(self._latest_debug.get("debug_state", "")).startswith("paused_")
            ):
                return
            if not self._transition(mapped):
                return
            if status == "started":
                self._set_debug_state("running")
            elif status == "paused":
                self._set_debug_state("paused_manual", reason="manual")
            elif status == "resumed":
                self._set_debug_state("running")
            elif status == "stopped":
                self._set_debug_state("stopped")
            elif status == "finished":
                self._set_debug_state("finished", reason="script_finished")
            elif status == "timed_out":
                self._set_debug_state("timed_out", reason="timeout")
            elif status == "reset":
                self._set_debug_state("idle")
            elif status == "error":
                self._set_debug_state("error", reason="error")
            if status in {"finished", "stopped", "timed_out", "reset", "error"}:
                self._publish_current_snapshot()
            self._push_event("status", {"status": mapped, "raw_status": status})
            outcome = {
                "finished": "finished",
                "stopped": "cancelled",
                "timed_out": "timed_out",
                "error": "error",
            }.get(mapped)
            if outcome is not None:
                self._complete_mission(outcome)

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
                changed = self._transition(SessionStatus.PAUSED)
                if not self._worker_executes:
                    self._service.pause()
                self._set_debug_state(
                    debug_state,
                    line=line,
                    function=function_name,
                    reason=reason or "step",
                    legacy=normalized,
                )
                if changed:
                    # Un breakpoint también pausa la sesión: editor, controles
                    # y telemetría deben recibir el mismo estado observable.
                    self._publish_current_snapshot()
                    self._push_event("status", {"status": self._status, "raw_status": "debug_paused"})
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
        elif (
            isinstance(self._latest_debug, dict)
            and self._latest_debug.get("function")
            and debug_state.startswith("paused_")
        ):
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
        self._events_ready.notify_all()

    def _transition(self, target: str | SessionStatus) -> bool:
        """Aplica una transición válida y descarta eventos de estado tardíos."""
        try:
            next_status = SessionStatus(target)
            current_status = SessionStatus(self._status)
        except ValueError as exc:
            raise InvalidSessionState(f"Estado de sesion no soportado: {target}.") from exc
        if current_status == next_status:
            return False
        if not can_transition(current_status, next_status):
            return False
        self._status = next_status.value
        return True

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
        "asset_catalog_version": 2,
        "assets": [
            {
                "key": item["asset_id"],
                "image": item["filename"],
                "sha256": item["sha256"],
                "source_width_px": item["source_width_px"],
                "source_height_px": item["source_height_px"],
                "type": item["type"],
                "layer": item["layer"],
                "width_cells": item["width_cells"],
                "height_cells": item["height_cells"],
                "logical_width_mm": item["logical_width_mm"],
                "logical_height_mm": item["logical_height_mm"],
                "placement_anchor": item["placement_anchor"],
                "visual_anchor": item["visual_anchor"],
                "connectors": item["connectors"],
            }
            for item in editor_asset_manifest()
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
    if len(raw) > 96:
        raise InvalidPayload("El nombre del mundo es demasiado largo.")
    # Permite nombres didacticos con espacios/acentos sin perder seguridad de ruta.
    if not re.fullmatch(r"[0-9A-Za-z_ \-().áéíóúÁÉÍÓÚñÑ]+", raw):
        raise InvalidPayload("Use solo letras, numeros, espacios y estos simbolos: _ - ( ) .")
    return f"{raw}.json"
