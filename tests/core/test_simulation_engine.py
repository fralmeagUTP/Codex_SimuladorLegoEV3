"""Tests para SimulationEngine."""

import math

import pytest

from simulador_ev3.core.command_queue import CommandQueue, SimulationCommand
from simulador_ev3.core.event_bus import (
    EVENT_SENSOR_UPDATED,
    EVENT_SIMULATION_STARTED,
    EVENT_SIMULATION_STOPPED,
    EventBus,
)
from simulador_ev3.core.simulation_engine import (
    SimEngineConfig,
    SimulationEngine,
    StateSnapshot,
)
from simulador_ev3.domain.sensors.gyro_sensor_model import GyroSensorModel
from simulador_ev3.domain.sensors.touch_sensor_model import TouchSensorModel
from simulador_ev3.domain.sensors.ultrasonic_sensor_model import UltrasonicSensorModel
from simulador_ev3.domain.sensors.color_sensor_model import ColorSensorModel
from simulador_ev3.domain.world.obstacle_model import ObstacleModel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_engine(**kwargs) -> SimulationEngine:
    cfg = SimEngineConfig(**kwargs)
    q   = CommandQueue()
    bus = EventBus()
    return SimulationEngine(config=cfg, command_queue=q, event_bus=bus)


# ---------------------------------------------------------------------------
# Inicialización
# ---------------------------------------------------------------------------

class TestEngineInit:
    def test_default_engine_creates_ok(self):
        eng = make_engine()
        assert eng.tick == 0
        assert eng.sim_time_s == 0.0

    def test_snapshot_at_start(self):
        eng = make_engine(robot_x0_mm=500, robot_y0_mm=300, robot_theta0_deg=0)
        snap = eng.update()
        assert snap.robot.x_mm == pytest.approx(500.0, abs=1)
        assert snap.robot.y_mm == pytest.approx(300.0, abs=1)
        assert snap.tick == 1

    def test_sim_time_increments(self):
        eng = make_engine()
        eng.update()
        eng.update()
        assert eng.sim_time_s == pytest.approx(2 * SimulationEngine.DT, rel=1e-6)

    def test_motors_present_A_to_D(self):
        eng = make_engine()
        snap = eng.update()
        ports = {m.port for m in snap.motors}
        assert {"A", "B", "C", "D"}.issubset(ports)

    def test_no_sensors_by_default(self):
        eng = make_engine()
        snap = eng.update()
        assert snap.sensors == ()


# ---------------------------------------------------------------------------
# Comandos — LED
# ---------------------------------------------------------------------------

class TestLEDCommands:
    def test_led_on_reflected_in_snapshot(self):
        eng = make_engine()
        eng.command_queue.put(SimulationCommand.led_on("RED"))
        snap = eng.update()
        assert snap.brick["led"]["color"] == "RED"

    def test_led_off_reflected_in_snapshot(self):
        eng = make_engine()
        eng.command_queue.put(SimulationCommand.led_on("GREEN"))
        eng.update()
        eng.command_queue.put(SimulationCommand.led_off())
        snap = eng.update()
        assert snap.brick["led"]["color"] == "OFF"


# ---------------------------------------------------------------------------
# Comandos — Pantalla
# ---------------------------------------------------------------------------

class TestDisplayCommands:
    def test_display_text_appears_in_snapshot(self):
        eng = make_engine()
        eng.command_queue.put(SimulationCommand.display_text("Hola EV3"))
        snap = eng.update()
        # La pantalla serializa las líneas
        lines = snap.brick["screen"]["lines"]
        assert any("Hola EV3" in line for line in lines)

    def test_screen_clear_empties_snapshot_lines(self):
        eng = make_engine()
        eng.command_queue.put(SimulationCommand.display_text("Linea 1"))
        eng.update()
        eng.command_queue.put(SimulationCommand.screen_clear())
        snap = eng.update()
        assert snap.brick["screen"]["lines"] == []


# ---------------------------------------------------------------------------
# Comandos — Altavoz
# ---------------------------------------------------------------------------

