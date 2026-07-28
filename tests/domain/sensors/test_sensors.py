"""
test_sensors.py
===============
Tests unitarios para los modelos de sensores EV3 (Fase 2).

Prueba los cinco sensores contra un WorldModel sintético controlado.
"""

import math

import pytest

from simulador_ev3.domain.sensors.color_sensor_model import ColorSensorModel
from simulador_ev3.domain.sensors.gyro_sensor_model import GyroSensorModel
from simulador_ev3.domain.sensors.infrared_sensor_model import InfraredSensorModel
from simulador_ev3.domain.sensors.touch_sensor_model import TouchSensorModel
from simulador_ev3.domain.sensors.ultrasonic_sensor_model import UltrasonicSensorModel
from simulador_ev3.domain.world.beacon_model import BeaconModel
from simulador_ev3.domain.world.obstacle_model import ObstacleModel
from simulador_ev3.domain.world.surface_model import SurfaceColor, SurfaceModel
from simulador_ev3.domain.world.world_model import WorldModel

# ------------------------------------------------------------------ #
# Mundo de prueba compartido
# ------------------------------------------------------------------ #


@pytest.fixture
def world_open() -> WorldModel:
    """Mundo vacío 2000×2000 mm con superficie blanca."""
    return WorldModel(width_mm=2000, height_mm=2000)


@pytest.fixture
def world_with_wall() -> WorldModel:
    """Mundo con una pared vertical a x=500 mm."""
    w = WorldModel(width_mm=2000, height_mm=2000)
    w.add_obstacle(ObstacleModel.from_rect(500, 0, 50, 2000, "wall"))
    return w


@pytest.fixture
def world_black_line() -> WorldModel:
    """Mundo con una línea negra horizontal (y=0-50, celda de 50 mm)."""
    w = WorldModel(width_mm=2000, height_mm=2000)
    w.surface = SurfaceModel(cell_size_mm=50.0)
    # Línea negra a lo largo de y ~ 0-50 mm
    w.surface.set_rect(0, 0, 2000, 50, SurfaceColor.BLACK)
    return w


# ================================================================== #
# TouchSensorModel
# ================================================================== #


class TestTouchSensor:
    def test_not_pressed_in_open_world(self, world_open: WorldModel) -> None:
        sensor = TouchSensorModel(port_name="S1", offset_x_mm=80.0)
        sensor.update(100.0, 1000.0, 0.0, world_open)
        assert not sensor.pressed()

    def test_pressed_when_against_wall(self, world_with_wall: WorldModel) -> None:
        # Robot a x=400 mm, sensor a +80 mm → x=480, cerca de la pared en x=500
        sensor = TouchSensorModel(port_name="S1", offset_x_mm=80.0, robot_radius_mm=25.0)
        sensor.update(400.0, 1000.0, 0.0, world_with_wall)
        assert sensor.pressed()

    def test_not_pressed_far_from_wall(self, world_with_wall: WorldModel) -> None:
        sensor = TouchSensorModel(port_name="S1", offset_x_mm=80.0, robot_radius_mm=5.0)
        sensor.update(100.0, 1000.0, 0.0, world_with_wall)
        assert not sensor.pressed()

    def test_to_dict_has_pressed_key(self, world_open: WorldModel) -> None:
        sensor = TouchSensorModel()
        sensor.update(100.0, 100.0, 0.0, world_open)
        d = sensor.to_dict()
        assert "pressed" in d


# ================================================================== #
# UltrasonicSensorModel
# ================================================================== #


class TestUltrasonicSensor:
    def test_reads_max_in_open_world(self, world_open: WorldModel) -> None:
        sensor = UltrasonicSensorModel(port_name="S4", offset_x_mm=0.0)
        # Robot en el centro apuntando al este — borde a 1000 mm
        sensor.update(1000.0, 1000.0, 0.0, world_open)
        assert sensor.distance() > 500  # al menos 500 mm libre

    def test_detects_wall(self, world_with_wall: WorldModel) -> None:
        # Robot en x=100, pared en x=500 → distancia ~400 mm
        sensor = UltrasonicSensorModel(port_name="S4", offset_x_mm=0.0)
        sensor.update(100.0, 1000.0, 0.0, world_with_wall)
        assert sensor.distance() < 450

    def test_distance_decreases_approaching_wall(self, world_with_wall: WorldModel) -> None:
        sensor = UltrasonicSensorModel(port_name="S4", offset_x_mm=0.0)
        sensor.update(100.0, 1000.0, 0.0, world_with_wall)
        d1 = sensor.distance()
        sensor.update(300.0, 1000.0, 0.0, world_with_wall)
        d2 = sensor.distance()
        assert d2 < d1

    def test_returns_int(self, world_open: WorldModel) -> None:
        sensor = UltrasonicSensorModel()
        sensor.update(500.0, 500.0, 0.0, world_open)
        assert isinstance(sensor.distance(), int)

    def test_presence_always_false(self, world_open: WorldModel) -> None:
        sensor = UltrasonicSensorModel()
        sensor.update(500.0, 500.0, 0.0, world_open)
        assert sensor.presence() is False


