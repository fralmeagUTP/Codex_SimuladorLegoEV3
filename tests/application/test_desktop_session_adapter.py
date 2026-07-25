from pathlib import Path

from simulador_ev3.application.desktop_session_adapter import DesktopSessionAdapter
from simulador_ev3.core.simulation_engine import SimEngineConfig


def test_desktop_session_adapter_exposes_local_simulation_use_cases() -> None:
    session = DesktopSessionAdapter(SimEngineConfig())

    session.load_script("x = 1")
    session.set_debug_watches(["x + 1"])

    assert session.is_running is False
    assert session.engine is not None
    assert session.get_debug_state() is None


def test_desktop_session_adapter_uses_worker_for_execution_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv("EV3_WORKER_ISOLATION_ENABLED", "true")
    session = DesktopSessionAdapter(SimEngineConfig())
    try:
        assert session._worker is not None
        session.load_script("from pybricks.tools import wait\nwait(100)\n")
        session.start()
        assert session.is_running is True
        assert session._service.is_running is False
    finally:
        session.close()


def test_desktop_session_adapter_recovers_worker_before_mirroring_world(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("EV3_WORKER_ISOLATION_ENABLED", "true")
    session = DesktopSessionAdapter(SimEngineConfig())
    world = tmp_path / "world.json"
    source_world = Path(__file__).resolve().parents[2] / "worlds" / "01_linea_negra_basica.json"
    world.write_text(source_world.read_text(encoding="utf-8"), encoding="utf-8")
    try:
        assert session._worker is not None
        session._worker.close()
        session.load_world_file(world)
        assert session._worker is not None
    finally:
        session.close()
