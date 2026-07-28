"""
simulation_service.py — Fachada de alto nivel para la sesión de simulación.

SimulationService es el punto de entrada único de la capa de aplicación.
Gestiona el ciclo de vida completo: crear engine, activar la API Pybricks,
cargar el script del usuario y orquestar RuntimeController.

La UI (Fase 7) solo debe interactuar con SimulationService —nunca con
RuntimeController, SimulationEngine ni PybricksFactory directamente.

Responsabilidades:
  1. Instanciar SimEngineConfig y SimulationEngine.
  2. Crear y registrar PybricksFactory (inyección de API virtual).
  3. Delegar arranque / pausa / parada al RuntimeController.
  4. Convertir cada StateSnapshot en SnapshotDTO y notificar callbacks de UI.
  5. Publicar errores de runtime a los callbacks de UI.
"""

from __future__ import annotations

import json
import math
import threading
from pathlib import Path
from typing import Callable, Optional

from simulador_ev3.application.mission_evaluator import MissionEvaluator
from simulador_ev3.application.simulation_trace import SimulationTrace
from simulador_ev3.application.snapshot_dto import SnapshotDTO
from simulador_ev3.application.world_editor_service import WorldEditorService
from simulador_ev3.core.event_bus import (
    EVENT_RUNTIME_ERROR,
    EVENT_SIMULATION_STOPPED,
)
from simulador_ev3.core.simulation_engine import SimEngineConfig, SimulationEngine
from simulador_ev3.core.simulation_profile import resolve_profile
from simulador_ev3.domain.assessment import MissionDefinition
from simulador_ev3.domain.editor.world_editor_model import (
    CELL_SIZE_MM,
    DEFAULT_WORLD_CELLS,
    GRID_SIZE_PX,
    MAX_WORLD_MM,
    MAX_WORLD_PIXELS,
    get_asset_spec,
)
from simulador_ev3.domain.robot.robot_model import Pose
from simulador_ev3.domain.world.beacon_model import BeaconModel
from simulador_ev3.domain.world.world_model import WorldModel
from simulador_ev3.persistence.world_repository import WorldRepository
from simulador_ev3.pybricks_api.factory import PybricksFactory
from simulador_ev3.runtime.execution_policy import ExecutionPolicy
from simulador_ev3.runtime.runtime_controller import ControllerState, RuntimeController

# Tipo de callback: recibe SnapshotDTO en cada tick
SnapshotCallback = Callable[[SnapshotDTO], None]
# Tipo de callback de error: recibe dict {"error": str, "traceback": str}
ErrorCallback = Callable[[dict], None]
# Tipo de callback de estado: recibe str ("started" | "stopped" | "error")
StatusCallback = Callable[[str], None]
# Tipo de callback de depuracion: recibe dict {"line": int}
DebugCallback = Callable[[dict], None]


