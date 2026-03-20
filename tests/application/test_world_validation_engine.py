"""Tests for ValidationEngine in the formal editor model."""

from __future__ import annotations

from simulador_ev3.application.world_validation_engine import ValidationEngine
from simulador_ev3.domain.editor.world_editor_model import EditorWorldModel, Placement


class TestWorldValidationEngine:
    def test_world_size_exceeds_max_is_invalid(self):
        engine = ValidationEngine()
        world = EditorWorldModel(
            grid_size_px=32,
            world_width_cells=161,
            world_height_cells=20,
            placements=[],
        )

        report = engine.validate(world)
        codes = {issue.code for issue in report.issues}
        assert "WORLD_SIZE_EXCEEDS_MAX" in codes

    def test_overlap_wall_robot_is_invalid(self):
        engine = ValidationEngine()
        world = EditorWorldModel(
            grid_size_px=32,
            world_width_cells=20,
            world_height_cells=20,
            placements=[
                Placement(id="w1", asset_key="wall_64x64_a", x_px=0, y_px=0, rotation=0),
                Placement(id="r1", asset_key="robot_ev3_32x32", x_px=0, y_px=0, rotation=0),
            ],
        )

        report = engine.validate(world)
        codes = {issue.code for issue in report.issues}
        assert "WALL_INCOMPATIBLE_OVERLAP" in codes

    def test_line_connectivity_detects_disconnected_components(self):
        engine = ValidationEngine()
        world = EditorWorldModel(
            grid_size_px=32,
            world_width_cells=30,
            world_height_cells=30,
            placements=[
                Placement(id="l1", asset_key="line_64_64_hor", x_px=0, y_px=0, rotation=0),
                Placement(id="l2", asset_key="line_64_64_hor", x_px=256, y_px=0, rotation=0),
            ],
        )

        report = engine.validate(world)
        codes = {issue.code for issue in report.issues}
        assert "LINE_DISCONNECTED_COMPONENTS" in codes

    def test_multiple_robots_is_invalid(self):
        engine = ValidationEngine()
        world = EditorWorldModel(
            grid_size_px=32,
            world_width_cells=20,
            world_height_cells=20,
            placements=[
                Placement(id="r1", asset_key="robot_ev3_32x32", x_px=0, y_px=0, rotation=0),
                Placement(id="r2", asset_key="robot_ev3_32x32", x_px=128, y_px=128, rotation=90),
            ],
        )

        report = engine.validate(world)
        codes = {issue.code for issue in report.issues}
        assert "MULTIPLE_ROBOTS" in codes

    def test_line_connectivity_valid_closed_loop(self):
        engine = ValidationEngine()
        world = EditorWorldModel(
            grid_size_px=32,
            world_width_cells=20,
            world_height_cells=20,
            placements=[
                Placement(id="a", asset_key="line_64_64_supizq", x_px=0, y_px=0, rotation=0),
                Placement(id="b", asset_key="line_64_64_supder", x_px=64, y_px=0, rotation=0),
                Placement(id="c", asset_key="line_64_64_infizq", x_px=0, y_px=64, rotation=0),
                Placement(id="d", asset_key="line_64_64_infder", x_px=64, y_px=64, rotation=0),
            ],
        )

        report = engine.validate(world)
        assert not report.has_errors
