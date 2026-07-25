import pytest

from simulador_ev3.application.desktop_session_adapter import DesktopSessionAdapter
from simulador_ev3.application.session_contract import SessionCommand, SessionEvent
from simulador_ev3.application.simulation_session_port import SimulationSessionPort
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.web.services.simulation_session import SimulationSession


def test_session_command_uses_versioned_worker_compatible_envelope() -> None:
    command = SessionCommand("session-1", "command-1", "start", {"debug": True})

    assert command.to_dict()["protocol_version"] == 1
    assert command.to_dict()["command_id"] == "command-1"


def test_session_event_validates_and_roundtrips_worker_event() -> None:
    raw = {
        "protocol_version": 1,
        "session_id": "session-1",
        "sequence": 3,
        "kind": "event",
        "type": "snapshot",
        "payload": {"tick": 4},
        "command_id": "command-1",
    }

    assert SessionEvent.from_dict(raw).to_dict() == raw


def test_session_event_rejects_unknown_protocol_version() -> None:
    with pytest.raises(ValueError, match="no compatible"):
        SessionEvent.from_dict({"protocol_version": 2})


def test_web_and_desktop_implement_the_same_session_port(tmp_path) -> None:
    web = SimulationSession(
        session_id="contract-session",
        config={"EXAMPLES_DIR": tmp_path, "WORLDS_DIR": tmp_path},
        max_runtime_s=1,
    )
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        assert isinstance(web, SimulationSessionPort)
        assert isinstance(desktop, SimulationSessionPort)
    finally:
        web.close()
        desktop.close()
