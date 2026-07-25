"""Tests para la Fase 5: Capa de Compatibilidad Pybricks."""

import sys
import threading
import time

import pytest

from simulador_ev3.core.command_queue import CommandType
from simulador_ev3.core.simulation_engine import SimEngineConfig, SimulationEngine
from simulador_ev3.pybricks_api._context import PybricksContext
from simulador_ev3.pybricks_api.factory import PybricksFactory
from simulador_ev3.pybricks_api.parameters import (
    PYBRICKS_TO_SURFACE,
    STOP_TO_STOPMODE,
    SURFACE_TO_PYBRICKS,
    Color,
    Direction,
    Port,
    Stop,
)
from simulador_ev3.pybricks_api.tools import StopWatch, wait
from simulador_ev3.runtime.execution_policy import ExecutionPolicy
from simulador_ev3.runtime.runtime_controller import RuntimeController

# ===========================================================================
# Fixture — engine + contexto Pybricks activo
# ===========================================================================


def make_engine(x=500.0, y=500.0):
    cfg = SimEngineConfig(
        robot_x0_mm=x,
        robot_y0_mm=y,
        world_width_mm=2000,
        world_height_mm=2000,
    )
    eng = SimulationEngine(config=cfg)
    return eng


@pytest.fixture(autouse=True)
def clean_context():
    """Garantiza contexto limpio antes y después de cada test."""
    PybricksContext.clear()
    PybricksFactory.cleanup()
    yield
    PybricksFactory.cleanup()
    PybricksContext.clear()


def setup_ctx(engine):
    """Crea y activa un PybricksContext para el engine dado."""
    stop_ev = threading.Event()
    return PybricksFactory.create(engine, stop_ev)


# ===========================================================================
# parameters.py
# ===========================================================================


class TestParameters:
    def test_port_str_values(self):
        assert str(Port.A) == "A"
        assert str(Port.S1) == "S1"

    def test_stop_to_stopmode_mapping(self):
        assert STOP_TO_STOPMODE[Stop.BRAKE] == "BRAKE"
        assert STOP_TO_STOPMODE[Stop.COAST] == "COAST"
        assert STOP_TO_STOPMODE[Stop.HOLD] == "HOLD"

    def test_color_to_surface_mapping_black(self):
        assert PYBRICKS_TO_SURFACE[Color.BLACK] == "BLACK"

    def test_surface_to_pybricks_white(self):
        assert SURFACE_TO_PYBRICKS["WHITE"] == Color.WHITE

    def test_color_roundtrip(self):
        for color in (Color.BLACK, Color.WHITE, Color.RED, Color.GREEN):
            name = PYBRICKS_TO_SURFACE[color]
            assert SURFACE_TO_PYBRICKS[name] == color


# ===========================================================================
# PybricksContext
# ===========================================================================


class TestPybricksContext:
    def test_get_current_raises_without_init(self):
        with pytest.raises(RuntimeError, match="no inicializado"):
            PybricksContext.get_current()

    def test_set_and_get_current(self):
        eng = make_engine()
        stop = threading.Event()
        ctx = PybricksContext(eng.command_queue, eng, stop)
        PybricksContext.set_current(ctx)
        assert PybricksContext.get_current() is ctx

    def test_clear_removes_instance(self):
        eng = make_engine()
        stop = threading.Event()
        ctx = PybricksContext(eng.command_queue, eng, stop)
        PybricksContext.set_current(ctx)
        PybricksContext.clear()
        with pytest.raises(RuntimeError):
            PybricksContext.get_current()


# ===========================================================================
# Factory
# ===========================================================================


class TestPybricksFactory:
    def test_create_does_not_register_pybricks_in_sys_modules(self):
        eng = make_engine()
        PybricksFactory.cleanup()
        mods = setup_ctx(eng)
        assert "pybricks" in mods
        assert "pybricks.hubs" in mods
        assert "pybricks.ev3devices" in mods
        assert "pybricks.parameters" in mods
        assert "pybricks.robotics" in mods
        assert "pybricks.tools" in mods
        assert "pybricks" not in sys.modules
        assert "pybricks.hubs" not in sys.modules

    def test_cleanup_removes_legacy_pybricks_from_sys_modules(self):
        make_engine()
        sys.modules["pybricks"] = object()  # type: ignore[assignment]
        sys.modules["pybricks.hubs"] = object()  # type: ignore[assignment]
        PybricksFactory.cleanup()
        assert "pybricks" not in sys.modules
        assert "pybricks.hubs" not in sys.modules

    def test_create_sets_context(self):
        eng = make_engine()
        setup_ctx(eng)
        ctx = PybricksContext.get_current()
        assert ctx.engine is eng

    def test_create_returns_dict_with_pybricks(self):
        eng = make_engine()
        stop = threading.Event()
        mods = PybricksFactory.create(eng, stop)
        assert "pybricks" in mods


