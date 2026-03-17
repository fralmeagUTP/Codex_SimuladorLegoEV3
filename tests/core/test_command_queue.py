"""Tests para CommandQueue y SimulationCommand."""

import threading
import time

import pytest

from simulador_ev3.core.command_queue import (
    CommandQueue,
    CommandType,
    SimulationCommand,
)


# ---------------------------------------------------------------------------
# SimulationCommand
# ---------------------------------------------------------------------------

class TestSimulationCommandCreation:
    def test_motor_run_no_blocking(self):
        cmd = SimulationCommand.motor_run("A", 500)
        assert cmd.cmd_type == CommandType.MOTOR_RUN
        assert cmd.port == "A"
        assert cmd.params["speed"] == 500
        assert cmd.blocking is False
        assert cmd.done_event is None

    def test_motor_run_time_is_blocking(self):
        cmd = SimulationCommand.motor_run_time("B", 300, 1000)
        assert cmd.cmd_type == CommandType.MOTOR_RUN_TIME
        assert cmd.blocking is True
        assert cmd.done_event is not None
        assert not cmd.done_event.is_set()

    def test_motor_run_angle_is_blocking(self):
        cmd = SimulationCommand.motor_run_angle("C", 200, 360)
        assert cmd.cmd_type == CommandType.MOTOR_RUN_ANGLE
        assert cmd.blocking is True
        assert cmd.params["angle_deg"] == 360

    def test_motor_stop_no_blocking(self):
        cmd = SimulationCommand.motor_stop("D")
        assert cmd.cmd_type == CommandType.MOTOR_STOP
        assert not cmd.blocking

    def test_motor_brake(self):
        cmd = SimulationCommand.motor_brake("A")
        assert cmd.cmd_type == CommandType.MOTOR_BRAKE

    def test_motor_hold(self):
        cmd = SimulationCommand.motor_hold("B")
        assert cmd.cmd_type == CommandType.MOTOR_HOLD

    def test_db_drive_no_blocking(self):
        cmd = SimulationCommand.db_drive(200, 0)
        assert cmd.cmd_type == CommandType.DB_DRIVE
        assert not cmd.blocking
        assert cmd.params["speed"] == 200
        assert cmd.params["turn_rate"] == 0

    def test_db_stop_no_blocking(self):
        cmd = SimulationCommand.db_stop()
        assert cmd.cmd_type == CommandType.DB_STOP
        assert not cmd.blocking

    def test_db_straight_is_blocking(self):
        cmd = SimulationCommand.db_straight(500)
        assert cmd.cmd_type == CommandType.DB_STRAIGHT
        assert cmd.blocking is True
        assert cmd.params["distance_mm"] == 500

    def test_db_turn_is_blocking(self):
        cmd = SimulationCommand.db_turn(90)
        assert cmd.cmd_type == CommandType.DB_TURN
        assert cmd.blocking is True
        assert cmd.params["angle_deg"] == 90

    def test_db_settings_no_blocking(self):
        cmd = SimulationCommand.db_settings(200, 200, 90, 90)
        assert cmd.cmd_type == CommandType.DB_SETTINGS
        assert not cmd.blocking
        assert cmd.params["straight_speed"] == 200

    def test_led_on_no_blocking(self):
        cmd = SimulationCommand.led_on("RED")
        assert cmd.cmd_type == CommandType.LED_ON
        assert cmd.params["color"] == "RED"

    def test_led_off_no_blocking(self):
        cmd = SimulationCommand.led_off()
        assert cmd.cmd_type == CommandType.LED_OFF

    def test_play_sound_no_blocking(self):
        cmd = SimulationCommand.play_sound(440, 200, 80)
        assert cmd.cmd_type == CommandType.PLAY_SOUND
        assert cmd.params["frequency"] == 440

    def test_display_text_no_blocking(self):
        cmd = SimulationCommand.display_text("Hola")
        assert cmd.cmd_type == CommandType.DISPLAY_TEXT
        assert cmd.params["text"] == "Hola"
        assert cmd.params["newline"] is True


class TestSimulationCommandBlocking:
    def test_signal_done_sets_event(self):
        cmd = SimulationCommand.db_straight(100)
        assert not cmd.done_event.is_set()
        cmd.signal_done()
        assert cmd.done_event.is_set()

    def test_wait_returns_true_when_done(self):
        cmd = SimulationCommand.db_straight(100)
        cmd.signal_done()
        assert cmd.wait(timeout=0.1) is True

    def test_wait_timeout(self):
        cmd = SimulationCommand.db_straight(100)
        # No señalamos → timeout
        result = cmd.wait(timeout=0.05)
        assert result is False

    def test_wait_non_blocking_returns_true(self):
        cmd = SimulationCommand.motor_run("A", 100)
        assert cmd.wait() is True  # trivialmente completado

    def test_signal_done_from_another_thread(self):
        cmd = SimulationCommand.db_turn(90)
        results = []

        def signal():
            time.sleep(0.05)
            cmd.signal_done()

        t = threading.Thread(target=signal)
        t.start()
        result = cmd.wait(timeout=1.0)
        t.join()
        assert result is True


# ---------------------------------------------------------------------------
# CommandQueue
# ---------------------------------------------------------------------------

class TestCommandQueue:
    def test_put_and_drain(self):
        q = CommandQueue()
        q.put(SimulationCommand.motor_run("A", 100))
        q.put(SimulationCommand.motor_stop("A"))
        items = q.drain()
        assert len(items) == 2
        assert items[0].cmd_type == CommandType.MOTOR_RUN
        assert items[1].cmd_type == CommandType.MOTOR_STOP

    def test_drain_empty_returns_empty_list(self):
        q = CommandQueue()
        assert q.drain() == []

    def test_drain_clears_queue(self):
        q = CommandQueue()
        q.put(SimulationCommand.led_on("GREEN"))
        q.drain()
        assert q.drain() == []

    def test_size(self):
        q = CommandQueue()
        assert q.size == 0
        q.put(SimulationCommand.db_stop())
        assert q.size == 1

    def test_clear(self):
        q = CommandQueue()
        q.put(SimulationCommand.db_stop())
        q.put(SimulationCommand.led_off())
        q.clear()
        assert q.size == 0

    def test_put_and_wait_blocking(self):
        q = CommandQueue()
        cmd = SimulationCommand.db_straight(100)

        def consumer():
            time.sleep(0.05)
            drained = q.drain()
            for c in drained:
                c.signal_done()

        t = threading.Thread(target=consumer)
        t.start()
        result = q.put_and_wait(cmd, timeout=1.0)
        t.join()
        assert result is True

    def test_put_and_wait_raises_on_non_blocking(self):
        q = CommandQueue()
        cmd = SimulationCommand.motor_run("A", 100)
        with pytest.raises(ValueError, match="no es bloqueante"):
            q.put_and_wait(cmd)

    def test_thread_safe_concurrent_puts(self):
        """Múltiples productores simultáneos no corrompen la cola."""
        q = CommandQueue()
        n = 200

        def producer():
            for _ in range(n // 10):
                q.put(SimulationCommand.motor_run("A", 100))

        threads = [threading.Thread(target=producer) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        all_items = q.drain()
        assert len(all_items) == n
