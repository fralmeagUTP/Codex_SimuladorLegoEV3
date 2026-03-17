"""
factory.py — Fábrica de la API Pybricks virtual.

PybricksFactory.create() hace tres cosas:
  1. Construye un árbol de módulos virtuales (types.ModuleType) que
     replican la estructura import de pybricks:
       pybricks
       pybricks.hubs
       pybricks.ev3devices
       pybricks.parameters
       pybricks.robotics
       pybricks.tools
  2. Registra ese árbol en sys.modules para que
     `from pybricks.hubs import EV3Brick` funcione dentro del sandbox.
  3. Inicializa el PybricksContext global con los refs al engine y la queue.

Limpieza:
  PybricksFactory.cleanup() elimina los módulos de sys.modules para no
  contaminar el intérprete entre sesiones.
"""
from __future__ import annotations

import sys
import types
import threading
from typing import Optional

from simulador_ev3.pybricks_api._context import PybricksContext

# Submodules que se registran en sys.modules
_PYBRICKS_SUBMODULES = (
    "pybricks",
    "pybricks.hubs",
    "pybricks.ev3devices",
    "pybricks.parameters",
    "pybricks.robotics",
    "pybricks.tools",
)


class PybricksFactory:
    """
    Fábrica que configura la API Pybricks virtual para el sandbox.

    Uso típico en RuntimeController (Fase 4) justo antes de start():

        mods = PybricksFactory.create(
            engine=engine,
            stop_event=sandbox.stop_event,
        )
        controller.set_pybricks_modules(mods)

    Args (create):
        engine:     SimulationEngine ya inicializado.
        stop_event: threading.Event del sandbox (para wait()).

    Returns (create):
        dict con {"pybricks": <módulo>} listo para inject en sandbox namespace.
        También registra todos los submódulos en sys.modules.
    """

    @classmethod
    def create(
        cls,
        engine,
        stop_event: threading.Event,
    ) -> dict[str, object]:
        from simulador_ev3.core.simulation_engine import SimulationEngine

        # 1. Inicializar contexto global
        ctx = PybricksContext(
            command_queue=engine.command_queue,
            engine=engine,
            stop_event=stop_event,
        )
        PybricksContext.set_current(ctx)

        # 2. Importar los módulos reales de simulador_ev3.pybricks_api.*
        import simulador_ev3.pybricks_api.parameters as _params_mod
        import simulador_ev3.pybricks_api.tools      as _tools_mod
        import simulador_ev3.pybricks_api.ev3devices as _ev3_mod
        import simulador_ev3.pybricks_api.robotics   as _rob_mod
        import simulador_ev3.pybricks_api.hubs       as _hubs_mod

        # 3. Crear módulos virtuales en sys.modules
        pybricks_pkg = types.ModuleType("pybricks")
        pybricks_pkg.__package__ = "pybricks"
        pybricks_pkg.__path__    = []  # marca como paquete

        # Subpackages como atributos del paquete raíz
        pybricks_pkg.hubs        = _hubs_mod    # type: ignore[attr-defined]
        pybricks_pkg.ev3devices  = _ev3_mod     # type: ignore[attr-defined]
        pybricks_pkg.parameters  = _params_mod  # type: ignore[attr-defined]
        pybricks_pkg.robotics    = _rob_mod     # type: ignore[attr-defined]
        pybricks_pkg.tools       = _tools_mod   # type: ignore[attr-defined]

        sys.modules["pybricks"]            = pybricks_pkg
        sys.modules["pybricks.hubs"]       = _hubs_mod
        sys.modules["pybricks.ev3devices"] = _ev3_mod
        sys.modules["pybricks.parameters"] = _params_mod
        sys.modules["pybricks.robotics"]   = _rob_mod
        sys.modules["pybricks.tools"]      = _tools_mod

        # 4. Devolver dict para sandbox namespace (redundante con sys.modules,
        #    pero permite inyectarlo explícitamente si se desea)
        return {"pybricks": pybricks_pkg}

    @classmethod
    def cleanup(cls) -> None:
        """
        Elimina los módulos virtuales de sys.modules y limpia el contexto.
        Llama después de que el sandbox termina.
        """
        for name in _PYBRICKS_SUBMODULES:
            sys.modules.pop(name, None)
        PybricksContext.clear()
