"""
test_motor_model.py
===================
Tests unitarios para MotorModel (domain/robot/motor_model.py).

Valida:
    - Transiciones de estado
    - Evolución temporal (update)
    - Comandos bloqueantes (run_time, run_angle)
    - Modos de detención (StopMode)
"""

import math
import pytest
from simulador_ev3.domain.robot.motor_model import MotorModel, MotorState, StopMode


# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #

@pytest.fixture
def motor() -> MotorModel:
    return MotorModel(port_name="A")


# ------------------------------------------------------------------ #
# Estado inicial
# ------------------------------------------------------------------ #

class TestInitialState:
    def test_initial_state_is_idle(self, motor: MotorModel) -> None:
        assert motor.state == MotorState.IDLE

    def test_initial_speed_is_zero(self, motor: MotorModel) -> None:
        assert motor.speed == 0.0

    def test_initial_angle_is_zero(self, motor: MotorModel) -> None:
        assert motor.angle == 0.0

    def test_initial_power_is_zero(self, motor: MotorModel) -> None:
        assert motor.power == 0.0


# ------------------------------------------------------------------ #
# Transiciones de estado
# ------------------------------------------------------------------ #

class TestStateTransitions:
    def test_run_transitions_to_run(self, motor: MotorModel) -> None:
        motor.cmd_run(300.0)
        assert motor.state == MotorState.RUN

    def test_stop_transitions_to_idle(self, motor: MotorModel) -> None:
        motor.cmd_run(300.0)
        motor.cmd_stop()
        assert motor.state == MotorState.IDLE

    def test_brake_transitions_to_brake(self, motor: MotorModel) -> None:
        motor.cmd_run(300.0)
        motor.cmd_brake()
        assert motor.state == MotorState.BRAKE

    def test_hold_transitions_to_hold(self, motor: MotorModel) -> None:
        motor.cmd_run(300.0)
        motor.cmd_hold()
        assert motor.state == MotorState.HOLD

    def test_run_time_transitions_to_run_time(self, motor: MotorModel) -> None:
        motor.cmd_run_time(speed=200.0, time_ms=1000.0)
        assert motor.state == MotorState.RUN_TIME

    def test_run_angle_transitions_to_run_angle(self, motor: MotorModel) -> None:
        motor.cmd_run_angle(speed=200.0, rotation_angle=360.0)
        assert motor.state == MotorState.RUN_ANGLE

    def test_brake_resolves_to_idle_after_update(self, motor: MotorModel) -> None:
        motor.cmd_brake()
        motor.update(dt=0.02)
        assert motor.state == MotorState.IDLE

    def test_any_state_can_transition_to_run(self, motor: MotorModel) -> None:
        motor.cmd_hold()
        motor.cmd_run(100.0)
        assert motor.state == MotorState.RUN


# ------------------------------------------------------------------ #
# Evolución temporal — RUN
# ------------------------------------------------------------------ #

class TestRunUpdate:
    def test_angle_accumulates_while_running(self, motor: MotorModel) -> None:
        motor.cmd_run(360.0)   # 360 deg/s
        motor.update(dt=1.0)   # 1 segundo → 360 grados
        assert math.isclose(motor.angle, 360.0, abs_tol=1e-6)

    def test_negative_speed_decreases_angle(self, motor: MotorModel) -> None:
        motor.cmd_run(-180.0)
        motor.update(dt=1.0)
        assert math.isclose(motor.angle, -180.0, abs_tol=1e-6)

    def test_multiple_updates_accumulate(self, motor: MotorModel) -> None:
        motor.cmd_run(100.0)
        for _ in range(50):    # 50 ticks * 0.02 s = 1 s
            motor.update(dt=0.02)
        assert math.isclose(motor.angle, 100.0, abs_tol=0.01)


# ------------------------------------------------------------------ #
# Evolución temporal — RUN_TIME
# ------------------------------------------------------------------ #

class TestRunTimeUpdate:
    def test_motor_stops_after_time(self, motor: MotorModel) -> None:
        motor.cmd_run_time(speed=360.0, time_ms=1000.0, then=StopMode.COAST)
        # 50 ticks * 20ms = 1000ms
        completed = False
        for _ in range(50):
            completed = motor.update(dt=0.02)
        assert completed is True
        assert motor.state == MotorState.IDLE

    def test_motor_holds_after_time_with_hold_mode(self, motor: MotorModel) -> None:
        motor.cmd_run_time(speed=200.0, time_ms=500.0, then=StopMode.HOLD)
        for _ in range(25):
            motor.update(dt=0.02)
        assert motor.state == MotorState.HOLD

    def test_angle_accumulated_during_run_time(self, motor: MotorModel) -> None:
        motor.cmd_run_time(speed=360.0, time_ms=1000.0)
        for _ in range(50):
            motor.update(dt=0.02)
        assert math.isclose(motor.angle, 360.0, abs_tol=1.0)


# ------------------------------------------------------------------ #
# Evolución temporal — RUN_ANGLE
# ------------------------------------------------------------------ #

class TestRunAngleUpdate:
    def test_motor_completes_target_angle(self, motor: MotorModel) -> None:
        motor.cmd_run_angle(speed=360.0, rotation_angle=360.0, then=StopMode.HOLD)
        for _ in range(100):
            if motor.update(dt=0.02):
                break
        assert math.isclose(motor.angle, 360.0, abs_tol=1.0)
        assert motor.state == MotorState.HOLD

    def test_negative_angle_direction(self, motor: MotorModel) -> None:
        motor.cmd_run_angle(speed=200.0, rotation_angle=-180.0)
        for _ in range(100):
            if motor.update(dt=0.02):
                break
        assert motor.angle < 0.0

    def test_zero_angle_does_not_change_state(self, motor: MotorModel) -> None:
        motor.cmd_run_angle(speed=200.0, rotation_angle=0.0)
        assert motor.state == MotorState.IDLE   # sin cambio


# ------------------------------------------------------------------ #
# Reset e idle
# ------------------------------------------------------------------ #

class TestUtilities:
    def test_reset_angle(self, motor: MotorModel) -> None:
        motor.cmd_run(360.0)
        motor.update(dt=1.0)
        motor.reset_angle()
        assert motor.angle == 0.0

    def test_idle_speed_is_zero(self, motor: MotorModel) -> None:
        motor.cmd_run(500.0)
        motor.cmd_stop()
        motor.update(dt=0.02)
        assert motor.speed == 0.0