# ===========================================================================
# tools.py
# ===========================================================================


class TestWait:
    def test_wait_sleeps_approximately(self):
        eng = make_engine()
        setup_ctx(eng)
        t0 = time.perf_counter()
        wait(50)  # 50 ms
        elapsed = (time.perf_counter() - t0) * 1000
        assert 40 <= elapsed <= 200, f"wait(50) tardó {elapsed:.1f} ms"

    def test_wait_interrupted_by_stop_event(self):
        eng = make_engine()
        stop = threading.Event()
        PybricksFactory.create(eng, stop)
        stop.set()  # ya señalado → wait debe retornar casi inmediatamente
        t0 = time.perf_counter()
        with pytest.raises(SystemExit):
            wait(500)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert elapsed_ms < 100


class TestStopWatch:
    def test_time_increases(self):
        sw = StopWatch()
        time.sleep(0.05)
        assert sw.time() >= 40

    def test_pause_freezes_time(self):
        sw = StopWatch()
        time.sleep(0.05)
        sw.pause()
        t1 = sw.time()
        time.sleep(0.05)
        t2 = sw.time()
        assert t1 == t2

    def test_resume_continues_counting(self):
        sw = StopWatch()
        sw.pause()
        t_paused = sw.time()
        sw.resume()
        time.sleep(0.05)
        assert sw.time() > t_paused

    def test_reset_starts_from_zero(self):
        sw = StopWatch()
        time.sleep(0.05)
        sw.reset()
        assert sw.time() < 20  # justo tras reset


# ===========================================================================
# ev3devices.py — Motor
# ===========================================================================


class TestMotorAPI:
    def setup_method(self):
        self.eng = make_engine()
        setup_ctx(self.eng)
        from simulador_ev3.pybricks_api.ev3devices import Motor as PyMotor

        self.Motor = PyMotor

    def test_motor_run_enqueues_command(self):
        m = self.Motor(Port.A)
        m.run(500)
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.MOTOR_RUN and c.port == "A" for c in items)

    def test_motor_stop_enqueues_command(self):
        m = self.Motor(Port.B)
        m.stop()
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.MOTOR_STOP for c in items)

    def test_motor_brake_enqueues_command(self):
        m = self.Motor(Port.C)
        m.brake()
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.MOTOR_BRAKE for c in items)

    def test_motor_hold_enqueues_command(self):
        m = self.Motor(Port.D)
        m.hold()
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.MOTOR_HOLD for c in items)

    def test_counterclockwise_inverts_speed(self):
        m = self.Motor(Port.A, Direction.COUNTERCLOCKWISE)
        m.run(300)
        items = self.eng.command_queue.drain()
        cmd = next(c for c in items if c.cmd_type == CommandType.MOTOR_RUN)
        assert cmd.params["speed"] == -300

    def test_angle_reads_from_domain_model(self):
        m = self.Motor(Port.A)
        # Sin ticks el ángulo es 0
        assert m.angle() == pytest.approx(0.0)

    def test_speed_reads_from_domain_model(self):
        m = self.Motor(Port.A)
        assert m.speed() == pytest.approx(0.0)

    def test_motor_dc_enqueues_run_scaled_speed(self):
        m = self.Motor(Port.A)
        m.dc(50)
        items = self.eng.command_queue.drain()
        cmd = next(c for c in items if c.cmd_type == CommandType.MOTOR_RUN)
        assert cmd.params["speed"] == pytest.approx(525.0)

    def test_motor_run_target_maps_to_run_angle_delta(self):
        m = self.Motor(Port.A)
        self.eng._motors["A"]._angle = 30.0
        m.run_target(speed=200, target_angle=80, wait=False)
        items = self.eng.command_queue.drain()
        cmd = next(c for c in items if c.cmd_type == CommandType.MOTOR_RUN_ANGLE)
        assert cmd.params["angle_deg"] == pytest.approx(50.0)

    def test_motor_done_true_when_idle(self):
        m = self.Motor(Port.A)
        assert m.done() is True

    def test_motor_load_reads_power(self):
        m = self.Motor(Port.A)
        self.eng._motors["A"].cmd_run(300)
        assert m.load() > 0

    def test_motor_close_enqueues_stop(self):
        m = self.Motor(Port.A)
        m.close()
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.MOTOR_STOP for c in items)

    def test_motor_track_target_enqueues_run_angle(self):
        m = self.Motor(Port.A)
        m.track_target(120)
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.MOTOR_RUN_ANGLE for c in items)

    def test_motor_run_until_stalled_returns_float(self):
        m = self.Motor(Port.A)
        moved = m.run_until_stalled(200)
        assert isinstance(moved, float)


