"""Tests para la Fase 6: Capa de Aplicación (SnapshotDTO + SimulationService)."""

import json
import sys
import time
import threading
from pathlib import Path

import pytest

from simulador_ev3.core.simulation_engine import SimEngineConfig, SimulationEngine
from simulador_ev3.core.command_queue import SimulationCommand
from simulador_ev3.application.snapshot_dto import SnapshotDTO
from simulador_ev3.application.simulation_service import SimulationService
from simulador_ev3.persistence.world_repository import WorldRepository
from simulador_ev3.domain.world.world_model import WorldModel
from simulador_ev3.domain.world.obstacle_model import ObstacleModel
from simulador_ev3.pybricks_api.factory import PybricksFactory
from simulador_ev3.pybricks_api._context import PybricksContext
from simulador_ev3.runtime.execution_policy import ExecutionPolicy


# ===========================================================================
# Fixture global: limpiar contexto Pybricks entre tests
# ===========================================================================

@pytest.fixture(autouse=True)
def clean_pybricks():
    PybricksContext.clear()
    PybricksFactory.cleanup()
    yield
    PybricksFactory.cleanup()
    PybricksContext.clear()


# ===========================================================================
# Helpers
# ===========================================================================

def make_engine():
    cfg = SimEngineConfig(
        robot_x0_mm=500.0, robot_y0_mm=500.0,
        world_width_mm=2000, world_height_mm=2000,
    )
    return SimulationEngine(config=cfg)


def make_snapshot(engine=None):
    """Obtiene un StateSnapshot real ejecutando un tick del engine."""
    eng = engine or make_engine()
    return eng.update()


# ===========================================================================
# SnapshotDTO
# ===========================================================================

class TestSnapshotDTO:
    def test_from_snapshot_returns_dto(self):
        snap = make_snapshot()
        dto = SnapshotDTO.from_snapshot(snap)
        assert isinstance(dto, SnapshotDTO)

    def test_tick_equals_snapshot_tick(self):
        eng = make_engine()
        eng.update()
        snap = eng.update()
        dto = SnapshotDTO.from_snapshot(snap)
        assert dto.tick == snap.tick

    def test_robot_dict_has_expected_keys(self):
        dto = SnapshotDTO.from_snapshot(make_snapshot())
        assert "x_mm" in dto.robot
        assert "y_mm" in dto.robot
        assert "theta_deg" in dto.robot

    def test_robot_position_in_range(self):
        dto = SnapshotDTO.from_snapshot(make_snapshot())
        assert 0 <= dto.robot["x_mm"] <= 2000
        assert 0 <= dto.robot["y_mm"] <= 2000

    def test_motors_list_has_four_entries(self):
        dto = SnapshotDTO.from_snapshot(make_snapshot())
        assert len(dto.motors) == 4

    def test_motor_dict_has_expected_keys(self):
        dto = SnapshotDTO.from_snapshot(make_snapshot())
        for m in dto.motors:
            assert "port" in m
            assert "speed" in m
            assert "angle" in m
            assert "state" in m

    def test_sensors_list_present(self):
        dto = SnapshotDTO.from_snapshot(make_snapshot())
        assert isinstance(dto.sensors, list)

    def test_brick_dict_has_expected_keys(self):
        dto = SnapshotDTO.from_snapshot(make_snapshot())
        assert "led" in dto.brick
        assert "screen" in dto.brick
        assert "speaker" in dto.brick
        assert "buttons" in dto.brick

    def test_screen_draw_ops_are_preserved(self):
        eng = make_engine()
        eng.command_queue.put(SimulationCommand.screen_pixel(10, 20, color=1))
        snap = eng.update()
        dto = SnapshotDTO.from_snapshot(snap)
        ops = dto.brick["screen"].get("draw_ops", [])
        assert len(ops) == 1
        assert ops[0].get("op") == "pixel"

    def test_to_dict_is_json_serializable(self):
        import json
        dto = SnapshotDTO.from_snapshot(make_snapshot())
        data = dto.to_dict()
        s = json.dumps(data)   # no debe lanzar excepción
        assert "tick" in s

    def test_colliding_is_bool(self):
        dto = SnapshotDTO.from_snapshot(make_snapshot())
        assert isinstance(dto.colliding, bool)

    def test_sim_time_s_positive_after_tick(self):
        eng = make_engine()
        eng.update()
        snap = eng.update()
        dto = SnapshotDTO.from_snapshot(snap)
        assert dto.sim_time_s > 0

    def test_repr_contains_tick(self):
        dto = SnapshotDTO.from_snapshot(make_snapshot())
        assert "tick" in repr(dto).lower() or "SnapshotDTO" in repr(dto)


