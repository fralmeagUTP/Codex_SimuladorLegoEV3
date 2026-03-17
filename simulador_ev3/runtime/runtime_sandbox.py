"""
runtime_sandbox.py — Sandbox de ejecución para el script del usuario.

Ejecuta el código fuente del script en un hilo dedicado con:
  - Namespace restringido (ExecutionPolicy.build_namespace)
  - Control de tiempo mediante un watchdog en hilo aparte
  - Captura de excepciones y publicación vía EventBus

La arquitectura de hilos es:
    MainThread (Tkinter)
    │
    ├── EngineThread  → SimulationEngine.update() cada 20 ms
    │   (gestionado por RuntimeController)
    │
    └── ScriptThread  ← RuntimeSandbox.run()
        Llama a pybricks.tools.wait() que hace threading.Event.wait()
        El Engine señala el Event al completar comandos bloqueantes.
"""

from __future__ import annotations

import sys
import threading
import traceback
from typing import Callable, Optional

from simulador_ev3.core.event_bus import EVENT_RUNTIME_ERROR, EventBus
from simulador_ev3.runtime.execution_policy import ExecutionPolicy


# ---------------------------------------------------------------------------
# Estado del sandbox
# ---------------------------------------------------------------------------

class SandboxState:
    IDLE      = "IDLE"
    RUNNING   = "RUNNING"
    FINISHED  = "FINISHED"
    ERROR     = "ERROR"
    TIMED_OUT = "TIMED_OUT"
    STOPPED   = "STOPPED"


# ---------------------------------------------------------------------------
# Sandbox
# ---------------------------------------------------------------------------

class RuntimeSandbox:
    """
    Ejecuta el script del usuario en un hilo aislado.

    Uso típico (gestionado por RuntimeController):
        sandbox = RuntimeSandbox(
            source_code=code,
            policy=ExecutionPolicy(),
            event_bus=bus,
            pybricks_modules={"pybricks": virtual_pkg},
        )
        sandbox.start()
        # … el engine corre en paralelo …
        sandbox.join(timeout=30)
        if sandbox.state == SandboxState.RUNNING:
            sandbox.stop()

    Señales de parada:
        - El hilo termina naturalmente.
        - sandbox.stop() → levanta _stop_flag; el script debe cooperar
          revisando el flag en wait() (vía pybricks.tools.wait).
        - Watchdog de tiempo → llama stop() automáticamente.
    """

    def __init__(
        self,
        source_code: str,
        policy: Optional[ExecutionPolicy]  = None,
        event_bus: Optional[EventBus]      = None,
        pybricks_modules: Optional[dict]   = None,
        on_finished: Optional[Callable[[], None]] = None,
    ) -> None:
        self._source       = source_code
        self._policy       = policy or ExecutionPolicy()
        self._bus          = event_bus or EventBus()
        self._pybricks     = pybricks_modules or {}
        self._on_finished  = on_finished

        self._state        = SandboxState.IDLE
        self._error: Optional[str]      = None
        self._tb:   Optional[str]       = None
        self._stop_event   = threading.Event()   # señal de parada cooperativa
        self._thread: Optional[threading.Thread] = None
        self._watchdog: Optional[threading.Timer] = None

    # ------------------------------------------------------------------
    # Propiedades públicas
    # ------------------------------------------------------------------

    @property
    def state(self) -> str:
        return self._state

    @property
    def error(self) -> Optional[str]:
        """Mensaje de la última excepción, o None."""
        return self._error

    @property
    def traceback_str(self) -> Optional[str]:
        """Traceback completo de la última excepción, o None."""
        return self._tb

    @property
    def stop_event(self) -> threading.Event:
        """
        Event que pybricks.tools.wait() puede observar para detener
        el script de forma cooperativa.
        """
        return self._stop_event

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Lanza el hilo de ejecución del script."""
        if self._state != SandboxState.IDLE:
            raise RuntimeError(
                f"El sandbox ya fue iniciado (estado: {self._state})"
            )
        self._state  = SandboxState.RUNNING
        self._thread = threading.Thread(
            target=self._run,
            name="ScriptThread",
            daemon=True,            # muere con el proceso principal
        )
        self._thread.start()

        # Watchdog opcional
        if self._policy.max_runtime_s > 0:
            self._watchdog = threading.Timer(
                self._policy.max_runtime_s,
                self._on_timeout,
            )
            self._watchdog.daemon = True
            self._watchdog.start()

    def stop(self, reason: str = "user_stop") -> None:
        """
        Solicita detención cooperativa del script.
        El script se detendrá en el próximo pybricks.tools.wait().
        """
        self._stop_event.set()
        if self._state == SandboxState.RUNNING:
            self._state = SandboxState.STOPPED

    def join(self, timeout: Optional[float] = None) -> bool:
        """
        Espera a que el hilo del script finalice.
        Devuelve True si terminó, False si expiró el timeout.
        """
        if self._thread is None:
            return True
        self._thread.join(timeout=timeout)
        return not self._thread.is_alive()

    def is_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    # ------------------------------------------------------------------
    # Ejecución interna
    # ------------------------------------------------------------------

    def _run(self) -> None:
        """Ejecutado dentro del ScriptThread."""
        ns = self._policy.build_namespace(self._pybricks)

        # Inyectamos el stop_event en el namespace para que el módulo
        # pybricks.tools.wait() pueda consultarlo
        ns["__stop_event__"] = self._stop_event

        try:
            # Compilación separada para mejor traceback
            code = compile(self._source, "<script>", "exec")
            exec(code, ns)  # noqa: S102

            if self._state == SandboxState.RUNNING:
                self._state = SandboxState.FINISHED

        except SystemExit:
            self._state = SandboxState.FINISHED

        except Exception as exc:  # noqa: BLE001
            if self._state == SandboxState.RUNNING:
                self._state   = SandboxState.ERROR
            self._error = str(exc)
            self._tb    = traceback.format_exc()
            self._bus.publish(
                EVENT_RUNTIME_ERROR,
                {"error": self._error, "traceback": self._tb},
            )

        finally:
            self._cancel_watchdog()
            if self._on_finished:
                try:
                    self._on_finished()
                except Exception:  # noqa: BLE001
                    pass

    def _on_timeout(self) -> None:
        """Watchdog: script excedió max_runtime_s."""
        self._state = SandboxState.TIMED_OUT
        self._error = f"Script excedió el tiempo máximo ({self._policy.max_runtime_s} s)"
        self._stop_event.set()
        self._bus.publish(
            EVENT_RUNTIME_ERROR,
            {"error": self._error, "traceback": ""},
        )

    def _cancel_watchdog(self) -> None:
        if self._watchdog is not None:
            self._watchdog.cancel()
            self._watchdog = None