# ================================================================== #
# ColorSensorModel
# ================================================================== #


class TestColorSensor:
    def test_reads_white_on_white_surface(self, world_open: WorldModel) -> None:
        sensor = ColorSensorModel(port_name="S3", offset_x_mm=0.0)
        sensor.update(100.0, 100.0, 0.0, world_open)
        assert sensor.color() == SurfaceColor.WHITE

    def test_reflection_white_is_high(self, world_open: WorldModel) -> None:
        sensor = ColorSensorModel(port_name="S3", offset_x_mm=0.0)
        sensor.update(100.0, 100.0, 0.0, world_open)
        assert sensor.reflection() > 80

    def test_reads_black_on_black_line(self, world_black_line: WorldModel) -> None:
        sensor = ColorSensorModel(port_name="S3", offset_x_mm=0.0)
        # Robot en y=25, sobre la línea negra
        sensor.update(100.0, 25.0, 0.0, world_black_line)
        assert sensor.color() == SurfaceColor.BLACK

    def test_reflection_black_is_low(self, world_black_line: WorldModel) -> None:
        sensor = ColorSensorModel(port_name="S3", offset_x_mm=0.0)
        sensor.update(100.0, 25.0, 0.0, world_black_line)
        assert sensor.reflection() < 20

    def test_ambient_always_zero(self, world_open: WorldModel) -> None:
        sensor = ColorSensorModel()
        sensor.update(100.0, 100.0, 0.0, world_open)
        assert sensor.ambient() == 0

    def test_to_dict_has_color_and_reflectance(self, world_open: WorldModel) -> None:
        sensor = ColorSensorModel()
        sensor.update(100.0, 100.0, 0.0, world_open)
        d = sensor.to_dict()
        assert "color" in d and "reflectance" in d


# ================================================================== #
# GyroSensorModel
# ================================================================== #


class TestGyroSensor:
    def test_initial_angle_is_zero(self) -> None:
        sensor = GyroSensorModel()
        sensor.update(robot_theta_rad=0.0, dt=0.02)
        assert sensor.angle() == 0

    def test_angle_after_rotation(self) -> None:
        sensor = GyroSensorModel()
        sensor.update(0.0, 0.02)  # primer tick (inicializa)
        sensor.update(math.pi / 2, 0.02)  # 90° de rotación
        assert 85 <= sensor.angle() <= 95  # ~90°

    def test_speed_during_rotation(self) -> None:
        sensor = GyroSensorModel()
        sensor.update(0.0, 0.02)
        # 90° en 0.02 s → ~4500 °/s
        sensor.update(math.pi / 2, 0.02)
        assert sensor.speed() > 1000  # claramente positivo

    def test_speed_idle_is_zero(self) -> None:
        sensor = GyroSensorModel()
        sensor.update(0.5, 0.02)
        sensor.update(0.5, 0.02)  # sin cambio de theta
        assert sensor.speed() == 0

    def test_reset_angle(self) -> None:
        sensor = GyroSensorModel()
        sensor.update(math.pi, 0.02)  # 180°
        sensor.update(math.pi, 0.02)
        sensor.reset_angle(0)
        assert sensor.angle() == 0

    def test_returns_int(self) -> None:
        sensor = GyroSensorModel()
        sensor.update(0.5, 0.02)
        assert isinstance(sensor.angle(), int)
        assert isinstance(sensor.speed(), int)


# ================================================================== #
# InfraredSensorModel
# ================================================================== #


class TestInfraredSensor:
    def test_proximity_in_open_world(self, world_open: WorldModel) -> None:
        sensor = InfraredSensorModel(port_name="S2", offset_x_mm=0.0)
        sensor.update(1000.0, 1000.0, 0.0, world_open)
        assert 0 <= sensor.distance() <= 100

    def test_proximity_increases_near_wall(self) -> None:
        world = WorldModel(width_mm=2000, height_mm=2000)
        world.add_obstacle(ObstacleModel.from_rect(300, 0, 50, 2000, "wall"))
        sensor = InfraredSensorModel(offset_x_mm=0.0)
        sensor.update(1000.0, 1000.0, 0.0, world)  # lejos
        d_far = sensor.distance()
        sensor.update(100.0, 1000.0, 0.0, world)  # cerca
        d_near = sensor.distance()
        assert d_near >= d_far

    def test_beacon_no_beacon_returns_zeros(self, world_open: WorldModel) -> None:
        sensor = InfraredSensorModel()
        dist, heading = sensor.beacon(1, world_open, 0, 0, 0)
        assert dist == 0 and heading == 0

    def test_beacon_with_beacon(self) -> None:
        world = WorldModel()
        world.add_beacon(BeaconModel(x_mm=300, y_mm=0, channel=1))
        sensor = InfraredSensorModel()
        dist, heading = sensor.beacon(1, world, 0, 0, 0)
        assert dist > 0
        assert -25 <= heading <= 25
