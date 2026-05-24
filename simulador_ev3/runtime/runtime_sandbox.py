"""
runtime_sandbox.py â€” Sandbox de ejecuciÃ³n para el script del usuario.

Ejecuta el cÃ³digo fuente del script en un hilo dedicado con:
  - Namespace restringido (ExecutionPolicy.build_namespace)
  - Control de tiempo mediante un watchdog en hilo aparte
  - Captura de excepciones y publicaciÃ³n vÃ­a EventBus

La arquitectura de hilos es:
    MainThread (Tkinter)
    â”‚
    â”œâ”€â”€ EngineThread  â†’ SimulationEngine.update() cada 20 ms
    â”‚   (gestionado por RuntimeController)
    â”‚
    â””â”€â”€ ScriptThread  â† RuntimeSandbox.run()
        Llama a pybricks.tools.wait() que hace threading.Event.wait()
        El Engine seÃ±ala el Event al completar comandos bloqueantes.
"""

from __future__ import annotations

import sys
import threading
import time
import traceback
import re
from collections import deque
from typing import Callable, Optional

from simulador_ev3.core.event_bus import EVENT_RUNTIME_ERROR, EventBus
from simulador_ev3.pybricks_api._context import PybricksContext
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

    Uso tÃ­pico (gestionado por RuntimeController):
        sandbox = RuntimeSandbox(
            source_code=code,
            policy=ExecutionPolicy(),
            event_bus=bus,
            pybricks_modules={"pybricks": virtual_pkg},
        )
        sandbox.start()
        # â€¦ el engine corre en paralelo â€¦
        sandbox.join(timeout=30)
        if sandbox.state == SandboxState.RUNNING:
            sandbox.stop()

    SeÃ±ales de parada:
        - El hilo termina naturalmente.
        - sandbox.stop() â†’ levanta _stop_flag; el script debe cooperar
          revisando el flag en wait() (vÃ­a pybricks.tools.wait).
        - Watchdog de tiempo â†’ llama stop() automÃ¡ticamente.
    """

    def __init__(
        self,
        source_code: str,
        policy: Optional[ExecutionPolicy]  = None,
        event_bus: Optional[EventBus]      = None,
        pybricks_modules: Optional[dict]   = None,
        on_finished: Optional[Callable[[], None]] = None,
        debug_enabled: bool = False,
        debug_step_mode: bool = False,
        debug_breakpoints: Optional[set[int]] = None,
        debug_watches: Optional[list[str]] = None,
        debug_callback: Optional[Callable[[dict], None]] = None,
    ) -> None:
        self._source       = source_code
        self._policy       = policy or ExecutionPolicy()
        self._bus          = event_bus or EventBus()
        self._pybricks     = pybricks_modules or {}
        self._on_finished  = on_finished
        self._debug_enabled = bool(debug_enabled)
        self._debug_step_mode = bool(debug_step_mode)
        self._debug_callback = debug_callback
        self._debug_lines = deque(maxlen=40)
        self._debug_breakpoints = {
            int(line) for line in (debug_breakpoints or set()) if int(line) > 0
        }
        self._debug_watches = [
            str(expr).strip() for expr in (debug_watches or []) if str(expr).strip()
        ]
        self._debug_current_line: Optional[int] = None
        self._debug_paused = False
        self._debug_lock = threading.Lock()
        self._debug_resume_event = threading.Event()
        self._debug_resume_event.set()

        self._state        = SandboxState.IDLE
        self._error: Optional[str]      = None
        self._tb:   Optional[str]       = None
        self._stop_event   = threading.Event()   # seÃ±al de parada cooperativa
        self._thread: Optional[threading.Thread] = None
        self._watchdog: Optional[threading.Timer] = None
        self._watchdog_lock = threading.Lock()
        self._watchdog_deadline_s: Optional[float] = None
        self._watchdog_remaining_s: Optional[float] = None
        self._watchdog_paused = False

    # ------------------------------------------------------------------
    # Propiedades pÃºblicas
    # ------------------------------------------------------------------

    @property
    def state(self) -> str:
        return self._state

    @property
    def error(self) -> Optional[str]:
        """Mensaje de la Ãºltima excepciÃ³n, o None."""
        return self._error

    @property
    def traceback_str(self) -> Optional[str]:
        """Traceback completo de la Ãºltima excepciÃ³n, o None."""
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
        """Lanza el hilo de ejecuciÃ³n del script."""
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
            self._arm_watchdog(self._policy.max_runtime_s)

    def stop(self, reason: str = "user_stop") -> None:
        """
        Solicita detenciÃ³n cooperativa del script.
        El script se detendrÃ¡ en el prÃ³ximo pybricks.tools.wait().
        """
        self._stop_event.set()
        self._debug_resume_event.set()
        if self._state == SandboxState.RUNNING:
            self._state = SandboxState.STOPPED

    def pause_timeout(self) -> None:
        """Pausa el watchdog para no contar tiempo mientras la ejecucion esta pausada."""
        with self._watchdog_lock:
            if self._watchdog_paused:
                return
            if self._watchdog is None:
                return
            now = time.perf_counter()
            if self._watchdog_deadline_s is not None:
                remaining = self._watchdog_deadline_s - now
            else:
                remaining = self._watchdog_remaining_s or 0.0
            self._watchdog.cancel()
            self._watchdog = None
            self._watchdog_deadline_s = None
            self._watchdog_remaining_s = max(0.0, float(remaining))
            self._watchdog_paused = True

    def resume_timeout(self) -> None:
        """Reanuda el watchdog conservando el tiempo restante previo a la pausa."""
        with self._watchdog_lock:
            if not self._watchdog_paused:
                return
            if self._state != SandboxState.RUNNING:
                self._watchdog_paused = False
                return
            remaining = float(self._watchdog_remaining_s or 0.0)
            self._watchdog_paused = False
            if remaining > 0.0:
                self._arm_watchdog_locked(remaining)
                return
        self._on_timeout()

    def set_debug_breakpoints(self, breakpoints: set[int]) -> None:
        with self._debug_lock:
            self._debug_breakpoints = {
                int(line) for line in breakpoints if int(line) > 0
            }

    def set_debug_watches(self, watches: list[str]) -> None:
        with self._debug_lock:
            self._debug_watches = [
                str(expr).strip() for expr in (watches or []) if str(expr).strip()
            ]

    def debug_continue(self) -> None:
        with self._debug_lock:
            self._debug_step_mode = False
        self._debug_resume_event.set()

    def debug_step(self) -> None:
        with self._debug_lock:
            self._debug_step_mode = True
        self._debug_resume_event.set()

    @property
    def is_debug_paused(self) -> bool:
        with self._debug_lock:
            return self._debug_paused

    def join(self, timeout: Optional[float] = None) -> bool:
        """
        Espera a que el hilo del script finalice.
        Devuelve True si terminÃ³, False si expirÃ³ el timeout.
        """
        if self._thread is None:
            return True
        self._thread.join(timeout=timeout)
        return not self._thread.is_alive()

    def is_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    # ------------------------------------------------------------------
    # EjecuciÃ³n interna
    # ------------------------------------------------------------------

    def _run(self) -> None:
        """Ejecutado dentro del ScriptThread."""
        ns = self._policy.build_namespace(self._pybricks)
        pybricks_ctx = self._pybricks.get("__pybricks_context__")
        if pybricks_ctx is not None:
            PybricksContext.set_current(pybricks_ctx)

        # Inyectamos el stop_event en el namespace para que el mÃ³dulo
        # pybricks.tools.wait() pueda consultarlo
        ns["__stop_event__"] = self._stop_event

        try:
            # CompilaciÃ³n separada para mejor traceback
            if self._debug_enabled:
                sys.settrace(self._trace_line_events)
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
            payload = {"error": self._error, "traceback": self._tb}
            if self._debug_enabled and self._debug_lines:
                payload["debug_last_lines"] = list(self._debug_lines)
            self._bus.publish(
                EVENT_RUNTIME_ERROR,
                payload,
            )

        finally:
            if self._debug_enabled:
                sys.settrace(None)
            if pybricks_ctx is not None:
                PybricksContext.clear()
            self._cancel_watchdog()
            if self._on_finished:
                try:
                    self._on_finished()
                except Exception:  # noqa: BLE001
                    pass

    def _trace_line_events(self, frame, event, arg):
        if event != "line":
            return self._trace_line_events
        if frame.f_code.co_filename != "<script>":
            return self._trace_line_events

        line_no = int(frame.f_lineno)
        self._debug_lines.append(line_no)
        pause_reason: Optional[str] = None
        with self._debug_lock:
            self._debug_current_line = line_no
            if line_no in self._debug_breakpoints:
                pause_reason = "breakpoint"
            elif self._debug_step_mode:
                pause_reason = "step"

        if self._debug_callback:
            try:
                payload = {
                    "type": "line",
                    "line": line_no,
                    "function": str(frame.f_code.co_name or "<module>"),
                }
                if pause_reason:
                    payload["pause_reason"] = pause_reason
                self._debug_callback(payload)
            except Exception:  # noqa: BLE001
                pass

        if pause_reason:
            debug_context = self._build_debug_context(frame, line_no)
            with self._debug_lock:
                self._debug_paused = True
            self.pause_timeout()
            self._debug_resume_event.clear()
            if self._debug_callback:
                try:
                    self._debug_callback(
                        {
                            "type": "paused",
                            "line": line_no,
                            "function": str(frame.f_code.co_name or "<module>"),
                            "reason": pause_reason,
                            **debug_context,
                        }
                    )
                except Exception:  # noqa: BLE001
                    pass
            while not self._stop_event.is_set():
                if self._debug_resume_event.wait(timeout=0.05):
                    break
            with self._debug_lock:
                self._debug_paused = False
            self.resume_timeout()
        return self._trace_line_events

    def _build_debug_context(self, frame, line_no: int) -> dict:
        stack: list[dict] = []
        cursor = frame
        depth = 0
        while cursor is not None and depth < 12:
            if cursor.f_code.co_filename == "<script>":
                stack.append(
                    {
                        "function": str(cursor.f_code.co_name or "<module>"),
                        "line": int(cursor.f_lineno),
                    }
                )
                depth += 1
            cursor = cursor.f_back

        locals_payload: dict[str, object] = {}
        try:
            items = list(frame.f_locals.items())
        except Exception:  # noqa: BLE001
            items = []
        for name, value in items:
            key = str(name)
            if key.startswith("__"):
                continue
            locals_payload[key] = self._serialize_debug_value(value, depth=0)
            if len(locals_payload) >= 40:
                locals_payload["__truncated__"] = f"{len(items) - len(locals_payload)}+"
                break

        return {
            "line": int(line_no),
            "stack": stack,
            "locals": locals_payload,
            "watches": self._evaluate_watches(frame),
        }

    def _serialize_debug_value(self, value, depth: int = 0):
        if depth >= 3:
            return "<max_depth>"
        if value is None or isinstance(value, (bool, int, float, str)):
            if isinstance(value, str) and len(value) > 200:
                return value[:200] + "...(truncated)"
            return value
        if isinstance(value, (list, tuple, set)):
            result = []
            for idx, item in enumerate(value):
                if idx >= 20:
                    result.append("...(truncated)")
                    break
                result.append(self._serialize_debug_value(item, depth=depth + 1))
            return result
        if isinstance(value, dict):
            result: dict[str, object] = {}
            for idx, (k, v) in enumerate(value.items()):
                if idx >= 20:
                    result["__truncated__"] = "..."
                    break
                result[str(k)] = self._serialize_debug_value(v, depth=depth + 1)
            return result
        try:
            text = repr(value)
        except Exception:  # noqa: BLE001
            text = f"<{type(value).__name__}>"
        if len(text) > 200:
            text = text[:200] + "...(truncated)"
        return text

    def _evaluate_watches(self, frame) -> list[dict]:
        with self._debug_lock:
            expressions = list(self._debug_watches)
        if not expressions:
            return []

        # Restriccion minima para evitar expresiones peligrosas.
        safe_builtin_funcs = {
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "len": len,
            "round": round,
        }
        eval_globals = dict(frame.f_globals)
        eval_globals["__builtins__"] = safe_builtin_funcs
        eval_locals = dict(frame.f_locals)

        results: list[dict] = []
        for expr in expressions[:20]:
            item = {"expr": expr, "value": None, "error": None}
            lowered = expr.lower()
            # Bloqueo simple de dunder y llamadas de import/exec/eval/open.
            if "__" in expr or re.search(r"\b(import|exec|eval|open|compile|input)\b", lowered):
                item["error"] = "expresion no permitida"
                results.append(item)
                continue
            try:
                value = eval(compile(expr, "<watch>", "eval"), eval_globals, eval_locals)  # noqa: S307
                item["value"] = self._serialize_debug_value(value, depth=0)
            except Exception as exc:  # noqa: BLE001
                item["error"] = str(exc)
            results.append(item)
        return results

    def _on_timeout(self) -> None:
        """Watchdog: script excedio max_runtime_s."""
        with self._watchdog_lock:
            if self._state not in {SandboxState.RUNNING, SandboxState.IDLE}:
                return
        self._state = SandboxState.TIMED_OUT
        self._error = f"Script excedio el tiempo maximo ({self._policy.max_runtime_s} s)"
        self._stop_event.set()
        self._bus.publish(
            EVENT_RUNTIME_ERROR,
            {"error": self._error, "traceback": ""},
        )

    def _cancel_watchdog(self) -> None:
        with self._watchdog_lock:
            if self._watchdog is not None:
                self._watchdog.cancel()
                self._watchdog = None
            self._watchdog_deadline_s = None
            self._watchdog_remaining_s = None
            self._watchdog_paused = False

    def _arm_watchdog(self, timeout_s: float) -> None:
        with self._watchdog_lock:
            self._arm_watchdog_locked(timeout_s)

    def _arm_watchdog_locked(self, timeout_s: float) -> None:
        if self._watchdog is not None:
            self._watchdog.cancel()
            self._watchdog = None
        timeout = max(0.001, float(timeout_s))
        self._watchdog_remaining_s = timeout
        self._watchdog_deadline_s = time.perf_counter() + timeout
        self._watchdog_paused = False
        self._watchdog = threading.Timer(timeout, self._on_timeout)
        self._watchdog.daemon = True
        self._watchdog.start()
