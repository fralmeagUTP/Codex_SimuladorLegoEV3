from simulador_ev3.application.simulation_service import SimulationService
from simulador_ev3.application.simulation_trace import SimulationTrace


def test_trace_exports_and_reloads_json() -> None:
    trace = SimulationTrace()
    trace.record({"tick": 1, "sim_time_s": 0.02, "colliding": False, "robot": {"x_mm": 10, "y_mm": 20, "theta_deg": 0}})

    restored = SimulationTrace.from_json(trace.to_json())

    assert restored.snapshots == trace.snapshots


def test_trace_exports_flat_csv() -> None:
    trace = SimulationTrace(
        [{"tick": 1, "sim_time_s": 0.02, "colliding": False, "robot": {"x_mm": 10, "y_mm": 20, "theta_deg": 0}}]
    )

    assert "tick,sim_time_s,x_mm,y_mm,theta_deg,colliding" in trace.to_csv()


def test_trace_is_bounded_and_declares_truncation() -> None:
    trace = SimulationTrace(max_snapshots=2)
    trace.record({"tick": 1})
    trace.record({"tick": 2})
    trace.record({"tick": 3})

    exported = trace.to_json()
    restored = SimulationTrace.from_json(exported)

    assert [item["tick"] for item in trace.snapshots] == [2, 3]
    assert trace.dropped_snapshots == 1
    assert '"truncated":true' in exported
    assert restored.dropped_snapshots == 1


def test_service_steps_exactly_one_tick_and_records_it() -> None:
    service = SimulationService()
    service.start_trace()

    snapshot = service.step_tick()

    assert snapshot.tick == 1
    assert '"tick":1' in service.export_trace("json")
