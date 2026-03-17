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

import threading
from pathlib import Path
from typing import Callable, Optional

from simulador_ev3.core.event_bus import (
    EVENT_RUNTIME_ERROR,
    EVENT_SIMULATION_STARTED,
    EVENT_SIMULATION_STOPPED,
)
from simulador_ev3.core.simulation_engine import SimEngineConfig, SimulationEngine
from simulador_ev3.pybricks_api.factory import PybricksFactory
from simulador_ev3.persistence.world_repository import WorldRepository
from simulador_ev3.runtime.execution_policy import ExecutionPolicy
from simulador_ev3.runtime.runtime_controller import ControllerState, RuntimeController
from simulador_ev3.domain.world.world_model import WorldModel

from simulador_ev3.application.snapshot_dto import SnapshotDTO


# Tipo de callback: recibe SnapshotDTO en cada tick
SnapshotCallback = Callable[[SnapshotDTO], None]
# Tipo de callback de error: recibe dict {"error": str, "traceback": str}
ErrorCallback    = Callable[[dict], None]
# Tipo de callback de estado: recibe str ("started" | "stopped" | "error")
StatusCallback   = Callable[[str], None]


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
        self._config       = config or SimEngineConfig()
        self._policy       = policy or ExecutionPolicy(max_runtime_s=0)
        self._tick_rate_hz = tick_rate_hz

        # Se construyen en _rebuild()
        self._engine:     Optional[SimulationEngine]  = None
        self._controller: Optional[RuntimeController] = None
        self._stop_event: Optional[threading.Event]   = None

        # Callbacks de UI
        self._snapshot_cb: Optional[SnapshotCallback] = None
        self._error_cb:    Optional[ErrorCallback]    = None
        self._status_cb:   Optional[StatusCallback]   = None

        # Script actual
        self._source_code: Optional[str] = None
        self._loaded_world: Optional[WorldModel] = None

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

    def load_world_file(self, path: str | Path) -> None:
        """
        Carga un mundo desde JSON y lo activa en el engine actual.

        Si la simulación está corriendo, se detiene antes de aplicar el cambio.
        """
        if self.is_running:
            self.stop(reason="world_change")
        world = WorldRepository.load(path)
        self._loaded_world = world
        self._engine.set_world(world)
        self._notify_status("world_loaded")

    # ------------------------------------------------------------------
    # Control del ciclo de vida
    # ------------------------------------------------------------------

    def start(self) -> None:
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

        if self._loaded_world is not None:
            self._engine.set_world(self._loaded_world)

        mods = PybricksFactory.create(self._engine, self._stop_event)
        self._controller.set_pybricks_modules(mods)

        if self._source_code:
            self._controller.load_script(self._source_code)

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
        return (self._controller is not None
                and self._controller.state == ControllerState.RUNNING)

    @property
    def is_paused(self) -> bool:
        return (self._controller is not None
                and self._controller.state == ControllerState.PAUSED)

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

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------

    def _rebuild(self) -> None:
        """Crea un engine + controller frescos."""
        self._engine     = SimulationEngine(config=self._config)
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
        self._engine.event_bus.subscribe(
            EVENT_RUNTIME_ERROR, self._on_runtime_error
        )

    def _on_snapshot(self, snapshot) -> None:
        """Callback que el RuntimeController invoca en cada tick."""
        if self._snapshot_cb:
            try:
                dto = SnapshotDTO.from_snapshot(snapshot)
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
        self._notify_status("error")

    def _notify_status(self, status: str) -> None:
        if self._status_cb:
            try:
                self._status_cb(status)
            except Exception:  # noqa: BLE001
                pass

    def __repr__(self) -> str:
        state = self._controller.state.name if self._controller else "NONE"
        return f"SimulationService(state={state})"
