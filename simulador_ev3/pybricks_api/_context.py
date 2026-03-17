"""
_context.py — Contexto global de la sesión Pybricks.

Se inicializa por PybricksFactory.create() antes de ejecutar el script.
Los módulos virtuales (hubs, ev3devices, robotics, tools) leen de aquí
para acceder al CommandQueue y al SimulationEngine.
"""
from __future__ import annotations

import threading
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from simulador_ev3.core.command_queue import CommandQueue
    from simulador_ev3.core.simulation_engine import SimulationEngine


class PybricksContext:
    """
    Singleton de sesión que vincula la API virtual con el motor.

    Solo existe una instancia activa durante la ejecución de un script.
    """
    _instance: Optional["PybricksContext"] = None
    _lock = threading.Lock()

    def __init__(
        self,
        command_queue: "CommandQueue",
        engine: "SimulationEngine",
        stop_event: threading.Event,
    ) -> None:
        self.command_queue = command_queue
        self.engine        = engine
        self.stop_event    = stop_event

    # ------------------------------------------------------------------
    # Registro global thread-safe
    # ------------------------------------------------------------------

    @classmethod
    def set_current(cls, ctx: "PybricksContext") -> None:
        with cls._lock:
            cls._instance = ctx

    @classmethod
    def get_current(cls) -> "PybricksContext":
        with cls._lock:
            if cls._instance is None:
                raise RuntimeError(
                    "PybricksContext no inicializado. "
                    "Llama a PybricksFactory.create() antes de ejecutar el script."
                )
            return cls._instance

    @classmethod
    def clear(cls) -> None:
        with cls._lock:
            cls._instance = None
