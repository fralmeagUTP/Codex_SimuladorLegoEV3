from __future__ import annotations

import json
import time

from simulador_ev3.application.desktop_session_adapter import DesktopSessionAdapter
from simulador_ev3.application.world_editor_service import WorldEditorService
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.domain.editor.world_editor_model import Placement
from simulador_ev3.web.services.simulation_session import SimulationSession


def test_web_and_desktop_finish_same_program_with_equivalent_snapshot() -> None:
    source = (
        "from pybricks.hubs import EV3Brick\n"
        "from pybricks.tools import wait\n"
        "ev3 = EV3Brick()\n"
        "ev3.speaker.beep(440, 100, 50)\n"
        "wait(20)\n"
    )
    web = SimulationSession(session_id="parity", config={}, max_runtime_s=2.0)
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        web.load_script(source)
        desktop.load_script(source)
        web.start()
        desktop.start()

        for _ in range(30):
            if web.status == "finished" and not desktop.is_running:
                break
            time.sleep(0.05)

        web_snapshot = web.snapshot_response()["snapshot"]
        desktop_snapshot = desktop.get_snapshot().to_dict()
        assert web.status == "finished"
        assert desktop.is_running is False
        assert web_snapshot["brick"]["speaker"]["freq"] == desktop_snapshot["brick"]["speaker"]["freq"] == 440
    finally:
        web.close()


def test_web_and_desktop_apply_the_same_simulation_profile() -> None:
    web = SimulationSession(session_id="profile-parity", config={}, max_runtime_s=2.0)
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        web_profile = web.set_simulation_profile("realistic")
        desktop.set_simulation_profile("realistic")

        assert web_profile["profile"] == "realistic"
        assert desktop.engine_config.simulation_profile == "realistic"
        assert web_profile["calibration"] == desktop.engine_config.calibration
    finally:
        web.close()
        desktop.stop()


def test_web_and_desktop_export_equivalent_trace_contract() -> None:
    web = SimulationSession(session_id="trace-parity", config={}, max_runtime_s=2.0)
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        web.start_trace()
        desktop.start_trace()
        web.step_tick()
        desktop.step_tick()
        web.stop_trace()
        desktop.stop_trace()

        web_trace = json.loads(web.export_trace("json"))
        desktop_trace = json.loads(desktop.export_trace("json"))
        assert len(web_trace["snapshots"]) == len(desktop_trace["snapshots"]) == 1
    finally:
        web.close()
        desktop.stop()
        desktop.stop()


def test_web_and_desktop_apply_equivalent_debug_configuration() -> None:
    web = SimulationSession(session_id="debug-parity", config={}, max_runtime_s=2.0)
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        web_breakpoints = web.set_debug_breakpoints({1, 3, -1})["breakpoints"]
        web_watches = web.set_debug_watches([" x + 1 ", "", "y * 2"])["watches"]
        desktop.set_debug_breakpoints({1, 3, -1})
        desktop.set_debug_watches([" x + 1 ", "", "y * 2"])

        assert web_breakpoints == [1, 3]
        assert web_watches == ["x + 1", "y * 2"]
        # El contrato compartido se comprueba directamente en ambas rutas de UI.
        assert desktop.debug_configuration() == {
            "breakpoints": web_breakpoints,
            "watches": web_watches,
        }
    finally:
        web.close()
        desktop.stop()


def test_web_and_desktop_pause_resume_before_finishing() -> None:
    source = "from pybricks.tools import wait\nwait(300)\n"
    web = SimulationSession(session_id="lifecycle-parity", config={}, max_runtime_s=2.0)
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        web.load_script(source)
        desktop.load_script(source)
        web.start()
        desktop.start()
        time.sleep(0.03)
        web.pause()
        desktop.pause()

        assert web.status == "paused"
        assert desktop.is_paused is True

        web.resume()
        desktop.resume()
        for _ in range(20):
            if web.status == "finished" and not desktop.is_running:
                break
            time.sleep(0.05)

        assert web.status == "finished"
        assert desktop.is_running is False
    finally:
        web.close()
        desktop.stop()


def test_web_and_desktop_world_editors_place_equivalent_asset() -> None:
    web = SimulationSession(session_id="world-parity", config={}, max_runtime_s=2.0)
    desktop_editor = WorldEditorService()
    try:
        web.create_editor_world(10, 10)
        web_placement = web.place_asset({"asset_key": "wall_64x64_a", "x": 32, "y": 64})["placement"]
        desktop_world = desktop_editor.create_world(width_cells=10, height_cells=10)
        desktop_editor.place_asset(
            desktop_world,
            Placement("desktop-wall", "wall_64x64_a", 32, 64),
        )
        desktop_placement = desktop_world.placements[0].to_dict()

        assert web_placement["asset_key"] == desktop_placement["asset_key"]
        assert (web_placement["x_px"], web_placement["y_px"], web_placement["rotation"]) == (
            desktop_placement["x_px"],
            desktop_placement["y_px"],
            desktop_placement["rotation"],
        )
    finally:
        web.close()
