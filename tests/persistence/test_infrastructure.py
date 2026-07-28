"""Tests de Fase 8: persistencia JSON y catÃ¡logo de ejemplos."""

from __future__ import annotations

from pathlib import Path

import pytest

from simulador_ev3.domain.world.beacon_model import BeaconModel
from simulador_ev3.domain.world.obstacle_model import ObstacleModel
from simulador_ev3.domain.world.surface_model import SurfaceColor, SurfaceModel
from simulador_ev3.domain.world.world_model import WorldModel
from simulador_ev3.examples.example_catalog import ExampleCatalog
from simulador_ev3.persistence.world_repository import WorldRepository

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "Documentos" / "Ejemplos"


def make_world() -> WorldModel:
    surface = SurfaceModel(cell_size_mm=25.0, default_color=SurfaceColor.WHITE)
    surface.set_cell(1, 2, SurfaceColor.BLACK, 5.0)
    surface.set_cell(3, 4, SurfaceColor.RED, 30.0)
    obstacles = [
        ObstacleModel.from_rect(100, 100, 200, 50, name="wall1"),
        ObstacleModel(vertices=[(400, 400), (500, 420), (450, 520)], name="tri"),
    ]
    beacons = [
        BeaconModel(x_mm=800, y_mm=700, channel=1, name="b1"),
        BeaconModel(x_mm=1200, y_mm=1500, channel=2, name="b2"),
    ]
    return WorldModel(
        width_mm=3000.0,
        height_mm=1800.0,
        surface=surface,
        obstacles=obstacles,
        beacons=beacons,
    )


class TestWorldRepository:
    def test_to_dict_has_expected_top_level_keys(self):
        data = WorldRepository.to_dict(make_world())
        assert set(data.keys()) == {"version", "world"}
        assert data["version"] == 1

    def test_to_dict_contains_surface_obstacles_beacons(self):
        data = WorldRepository.to_dict(make_world())
        world = data["world"]
        assert "surface" in world
        assert "obstacles" in world
        assert "beacons" in world

    def test_from_dict_roundtrip_dimensions(self):
        world = make_world()
        loaded = WorldRepository.from_dict(WorldRepository.to_dict(world))
        assert loaded.width_mm == pytest.approx(world.width_mm)
        assert loaded.height_mm == pytest.approx(world.height_mm)

    def test_from_dict_roundtrip_obstacle_count(self):
        world = make_world()
        loaded = WorldRepository.from_dict(WorldRepository.to_dict(world))
        assert len(loaded.obstacles) == 2
        assert loaded.obstacles[0].name == "wall1"

    def test_from_dict_roundtrip_beacons(self):
        world = make_world()
        loaded = WorldRepository.from_dict(WorldRepository.to_dict(world))
        assert len(loaded.beacons) == 2
        assert loaded.beacons[1].channel == 2

    def test_from_dict_roundtrip_surface_cells(self):
        world = make_world()
        loaded = WorldRepository.from_dict(WorldRepository.to_dict(world))
        color, refl = loaded.surface.query(26, 51)  # cell (1,2)
        assert color == SurfaceColor.BLACK
        assert refl == pytest.approx(5.0)

    def test_save_and_load_file(self, tmp_path: Path):
        path = tmp_path / "world.json"
        WorldRepository.save(make_world(), path)
        assert path.exists()
        loaded = WorldRepository.load(path)
        assert loaded.width_mm == pytest.approx(3000.0)
        assert len(loaded.obstacles) == 2

    def test_invalid_version_raises(self):
        with pytest.raises(ValueError):
            WorldRepository.from_dict({"version": 999, "world": {}})


class TestExampleCatalog:
    def test_list_examples_returns_items(self):
        catalog = ExampleCatalog(EXAMPLES_DIR)
        items = catalog.list_examples()
        assert len(items) >= 1
        assert items[0].name.endswith(".py")

    def test_exists_true_for_known_example(self):
        catalog = ExampleCatalog(EXAMPLES_DIR)
        assert catalog.exists("03_movimiento_basico.py")

    def test_read_example_contains_pybricks_import(self):
        catalog = ExampleCatalog(EXAMPLES_DIR)
        code = catalog.read_example("03_movimiento_basico.py")
        assert "from pybricks" in code

    def test_read_example_by_absolute_path(self):
        catalog = ExampleCatalog(EXAMPLES_DIR)
        path = EXAMPLES_DIR / "14_navegacion_hasta_pared.py"
        code = catalog.read_example(str(path))
        assert "DriveBase" in code
