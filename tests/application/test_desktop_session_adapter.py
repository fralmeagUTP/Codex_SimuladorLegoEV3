import json
import time
from pathlib import Path

from simulador_ev3.application.desktop_session_adapter import DesktopSessionAdapter
from simulador_ev3.application.snapshot_dto import SnapshotDTO
from simulador_ev3.core.simulation_engine import SimEngineConfig, SimulationEngine


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


def test_desktop_session_adapter_exports_snapshots_emitted_by_real_worker(monkeypatch) -> None:
    monkeypatch.setenv("EV3_WORKER_ISOLATION_ENABLED", "true")
    session = DesktopSessionAdapter(SimEngineConfig())
    try:
        session.start_trace()
        session.load_script("from pybricks.tools import wait\nwait(150)\n")
        session.start()
        deadline = time.monotonic() + 4.0
        while time.monotonic() < deadline:
            session.drain_worker_events()
            if not session.is_running:
                break
            time.sleep(0.02)

        trace = json.loads(session.export_trace("json"))
        assert trace["snapshots"]
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


def test_desktop_session_adapter_records_worker_snapshots_in_active_trace(monkeypatch) -> None:
    monkeypatch.setenv("EV3_WORKER_ISOLATION_ENABLED", "false")
    session = DesktopSessionAdapter(SimEngineConfig())
    snapshot = SnapshotDTO.from_snapshot(SimulationEngine(SimEngineConfig()).update())

    class FakeWorker:
        def drain_events(self):
            return [{
                "protocol_version": 1,
                "session_id": "desktop-shadow",
                "sequence": 1,
                "type": "snapshot",
                "payload": snapshot.to_dict(),
                "command_id": None,
            }]

        def close(self):
            pass

    session._worker = FakeWorker()
    try:
        session.start_trace()
        session.drain_worker_events()
        assert '"snapshots":[' in session.export_trace("json")
        assert str(snapshot.tick) in session.export_trace("json")
    finally:
        session.close()


def test_desktop_session_adapter_converts_terminal_worker_error_to_terminal_state(monkeypatch) -> None:
    monkeypatch.setenv("EV3_WORKER_ISOLATION_ENABLED", "false")
    session = DesktopSessionAdapter(SimEngineConfig())

    class FakeWorker:
        def drain_events(self):
            return [{
                "protocol_version": 1,
                "session_id": "desktop-shadow",
                "sequence": 1,
                "type": "error",
                "payload": {"error": "invalid syntax"},
                "command_id": None,
            }]

        def close(self):
            pass

    session._worker = FakeWorker()
    session._worker_status = "running"
    try:
        session.drain_worker_events()
        assert session.is_running is False
        assert session._worker_status == "error"
    finally:
        session.close()