# ===========================================================================
# ev3devices.py — Sensores
# ===========================================================================


class TestSensorAPI:
    def setup_method(self):
        self.eng = make_engine()
        setup_ctx(self.eng)

    def test_touch_sensor_attaches_to_engine(self):
        from simulador_ev3.pybricks_api.ev3devices import TouchSensor

        TouchSensor(Port.S1)
        # Debe estar adjunto al engine
        assert self.eng._sensors["S1"] is not None

    def test_touch_sensor_pressed_false_open_world(self):
        from simulador_ev3.pybricks_api.ev3devices import TouchSensor

        ts = TouchSensor(Port.S1)
        self.eng.update()  # tick para actualizar sensor
        assert ts.pressed() is False

    def test_ultrasonic_sensor_distance_positive(self):
        from simulador_ev3.pybricks_api.ev3devices import UltrasonicSensor

        us = UltrasonicSensor(Port.S2)
        self.eng.update()
        assert us.distance() > 0

    def test_color_sensor_reflection_in_range(self):
        from simulador_ev3.pybricks_api.ev3devices import ColorSensor

        cs = ColorSensor(Port.S3)
        self.eng.update()
        assert 0 <= cs.reflection() <= 100

    def test_gyro_sensor_initial_angle_zero(self):
        from simulador_ev3.pybricks_api.ev3devices import GyroSensor

        gs = GyroSensor(Port.S4)
        self.eng.update()
        assert gs.angle() == 0

    def test_infrared_sensor_distance_in_range(self):
        from simulador_ev3.pybricks_api.ev3devices import InfraredSensor

        ir = InfraredSensor(Port.S1)
        self.eng.update()
        assert 0 <= ir.distance() <= 100

    def test_color_sensor_detectable_colors_filters_output(self):
        from simulador_ev3.pybricks_api.ev3devices import ColorSensor

        cs = ColorSensor(Port.S3)
        cs.detectable_colors([Color.BLACK])
        self.eng.update()
        assert cs.color() in (Color.BLACK, Color.NONE)
        assert isinstance(cs.hsv(), Color)

    def test_infrared_sensor_reflection_and_count_exist(self):
        from simulador_ev3.pybricks_api.ev3devices import InfraredSensor

        ir = InfraredSensor(Port.S1)
        self.eng.update()
        assert isinstance(ir.reflection(), int)
        assert ir.count() == 0


# ===========================================================================
# robotics.py — DriveBase
# ===========================================================================


class TestDriveBaseAPI:
    def setup_method(self):
        self.eng = make_engine()
        setup_ctx(self.eng)
        from simulador_ev3.pybricks_api.ev3devices import Motor as PyMotor
        from simulador_ev3.pybricks_api.robotics import DriveBase as PyDB

        left_motor = PyMotor(Port.B)
        right_motor = PyMotor(Port.C)
        self.db = PyDB(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

    def test_drive_enqueues_command(self):
        self.db.drive(200, 0)
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.DB_DRIVE for c in items)

    def test_stop_enqueues_command(self):
        self.db.stop()
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.DB_STOP for c in items)

    def test_settings_enqueues_command(self):
        self.db.settings(300, 300, 120, 120)
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.DB_SETTINGS for c in items)

    def test_brake_enqueues_stop_command(self):
        self.db.brake()
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.DB_STOP for c in items)
        assert any(c.params.get("stop_mode") == "BRAKE" for c in items)

    def test_curve_enqueues_drive_command(self):
        self.db.curve(radius=120, angle=30, wait=False)
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.DB_DRIVE for c in items)

    def test_state_returns_4_tuple(self):
        st = self.db.state()
        assert isinstance(st, tuple)
        assert len(st) == 4

    def test_done_true_when_idle(self):
        assert self.db.done() is True

    def test_wheel_diameter_updated_in_drivebase(self):
        # El DriveBase del engine debe tener el diámetro actualizado
        assert self.eng._drivebase.wheel_diameter_mm == pytest.approx(55.5)

    def test_axle_track_updated_in_drivebase(self):
        assert self.eng._drivebase.axle_track_mm == pytest.approx(104.0)


# ===========================================================================
# hubs.py — EV3Brick
# ===========================================================================


