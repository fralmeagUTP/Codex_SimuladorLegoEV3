import time
from pathlib import Path

import pytest

from simulador_ev3.runtime.isolated_worker import (
    IsolatedRuntimeWorker,
    WorkerMessage,
    WorkerResourcePolicy,
    worker_isolation_enabled,
)
from simulador_ev3.web.services.simulation_session import SimulationSession


def test_worker_message_has_versioned_serializable_envelope() -> None:
    message = WorkerMessage("session", 1, "command", "initialize", {"x": 1}, "command-1")

    assert message.to_dict()["protocol_version"] == 1
    assert message.to_dict()["command_id"] == "command-1"


def test_isolated_worker_initializes_and_stops() -> None:
    worker = IsolatedRuntimeWorker("test-worker")
    worker.start()
    try:
        assert worker.receive()["type"] == "ready"
        command_id = worker.send(
            "initialize", {"execution_policy": {"max_runtime_s": 2, "max_memory_mb": 128, "max_cpu_s": 2}}
        )
        event = worker.receive()
        assert event["type"] == "status"
        assert event["payload"]["status"] == "ready"
        assert event["command_id"] == command_id
        assert event["payload"]["resource_limits"]["runtime"] is True
        assert event["payload"]["resource_limits"]["privileges"] is True
        assert isinstance(event["payload"]["resource_limits"]["cpu"], bool)
        assert isinstance(event["payload"]["resource_limits"]["memory"], bool)

        configured = worker.send(
            "initialize",
            {
                "execution_policy": {"max_runtime_s": 2, "max_memory_mb": 128, "max_cpu_s": 2},
                "engine_config": {"world_width_mm": 1234.0},
            },
        )
        event = worker.receive()
        assert event["command_id"] == configured
        assert event["payload"]["engine_config"]["world_width_mm"] == 1234.0
    finally:
        worker.close()


def test_worker_resource_policy_requires_positive_limits() -> None:
    with pytest.raises(ValueError, match="positivos"):
        WorkerResourcePolicy.from_payload({"max_runtime_s": 0, "max_memory_mb": 128, "max_cpu_s": 1})


def test_worker_feature_flag_is_opt_in(monkeypatch) -> None:
    monkeypatch.delenv("EV3_WORKER_ISOLATION_ENABLED", raising=False)
    assert worker_isolation_enabled() is False
    monkeypatch.setenv("EV3_WORKER_ISOLATION_ENABLED", "true")
    assert worker_isolation_enabled() is True


def test_isolated_worker_rejects_incompatible_protocol() -> None:
    worker = IsolatedRuntimeWorker("protocol-worker")
    worker.start()
    try:
        worker.receive()
        worker.send_raw_for_diagnostics({"protocol_version": 999})
        event = worker.receive()
        assert event["type"] == "error"
        assert event["payload"]["code"] == "IPC_PROTOCOL_ERROR"
    finally:
        worker.close()


def test_isolated_worker_drains_events_without_blocking() -> None:
    worker = IsolatedRuntimeWorker("drain-worker")
    worker.start()
    try:
        ready = worker.receive()
        assert ready["type"] == "ready"
        assert worker.drain_events() == []
        worker.send("load_script")
        for _ in range(20):
            events = worker.drain_events()
            if events:
                break
        else:
            events = [worker.receive()]
        assert events[0]["type"] == "loaded"
    finally:
        worker.close()


def test_isolated_worker_emits_lifecycle_states() -> None:
    worker = IsolatedRuntimeWorker("lifecycle-worker")
    worker.start()
    try:
        worker.receive()
        expected = (
            ("load_script", "loaded", "ready"),
            ("start", "status", "running"),
            ("pause", "status", "paused"),
            ("resume", "status", "running"),
            ("stop", "status", "stopped"),
            ("reset", "status", "created"),
        )
        for command, event_type, status in expected:
            worker.send(command)
            event = worker.receive()
            assert event["type"] == event_type
            assert event["payload"]["status"] == status
    finally:
        worker.close()


