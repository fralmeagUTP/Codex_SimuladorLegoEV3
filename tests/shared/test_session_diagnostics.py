from simulador_ev3.shared.session_diagnostics import (
    DIAGNOSTIC_SCHEMA_VERSION,
    build_session_diagnostic_payload,
)


def test_session_diagnostic_payload_is_versioned_and_portable() -> None:
    payload = build_session_diagnostic_payload(
        {"session_id": "session-1", "status": "finished"},
        runtime={"tick": 8},
        render={"renderedFrames": 3},
        worker={"worker_id": "worker-1"},
        generated_at="2026-08-24T00:00:00+00:00",
    )

    assert payload == {
        "schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "generated_at": "2026-08-24T00:00:00+00:00",
        "session": {"session_id": "session-1", "status": "finished"},
        "runtime": {"tick": 8},
        "render": {"renderedFrames": 3},
        "worker": {"worker_id": "worker-1"},
    }
