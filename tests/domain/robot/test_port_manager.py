"""
test_port_manager.py
====================
Tests unitarios para PortManager (domain/robot/port_manager.py).
"""

import pytest
from simulador_ev3.domain.robot.port_manager import (
    PortManager,
    DeviceCategory,
    PortError,
    PortType,
)


class FakeMotor:
    pass


class FakeSensor:
    pass


@pytest.fixture
def pm() -> PortManager:
    return PortManager()


class TestRegistration:
    def test_register_motor_in_output_port(self, pm: PortManager) -> None:
        motor = FakeMotor()
        pm.register("B", motor, DeviceCategory.MOTOR)
        assert pm.is_registered("B")

    def test_register_sensor_in_input_port(self, pm: PortManager) -> None:
        sensor = FakeSensor()
        pm.register("S1", sensor, DeviceCategory.SENSOR)
        assert pm.is_registered("S1")

    def test_register_motor_in_input_port_raises(self, pm: PortManager) -> None:
        with pytest.raises(PortError, match="MOTOR"):
            pm.register("S2", FakeMotor(), DeviceCategory.MOTOR)

    def test_register_sensor_in_output_port_raises(self, pm: PortManager) -> None:
        with pytest.raises(PortError, match="SENSOR"):
            pm.register("A", FakeSensor(), DeviceCategory.SENSOR)

    def test_register_invalid_port_raises(self, pm: PortManager) -> None:
        with pytest.raises(PortError, match="no existe"):
            pm.register("X5", FakeMotor(), DeviceCategory.MOTOR)

    def test_register_duplicate_port_raises(self, pm: PortManager) -> None:
        pm.register("C", FakeMotor(), DeviceCategory.MOTOR)
        with pytest.raises(PortError, match="ya tiene registrado"):
            pm.register("C", FakeMotor(), DeviceCategory.MOTOR)

    def test_port_name_is_case_insensitive(self, pm: PortManager) -> None:
        pm.register("b", FakeMotor(), DeviceCategory.MOTOR)
        assert pm.is_registered("B")


class TestUnregister:
    def test_unregister_removes_device(self, pm: PortManager) -> None:
        pm.register("D", FakeMotor(), DeviceCategory.MOTOR)
        pm.unregister("D")
        assert not pm.is_registered("D")

    def test_unregister_empty_port_raises(self, pm: PortManager) -> None:
        with pytest.raises(PortError):
            pm.unregister("A")


class TestAccess:
    def test_get_device_returns_registered(self, pm: PortManager) -> None:
        motor = FakeMotor()
        pm.register("A", motor, DeviceCategory.MOTOR)
        assert pm.get_device("A") is motor

    def test_get_device_unregistered_raises(self, pm: PortManager) -> None:
        with pytest.raises(PortError):
            pm.get_device("S3")

    def test_all_motors(self, pm: PortManager) -> None:
        pm.register("A", FakeMotor(), DeviceCategory.MOTOR)
        pm.register("B", FakeMotor(), DeviceCategory.MOTOR)
        pm.register("S1", FakeSensor(), DeviceCategory.SENSOR)
        assert set(pm.all_motors().keys()) == {"A", "B"}

    def test_all_sensors(self, pm: PortManager) -> None:
        pm.register("S1", FakeSensor(), DeviceCategory.SENSOR)
        pm.register("S2", FakeSensor(), DeviceCategory.SENSOR)
        pm.register("A", FakeMotor(), DeviceCategory.MOTOR)
        assert set(pm.all_sensors().keys()) == {"S1", "S2"}

    def test_available_ports_returns_all_8(self, pm: PortManager) -> None:
        ports = PortManager.available_ports()
        assert len(ports) == 8
        assert "A" in ports
        assert "S4" in ports
