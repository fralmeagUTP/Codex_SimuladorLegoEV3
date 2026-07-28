"""
_context.py — Contexto global de la sesión Pybricks.

Se inicializa por PybricksFactory.create() antes de ejecutar el script.
Los módulos virtuales (hubs, ev3devices, robotics, tools) leen de aquí
para acceder al CommandQueue y al SimulationEngine.
"""

from __future__ import annotations

import threading
from contextvars import ContextVar
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from simulador_ev3.core.command_queue import CommandQueue
    from simulador_ev3.core.simulation_engine import SimulationEngine


class PybricksContext:
    """
    Singleton de sesión que vincula la API virtual con el motor.

    Solo existe una instancia activa durante la ejecución de un script.
    """

    _instance: Optional["PybricksContext"] = None
    _current: ContextVar[Optional["PybricksContext"]] = ContextVar(
        "pybricks_context",
        default=None,
    )
    _lock = threading.Lock()

    def __init__(
        self,
        command_queue: "CommandQueue",
        engine: "SimulationEngine",
        stop_event: threading.Event,
        pause_event: threading.Event | None = None,
    ) -> None:
        self.command_queue = command_queue
        self.engine = engine
        self.stop_event = stop_event
        # Se comparte con el runtime para que las esperas cooperativas no
        # consuman tiempo de script mientras la simulación está pausada.
        self.pause_event = pause_event or threading.Event()

    # ------------------------------------------------------------------
    # Registro global thread-safe
    # ------------------------------------------------------------------

    @classmethod
    def set_current(cls, ctx: "PybricksContext") -> None:
        cls._current.set(ctx)
        with cls._lock:
            cls._instance = ctx

    @classmethod
    def get_current(cls) -> "PybricksContext":
        current = cls._current.get()
        if current is not None:
            return current
        with cls._lock:
            if cls._instance is None:
                raise RuntimeError(
                    "PybricksContext no inicializado. Llama a PybricksFactory.create() antes de ejecutar el script."
                )
            return cls._instance

    @classmethod
    def clear(cls) -> None:
        cls._current.set(None)
        with cls._lock:
            cls._instance = None
