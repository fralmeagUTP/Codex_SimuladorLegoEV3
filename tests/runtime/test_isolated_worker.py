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


def test_isolated_worker_ignores_a_queue_closed_during_session_shutdown() -> None:
    """Un stream SSE tardÃ­o no debe convertir un cierre normal en error 500."""

    worker = IsolatedRuntimeWorker("closed-drain-worker")
    worker.close()

    assert worker.drain_events() == []


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
            ("reset", "status", "reset"),
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


def test_isolated_worker_snapshot_and_tick_step_use_the_same_authoritative_state() -> None:
    """El tick manual debe proceder del worker que suministra los snapshots Web."""

    worker = IsolatedRuntimeWorker("tick-step-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("initialize", {"execution_policy": {"max_runtime_s": 2, "max_memory_mb": 128, "max_cpu_s": 2}})
        worker.receive()
        worker.send("load_script", {"source": "from pybricks.tools import wait\nwait(1)\n"})
        worker.receive()

        snapshot_command = worker.send("snapshot")
        initial = worker.receive()
        assert initial["type"] == "snapshot"
        assert initial["command_id"] == snapshot_command
        initial_tick = initial["payload"]["tick"]

        step_command = worker.send("step_tick")
        events: list[dict[str, object]] = []
        for _ in range(5):
            event = worker.receive(0.5)
            events.append(event)
            if event["type"] == "tick_step" and event["command_id"] == step_command:
                break

        acknowledged = next(event for event in events if event["type"] == "tick_step")
        stepped_snapshots = [event["payload"] for event in events if event["type"] == "snapshot"]
        assert acknowledged["payload"]["tick"] > initial_tick
        assert stepped_snapshots
        assert stepped_snapshots[-1]["tick"] == acknowledged["payload"]["tick"]
    finally:
        worker.close()


def test_isolated_worker_pauses_on_configured_debug_breakpoint() -> None:
    """La ruta aislada debe emitir la pausa que consume la interfaz Web."""

    worker = IsolatedRuntimeWorker("debug-breakpoint-worker")
    worker.start()
    try:
        worker.receive()
        # Esta prueba mide el ritmo de `wait`, no el límite de memoria. En los
        # runners Linux, un límite bajo puede terminar el proceso durante la carga de
        # módulos antes de que el script alcance el reloj de referencia.
        worker.send("initialize", {"execution_policy": {"max_runtime_s": 5, "max_memory_mb": 2048, "max_cpu_s": 5}})
        worker.receive()
        worker.send("load_script", {"source": "from pybricks.tools import wait\nx = 1\nwait(1000)\n"})
        worker.receive()
        worker.send("set_debug", {"breakpoints": [3], "watches": []})
        worker.receive()
        worker.send("start", {"debug": True})

        events: list[dict[str, object]] = []
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            try:
                event = worker.receive(0.2)
            except TimeoutError:
                continue
            events.append(event)
            if event["type"] == "debug" and event["payload"].get("type") == "paused":
                break

        paused = next(
            event for event in events if event["type"] == "debug" and event["payload"].get("type") == "paused"
        )
        assert paused["payload"]["line"] == 3
        assert paused["payload"]["reason"] == "breakpoint"
    finally:
        worker.close()


def test_web_session_consumes_isolated_worker_debug_pause(monkeypatch) -> None:
    """El estado pausado del worker debe alcanzar los controles de la sesión."""

    monkeypatch.setenv("EV3_WORKER_ISOLATION_ENABLED", "true")
    session = SimulationSession(session_id="web-isolated-debug", config={}, max_runtime_s=5.0)
    try:
        session.load_script("from pybricks.tools import wait\nx = 1\nwait(1000)\n")
        session.set_debug_breakpoints({3})
        session.start(debug=True)
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline and session.status != "paused":
            session.snapshot_response()
            time.sleep(0.03)

        assert session.status == "paused", {
            "debug": session.summary()["debug"],
            "events": [
                (event["type"], event["payload"].get("type"), event["payload"].get("line"))
                for event in session.events_since()[-12:]
            ],
            "worker_sequence": session._worker_shadow_last_sequence,
        }
        assert session.summary()["debug"]["debug_state"] == "paused_breakpoint"
        paused_tick = session.snapshot_response()["snapshot"]["tick"]
        time.sleep(0.12)
        assert session.snapshot_response()["snapshot"]["tick"] == paused_tick
        reset = session.reset()
        assert reset["status"] == "created"
        assert session.status == "created"
    finally:
        session.close()


def test_isolated_worker_resets_a_script_paused_at_a_breakpoint() -> None:
    """Reset debe cancelar el wait del depurador sin agotar el timeout IPC."""

    worker = IsolatedRuntimeWorker("debug-reset-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("initialize", {"execution_policy": {"max_runtime_s": 5, "max_memory_mb": 128, "max_cpu_s": 5}})
        worker.receive()
        worker.send("load_script", {"source": "from pybricks.tools import wait\nx = 1\nwait(10000)\n"})
        worker.receive()
        worker.send("set_debug", {"breakpoints": [3], "watches": []})
        worker.receive()
        worker.send("start", {"debug": True})

        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            event = worker.receive(0.5)
            if event["type"] == "debug" and event["payload"].get("type") == "paused":
                break
        else:
            pytest.fail("El worker no alcanzó el breakpoint.")

        reset_command = worker.send("reset")
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            event = worker.receive(0.5)
            if event["command_id"] == reset_command and event["type"] == "status":
                assert event["payload"]["status"] == "reset"
                break
        else:
            pytest.fail("El worker no confirmó reset tras el breakpoint.")
    finally:
        worker.close()


def test_isolated_worker_keeps_wait_close_to_wall_clock_time() -> None:
    """El aislamiento no puede acelerar artificialmente el reloj de la misión."""

    worker = IsolatedRuntimeWorker("worker-wall-clock")
    worker.start()
    try:
        worker.receive()
        worker.send("initialize", {"execution_policy": {"max_runtime_s": 5, "max_memory_mb": 128, "max_cpu_s": 5}})
        worker.receive()
        worker.send("load_script", {"source": "from pybricks.tools import wait\nwait(900)\n"})
        worker.receive()

        started_at = time.monotonic()
        worker.send("start")
        latest_snapshot: dict[str, object] | None = None
        deadline = started_at + 4.0
        while time.monotonic() < deadline:
            event = worker.receive(0.5)
            if event["type"] == "snapshot":
                latest_snapshot = event["payload"]
            if event["type"] == "status" and event["payload"].get("status") == "finished":
                break
        else:
            pytest.fail("El worker no terminó el wait de referencia.")

        elapsed_s = time.monotonic() - started_at
        assert latest_snapshot is not None
        assert float(latest_snapshot["sim_time_s"]) >= 0.9
        assert elapsed_s >= 0.75, elapsed_s
        assert elapsed_s <= 1.8, elapsed_s
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


def test_web_session_recovery_preserves_its_configured_runtime_limit(monkeypatch) -> None:
    """Una recuperacion no puede degradar el limite elegido por el usuario."""

    monkeypatch.setenv("EV3_WORKER_ISOLATION_ENABLED", "true")
    session = SimulationSession(
        session_id="web-recovery-runtime-limit",
        config={"SCRIPT_MAX_RUNTIME_S": 30.0},
        max_runtime_s=30.0,
    )
    try:
        session.set_max_runtime_s(300.0)
        session.recover_worker()

        assert session._max_runtime_s == 300.0
        assert session._worker_shadow is not None
        # El worker confirma su politica por el evento de configuracion; no
        # basta con conservar el valor solamente en la sesion local.
        assert session._service.max_runtime_s == 300.0
        assert session.worker_diagnostics()["max_runtime_s"] == 300.0
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


def test_isolated_worker_reset_emits_initial_pose_snapshot() -> None:
    worker = IsolatedRuntimeWorker("reset-pose-worker")
    worker.start()
    try:
        worker.receive()
        worker.send("initialize", {"execution_policy": {"max_runtime_s": 2, "max_memory_mb": 128, "max_cpu_s": 2}})
        worker.receive()
        worker.send("set_robot_start", {"x_mm": 120, "y_mm": 340, "theta_deg": 90})
        worker.receive()

        command_id = worker.send("reset")
        events = [worker.receive() for _ in range(6)]
        assert any(event["type"] == "snapshot" for event in events), [
            (event["type"], event["payload"]) for event in events
        ]
        snapshot = next(
            event
            for event in events
            if event["type"] == "snapshot" and event["command_id"] == command_id
        )
        status = next(
            event
            for event in events
            if event["type"] == "status" and event["command_id"] == command_id
        )

        assert snapshot["command_id"] == command_id
        assert snapshot["payload"]["robot"] == {"x_mm": 120.0, "y_mm": 340.0, "theta_deg": 90.0}
        assert status["payload"]["status"] == "reset"
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


def test_web_session_applies_editor_world_to_the_isolated_worker(tmp_path, monkeypatch) -> None:
    """El Editor Web no debe depender del runtime local al aplicar un mundo."""

    monkeypatch.setenv("EV3_WORKER_ISOLATION_ENABLED", "true")
    session = SimulationSession(
        session_id="editor-world-worker",
        config={"WORLDS_DIR": tmp_path, "EXAMPLES_DIR": tmp_path},
        max_runtime_s=2.0,
    )
    try:
        session.create_editor_world(10, 10)
        session.place_asset({"asset_key": "robot_ev3_32x32", "x": 64, "y": 64, "rotation": 90})
        session.place_asset({"asset_key": "wall_64x64_a", "x": 160, "y": 64, "rotation": 0})

        applied = session.apply_editor_world()

        assert applied["status"] == "ready"
        assert applied["world"]["editor_spec"]["placements"]
        assert session._worker_shadow is not None
        assert session._worker_shadow._process.is_alive()
    finally:
        session.close()


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