def test_isolated_worker_blocks_network_inside_process() -> None:
    worker = IsolatedRuntimeWorker("network-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("probe_network")
        event = worker.receive()

        assert event["type"] == "sandbox"
        assert event["payload"]["network_enabled"] is False
    finally:
        worker.close()


def test_isolated_worker_uses_private_working_directory() -> None:
    worker = IsolatedRuntimeWorker("filesystem-worker")
    worker.start()
    try:
        ready = worker.receive()
        assert ready["payload"]["workdir"]
        assert "ev3-worker-" in ready["payload"]["workdir"]
    finally:
        worker.close()


def test_isolated_worker_removes_inherited_secret_environment_variable(monkeypatch) -> None:
    monkeypatch.setenv("EV3_TEST_SECRET", "do-not-expose")
    worker = IsolatedRuntimeWorker("environment-worker")
    worker.start()
    try:
        ready = worker.receive()
        assert ready["payload"]["environment_sanitized"] is True
        worker.send("probe_environment", {"name": "EV3_TEST_SECRET"})
        event = worker.receive()
        assert event["type"] == "sandbox"
        assert event["payload"]["value_present"] is False
    finally:
        worker.close()


def test_isolated_worker_restricts_open_outside_private_directory() -> None:
    worker = IsolatedRuntimeWorker("filesystem-guard-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("probe_filesystem")
        event = worker.receive()
        assert event["type"] == "sandbox"
        assert event["payload"]["filesystem_restricted"] is True
    finally:
        worker.close()


def test_isolated_worker_executes_script_and_emits_snapshot() -> None:
    worker = IsolatedRuntimeWorker("execution-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("initialize", {"execution_policy": {"max_runtime_s": 2, "max_memory_mb": 128, "max_cpu_s": 2}})
        worker.receive()
        worker.send("load_script", {"source": "from pybricks.tools import wait\nwait(30)\n"})
        worker.receive()
        worker.send("start")
        events = []
        for _ in range(10):
            try:
                events.append(worker.receive(0.2))
            except TimeoutError:
                break
            if any(event["type"] == "status" and event["payload"]["status"] == "running" for event in events) and any(
                event["type"] == "snapshot" for event in events
            ):
                break

        assert any(event["type"] == "status" and event["payload"]["status"] == "running" for event in events)
        assert any(event["type"] == "snapshot" for event in events)
    finally:
        worker.close()


def test_web_session_starts_shadow_worker_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv("EV3_WORKER_ISOLATION_ENABLED", "true")
    session = SimulationSession(session_id="web-shadow-test", config={}, max_runtime_s=1.0)
    try:
        assert session._worker_shadow is not None
        session.load_script("from pybricks.tools import wait\nwait(10)\n")
        session.start()
        for _ in range(20):
            response = session.snapshot_response()
            if session._worker_shadow_snapshot is not None:
                break
            time.sleep(0.02)
        assert session._worker_shadow_last_sequence > 0
        assert session._worker_shadow_snapshot is not None
        assert response["status"] in {"running", "finished", "stopped"}
        assert any(event["type"] == "snapshot" for event in session.events_since())
    finally:
        session.close()


def test_web_session_recovers_worker_and_replays_loaded_script(monkeypatch) -> None:
    monkeypatch.setenv("EV3_WORKER_ISOLATION_ENABLED", "true")
    session = SimulationSession(session_id="web-recovery-test", config={}, max_runtime_s=1.0)
    try:
        session.load_script("x = 1")
        assert session._worker_shadow is not None
        previous_pid = session._worker_shadow._process.pid

        summary = session.recover_worker()

        assert summary["status"] == "ready"
        assert session._worker_shadow._process.pid != previous_pid
        assert session._source_code == "x = 1"
    finally:
        session.close()


def test_isolated_worker_cancels_long_running_script() -> None:
    worker = IsolatedRuntimeWorker("cancel-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("initialize", {"execution_policy": {"max_runtime_s": 5, "max_memory_mb": 128, "max_cpu_s": 5}})
        worker.receive()
        worker.send("load_script", {"source": "from pybricks.tools import wait\nwhile True:\n    wait(10)\n"})
        worker.receive()
        worker.send("start")
        worker.send("stop", command_id="stop-long-script")
        events = []
        for _ in range(30):
            events.extend(worker.drain_events())
            if any(event.get("command_id") == "stop-long-script" for event in events):
                break
            time.sleep(0.03)

        stopped = next(event for event in events if event.get("command_id") == "stop-long-script")
        assert stopped["type"] == "status"
        assert stopped["payload"]["status"] == "stopped"
    finally:
        worker.close()


def test_isolated_worker_times_out_unbounded_script() -> None:
    worker = IsolatedRuntimeWorker("timeout-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("initialize", {"execution_policy": {"max_runtime_s": 0.1, "max_memory_mb": 128, "max_cpu_s": 1}})
        worker.receive()
        worker.send("load_script", {"source": "from pybricks.tools import wait\nwhile True:\n    wait(10)\n"})
        worker.receive()
        worker.send("start")
        events = []
        for _ in range(60):
            events.extend(worker.drain_events())
            if any(
                event.get("type") == "status" and event.get("payload", {}).get("status") == "timed_out"
                for event in events
            ):
                break
            time.sleep(0.03)

        assert any(
            event.get("type") == "status" and event.get("payload", {}).get("status") == "timed_out" for event in events
        )
    finally:
        worker.close()


def test_isolated_worker_recovers_after_forced_restart() -> None:
    worker = IsolatedRuntimeWorker("recovery-worker")
    worker.start()
    try:
        first = worker.receive()
        worker.restart()
        recovered = worker.receive()

        assert first["type"] == "ready"
        assert recovered["type"] == "ready"
        assert first["payload"]["worker_pid"] != recovered["payload"]["worker_pid"]
    finally:
        worker.close()


def test_isolated_worker_heartbeat_reports_resource_usage() -> None:
    worker = IsolatedRuntimeWorker("heartbeat-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("heartbeat")
        event = worker.receive()

        assert event["type"] == "heartbeat"
        assert event["payload"]["cpu_s"] >= 0
        assert event["payload"]["memory_bytes"] >= 0
    finally:
        worker.close()


def test_isolated_worker_applies_debug_configuration() -> None:
    worker = IsolatedRuntimeWorker("debug-config-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("initialize", {"execution_policy": {"max_runtime_s": 2, "max_memory_mb": 128, "max_cpu_s": 2}})
        worker.receive()
        worker.send("set_debug", {"breakpoints": [8, "3", 0], "watches": ["motor.angle()", "  "]})
        event = worker.receive()

        assert event["type"] == "debug_configured"
        assert event["payload"]["breakpoints"] == [3, 8]
        assert event["payload"]["watches"] == ["motor.angle()"]
    finally:
        worker.close()


def test_isolated_worker_accepts_debug_control_commands() -> None:
    worker = IsolatedRuntimeWorker("debug-command-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("debug_step")
        step = worker.receive()
        worker.send("debug_continue")
        resumed = worker.receive()

        assert step["type"] == "debug_command"
        assert step["payload"]["action"] == "step"
        assert resumed["type"] == "debug_command"
        assert resumed["payload"]["action"] == "continue"
    finally:
        worker.close()


def test_isolated_worker_accepts_robot_start_configuration() -> None:
    worker = IsolatedRuntimeWorker("robot-start-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("set_robot_start", {"x_mm": 120, "y_mm": 340, "theta_deg": 90})
        event = worker.receive()

        assert event["type"] == "robot_start_configured"
        assert event["payload"] == {"x_mm": 120.0, "y_mm": 340.0, "theta_deg": 90.0}
    finally:
        worker.close()


def test_isolated_worker_loads_world_from_ipc_source() -> None:
    worker = IsolatedRuntimeWorker("world-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("initialize", {"execution_policy": {"max_runtime_s": 2, "max_memory_mb": 128, "max_cpu_s": 2}})
        worker.receive()
        source = (Path(__file__).parents[2] / "worlds" / "01_linea_negra_basica.json").read_text(encoding="utf-8")
        command_id = worker.send("load_world", {"source": source})
        events = [worker.receive() for _ in range(2)]

        loaded = next(event for event in events if event.get("command_id") == command_id)
        assert loaded["type"] == "world_loaded"
        assert loaded["payload"]["snapshot"] is not None
    finally:
        worker.close()


def test_isolated_worker_loads_blank_world_from_dimensions() -> None:
    worker = IsolatedRuntimeWorker("blank-world-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("initialize", {"execution_policy": {"max_runtime_s": 2, "max_memory_mb": 128, "max_cpu_s": 2}})
        worker.receive()
        command_id = worker.send("load_blank_world", {"width_mm": 1000, "height_mm": 1500})
        events = [worker.receive() for _ in range(2)]

        loaded = next(event for event in events if event.get("command_id") == command_id)
        assert loaded["type"] == "world_loaded"
        assert loaded["payload"]["blank"] is True
    finally:
        worker.close()


def test_isolated_worker_configures_simulation_profile() -> None:
    worker = IsolatedRuntimeWorker("profile-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("initialize", {"execution_policy": {"max_runtime_s": 2, "max_memory_mb": 128, "max_cpu_s": 2}})
        worker.receive()
        worker.send("set_simulation_profile", {"profile": "calibrated", "calibration": {"traction_scale": 0.9}})
        event = worker.receive()

        assert event["type"] == "profile_configured"
        assert event["payload"]["profile"] == "calibrated"
    finally:
        worker.close()