# ===========================================================================
# SimulationService — ciclo de vida básico
# ===========================================================================

class TestSimulationServiceLifecycle:
    def test_service_starts_idle(self):
        svc = SimulationService()
        from simulador_ev3.runtime.runtime_controller import ControllerState
        assert svc.controller_state == ControllerState.IDLE
        svc.stop()

    def test_start_changes_state_to_running(self):
        svc = SimulationService()
        svc.start()
        assert svc.is_running
        svc.stop()

    def test_stop_changes_state_to_stopped(self):
        svc = SimulationService()
        svc.start()
        svc.stop()
        assert not svc.is_running
        from simulador_ev3.runtime.runtime_controller import ControllerState
        assert svc.controller_state == ControllerState.STOPPED

    def test_pause_and_resume(self):
        svc = SimulationService()
        svc.start()
        svc.pause()
        assert svc.is_paused
        svc.resume()
        assert svc.is_running
        svc.stop()

    def test_double_start_is_idempotent(self):
        svc = SimulationService()
        svc.start()
        svc.start()   # segunda llamada no debe lanzar excepción
        assert svc.is_running
        svc.stop()

    def test_stop_without_start_is_safe(self):
        svc = SimulationService()
        svc.stop()    # no debe lanzar

    def test_reset_clears_script(self):
        svc = SimulationService()
        svc.load_script("x = 1")
        svc.reset()
        assert svc._source_code is None

    def test_engine_accessible(self):
        svc = SimulationService()
        assert svc.engine is not None


# ===========================================================================
# SimulationService — script y callbacks
# ===========================================================================

class TestSimulationServiceScript:
    def test_load_and_run_script(self):
        svc = SimulationService()
        svc.load_script("x = 1 + 1")
        svc.start()
        time.sleep(0.3)
        svc.stop()
        assert not svc.is_running

    def test_snapshot_callback_receives_dto(self):
        received = []
        svc = SimulationService()
        svc.set_snapshot_callback(lambda dto: received.append(dto))
        svc.start()
        time.sleep(0.1)
        svc.stop()
        assert len(received) > 0
        assert isinstance(received[0], SnapshotDTO)

    def test_error_callback_on_bad_script(self):
        errors = []
        svc = SimulationService()
        svc.set_error_callback(lambda e: errors.append(e))
        svc.load_script("raise RuntimeError('intencional')")
        svc.start()
        time.sleep(0.5)
        svc.stop()
        assert len(errors) >= 1
        assert "intencional" in errors[0].get("error", "")

    def test_status_callback_started(self):
        statuses = []
        svc = SimulationService()
        svc.set_status_callback(lambda s: statuses.append(s))
        svc.start()
        time.sleep(0.05)
        svc.stop()
        assert "started" in statuses
        assert "stopped" in statuses

    def test_status_callback_stopped_when_script_finishes(self):
        statuses = []
        svc = SimulationService(policy=ExecutionPolicy(max_runtime_s=2.0))
        svc.set_status_callback(lambda s: statuses.append(s))
        svc.load_script("from pybricks.tools import wait\nwait(100)\n")
        svc.start()
        for _ in range(30):
            if "stopped" in statuses:
                break
            time.sleep(0.1)
        assert "stopped" in statuses
        assert not svc.is_running

    def test_tick_returns_dto_in_manual_mode(self):
        svc = SimulationService()
        svc.start()
        dto = svc.tick()
        assert isinstance(dto, SnapshotDTO)
        svc.stop()

    def test_get_snapshot_returns_dto(self):
        svc = SimulationService()
        dto = svc.get_snapshot()
        assert isinstance(dto, SnapshotDTO)

    def test_pybricks_script_motor_command(self):
        svc = SimulationService()
        svc.load_script("""\
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
m = Motor(Port.A)
m.run(500)
""")
        svc.start()
        time.sleep(0.3)
        svc.stop()
        assert not svc.is_running

    def test_pybricks_script_drivebase(self):
        svc = SimulationService()
        svc.load_script("""\
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait
l = Motor(Port.B)
r = Motor(Port.C)
bot = DriveBase(l, r, 55.5, 104)
bot.drive(100, 0)
wait(100)
bot.stop()
""")
        svc.start()
        time.sleep(1.5)
        svc.stop()

    def test_start_again_after_stop(self):
        """Reiniciar desde cero después de stop debe funcionar."""
        svc = SimulationService()
        svc.load_script("x = 1")
        svc.start()
        time.sleep(0.2)
        svc.stop()
        # Cargar nuevo script y arrancar de nuevo
        svc.load_script("y = 2")
        svc.start()
        assert svc.is_running
        svc.stop()

    def test_repr_contains_state(self):
        svc = SimulationService()
        assert "SimulationService" in repr(svc)


