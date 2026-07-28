"""
test_robot_model.py
===================
Tests unitarios para RobotModel y Pose (domain/robot/robot_model.py).

Valida:
    - Integración cinemática correcta (SAD §13)
    - Actualización de pose x, y, theta
    - Avance recto, giro y combinación
    - Reset de pose
"""

import math

from simulador_ev3.domain.robot.drivebase_model import DriveBaseModel
from simulador_ev3.domain.robot.port_manager import PortManager
from simulador_ev3.domain.robot.robot_model import Pose, RobotModel

WHEEL_D = 55.5
AXLE_T = 104.0


def make_robot(x: float = 0.0, y: float = 0.0, theta: float = 0.0) -> RobotModel:
    drivebase = DriveBaseModel(wheel_diameter_mm=WHEEL_D, axle_track_mm=AXLE_T)
    pm = PortManager()
    return RobotModel(
        drivebase=drivebase,
        port_manager=pm,
        initial_pose=Pose(x=x, y=y, theta=theta),
    )


# ------------------------------------------------------------------ #
# Pose inicial
# ------------------------------------------------------------------ #


class TestInitialPose:
    def test_default_pose_is_origin(self) -> None:
        robot = make_robot()
        assert robot.x == 0.0 and robot.y == 0.0 and robot.theta == 0.0

    def test_custom_initial_pose(self) -> None:
        robot = make_robot(x=100.0, y=50.0, theta=math.pi / 2)
        assert math.isclose(robot.x, 100.0)
        assert math.isclose(robot.y, 50.0)
        assert math.isclose(robot.theta, math.pi / 2)

    def test_initial_pose_not_mutated(self) -> None:
        pose = Pose(x=10.0, y=20.0, theta=0.5)
        robot = make_robot(x=10.0, y=20.0, theta=0.5)
        robot.update(dt=1.0)  # aunque sea idle, comprobamos aislamiento
        assert pose.x == 10.0  # el argumento no fue mutado


# ------------------------------------------------------------------ #
# Cinemática — avance recto (theta = 0 → avanza en +X)
# ------------------------------------------------------------------ #


class TestKinematicsStraight:
    def test_drive_forward_increases_x(self) -> None:
        robot = make_robot()
        robot.drivebase.cmd_drive(200.0, 0.0)  # 200 mm/s hacia +X
        robot.update(dt=1.0)
        assert math.isclose(robot.x, 200.0, abs_tol=1e-4)
        assert math.isclose(robot.y, 0.0, abs_tol=1e-4)

    def test_drive_forward_multiple_ticks(self) -> None:
        robot = make_robot()
        robot.drivebase.cmd_drive(100.0, 0.0)
        for _ in range(50):  # 50 * 0.02 s = 1 s
            robot.update(dt=0.02)
        assert math.isclose(robot.x, 100.0, abs_tol=0.5)


# ------------------------------------------------------------------ #
# Cinemática — giro (avanza en +Y con theta = π/2)
# ------------------------------------------------------------------ #


class TestKinematicsAngle:
    def test_drive_at_90_degrees_increases_y(self) -> None:
        robot = make_robot(theta=math.pi / 2)  # apunta hacia +Y
        robot.drivebase.cmd_drive(200.0, 0.0)
        robot.update(dt=1.0)
        assert math.isclose(robot.x, 0.0, abs_tol=1e-3)
        assert math.isclose(robot.y, 200.0, abs_tol=1e-3)

    def test_angular_speed_updates_theta(self) -> None:
        robot = make_robot()
        robot.drivebase.cmd_drive(0.0, 90.0)  # gira 90°/s sin avanzar
        robot.update(dt=1.0)
        expected_theta = math.radians(90.0)
        # Normalizado en [-π, π]
        assert math.isclose(robot.theta, expected_theta, abs_tol=1e-4)

    def test_theta_normalized_after_full_turn(self) -> None:
        """Theta debe permanecer en [-π, π] tras una vuelta completa."""
        robot = make_robot()
        robot.drivebase.cmd_drive(0.0, 360.0)  # vuelta completa en 1 s
        robot.update(dt=1.0)
        assert -math.pi <= robot.theta <= math.pi


# ------------------------------------------------------------------ #
# theta_deg
# ------------------------------------------------------------------ #


class TestThetaDeg:
    def test_theta_deg_matches_radians(self) -> None:
        robot = make_robot(theta=math.pi)
        assert math.isclose(robot.theta_deg, 180.0, abs_tol=1e-6)


# ------------------------------------------------------------------ #
# Reset de pose
# ------------------------------------------------------------------ #


class TestResetPose:
    def test_reset_returns_to_origin(self) -> None:
        robot = make_robot()
        robot.drivebase.cmd_drive(300.0, 0.0)
        robot.update(dt=1.0)
        robot.reset_pose()
        assert robot.x == 0.0 and robot.y == 0.0 and robot.theta == 0.0

    def test_reset_to_custom_pose(self) -> None:
        robot = make_robot()
        new_pose = Pose(x=500.0, y=200.0, theta=math.pi / 4)
        robot.reset_pose(new_pose)
        assert math.isclose(robot.x, 500.0)
        assert math.isclose(robot.y, 200.0)
