"""
runtime_controller.py — Controlador de ciclo de vida de la simulación.

Responsabilidades (SAD §9):
  1. Arrancar / pausar / detener la simulación.
  2. Ejecutar el loop de ticks del SimulationEngine en un EngineThread.
  3. Lanzar el RuntimeSandbox (ScriptThread) con el código del usuario.
  4. Publicar eventos de ciclo de vida al EventBus.

El EngineThread corre a 50 Hz (dt = 0.02 s) usando un bucle con sleep
preciso. Para la UI Tkinter (Fase 7) el controlador también soporta un
modo "widget.after()" donde Tkinter llama a tick() desde su mainloop.

Diagrama de hilos:
    MainThread (Tkinter / tests)
        RuntimeController.start()
            → EngineThread  loops engine.update(dt)
            → ScriptThread  runs user script

    RuntimeController.stop()
        → señala EngineThread / ScriptThread para terminar
"""

from __future__ import annotations

import threading
import time
from enum import Enum, auto
from typing import Optional

from simulador_ev3.core.event_bus import (
    EventBus,
)
from simulador_ev3.core.simulation_engine import SimulationEngine, StateSnapshot
from simulador_ev3.runtime.execution_policy import ExecutionPolicy
from simulador_ev3.runtime.runtime_sandbox import RuntimeSandbox, SandboxState


