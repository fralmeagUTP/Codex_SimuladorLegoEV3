"""Tests for WorldEditorService."""

from __future__ import annotations

import json

import pytest

from simulador_ev3.application.world_editor_service import WorldEditorService
from simulador_ev3.domain.editor.world_editor_model import Placement
from simulador_ev3.domain.world.surface_model import SurfaceColor


class TestWorldEditorService:
    def test_resize_formal_world_rejects_size_over_5120_px(self):
        svc = WorldEditorService()
        ok = svc.resize_formal_world(161, 20)
        assert ok is False

    def test_build_world_model_from_objects(self):
        svc = WorldEditorService()
        svc.new_world(2000.0, 2000.0)
        svc.add_wall(100, 100, 300, 40)
        svc.add_zone("RED", 500, 500, 200, 200)
        svc.add_line(points=[[200, 200], [800, 200]], width_mm=30.0)
        svc.add_suitcase(900, 900, 120, 80, mass=1.2, movable=True)

        world = svc.to_world_model()

        # wall + suitcase as physical obstacles
        assert len(world.obstacles) == 2
        # zone and line paint surface
        c_zone, _ = world.surface.query(550, 550)
        c_line, _ = world.surface.query(400, 300)
        assert c_zone == SurfaceColor.RED
        assert c_line == SurfaceColor.BLACK

    def test_save_load_roundtrip_editor_metadata(self, tmp_path):
        svc = WorldEditorService()
        svc.add_wall(100, 100, 200, 50, rotation_deg=10)
        svc.add_zone("GREEN", 400, 600, 180, 180)
        svc.add_line(points=[[100, 100], [300, 100]], width_mm=20)
        svc.add_suitcase(700, 700)

        out = tmp_path / "editor_world.json"
        svc.save_json(out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "editor_objects" in data
        assert "editor_spec" in data

        svc2 = WorldEditorService()
        _, note = svc2.load_json(out)
        assert note is None or isinstance(note, str)
        assert len(svc2.walls) == 1
        assert len(svc2.lines) >= 1
        assert len(svc2.zones) == 1
        assert len(svc2.current_formal_world().placements) >= 1

    def test_formal_api_rejects_misaligned_placement(self):
        svc = WorldEditorService()
        world = svc.create_world(grid_size=32, width_cells=20, height_cells=20)
        with pytest.raises(ValueError):
            svc.place_asset(
                world,
                Placement(id="p1", asset_key="wall_64x64_a", x_px=5, y_px=0, rotation=0),
            )

    def test_formal_api_save_load_roundtrip(self):
        svc = WorldEditorService()
        world = svc.create_world(grid_size=32, width_cells=20, height_cells=20)
        svc.place_asset(
            world,
            Placement(id="p1", asset_key="zone_red_128", x_px=0, y_px=0, rotation=0),
        )
        text = svc.save(world)
        loaded = svc.load(text)
        assert loaded.grid_size_px == 32
        assert loaded.world_width_cells == 20
        assert len(loaded.placements) == 1
        assert loaded.placements[0].asset_key == "zone_red_128"

    def test_place_second_robot_is_rejected(self):
        svc = WorldEditorService()
        svc.place_asset_current("robot_ev3_32x32", 0, 0, rotation=0)

        with pytest.raises(ValueError):
            svc.place_asset_current("robot_ev3_32x32", 128, 128, rotation=90)