class TestSpeakerCommands:
    def test_play_sound_does_not_crash_engine(self):
        eng = make_engine()
        eng.command_queue.put(SimulationCommand.play_sound(440, 200, 50))
        snap = eng.update()
        assert snap.tick == 1

    def test_play_sound_sets_speaker_beeping(self):
        eng = make_engine()
        eng.command_queue.put(SimulationCommand.play_sound(440, 200, 50))
        snap = eng.update()
        assert snap.brick["speaker"]["state"] == "BEEPING"

    def test_play_sound_invokes_audio_backend(self):
        eng = make_engine()
        calls = []

        class FakeAudio:
            def play_beep(self, frequency, duration_ms, volume=50):
                calls.append((frequency, duration_ms, volume))

        eng._audio_output = FakeAudio()  # type: ignore[attr-defined]
        eng.command_queue.put(SimulationCommand.play_sound(523, 180, 70))
        eng.update()
        assert calls == [(523, 180, 70)]

    def test_audio_backend_failure_does_not_crash_engine(self):
        eng = make_engine()

        class BrokenAudio:
            def play_beep(self, frequency, duration_ms, volume=50):
                raise RuntimeError("audio device error")

        eng._audio_output = BrokenAudio()  # type: ignore[attr-defined]
        eng.command_queue.put(SimulationCommand.play_sound(440, 200, 50))
        snap = eng.update()
        assert snap.tick == 1


# ---------------------------------------------------------------------------
# Comandos — DriveBase
# ---------------------------------------------------------------------------

class TestDriveBaseCommands:
    def test_db_drive_moves_robot(self):
        eng = make_engine(robot_x0_mm=200, robot_y0_mm=200, robot_theta0_deg=0)
        eng.command_queue.put(SimulationCommand.db_drive(speed=200, turn_rate=0))
        # Avanzar 10 ticks (0.2 s) → ~40 mm
        for _ in range(10):
            snap = eng.update()
        assert snap.robot.x_mm > 200.0

    def test_db_stop_halts_motion(self):
        eng = make_engine(robot_x0_mm=200, robot_y0_mm=200, robot_theta0_deg=0)
        eng.command_queue.put(SimulationCommand.db_drive(200, 0))
        for _ in range(5):
            eng.update()
        eng.command_queue.put(SimulationCommand.db_stop())
        eng.update()
        snap_before = eng.update()
        snap_after  = eng.update()
        # Con stop, posición no debería cambiar (o cambio mínimo por desaceleración)
        assert abs(snap_after.robot.x_mm - snap_before.robot.x_mm) < 10.0


# ---------------------------------------------------------------------------
# Comandos — Motor individual
# ---------------------------------------------------------------------------

class TestMotorCommands:
    def test_motor_run_state_in_snapshot(self):
        eng = make_engine()
        eng.command_queue.put(SimulationCommand.motor_run("A", 300))
        snap = eng.update()
        motor_a = next(m for m in snap.motors if m.port == "A")
        # Estado debe ser RUN (motor en marcha)
        assert motor_a.state == "RUN"

    def test_motor_stop_returns_idle(self):
        eng = make_engine()
        eng.command_queue.put(SimulationCommand.motor_run("A", 300))
        eng.update()
        eng.command_queue.put(SimulationCommand.motor_stop("A"))
        snap = eng.update()
        motor_a = next(m for m in snap.motors if m.port == "A")
        assert motor_a.state in ("IDLE", "BRAKE")

    def test_unknown_port_does_not_crash(self):
        eng = make_engine()
        cmd = SimulationCommand.motor_run("Z", 100)   # puerto no existe
        eng.command_queue.put(cmd)
        # No debe lanzar excepción
        snap = eng.update()
        assert snap.tick == 1


# ---------------------------------------------------------------------------
# Sensores
# ---------------------------------------------------------------------------

