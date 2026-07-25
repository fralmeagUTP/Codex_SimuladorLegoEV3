"""Factory for the virtual Pybricks API used by RuntimeSandbox."""

from __future__ import annotations

import sys
import threading
import types

from simulador_ev3.pybricks_api._context import PybricksContext

_PYBRICKS_SUBMODULES = (
    "pybricks",
    "pybricks.hubs",
    "pybricks.ev3devices",
    "pybricks.parameters",
    "pybricks.robotics",
    "pybricks.tools",
)


class PybricksFactory:
    """Builds a per-session Pybricks module tree for the sandbox.

    Modules returned by ``create`` are resolved by the sandbox import hook.
    They are not registered in ``sys.modules`` because that registry is global
    and can mix contexts across concurrent web sessions.
    """

    @classmethod
    def create(
        cls,
        engine,
        stop_event: threading.Event,
    ) -> dict[str, object]:
        ctx = PybricksContext(
            command_queue=engine.command_queue,
            engine=engine,
            stop_event=stop_event,
        )
        PybricksContext.set_current(ctx)

        import simulador_ev3.pybricks_api.ev3devices as _ev3_mod
        import simulador_ev3.pybricks_api.hubs as _hubs_mod
        import simulador_ev3.pybricks_api.parameters as _params_mod
        import simulador_ev3.pybricks_api.robotics as _rob_mod
        import simulador_ev3.pybricks_api.tools as _tools_mod

        pybricks_pkg = types.ModuleType("pybricks")
        pybricks_pkg.__package__ = "pybricks"
        pybricks_pkg.__path__ = []
        pybricks_pkg.hubs = _hubs_mod  # type: ignore[attr-defined]
        pybricks_pkg.ev3devices = _ev3_mod  # type: ignore[attr-defined]
        pybricks_pkg.parameters = _params_mod  # type: ignore[attr-defined]
        pybricks_pkg.robotics = _rob_mod  # type: ignore[attr-defined]
        pybricks_pkg.tools = _tools_mod  # type: ignore[attr-defined]

        return {
            "pybricks": pybricks_pkg,
            "pybricks.hubs": _hubs_mod,
            "pybricks.ev3devices": _ev3_mod,
            "pybricks.parameters": _params_mod,
            "pybricks.robotics": _rob_mod,
            "pybricks.tools": _tools_mod,
            "__pybricks_context__": ctx,
        }

    @classmethod
    def cleanup(cls) -> None:
        """Clear current context and remove legacy global modules if present."""

        for name in _PYBRICKS_SUBMODULES:
            sys.modules.pop(name, None)
        PybricksContext.clear()
