"""Pruebas integrales de salud del programa completo (release)."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from simulador_ev3.application.simulation_service import SimulationService
from simulador_ev3.pybricks_api._context import PybricksContext
from simulador_ev3.pybricks_api.factory import PybricksFactory
from simulador_ev3.runtime.runtime_controller import ControllerState

ROOT_DIR = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = ROOT_DIR / "Documentos" / "Ejemplos"
WORLDS_DIR = ROOT_DIR / "Documentos" / "Mundos"


@pytest.fixture(autouse=True)
def clean_pybricks():
    PybricksContext.clear()
    PybricksFactory.cleanup()
    yield
    PybricksFactory.cleanup()
    PybricksContext.clear()


def _wait_until(predicate, timeout_s: float = 4.0) -> bool:
    deadline = time.perf_counter() + timeout_s
    while time.perf_counter() < deadline:
        if predicate():
            return True
        time.sleep(0.02)
    return False


def _world_for_example(example_name: str) -> Path:
    name = example_name.lower()
    if "linea" in name or "siguelineas" in name or "color" in name:
        return WORLDS_DIR / "01_linea_negra.json"
    return WORLDS_DIR / "02_obstaculos_beacon.json"


def test_full_program_health_devices_and_telemetry():
    world_path = WORLDS_DIR / "02_obstaculos_beacon.json"
    assert world_path.exists(), f"Mundo no encontrado: {world_path}"

    statuses: list[str] = []
    runtime_errors: list[dict] = []
    snapshots = []

    service = SimulationService()
    service.set_status_callback(lambda status: statuses.append(status))
    service.set_error_callback(lambda payload: runtime_errors.append(payload))
    service.set_snapshot_callback(lambda dto: snapshots.append(dto))

    service.load_world_file(world_path)
    service.load_script(
        """
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, InfraredSensor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Color
from pybricks.robotics import DriveBase
from pybricks.tools import wait

ev3 = EV3Brick()
left = Motor(Port.B)
right = Motor(Port.C)
arm = Motor(Port.A)
bot = DriveBase(left, right, 55.5, 104)

touch = TouchSensor(Port.S1)
infra = InfraredSensor(Port.S2)
color = ColorSensor(Port.S3)
ultra = UltrasonicSensor(Port.S4)

ev3.light.on(Color.GREEN)
ev3.screen.print("QA start")
ev3.speaker.beep(440, 400)
arm.run_time(180, 250, wait=False)

for _ in range(10):
    bot.drive(90, 20)
    _ = touch.pressed()
    _ = infra.distance()
    _ = infra.reflection()
    _ = infra.count()
    _ = infra.beacon(1)
    _ = color.reflection()
    _ = color.color()
    _ = ultra.distance()
    _ = ultra.presence()
    wait(30)

bot.stop()
arm.stop()
ev3.screen.print("QA ok")
ev3.light.off()
"""
    )

    service.start()
    finished = _wait_until(
        lambda: service.controller_state == ControllerState.STOPPED,
        timeout_s=5.0,
    )
    if not finished:
        service.stop(reason="test_timeout")
    else:
        service.stop(reason="test_cleanup")

    assert "world_loaded" in statuses
    assert "started" in statuses
    assert runtime_errors == []
    assert snapshots, "No se recibieron snapshots de telemetria"

    saw_motor_activity = any(
        abs(motor["speed"]) > 1.0 for snap in snapshots for motor in snap.motors if motor["port"] in {"A", "B", "C"}
    )
    assert saw_motor_activity

    sensor_ports = {
        sensor["port"] for snap in snapshots for sensor in snap.sensors if sensor.get("type") and sensor["type"] != "-"
    }
    assert {"S1", "S2", "S3", "S4"}.issubset(sensor_ports)

    assert any(snap.brick["led"] == "GREEN" for snap in snapshots)
    assert any(snap.brick["screen"]["lines"] for snap in snapshots)
    assert any(snap.brick["speaker"] is not None for snap in snapshots)


@pytest.mark.parametrize(
    ("example_file", "run_s"),
    [
        ("03_movimiento_basico.py", 2.4),
        ("08_sensor_ultrasonido_frenado.py", 1.2),
        ("11_siguelineas_basico.py", 1.0),
        ("01_intro_led.py", 1.0),
        ("02_intro_pantalla_altavoz.py", 2.2),
    ],
)
def test_release_examples_smoke_extended(example_file: str, run_s: float):
    example_path = EXAMPLES_DIR / example_file
    world_path = _world_for_example(example_file)

    assert example_path.exists(), f"Ejemplo no encontrado: {example_path}"
    assert world_path.exists(), f"Mundo no encontrado: {world_path}"

    statuses: list[str] = []
    runtime_errors: list[dict] = []

    service = SimulationService()
    service.set_status_callback(lambda status: statuses.append(status))
    service.set_error_callback(lambda payload: runtime_errors.append(payload))

    service.load_world_file(world_path)
    service.load_script(example_path.read_text(encoding="utf-8"))
    service.start()
    time.sleep(run_s)
    service.stop(reason="smoke_extended")

    assert "world_loaded" in statuses
    assert "started" in statuses
    assert "stopped" in statuses
    assert runtime_errors == []
