from __future__ import annotations

import json
import time

import pytest

from simulador_ev3.application.desktop_session_adapter import DesktopSessionAdapter
from simulador_ev3.application.world_editor_service import WorldEditorService
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.domain.editor.world_editor_model import Placement
from simulador_ev3.shared.paths import resolve_worlds_dir
from simulador_ev3.shared.world_editor_projection import editor_placements, placement_geometry
from simulador_ev3.web.errors import InvalidPayload
from simulador_ev3.web.services.simulation_session import SimulationSession


@pytest.mark.parametrize("limit", [0.0, 30.0, 60.0, 120.0, 300.0])
def test_web_and_desktop_share_the_visible_runtime_limit_options(limit: float) -> None:
    web = SimulationSession(session_id=f"runtime-limit-{limit}", config={}, max_runtime_s=30.0)
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        web_result = web.set_max_runtime_s(limit)
        desktop.set_max_runtime_s(limit)

        assert web_result["max_runtime_s"] == desktop.max_runtime_s == limit
    finally:
        web.close()
        desktop.close()


def test_web_and_desktop_reject_runtime_limits_outside_the_visible_menu() -> None:
    web = SimulationSession(session_id="runtime-limit-invalid", config={}, max_runtime_s=30.0)
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        with pytest.raises(InvalidPayload, match="tiempo maximo"):
            web.set_max_runtime_s(45.0)
        with pytest.raises(ValueError, match="tiempo maximo"):
            desktop.set_max_runtime_s(45.0)
    finally:
        web.close()
        desktop.close()


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


def test_terminal_snapshot_keeps_robot_telemetry_and_lcd_equivalent_in_both_interfaces() -> None:
    """Canvas, telemetría y Brick deben derivar del mismo snapshot terminal."""

    source = (
        "from pybricks.hubs import EV3Brick\n"
        "from pybricks.parameters import Color\n"
        "from pybricks.tools import wait\n"
        "ev3 = EV3Brick()\n"
        "ev3.light.on(Color.GREEN)\n"
        "ev3.screen.print('snapshot terminal')\n"
        "wait(20)\n"
    )
    web = SimulationSession(session_id="terminal-snapshot-parity", config={}, max_runtime_s=2.0)
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        web.load_script(source)
        desktop.load_script(source)
        web.start()
        desktop.start()

        for _ in range(30):
            if web.status == "finished" and desktop.presentation_state().status == "finished":
                break
            time.sleep(0.05)

        web_snapshot = web.snapshot_response()["snapshot"]
        desktop_snapshot = desktop.current_snapshot().to_dict()
        assert web.status == desktop.presentation_state().status == "finished"
        assert web_snapshot["robot"] == desktop_snapshot["robot"]
        assert web_snapshot["colliding"] == desktop_snapshot["colliding"]
        assert web_snapshot["motors"] == desktop_snapshot["motors"]
        assert web_snapshot["sensors"] == desktop_snapshot["sensors"]
        assert web_snapshot["brick"] == desktop_snapshot["brick"]
        assert web_snapshot["brick"]["screen"]["lines"] == ["snapshot terminal"]
    finally:
        web.close()
        desktop.close()


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


def test_web_and_desktop_cancel_expose_the_same_terminal_presentation_state() -> None:
    source = "from pybricks.tools import wait\nwhile True:\n    wait(10)\n"
    web = SimulationSession(session_id="cancel-parity", config={}, max_runtime_s=2.0)
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        web.load_script(source)
        desktop.load_script(source)
        web.start()
        desktop.start()
        time.sleep(0.03)

        web.stop()
        desktop.stop()

        assert web.presentation_state().status == desktop.presentation_state().status == "stopped"
        assert web.presentation_state().controls == desktop.presentation_state().controls
    finally:
        web.close()
        desktop.close()


def test_web_and_desktop_runtime_errors_expose_the_same_terminal_presentation_state() -> None:
    """Un error de programa no puede dejar una interfaz en estado ejecutando."""

    source = "raise RuntimeError('fallo cruzado de QA')\n"
    web = SimulationSession(session_id="error-parity", config={}, max_runtime_s=2.0)
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        web.load_script(source)
        desktop.load_script(source)
        web.start()
        desktop.start()

        for _ in range(100):
            # Tkinter procesa esta cola desde su ciclo ``after``; reproducir
            # esa ruta pública evita comparar contra un worker sin eventos
            # consumidos, estado que la UI real nunca presenta al usuario.
            desktop.drain_worker_events()
            if web.status == "error" and desktop.presentation_state().status == "error":
                break
            time.sleep(0.05)

        assert web.presentation_state().status == desktop.presentation_state().status == "error"
        assert web.presentation_state().controls == desktop.presentation_state().controls
    finally:
        web.close()
        desktop.close()


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


def test_web_and_desktop_reset_restore_the_configured_robot_start_snapshot() -> None:
    """Reiniciar conserva un Ãºnico punto de inicio coherente en ambas UI."""

    web = SimulationSession(session_id="reset-parity", config={}, max_runtime_s=2.0)
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        web.load_blank_world(10, 10)
        desktop.load_blank_world(320, 320)
        web.set_robot_start(96, 128, 90)
        desktop.set_robot_start(96, 128, 90)

        web.reset()
        desktop.reset()
        web_snapshot = web.snapshot_response()["snapshot"]
        desktop_snapshot = desktop.current_snapshot().to_dict()

        assert web.status == desktop.presentation_state().status == "created"
        assert web_snapshot["robot"] == desktop_snapshot["robot"] == {
            "x_mm": 96.0,
            "y_mm": 128.0,
            "theta_deg": 90.0,
        }
        assert web_snapshot["tick"] == desktop_snapshot["tick"] == 0
        assert web_snapshot["sim_time_s"] == desktop_snapshot["sim_time_s"] == 0.0
        assert web_snapshot["brick"]["screen"]["lines"] == desktop_snapshot["brick"]["screen"]["lines"] == []
    finally:
        web.close()
        desktop.close()


def test_line_world_uses_identical_start_pose_and_asset_geometry_in_both_clients() -> None:
    """El mundo de línea no puede cambiar de escala, capa o pose por la UI."""

    world_name = "01_linea_negra_basica.json"
    world_path = resolve_worlds_dir() / world_name
    web = SimulationSession(
        session_id="line-world-parity",
        config={"WORLDS_DIR": str(resolve_worlds_dir())},
        max_runtime_s=2.0,
    )
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        web_world = web.load_world_name(world_name)["world"]
        desktop.load_world_file(world_path)

        assert web.snapshot_response()["snapshot"]["robot"] == desktop.current_snapshot().to_dict()["robot"]
        web_placements = editor_placements(web_world.get("editor_spec"))
        source_placements = editor_placements(json.loads(world_path.read_text(encoding="utf-8")).get("editor_spec"))
        assert [item["asset_key"] for item in web_placements] == [item["asset_key"] for item in source_placements]
        assert [placement_geometry(item) for item in web_placements] == [placement_geometry(item) for item in source_placements]
        assert all(item and item["layer"] in {"floor", "zone", "line", "wall", "robot"} for item in map(placement_geometry, web_placements))
    finally:
        web.close()
        desktop.close()