class TestEV3BrickAPI:
    def setup_method(self):
        self.eng = make_engine()
        setup_ctx(self.eng)
        from simulador_ev3.pybricks_api.hubs import EV3Brick as PyBrick

        self.ev3 = PyBrick()

    def test_light_on_enqueues_led_on(self):
        self.ev3.light.on(Color.RED)
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.LED_ON for c in items)

    def test_light_off_enqueues_led_off(self):
        self.ev3.light.off()
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.LED_OFF for c in items)

    def test_speaker_beep_enqueues_play_sound(self):
        self.ev3.speaker.beep(440, 100)
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.PLAY_SOUND for c in items)

    def test_screen_print_enqueues_display_text(self):
        self.ev3.screen.print("Test")
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.DISPLAY_TEXT for c in items)

    def test_screen_print_multiple_args(self):
        self.ev3.screen.print("Temp:", 42, "C")
        items = self.eng.command_queue.drain()
        cmd = next(c for c in items if c.cmd_type == CommandType.DISPLAY_TEXT)
        assert "42" in cmd.params["text"]

    def test_screen_clear_enqueues_clear_command(self):
        self.ev3.screen.clear()
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.SCREEN_CLEAR for c in items)

    def test_screen_draw_pixel_enqueues_command(self):
        self.ev3.screen.draw_pixel(10, 20)
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.SCREEN_PIXEL for c in items)

    def test_screen_pixel_alias_enqueues_command(self):
        self.ev3.screen.pixel(11, 22)
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.SCREEN_PIXEL for c in items)

    def test_screen_draw_line_enqueues_command(self):
        self.ev3.screen.draw_line(0, 0, 50, 60)
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.SCREEN_LINE for c in items)

    def test_screen_draw_circle_enqueues_command(self):
        self.ev3.screen.draw_circle(60, 40, 20, fill=True)
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.SCREEN_CIRCLE for c in items)

    def test_screen_draw_box_enqueues_command(self):
        self.ev3.screen.draw_box(5, 6, 30, 20, fill=False)
        items = self.eng.command_queue.drain()
        assert any(c.cmd_type == CommandType.SCREEN_BOX for c in items)

    def test_buttons_pressed_returns_list(self):
        result = self.ev3.buttons.pressed()
        assert isinstance(result, list)


# ===========================================================================
# End-to-end: script completo corriendo con import pybricks.*
# ===========================================================================


class TestEndToEnd:
    """Ejecuta scripts de usuario reales con el RuntimeController."""

    def _run_script(self, code: str, timeout: float = 2.0) -> RuntimeController:
        eng = make_engine()
        bus = eng.event_bus
        stop = threading.Event()
        mods = PybricksFactory.create(eng, stop)

        policy = ExecutionPolicy(max_runtime_s=0)  # sin watchdog para tests
        ctrl = RuntimeController(eng, bus, policy)
        ctrl.set_pybricks_modules(mods)
        ctrl.load_script(code)
        ctrl.start()

        # Esperamos a que el sandwich termine o timeout
        deadline = time.perf_counter() + timeout
        while time.perf_counter() < deadline:
            if ctrl.state.name in ("STOPPED",):
                break
            time.sleep(0.05)

        ctrl.stop()
        return ctrl

    def test_basic_motor_script(self):
        code = """\
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
m = Motor(Port.A)
m.run(500)
"""
        ctrl = self._run_script(code)
        assert ctrl.sandbox is not None
        assert ctrl.sandbox.state == "FINISHED"

    def test_ev3brick_led_script(self):
        code = """\
from pybricks.hubs import EV3Brick
from pybricks.parameters import Color
ev3 = EV3Brick()
ev3.light.on(Color.GREEN)
ev3.light.off()
"""
        ctrl = self._run_script(code)
        assert ctrl.sandbox is not None
        assert ctrl.sandbox.state == "FINISHED"

    def test_drive_base_script(self):
        code = """\
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
l = Motor(Port.B)
r = Motor(Port.C)
bot = DriveBase(l, r, 55.5, 104)
bot.drive(100, 0)
"""
        ctrl = self._run_script(code, timeout=3.0)
        assert ctrl.sandbox is not None
        assert ctrl.sandbox.state == "FINISHED"

    def test_wait_in_script(self):
        code = """\
from pybricks.tools import wait
wait(50)
"""
        ctrl = self._run_script(code, timeout=2.0)
        assert ctrl.sandbox is not None
        assert ctrl.sandbox.state == "FINISHED"

    def test_runtime_error_in_script(self):
        errors = []
        from simulador_ev3.core.event_bus import EVENT_RUNTIME_ERROR

        eng = make_engine()
        eng.event_bus.subscribe(EVENT_RUNTIME_ERROR, lambda e, p: errors.append(p))
        stop = threading.Event()
        mods = PybricksFactory.create(eng, stop)
        policy = ExecutionPolicy(max_runtime_s=0)
        ctrl = RuntimeController(eng, eng.event_bus, policy)
        ctrl.set_pybricks_modules(mods)
        ctrl.load_script("raise ValueError('fallo intencional')")
        ctrl.start()
        time.sleep(0.5)
        ctrl.stop()
        assert len(errors) >= 1
        assert "fallo intencional" in errors[0].get("error", "")
