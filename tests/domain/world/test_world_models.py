"""
test_world_models.py
====================
Tests unitarios para SurfaceModel, ObstacleModel, BeaconModel y WorldModel.
"""

import math
import pytest
from simulador_ev3.domain.world.surface_model  import SurfaceModel, SurfaceColor
from simulador_ev3.domain.world.obstacle_model import ObstacleModel
from simulador_ev3.domain.world.beacon_model   import BeaconModel
from simulador_ev3.domain.world.world_model    import WorldModel


# ================================================================== #
# SurfaceModel
# ================================================================== #

class TestSurfaceModel:
    def test_default_background_is_white(self) -> None:
        s = SurfaceModel()
        color, _ = s.query(100.0, 100.0)
        assert color == SurfaceColor.WHITE

    def test_set_cell_and_query(self) -> None:
        s = SurfaceModel(cell_size_mm=50.0)
        s.set_cell(0, 0, SurfaceColor.BLACK)
        color, ref = s.query(10.0, 10.0)     # dentro de celda (0,0)
        assert color == SurfaceColor.BLACK

    def test_reflectance_black_is_low(self) -> None:
        s = SurfaceModel(cell_size_mm=50.0)
        s.set_cell(0, 0, SurfaceColor.BLACK)
        _, ref = s.query(10.0, 10.0)
        assert ref < 20.0

    def test_reflectance_white_is_high(self) -> None:
        s = SurfaceModel()
        _, ref = s.query(0.0, 0.0)
        assert ref > 80.0

    def test_custom_reflectance(self) -> None:
        s = SurfaceModel(cell_size_mm=50.0)
        s.set_cell(1, 0, SurfaceColor.RED, reflectance=42.0)
        _, ref = s.query(60.0, 10.0)
        assert math.isclose(ref, 42.0)

    def test_set_rect_fills_multiple_cells(self) -> None:
        s = SurfaceModel(cell_size_mm=50.0)
        s.set_rect(0, 0, 150, 50, SurfaceColor.BLACK)
        for x in [10.0, 60.0, 110.0]:
            color, _ = s.query(x, 25.0)
            assert color == SurfaceColor.BLACK

    def test_invalid_cell_size_raises(self) -> None:
        with pytest.raises(ValueError):
            SurfaceModel(cell_size_mm=0.0)

    def test_query_color_shortcut(self) -> None:
        s = SurfaceModel(cell_size_mm=50.0)
        s.set_cell(0, 0, SurfaceColor.RED)
        assert s.query_color(25.0, 25.0) == SurfaceColor.RED

    def test_query_reflectance_shortcut(self) -> None:
        s = SurfaceModel(cell_size_mm=50.0)
        s.set_cell(0, 0, SurfaceColor.BLACK)
        assert s.query_reflectance(25.0, 25.0) < 20.0


# ================================================================== #
# ObstacleModel
# ================================================================== #

class TestObstacleModel:
    def test_from_rect_creates_4_vertices(self) -> None:
        obs = ObstacleModel.from_rect(0, 0, 100, 100)
        assert len(obs.vertices) == 4

    def test_contains_point_inside(self) -> None:
        obs = ObstacleModel.from_rect(0, 0, 100, 100)
        assert obs.contains_point(50, 50)

    def test_contains_point_outside(self) -> None:
        obs = ObstacleModel.from_rect(0, 0, 100, 100)
        assert not obs.contains_point(150, 50)

    def test_aabb_correct(self) -> None:
        obs = ObstacleModel.from_rect(10, 20, 100, 50)
        min_x, min_y, max_x, max_y = obs.aabb
        assert min_x == 10 and min_y == 20
        assert max_x == 110 and max_y == 70

    def test_ray_intersection_hits(self) -> None:
        obs = ObstacleModel.from_rect(200, 0, 100, 200)  # pared a x=200
        dist = obs.ray_intersection_distance(0, 100, 1, 0, max_dist=500)
        assert dist is not None
        assert math.isclose(dist, 200.0, abs_tol=1.0)

    def test_ray_intersection_miss(self) -> None:
        obs = ObstacleModel.from_rect(0, 300, 100, 100)  # por encima
        dist = obs.ray_intersection_distance(0, 0, 1, 0, max_dist=200)
        assert dist is None

    def test_too_few_vertices_raises(self) -> None:
        with pytest.raises(ValueError):
            ObstacleModel(vertices=[(0, 0), (1, 1)])

    def test_centroid_of_rect(self) -> None:
        obs = ObstacleModel.from_rect(0, 0, 100, 100)
        cx, cy = obs.centroid
        assert math.isclose(cx, 50.0, abs_tol=1.0)
        assert math.isclose(cy, 50.0, abs_tol=1.0)