class SimulationService:
    """
    Fachada de la capa de aplicación para la simulación EV3.

    Args:
        config:         Configuración del engine (posición inicial del robot,
                        dimensiones del mundo…).  Si None, se usan defaults.
        policy:         Política de sandbox (tiempo máximo, etc.).
                        Si None, se usa política por defecto sin límite.
        tick_rate_hz:   Frecuencia del engine thread.  50 Hz por defecto.

    Callbacks disponibles (opcionales, se registran con set_*):
        set_snapshot_callback(cb):  cb(SnapshotDTO) en cada tick.
        set_error_callback(cb):     cb(dict) cuando el script lanza excepción.
        set_status_callback(cb):    cb(str) al cambiar el estado del servicio.

    Ejemplo de uso mínimo:
        service = SimulationService()
        service.load_script(source)
        service.start()
        # ... UI llama a service.tick() o deja que EngineThread corra
        service.stop()
    """

    def __init__(
        self,
        config: Optional[SimEngineConfig] = None,
        policy: Optional[ExecutionPolicy] = None,
        tick_rate_hz: float = 50.0,
    ) -> None:
        self._config = config or SimEngineConfig()
        self._policy = policy or ExecutionPolicy()
        self._tick_rate_hz = tick_rate_hz

        # Se construyen en _rebuild()
        self._engine: Optional[SimulationEngine] = None
        self._controller: Optional[RuntimeController] = None
        self._stop_event: Optional[threading.Event] = None

        # Callbacks de UI
        self._snapshot_cb: Optional[SnapshotCallback] = None
        self._error_cb: Optional[ErrorCallback] = None
        self._status_cb: Optional[StatusCallback] = None
        self._debug_cb: Optional[DebugCallback] = None

        # Script actual
        self._source_code: Optional[str] = None
        self._loaded_world: Optional[WorldModel] = None
        self._debug_breakpoints: set[int] = set()
        self._debug_watches: list[str] = []
        self._latest_debug_event: dict | None = None
        self._trace = SimulationTrace()
        self._trace_recording = False
        self._active_mission: MissionDefinition | None = None
        self._mission_result: dict | None = None

        # Construir la infraestructura inicial
        self._rebuild()

    # ------------------------------------------------------------------
    # Configuración de callbacks
    # ------------------------------------------------------------------

    def set_snapshot_callback(self, cb: SnapshotCallback) -> None:
        self._snapshot_cb = cb
        if self._controller:
            self._controller.set_snapshot_callback(self._on_snapshot)

    def set_error_callback(self, cb: ErrorCallback) -> None:
        self._error_cb = cb

    def set_status_callback(self, cb: StatusCallback) -> None:
        self._status_cb = cb

    def set_debug_callback(self, cb: DebugCallback) -> None:
        self._debug_cb = cb
        if self._controller:
            self._controller.set_debug_callback(self._on_debug_event)

    @property
    def engine_config(self) -> SimEngineConfig:
        """Configuracion actual del motor para los adaptadores de interfaz."""
        return self._config

    @property
    def debug_configuration(self) -> dict[str, object]:
        """Configuración pública de depuración para adaptadores de interfaz."""
        return {"breakpoints": sorted(self._debug_breakpoints), "watches": list(self._debug_watches)}

    def world_visual_data(self) -> dict:
        """DTO de mundo para renderizado sin exponer atributos privados de dominio."""
        world = self._engine.world if self._engine is not None else None
        if world is None:
            return {"name": "Basico", "width_mm": 0.0, "height_mm": 0.0, "surface_cells": [], "obstacles": []}
        cell_size = world.surface.cell_size_mm
        return {
            "name": getattr(world, "name", "Basico"),
            "width_mm": world.width_mm,
            "height_mm": world.height_mm,
            "surface_cells": [
                {"x_mm": col * cell_size, "y_mm": row * cell_size, "size_mm": cell_size, "color": cell.color.name}
                for col, row, cell in world.surface.iter_defined_cells()
            ],
            "obstacles": [
                {
                    "x_mm": obstacle.aabb[0],
                    "y_mm": obstacle.aabb[1],
                    "width_mm": obstacle.aabb[2] - obstacle.aabb[0],
                    "height_mm": obstacle.aabb[3] - obstacle.aabb[1],
                    "name": getattr(obstacle, "name", "obstacle"),
                }
                for obstacle in world.obstacles
            ],
        }

    def set_simulation_profile(self, profile: str, calibration: dict[str, float] | None = None) -> None:
        """Cambia el perfil antes de ejecutar y reconstruye el motor de forma segura."""
        if self.is_running:
            raise RuntimeError("No se puede cambiar el perfil durante una simulacion activa.")
        resolve_profile(profile, calibration)
        self._config.simulation_profile = str(profile).lower()
        self._config.calibration = dict(calibration or {})
        self._rebuild()

    def start_trace(self) -> None:
        self._trace.clear()
        self._trace_recording = True

    def stop_trace(self) -> None:
        self._trace_recording = False

    def activate_mission(self, mission: MissionDefinition) -> None:
        """Asocia una misión a la próxima ejecución y registra su evidencia."""
        self._active_mission = mission
        self._mission_result = None
        self.start_trace()

    def clear_active_mission(self) -> None:
        self._active_mission = None
        self._mission_result = None

    @property
    def active_mission(self) -> MissionDefinition | None:
        return self._active_mission

    @property
    def mission_result(self) -> dict | None:
        return dict(self._mission_result) if self._mission_result is not None else None

    def complete_active_mission(self, outcome: str) -> dict | None:
        """Evalúa una misión una sola vez al finalizar, fallar o cancelar."""
        if self._active_mission is None or self._mission_result is not None:
            return None
        result = MissionEvaluator().evaluate(
            self._active_mission, self._trace, self._config.simulation_profile
        ).to_dict()
        if outcome in {"cancelled", "error", "timed_out"}:
            result["passed"] = False
            result["score"] = 0.0
        self.stop_trace()
        self._mission_result = {
            "event_version": 1,
            "outcome": outcome,
            "mission": {
                "id": self._active_mission.identifier,
                "title": self._active_mission.title,
                "version": self._active_mission.version,
            },
            "result": result,
        }
        return dict(self._mission_result)

    def record_external_snapshot(self, dto: SnapshotDTO) -> None:
        """Incorpora un snapshot emitido por un worker aislado a la traza."""
        if self._trace_recording:
            self._trace.record(dto.to_dict())

    def export_trace(self, format: str = "json") -> str:
        if format == "json":
            return self._trace.to_json()
        if format == "csv":
            return self._trace.to_csv()
        raise ValueError("format debe ser json o csv")

    def import_trace(self, payload: str) -> SimulationTrace:
        return SimulationTrace.from_json(payload)

    def step_tick(self) -> SnapshotDTO:
        """Avanza exactamente un tick fuera de una ejecución continua."""
        if self.is_running or self._engine is None:
            raise RuntimeError("El paso de tick requiere una simulacion detenida.")
        dto = SnapshotDTO.from_snapshot(self._engine.update(1 / self._tick_rate_hz))
        if self._trace_recording:
            self._trace.record(dto.to_dict())
        if self._snapshot_cb:
            self._snapshot_cb(dto)
        return dto

    def set_debug_breakpoints(self, breakpoints: set[int]) -> None:
        self._debug_breakpoints = {int(line) for line in breakpoints if int(line) > 0}
        if self._controller:
            self._controller.set_debug_breakpoints(self._debug_breakpoints)

    def set_debug_watches(self, watches: list[str]) -> None:
        self._debug_watches = [str(expr).strip() for expr in (watches or []) if str(expr).strip()]
        if self._controller:
            self._controller.set_debug_watches(self._debug_watches)

    def debug_continue(self) -> None:
        if self._controller:
            self._controller.debug_continue()

    def debug_step(self) -> None:
        if self._controller:
            self._controller.debug_step()

    def get_debug_state(self) -> dict | None:
        """Devuelve el ultimo payload de depuracion emitido por runtime."""
        if self._latest_debug_event is None:
            return None
        return dict(self._latest_debug_event)

    # ------------------------------------------------------------------
    # API de script
    # ------------------------------------------------------------------

    def load_script(self, source_code: str) -> None:
        """
        Carga el código fuente Python del usuario.
        Si la simulación corre, la detiene antes de cargar el nuevo script.
        """
        if self.is_running:
            self.stop()
        self._source_code = source_code
        self._latest_debug_event = None

    def set_robot_start(
        self,
        x_mm: float,
        y_mm: float,
        theta_deg: float | None = None,
    ) -> None:
        """
        Actualiza la posición inicial del robot para la siguiente ejecución.

        Los cambios surten efecto la próxima vez que se inicie la simulación
        (se usa en ``_rebuild`` al crear el engine fresco).

        Args:
            x_mm:      Posición X inicial en mm.
            y_mm:      Posición Y inicial en mm.
            theta_deg: Ángulo inicial en grados (None → no cambia).
        """
        self._config.robot_x0_mm = x_mm
        self._config.robot_y0_mm = y_mm
        if theta_deg is not None:
            self._config.robot_theta0_deg = theta_deg
        if self._engine is not None and not self.is_running:
            try:
                theta = math.radians(self._config.robot_theta0_deg)
                self._engine.robot.reset_pose(Pose(x=float(x_mm), y=float(y_mm), theta=theta))
            except Exception:  # noqa: BLE001
                pass

    def set_max_runtime_s(self, max_runtime_s: float) -> None:
        """Actualiza el watchdog para futuras ejecuciones sin perder el mundo activo."""
        value = float(max_runtime_s)
        if value < 0:
            raise ValueError("El tiempo maximo debe ser mayor o igual que cero.")
        if self.is_running or self.is_paused:
            raise RuntimeError("No se puede cambiar el tiempo maximo durante una simulacion activa.")
        self._policy = ExecutionPolicy(max_runtime_s=value)
        self._rebuild()

    @property
    def max_runtime_s(self) -> float:
        return float(self._policy.max_runtime_s)

    def load_world_file(self, path: str | Path) -> None:
        """
        Carga un mundo desde JSON y lo activa en el engine actual.

        Si la simulación está corriendo, se detiene antes de aplicar el cambio.
        """
        if self.is_running:
            self.stop(reason="world_change")
        world, robot_start = self._load_world_with_editor_physics(path)
        if world.width_mm > MAX_WORLD_MM or world.height_mm > MAX_WORLD_MM:
            raise ValueError(
                f"El mundo excede el maximo permitido ({MAX_WORLD_PIXELS} px por eje en visor/editor). "
                f"Tamano recibido: {world.width_mm:.0f}x{world.height_mm:.0f} mm."
            )
        self._loaded_world = world
        if self._engine is not None:
            self._engine.set_world(world)
        if robot_start is not None:
            x_mm, y_mm, theta_deg = robot_start
            self.set_robot_start(x_mm, y_mm, theta_deg)
        self._notify_status("world_loaded")

    def load_blank_world(self, width_mm: float | None = None, height_mm: float | None = None) -> None:
        """Carga un mundo vacío (sin obstáculos, líneas ni zonas) para empezar desde cero."""
        if self.is_running:
            self.stop(reason="world_change")

        target_w = float(width_mm) if width_mm is not None else float(DEFAULT_WORLD_CELLS * CELL_SIZE_MM)
        target_h = float(height_mm) if height_mm is not None else float(DEFAULT_WORLD_CELLS * CELL_SIZE_MM)
        if target_w > MAX_WORLD_MM or target_h > MAX_WORLD_MM:
            raise ValueError(
                f"El mundo excede el maximo permitido ({MAX_WORLD_PIXELS} px por eje en visor/editor). "
                f"Tamano recibido: {target_w:.0f}x{target_h:.0f} mm."
            )

        world = WorldModel(
            width_mm=target_w,
            height_mm=target_h,
        )
        self._loaded_world = world
        if self._engine is not None:
            self._engine.set_world(world)
        self._notify_status("world_loaded")

    def apply_world_model(self, world: WorldModel) -> None:
        """Activa un mundo ya validado por el editor mediante una API pública."""
        if self.is_running:
            self.stop(reason="world_change")
        self._loaded_world = world
        if self._engine is not None:
            self._engine.set_world(world)
        self._notify_status("world_loaded")

    @property
    def current_world_model(self) -> WorldModel | None:
        """Mundo activo para DTOs de aplicación, sin filtrar el engine privado."""
        return self._engine.world if self._engine is not None else None

    def _load_world_with_editor_physics(self, path: str | Path) -> tuple[WorldModel, tuple[float, float, float] | None]:
        src = Path(path)
        try:
            raw = json.loads(src.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                wrapped_beacons = self._extract_beacons_from_wrapped_world(raw)
                if isinstance(raw.get("editor_spec"), dict):
                    svc = WorldEditorService()
                    svc.load_json(src)
                    self._normalize_loaded_world_size_for_simulation(svc)
                    robot_start = self._extract_robot_start_from_editor_spec(raw["editor_spec"])
                    world = svc.to_world_model()
                    if wrapped_beacons:
                        world.beacons = wrapped_beacons
                    return world, robot_start

                if all(
                    key in raw for key in ("schema_version", "world_width_cells", "world_height_cells", "placements")
                ):
                    svc = WorldEditorService()
                    svc._formal_world = svc.load(json.dumps(raw, ensure_ascii=False))
                    self._normalize_loaded_world_size_for_simulation(svc)
                    robot_start = self._extract_robot_start_from_editor_spec(raw)
                    world = svc.to_world_model()
                    if wrapped_beacons:
                        world.beacons = wrapped_beacons
                    return world, robot_start

                if isinstance(raw.get("editor_objects"), dict):
                    svc = WorldEditorService()
                    svc.from_editor_dict(raw["editor_objects"])
                    self._normalize_loaded_world_size_for_simulation(svc)
                    return svc.to_world_model(), None

                if all(key in raw for key in ("world", "walls", "lines", "zones")):
                    svc = WorldEditorService()
                    svc.from_editor_dict(raw)
                    self._normalize_loaded_world_size_for_simulation(svc)
                    return svc.to_world_model(), None
        except Exception:  # noqa: BLE001
            pass
        return WorldRepository.load(src), None

    def _extract_beacons_from_wrapped_world(self, raw: dict) -> list[BeaconModel]:
        world_block = raw.get("world")
        if not isinstance(world_block, dict):
            return []
        beacon_items = world_block.get("beacons")
        if not isinstance(beacon_items, list):
            return []

        parsed: list[BeaconModel] = []
        for item in beacon_items:
            if not isinstance(item, dict):
                continue
            try:
                parsed.append(
                    BeaconModel(
                        x_mm=float(item["x_mm"]),
                        y_mm=float(item["y_mm"]),
                        channel=int(item.get("channel", 1)),
                        name=str(item.get("name", "beacon")),
                    )
                )
            except Exception:  # noqa: BLE001
                continue
        return parsed

    def _normalize_loaded_world_size_for_simulation(self, svc: WorldEditorService) -> None:
        """Preserve authored editor-world size; do not crop legacy maps silently."""
        world = svc.current_formal_world()
        if world.world_width_cells < 1:
            world.world_width_cells = DEFAULT_WORLD_CELLS
        if world.world_height_cells < 1:
            world.world_height_cells = DEFAULT_WORLD_CELLS

    def _extract_robot_start_from_editor_spec(self, editor_spec: dict) -> tuple[float, float, float] | None:
        placements = editor_spec.get("placements")
        if not isinstance(placements, list):
            return None
        grid_size_px = int(editor_spec.get("grid_size_px", GRID_SIZE_PX))
        if grid_size_px <= 0:
            grid_size_px = GRID_SIZE_PX
        mm_per_px = CELL_SIZE_MM / float(grid_size_px)

        for item in placements:
            if not isinstance(item, dict):
                continue
            asset_key = str(item.get("asset_key", "")).strip()
            spec = get_asset_spec(asset_key)
            if spec is None or spec.asset_type != "robot":
                continue

            x_px = int(item.get("x_px", item.get("x", 0)) or 0)
            y_px = int(item.get("y_px", item.get("y", 0)) or 0)
            rotation = int(item.get("rotation", 0)) % 360
            width_cells = spec.width_cells
            height_cells = spec.height_cells
            if rotation % 180 == 90:
                width_cells, height_cells = height_cells, width_cells

            x_mm = (x_px * mm_per_px) + ((width_cells * CELL_SIZE_MM) / 2.0)
            y_mm = (y_px * mm_per_px) + ((height_cells * CELL_SIZE_MM) / 2.0)
            return float(x_mm), float(y_mm), float(rotation)
        return None

    # ------------------------------------------------------------------
    # Control del ciclo de vida
    # ------------------------------------------------------------------

    def start(self, debug: bool = False, step_mode: bool = False) -> None:
        """
        Arranca la simulación.

        Si había una sesión previa detenida, reconstruye el engine
        fresh (reset de estado) antes de iniciar.
        """
        if self.is_running:
            return

        # Si el servicio ya fue usado y detenido, reconstruir engine fresco
        if self._controller and self._controller.state == ControllerState.STOPPED:
            PybricksFactory.cleanup()
            self._rebuild()

        if self._engine is None or self._controller is None or self._stop_event is None:
            raise RuntimeError("El servicio de simulación no se inicializó correctamente.")

        if self._loaded_world is not None:
            self._engine.set_world(self._loaded_world)

        mods = PybricksFactory.create(self._engine, self._stop_event)
        self._controller.set_pybricks_modules(mods)

        if self._source_code:
            self._controller.load_script(self._source_code)

        self._controller.set_debug_mode(debug)
        self._controller.set_debug_step_mode(step_mode if debug else False)
        self._controller.set_debug_breakpoints(self._debug_breakpoints if debug else set())
        self._controller.set_debug_watches(self._debug_watches if debug else [])
        self._controller.start()
        self._notify_status("started")

    def pause(self) -> None:
        """Pausa el engine (el script queda bloqueado en wait())."""
        if self._controller:
            self._controller.pause()
            self._notify_status("paused")

    def resume(self) -> None:
        """Reanuda el engine desde pausa."""
        if self._controller:
            self._controller.resume()
            self._notify_status("resumed")

    def stop(self, reason: str = "user_stop") -> None:
        """Detiene la simulación y limpia la sesión Pybricks."""
        if self._controller:
            self._controller.stop(reason=reason)
        PybricksFactory.cleanup()
        self._notify_status("stopped")

    def reset(self) -> None:
        """
        Detiene, resetea el engine y vuelve al estado IDLE.
        El script cargado se borra también.
        """
        self.stop(reason="reset")
        self._source_code = None
        self._latest_debug_event = None
        self._rebuild()
        self._notify_status("reset")

    def tick(self) -> Optional[SnapshotDTO]:
        """
        Ejecuta un tick manual del engine.

        Útil cuando la UI gestiona su propio mainloop (Tkinter widget.after).
        Devuelve None si la simulación no está activa.
        """
        if not self._controller:
            return None
        snap = self._controller.tick()
        if snap is None:
            return None
        return SnapshotDTO.from_snapshot(snap)

    # ------------------------------------------------------------------
    # Propiedades de estado
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        return self._controller is not None and self._controller.state == ControllerState.RUNNING

    @property
    def is_paused(self) -> bool:
        return self._controller is not None and self._controller.state == ControllerState.PAUSED

    @property
    def controller_state(self) -> Optional[ControllerState]:
        return self._controller.state if self._controller else None

    @property
    def engine(self) -> Optional[SimulationEngine]:
        """Acceso al engine (para tests e inspección)."""
        return self._engine

    @property
    def controller(self) -> Optional[RuntimeController]:
        """Acceso directo al controlador (para tests avanzados)."""
        return self._controller

    # ------------------------------------------------------------------
    # Acceso al último snapshot (sin callbacks)
    # ------------------------------------------------------------------

    def get_snapshot(self) -> Optional[SnapshotDTO]:
        """
        Fuerza un tick y devuelve el snapshot como DTO, sin avanzar tiempo.
        Método conveniente para tests donde no corre el EngineThread.
        """
        if not self._engine:
            return None
        snap = self._engine.update(1 / self._tick_rate_hz)
        return SnapshotDTO.from_snapshot(snap)

    def current_snapshot(self) -> Optional[SnapshotDTO]:
        """Obtiene el estado visual actual sin ejecutar un tick adicional."""
        if not self._engine:
            return None
        return SnapshotDTO.from_snapshot(self._engine.snapshot())

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------

    def _rebuild(self) -> None:
        """Crea un engine + controller frescos."""
        self._engine = SimulationEngine(config=self._config)
        if self._loaded_world is not None:
            self._engine.set_world(self._loaded_world)
        self._stop_event = threading.Event()
        self._controller = RuntimeController(
            engine=self._engine,
            bus=self._engine.event_bus,
            policy=self._policy,
            tick_rate_hz=self._tick_rate_hz,
        )
        # Registrar callbacks internos
        self._controller.set_snapshot_callback(self._on_snapshot)
        self._controller.set_debug_callback(self._on_debug_event)
        self._controller.set_debug_breakpoints(self._debug_breakpoints)
        self._controller.set_debug_watches(self._debug_watches)
        self._engine.event_bus.subscribe(EVENT_RUNTIME_ERROR, self._on_runtime_error)
        self._engine.event_bus.subscribe(EVENT_SIMULATION_STOPPED, self._on_simulation_stopped)

    def _on_snapshot(self, snapshot) -> None:
        """Callback que el RuntimeController invoca en cada tick."""
        dto = SnapshotDTO.from_snapshot(snapshot)
        if self._trace_recording:
            self._trace.record(dto.to_dict())
        if self._snapshot_cb:
            try:
                self._snapshot_cb(dto)
            except Exception:  # noqa: BLE001
                pass

    def _on_runtime_error(self, event: str, payload: dict) -> None:
        """Callback recibido cuando el script lanza una excepción."""
        if self._error_cb:
            try:
                self._error_cb(payload)
            except Exception:  # noqa: BLE001
                pass
        message = str((payload or {}).get("error", "")).lower()
        self._notify_status("timed_out" if "tiempo maximo" in message else "error")

    def _on_simulation_stopped(self, event: str, payload: dict) -> None:
        """Callback recibido cuando el controller detiene el engine internamente."""
        reason = str((payload or {}).get("reason", ""))
        if reason in {"script_error", "script_timed_out"}:
            return
        # Una finalizacion natural conserva el ultimo estado observable del
        # robot/brick. Las interfaces deciden cuando el usuario lo reinicia.
        if reason == "script_finished":
            self._notify_status("finished")
            return
        self._notify_status("stopped")

    def _on_debug_event(self, payload: dict) -> None:
        self._latest_debug_event = dict(payload)
        if self._debug_cb:
            try:
                self._debug_cb(payload)
            except Exception:  # noqa: BLE001
                pass

    def _notify_status(self, status: str) -> None:
        if self._status_cb:
            try:
                self._status_cb(status)
            except Exception:  # noqa: BLE001
                pass

    def __repr__(self) -> str:
        state = self._controller.state.name if self._controller else "NONE"
        return f"SimulationService(state={state})"
