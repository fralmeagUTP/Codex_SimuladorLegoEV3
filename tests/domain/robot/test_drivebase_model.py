"""
test_drivebase_model.py
=======================
Tests unitarios para DriveBaseModel (domain/robot/drivebase_model.py).

Valida:
    - Cinemática diferencial
    - Comandos drive / stop / straight / turn / settings
    - Completado correcto de movimientos acotados
"""

import math
import pytest
from simulador_ev3.domain.robot.drivebase_model import (
    DriveBaseModel,
    DriveState,
    AccelerationProfile,
)


WHEEL_D  = 55.5   # mm — valor nominal EV3 de los ejemplos
AXLE_T   = 104.0  # mm — valor nominal EV3 de los ejemplos


@pytest.fixture
def drivebase() -> DriveBaseModel:
    return DriveBaseModel(wheel_diameter_mm=WHEEL_D, axle_track_mm=AXLE_T)


# ------------------------------------------------------------------ #
# Validación de construcción
# ------------------------------------------------------------------ #

class TestConstruction:
    def test_default_state_is_idle(self, drivebase: DriveBaseModel) -> None:
        assert drivebase.state == DriveState.IDLE

    def test_invalid_wheel_diameter_raises(self) -> None:
        with pytest.raises(ValueError, match="wheel_diameter_mm"):
            DriveBaseModel(wheel_diameter_mm=0.0, axle_track_mm=100.0)

    def test_invalid_axle_track_raises(self) -> None:
        with pytest.raises(ValueError, match="axle_track_mm"):
            DriveBaseModel(wheel_diameter_mm=55.5, axle_track_mm=-10.0)

    def test_acceleration_profile_defaults(self, drivebase: DriveBaseModel) -> None:
        assert drivebase.profile.straight_speed > 0
        assert drivebase.profile.turn_rate > 0


# ------------------------------------------------------------------ #
# Comando drive
# ------------------------------------------------------------------ #

class TestDrive:
    def test_drive_sets_state(self, drivebase: DriveBaseModel) -> None:
        drivebase.cmd_drive(200.0, 0.0)
        assert drivebase.state == DriveState.DRIVE

    def test_drive_produces_forward_delta(self, drivebase: DriveBaseModel) -> None:
        drivebase.cmd_drive(200.0, 0.0)
        dd, da, completed = drivebase.update(dt=1.0)
        assert math.isclose(dd, 200.0, abs_tol=1e-6)
        assert math.isclose(da, 0.0, abs_tol=1e-6)
        assert not completed

    def test_drive_negative_speed_reverses(self, drivebase: DriveBaseModel) -> None:
        drivebase.cmd_drive(-100.0, 0.0)
        dd, da, _ = drivebase.update(dt=1.0)
        assert dd < 0.0

    def test_drive_with_turn_rate(self, drivebase: DriveBaseModel) -> None:
        drivebase.cmd_drive(0.0, 90.0)
        dd, da, _ = drivebase.update(dt=1.0)
        assert math.isclose(da, 90.0, abs_tol=1e-6)


# ------------------------------------------------------------------ #
# Comando stop
# ------------------------------------------------------------------ #

class TestStop:
    def test_stop_transitions_to_idle(self, drivebase: DriveBaseModel) -> None:
        drivebase.cmd_drive(200.0, 0.0)
        drivebase.cmd_stop()
        assert drivebase.state == DriveState.IDLE

    def test_stop_produces_zero_deltas(self, drivebase: DriveBaseModel) -> None:
        drivebase.cmd_drive(200.0, 0.0)
        drivebase.cmd_stop()
        dd, da, completed = drivebase.update(dt=1.0)
        assert dd == 0.0 and da == 0.0


# ------------------------------------------------------------------ #
# Comando straight
# ------------------------------------------------------------------ #

class TestStraight:
    def test_straight_sets_state(self, drivebase: DriveBaseModel) -> None:
        drivebase.cmd_straight(200.0)
        assert drivebase.state == DriveState.STRAIGHT

    def test_straight_completes_and_returns_to_idle(self, drivebase: DriveBaseModel) -> None:
        drivebase.cmd_straight(100.0)
        total_dd = 0.0
        completed = False
        for _ in range(1000):
            dd, _, done = drivebase.update(dt=0.02)
            total_dd += dd
            if done:
                completed = True
                break
        assert completed
        assert drivebase.state == DriveState.IDLE
        assert math.isclose(total_dd, 100.0, abs_tol=1.0)

    def test_straight_negative_reverses(self, drivebase: DriveBaseModel) -> None:
        drivebase.cmd_straight(-50.0)
        total_dd = 0.0
        for _ in range(1000):
            dd, _, done = drivebase.update(dt=0.02)
            total_dd += dd
            if done:
                break
        assert total_dd < 0.0


# ------------------------------------------------------------------ #
# Comando turn
# ------------------------------------------------------------------ #

class TestTurn:
    def test_turn_sets_state(self, drivebase: DriveBaseModel) -> None:
        drivebase.cmd_turn(90.0)
        assert drivebase.state == DriveState.TURN

    def test_turn_completes_and_returns_to_idle(self, drivebase: DriveBaseModel) -> None:
        drivebase.cmd_turn(90.0)
        total_da = 0.0
        completed = False
        for _ in range(1000):
            _, da, done = drivebase.update(dt=0.02)
            total_da += da
            if done:
                completed = True
                break
        assert completed
        assert drivebase.state == DriveState.IDLE
        assert math.isclose(total_da, 90.0, abs_tol=1.0)

    def test_turn_negative_direction(self, drivebase: DriveBaseModel) -> None:
        drivebase.cmd_turn(-90.0)
        total_da = 0.0
        for _ in range(1000):
            _, da, done = drivebase.update(dt=0.02)
            total_da += da
            if done:
                break
        assert total_da < 0.0


# ------------------------------------------------------------------ #
# Comando settings
# ------------------------------------------------------------------ #

class TestSettings:
    def test_settings_updates_profile(self, drivebase: DriveBaseModel) -> None:
        drivebase.cmd_settings(
            straight_speed=500.0,
            straight_acceleration=300.0,
            turn_rate=180.0,
            turn_acceleration=180.0,
        )
        assert drivebase.profile.straight_speed == 500.0
        assert drivebase.profile.turn_rate == 180.0

    def test_settings_invalid_speed_raises(self, drivebase: DriveBaseModel) -> None:
        with pytest.raises(ValueError):
            drivebase.cmd_settings(
                straight_speed=-100.0,
                straight_acceleration=300.0,
                turn_rate=90.0,
                turn_acceleration=90.0,
            )