# ================================================================== #
# BeaconModel
# ================================================================== #

class TestBeaconModel:
    def test_invalid_channel_raises(self) -> None:
        with pytest.raises(ValueError):
            BeaconModel(x_mm=0, y_mm=0, channel=5)

    def test_distance_to(self) -> None:
        b = BeaconModel(x_mm=300, y_mm=400, channel=1)
        dist = b.distance_to(0, 0)
        assert math.isclose(dist, 500.0, abs_tol=0.1)

    def test_relative_distance_scales_to_100(self) -> None:
        b = BeaconModel(x_mm=3000, y_mm=0, channel=1)  # 3 m → 100
        assert b.relative_distance(0, 0) == 100

    def test_relative_heading_front_is_zero(self) -> None:
        b = BeaconModel(x_mm=500, y_mm=0, channel=1)
        heading = b.relative_heading(0, 0, robot_theta=0.0)   # apunta +X
        assert heading == 0

    def test_relative_heading_left_is_positive(self) -> None:
        # Baliza a la izquierda del robot (robot mira +X, baliza en +Y)
        b = BeaconModel(x_mm=0, y_mm=500, channel=1)
        heading = b.relative_heading(0, 0, robot_theta=0.0)
        assert heading > 0


# ================================================================== #
# WorldModel
# ================================================================== #

class TestWorldModel:
    def test_default_world_created(self) -> None:
        w = WorldModel()
        assert w.width_mm == 2000.0
        assert len(w.obstacles) == 0

    def test_add_obstacle(self) -> None:
        w = WorldModel()
        w.add_obstacle(ObstacleModel.from_rect(100, 100, 50, 50, "wall"))
        assert len(w.obstacles) == 1

    def test_remove_obstacle(self) -> None:
        w = WorldModel()
        w.add_obstacle(ObstacleModel.from_rect(100, 100, 50, 50, "wall"))
        result = w.remove_obstacle("wall")
        assert result is True
        assert len(w.obstacles) == 0

    def test_remove_nonexistent_returns_false(self) -> None:
        w = WorldModel()
        assert w.remove_obstacle("ghost") is False

    def test_is_colliding_with_obstacle(self) -> None:
        w = WorldModel()
        w.add_obstacle(ObstacleModel.from_rect(100, 100, 200, 200))
        assert w.is_colliding(150, 150)

    def test_is_colliding_outside_world(self) -> None:
        w = WorldModel(width_mm=500, height_mm=500)
        assert w.is_colliding(-10, 250)

    def test_is_not_colliding_free_space(self) -> None:
        w = WorldModel()
        w.add_obstacle(ObstacleModel.from_rect(500, 500, 100, 100))
        assert not w.is_colliding(100, 100)

    def test_ray_cast_hits_wall(self) -> None:
        w = WorldModel(width_mm=1000, height_mm=1000)
        w.add_obstacle(ObstacleModel.from_rect(400, 0, 50, 1000, "wall"))
        dist = w.ray_cast(0, 500, angle_rad=0.0, max_dist_mm=1000)
        assert math.isclose(dist, 400.0, abs_tol=5.0)

    def test_ray_cast_no_obstacle_returns_max(self) -> None:
        w = WorldModel(width_mm=2000, height_mm=2000)
        # Rayo hacia +X desde centro — llegará al borde derecho
        dist = w.ray_cast(1000, 1000, angle_rad=0.0, max_dist_mm=2500)
        assert math.isclose(dist, 1000.0, abs_tol=10.0)

    def test_add_and_get_beacon(self) -> None:
        w = WorldModel()
        b = BeaconModel(x_mm=500, y_mm=500, channel=1)
        w.add_beacon(b)
        assert w.get_beacon(1) is b
        assert w.get_beacon(2) is None
