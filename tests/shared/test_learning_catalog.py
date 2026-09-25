from __future__ import annotations

import time

from simulador_ev3.application.desktop_session_adapter import DesktopSessionAdapter
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.examples.example_catalog import ExampleCatalog
from simulador_ev3.shared.learning_catalog import LEARNING_ROUTES, initial_learning_route, route_by_id
from simulador_ev3.shared.paths import resolve_examples_dir
from simulador_ev3.web.services.simulation_session import SimulationSession


def test_learning_routes_have_stable_guidance_and_existing_examples() -> None:
    available_examples = {item.name for item in ExampleCatalog(resolve_examples_dir()).list_examples()}

    assert [route.identifier for route in LEARNING_ROUTES] == [
        "first-simulation",
        "motors-and-sensors",
        "debug-and-recovery",
    ]
    for route in LEARNING_ROUTES:
        assert route.objective
        assert route.prerequisites
        assert route.guide_ids
        assert route.example_files
        assert route.practice
        assert route.success_criteria
        assert route.recovery
        assert set(route.example_files) <= available_examples


def test_web_and_desktop_publish_the_same_initial_learning_activity() -> None:
    web = SimulationSession(session_id="learning-parity", config={}, max_runtime_s=30.0)
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        route = initial_learning_route()
        assert route_by_id(route.identifier) == route
        assert web.learning_state().to_dict() == {
            **desktop.learning_state().to_dict(),
            "session_id": "learning-parity",
        }
    finally:
        web.close()
        desktop.close()


def test_web_and_desktop_publish_progress_and_success_after_a_completed_activity() -> None:
    source = "from pybricks.tools import wait\nwait(20)\n"
    web = SimulationSession(session_id="learning-completed", config={}, max_runtime_s=30.0)
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

        for state in (web.learning_state(), desktop.learning_state()):
            assert state.progress_current == state.progress_total == 1
            assert state.result == "Actividad completada."
    finally:
        web.close()
        desktop.close()