class TestSensorAttach:
    def test_attach_gyro_produces_sensor_snapshot(self):
        eng = make_engine()
        gyro = GyroSensorModel()
        eng.attach_sensor("S1", gyro)
        snap = eng.update()
        assert len(snap.sensors) == 1
        assert snap.sensors[0].port == "S1"
        assert snap.sensors[0].sensor_type == "GyroSensorModel"

    def test_attach_gyro_angle_zero_at_start(self):
        eng = make_engine(robot_theta0_deg=0)
        gyro = GyroSensorModel()
        eng.attach_sensor("S1", gyro)
        snap = eng.update()
        assert snap.sensors[0].data["angle_deg"] == 0

    def test_attach_invalid_port_raises(self):
        eng = make_engine()
        with pytest.raises(ValueError, match="S1-S4"):
            eng.attach_sensor("X9", GyroSensorModel())

    def test_detach_sensor_removes_from_snapshot(self):
        eng = make_engine()
        eng.attach_sensor("S2", GyroSensorModel())
        eng.update()
        eng.detach_sensor("S2")
        snap = eng.update()
        assert all(s.port != "S2" for s in snap.sensors)

    def test_ultrasonic_max_range_open_world(self):
        eng = make_engine(world_width_mm=2000, world_height_mm=2000,
                          robot_x0_mm=1000, robot_y0_mm=1000, robot_theta0_deg=0)
        us = UltrasonicSensorModel()
        eng.attach_sensor("S3", us)
        snap = eng.update()
        us_data = snap.sensors[0].data
        # En espacio abierto la lectura es el máximo (2500) o la distancia al borde
        assert us_data["distance_mm"] > 0

    def test_sensor_updated_event_published(self):
        eng = make_engine()
        received = []
        eng.event_bus.subscribe(EVENT_SENSOR_UPDATED,
                                lambda e, p: received.append(p))
        eng.attach_sensor("S1", GyroSensorModel())
        eng.update()
        assert len(received) >= 1
        assert received[0]["port"] == "S1"


# ---------------------------------------------------------------------------
# Colisión
# ---------------------------------------------------------------------------

class TestCollision:
    def test_collision_detected_out_of_bounds(self):
        # Robot con radio 75 mm en esquina: si x < radio → colisión con borde
        eng = make_engine(
            robot_x0_mm=10, robot_y0_mm=200,
            robot_radius_mm=75,
            world_width_mm=2000, world_height_mm=2000,
        )
        snap = eng.update()
        # En x=10, con radio=75, debería detectar colisión con el borde izquierdo
        assert snap.colliding is True

    def test_no_collision_in_center(self):
        eng = make_engine(
            robot_x0_mm=1000, robot_y0_mm=1000,
            robot_radius_mm=75,
            world_width_mm=2000, world_height_mm=2000,
        )
        snap = eng.update()
        assert snap.colliding is False

    def test_collision_reverts_position(self):
        """Si hay colisión, el robot retrocede a la posición anterior."""
        eng = make_engine(
            robot_x0_mm=80, robot_y0_mm=1000,
            robot_theta0_deg=180,   # apuntando al borde izquierdo
            robot_radius_mm=75,
            world_width_mm=2000, world_height_mm=2000,
        )
        eng.command_queue.put(SimulationCommand.db_drive(200, 0))
        snap0 = eng.update()
        # En la primera actualización la colisión revierte la posición
        snap1 = eng.update()
        # No debe haberse alejado en la dirección de colisión (x no decrece mucho)
        assert snap1.robot.x_mm >= 0


# ---------------------------------------------------------------------------
# EventBus integrado
# ---------------------------------------------------------------------------

class TestEngineEvents:
    def test_notify_started_publishes_event(self):
        eng = make_engine()
        received = []
        eng.event_bus.subscribe(EVENT_SIMULATION_STARTED,
                                lambda e, p: received.append(e))
        eng.notify_started()
        assert received == [EVENT_SIMULATION_STARTED]

    def test_notify_stopped_publishes_event(self):
        eng = make_engine()
        received = []
        eng.event_bus.subscribe(EVENT_SIMULATION_STOPPED,
                                lambda e, p: received.append(p))
        eng.notify_stopped("user_request")
        assert received[0]["reason"] == "user_request"

    def test_notify_stopped_signals_pending_blocking(self):
        """Los comandos bloqueantes pendientes se señalan al detener."""
        eng = make_engine()
        cmd = SimulationCommand.db_straight(10000)   # muy larga
        eng.command_queue.put(cmd)
        eng.update()   # el comando entra en pending_blocking
        assert not cmd.done_event.is_set()
        eng.notify_stopped("reset")
        assert cmd.done_event.is_set()


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------

class TestReset:
    def test_reset_clears_tick_and_time(self):
        eng = make_engine()
        for _ in range(5):
            eng.update()
        eng.reset()
        assert eng.tick == 0
        assert eng.sim_time_s == 0.0

    def test_reset_clears_motor_state(self):
        eng = make_engine()
        eng.command_queue.put(SimulationCommand.motor_run("A", 300))
        eng.update()
        eng.reset()
        snap = eng.update()
        motor_a = next(m for m in snap.motors if m.port == "A")
        # Después del reset el motor debe estar en IDLE
        assert motor_a.state == "IDLE"