class TestSimulationServiceWorlds:
    def test_load_world_file_updates_engine_world(self, tmp_path: Path):
        world = WorldModel(width_mm=1500.0, height_mm=1100.0)
        world.add_obstacle(ObstacleModel.from_rect(100, 100, 120, 60, name="box"))
        world_path = tmp_path / "world_test.json"
        WorldRepository.save(world, world_path)

        svc = SimulationService()
        svc.load_world_file(world_path)

        assert svc.engine.world.width_mm == pytest.approx(1500.0)
        assert svc.engine.world.height_mm == pytest.approx(1100.0)
        assert len(svc.engine.world.obstacles) == 1

    def test_load_world_file_emits_world_loaded_status(self, tmp_path: Path):
        world = WorldModel(width_mm=1200.0, height_mm=1200.0)
        world_path = tmp_path / "world_status.json"
        WorldRepository.save(world, world_path)

        statuses = []
        svc = SimulationService()
        svc.set_status_callback(lambda s: statuses.append(s))
        svc.load_world_file(world_path)

        assert "world_loaded" in statuses

    def test_loaded_world_persists_after_restart_cycle(self, tmp_path: Path):
        world = WorldModel(width_mm=1700.0, height_mm=1300.0)
        world.add_obstacle(ObstacleModel.from_rect(200, 200, 100, 80, name="wall"))
        world_path = tmp_path / "world_persist.json"
        WorldRepository.save(world, world_path)

        svc = SimulationService()
        svc.load_world_file(world_path)
        svc.load_script("x = 1")

        svc.start()
        time.sleep(0.2)
        svc.stop()

        svc.start()
        time.sleep(0.2)
        svc.stop()

        assert svc.engine.world.width_mm == pytest.approx(1700.0)
        assert svc.engine.world.height_mm == pytest.approx(1300.0)
        assert len(svc.engine.world.obstacles) == 1

    def test_load_editor_world_sets_robot_start_pose(self, tmp_path: Path):
        world_path = tmp_path / "world_editor_robot.json"
        data = {
            "editor_spec": {
                "schema_version": 1,
                "grid_size_px": 32,
                "world_width_cells": 20,
                "world_height_cells": 20,
                "placements": [
                    {
                        "id": "robot_0001",
                        "asset_key": "robot_ev3_32x32",
                        "x": 64,
                        "y": 96,
                        "rotation": 90,
                    }
                ],
            }
        }
        world_path.write_text(json.dumps(data), encoding="utf-8")

        svc = SimulationService()
        svc.load_world_file(world_path)

        assert svc.engine.world.width_mm == pytest.approx(2000.0)
        assert svc.engine.world.height_mm == pytest.approx(2000.0)
        assert svc.engine._cfg.robot_x0_mm == pytest.approx(250.0)
        assert svc.engine._cfg.robot_y0_mm == pytest.approx(350.0)
        assert svc.engine._cfg.robot_theta0_deg == pytest.approx(90.0)