class ControllerState(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()


class RuntimeController:
    """
    Controla el ciclo de vida completo de la simulación.

    Args:
        engine:  Motor de simulación ya configurado.
        bus:     EventBus (puede ser el mismo del engine).
        policy:  Política de ejecución del script de usuario.
        tick_rate_hz: Frecuencia del EngineThread. Por defecto 50 Hz.

    Ejemplo de uso en tests:
        ctrl = RuntimeController(engine, bus, policy)
        ctrl.load_script("from pybricks.robotics import DriveBase\\n…")
        ctrl.start()
        time.sleep(1)
        ctrl.stop()
    """

    def __init__(
        self,
        engine: SimulationEngine,
        bus: Optional[EventBus] = None,
        policy: Optional[ExecutionPolicy] = None,
        tick_rate_hz: float = 50.0,
    ) -> None:
        self._engine = engine
        self._bus = bus or engine.event_bus
        self._policy = policy or ExecutionPolicy()
        self._dt = 1.0 / tick_rate_hz
        self._state = ControllerState.IDLE

        # Hilos
        self._engine_thread: Optional[threading.Thread] = None
        self._sandbox: Optional[RuntimeSandbox] = None

        # Señales
        self._stop_flag = threading.Event()
        self._pause_flag = threading.Event()  # set = pausado

        # Código de usuario
        self._source_code: Optional[str] = None
        self._pybricks_modules: dict = {}
        self._debug_mode: bool = False
        self._debug_step_mode: bool = False
        self._debug_breakpoints: set[int] = set()
        self._debug_watches: list[str] = []
        self._debug_cb = None

        # Callback opcional que la UI puede registrar para recibir snapshots
        self._snapshot_cb = None

        # Última excepción del sandbox (para tests)
        self._last_sandbox: Optional[RuntimeSandbox] = None

    # ------------------------------------------------------------------
    # Propiedades
    # ------------------------------------------------------------------

    @property
    def state(self) -> ControllerState:
        return self._state

    @property
    def engine(self) -> SimulationEngine:
        return self._engine

    @property
    def sandbox(self) -> Optional[RuntimeSandbox]:
        return self._last_sandbox

    # ------------------------------------------------------------------
    # Configuración previa al arranque
    # ------------------------------------------------------------------

    def load_script(self, source_code: str) -> None:
        """
        Carga el código fuente del script de usuario.
        Debe llamarse ANTES de start().
        """
        if self._state == ControllerState.RUNNING:
            raise RuntimeError("No se puede cargar el script mientras la simulación corre.")
        self._source_code = source_code

    def set_pybricks_modules(self, modules: dict) -> None:
        """
        Inyecta el namespace de la API Pybricks virtual en el sandbox.
        Llamado por la capa pybricks_api (Fase 5) durante la inicialización.
        """
        self._pybricks_modules = modules

    def set_snapshot_callback(self, callback) -> None:
        """
        Registra un callback(snapshot: StateSnapshot) que se invoca
        al final de cada tick del engine.  Útil para la UI.
        """
        self._snapshot_cb = callback

    def set_debug_mode(self, enabled: bool) -> None:
        """Activa/desactiva depuracion para la siguiente ejecucion."""
        self._debug_mode = bool(enabled)

    def set_debug_step_mode(self, enabled: bool) -> None:
        """Activa/desactiva pausa automatica en cada linea."""
        self._debug_step_mode = bool(enabled)

    def set_debug_breakpoints(self, breakpoints: set[int]) -> None:
        self._debug_breakpoints = {int(line) for line in breakpoints if int(line) > 0}
        if self._sandbox is not None:
            self._sandbox.set_debug_breakpoints(self._debug_breakpoints)

    def set_debug_watches(self, watches: list[str]) -> None:
        self._debug_watches = [str(expr).strip() for expr in (watches or []) if str(expr).strip()]
        if self._sandbox is not None:
            self._sandbox.set_debug_watches(self._debug_watches)

    def set_debug_callback(self, callback) -> None:
        """Registra callback para eventos de depuracion (linea ejecutada)."""
        self._debug_cb = callback

    def debug_continue(self) -> None:
        if self._sandbox is not None:
            self._sandbox.debug_continue()

    def debug_step(self) -> None:
        if self._sandbox is not None:
            self._sandbox.debug_step()

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def start(self) -> None:
        """
        Arranca el EngineThread y, si hay script cargado, el ScriptThread.

        Lanza RuntimeError si ya está en marcha.
        """
        if self._state == ControllerState.RUNNING:
            raise RuntimeError("El controlador ya está en marcha.")

        self._stop_flag.clear()
        self._pause_flag.clear()
        self._state = ControllerState.RUNNING

        # Notificar al engine
        self._engine.notify_started()

        # EngineThread
        self._engine_thread = threading.Thread(
            target=self._engine_loop,
            name="EngineThread",
            daemon=True,
        )
        self._engine_thread.start()

        # ScriptThread (opcional)
        if self._source_code:
            self._sandbox = RuntimeSandbox(
                source_code=self._source_code,
                policy=self._policy,
                event_bus=self._bus,
                pybricks_modules=self._pybricks_modules,
                on_finished=self._on_script_finished,
                debug_enabled=self._debug_mode,
                debug_step_mode=self._debug_step_mode,
                debug_breakpoints=self._debug_breakpoints,
                debug_watches=self._debug_watches,
                debug_callback=self._debug_cb,
            )
            self._last_sandbox = self._sandbox

            # Si la API Pybricks ya fue inicializada por la capa superior,
            # redirigimos su stop_event al del sandbox real para que
            # pybricks.tools.wait() pueda interrumpirse al pulsar Stop.
            try:
                from simulador_ev3.pybricks_api._context import PybricksContext

                PybricksContext.get_current().stop_event = self._sandbox.stop_event
            except Exception:  # noqa: BLE001
                pass

            self._sandbox.start()

    def pause(self) -> None:
        """Pausa el engine (el ScriptThread queda en wait bloqueante)."""
        if self._state != ControllerState.RUNNING:
            return
        self._pause_flag.set()
        if self._sandbox and self._sandbox.is_alive():
            self._sandbox.pause_timeout()
        self._state = ControllerState.PAUSED

    def resume(self) -> None:
        """Reanuda el engine desde pausa."""
        if self._state != ControllerState.PAUSED:
            return
        self._pause_flag.clear()
        if self._sandbox and self._sandbox.is_alive():
            self._sandbox.resume_timeout()
        self._state = ControllerState.RUNNING

    def stop(self, timeout: float = 3.0, reason: str = "user_stop") -> None:
        """
        Detiene el engine y el script.

        Args:
            timeout: Segundos máximos para esperar que los hilos terminen.
            reason:  Motivo de la parada (se publica en EventBus).
        """
        if self._state == ControllerState.STOPPED:
            return

        self._stop_flag.set()
        self._state = ControllerState.STOPPED

        # Detener sandbox primero para que wait() no bloquee al engine
        if self._sandbox and self._sandbox.is_alive():
            self._sandbox.stop(reason)
            self._sandbox.join(timeout=timeout)

        # Notificar al engine (señala eventos bloqueantes pendientes)
        self._engine.notify_stopped(reason)

        # Esperar al engine thread
        if self._engine_thread and self._engine_thread.is_alive():
            self._engine_thread.join(timeout=timeout)

    def reset(self) -> None:
        """
        Detiene la simulación, resetea el engine y vuelve al estado IDLE.
        """
        self.stop(reason="reset")
        self._engine.reset()
        self._source_code = None
        self._pybricks_modules = {}
        self._sandbox = None
        self._last_sandbox = None
        self._debug_mode = False
        self._debug_step_mode = False
        self._debug_breakpoints = set()
        self._debug_watches = []
        self._debug_cb = None
        self._stop_flag.clear()
        self._pause_flag.clear()
        self._state = ControllerState.IDLE

    # ------------------------------------------------------------------
    # Tick manual (útil para Tkinter widget.after y para tests)
    # ------------------------------------------------------------------

    def tick(self) -> Optional[StateSnapshot]:
        """
        Ejecuta un único tick del engine manualmente.
        Útil en tests o cuando el loop de ticks lo gestiona Tkinter.
        """
        if self._state not in (ControllerState.RUNNING, ControllerState.PAUSED):
            return None
        if self._pause_flag.is_set():
            return None  # pausado → no actualizar

        snap = self._engine.update(self._dt)
        if self._snapshot_cb:
            try:
                self._snapshot_cb(snap)
            except Exception:  # noqa: BLE001
                pass
        return snap

    # ------------------------------------------------------------------
    # Loop del Engine Thread
    # ------------------------------------------------------------------

    def _engine_loop(self) -> None:
        """
        Loop interno del EngineThread.
        Corre a ~tick_rate_hz usando sleep precisionado.
        """
        while not self._stop_flag.is_set():
            t0 = time.perf_counter()

            # Si pausado, esperar hasta reanudar o stop
            if self._pause_flag.is_set():
                self._stop_flag.wait(timeout=0.02)
                continue

            snap = self._engine.update(self._dt)

            if self._snapshot_cb:
                try:
                    self._snapshot_cb(snap)
                except Exception:  # noqa: BLE001
                    pass

            # Sleep residual para ajustar frecuencia
            elapsed = time.perf_counter() - t0
            remaining = self._dt - elapsed
            if remaining > 0:
                time.sleep(remaining)

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_script_finished(self) -> None:
        """
        El sandbox llama aquí cuando el ScriptThread termina (éxito o error).
        Si el script termina de forma natural → detenemos el engine también.
        """
        if self._sandbox and self._sandbox.state in (SandboxState.FINISHED, SandboxState.ERROR, SandboxState.TIMED_OUT):
            reason = (
                "script_finished"
                if self._sandbox.state == SandboxState.FINISHED
                else "script_timed_out"
                if self._sandbox.state == SandboxState.TIMED_OUT
                else "script_error"
            )

            # Si terminó sin error, dejamos una ventana de ~1 tick para que
            # comandos no bloqueantes encolados al final (p.ej. screen.print)
            # alcancen a procesarse antes de detener el engine.
            delay_s = self._dt if reason == "script_finished" else 0.0

            # Detenemos en un hilo aparte para no deadlock
            t = threading.Thread(
                target=self._deferred_stop,
                kwargs={"reason": reason, "delay_s": delay_s},
                daemon=True,
            )
            t.start()

    def _deferred_stop(self, *, reason: str, delay_s: float = 0.0) -> None:
        if delay_s > 0:
            time.sleep(delay_s)
        self.stop(reason=reason)
