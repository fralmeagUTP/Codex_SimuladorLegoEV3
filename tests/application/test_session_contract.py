import pytest

from simulador_ev3.application.desktop_session_adapter import DesktopSessionAdapter
from simulador_ev3.application.interface_ports import (
    OBSERVABILITY_REDACTED_FIELDS,
    OBSERVABILITY_RETENTION_DAYS,
    LearningPort,
    ObservabilityPort,
    ObservabilitySnapshot,
    PresentationPort,
)
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


def test_session_event_roundtrips_versioned_mission_result() -> None:
    raw = {
        "protocol_version": 1,
        "session_id": "session-1",
        "sequence": 4,
        "kind": "event",
        "type": "mission_result",
        "payload": {"event_version": 1, "outcome": "finished", "result": {"passed": True, "score": 10}},
        "command_id": None,
    }

    assert SessionEvent.from_dict(raw).to_dict() == raw


def test_session_event_rejects_unknown_protocol_version() -> None:
    with pytest.raises(ValueError, match="no compatible"):
        SessionEvent.from_dict({"protocol_version": 2})


def test_observability_snapshot_is_minimal_and_excludes_sensitive_fields() -> None:
    payload = ObservabilitySnapshot(
        session_id="session-safe",
        command_id="command-safe",
        worker_id="worker-safe",
        status="finished",
        tick=12,
    ).to_dict()

    assert payload["session_id"] == "session-safe"
    assert payload["command_id"] == "command-safe"
    assert not (set(payload) & OBSERVABILITY_REDACTED_FIELDS)
    assert OBSERVABILITY_RETENTION_DAYS == 30


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


def test_web_and_desktop_expose_versioned_presentation_learning_and_observability_ports() -> None:
    web = SimulationSession(
        session_id="interface-contract-session",
        config={},
        max_runtime_s=1,
    )
    desktop = DesktopSessionAdapter(SimEngineConfig())
    try:
        for session in (web, desktop):
            assert isinstance(session, PresentationPort)
            assert isinstance(session, LearningPort)
            assert isinstance(session, ObservabilityPort)
            assert session.presentation_state().to_dict()["version"] == 1
            assert session.learning_state().to_dict()["version"] == 1
            assert session.observability_snapshot().to_dict()["version"] == 1
    finally:
        web.close()
        desktop.close()
