"""
world_editor_service.py
=======================
Application service for the EV3 world editor.

This service keeps editor objects (walls, lines, color zones, suitcases),
converts them to WorldModel for simulation, and handles JSON load/save.
"""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
from typing import Any, Optional

from simulador_ev3.application.world_validation_engine import ValidationEngine, rotated_connectors
from simulador_ev3.domain.editor.world_editor_model import (
    CELL_SIZE_MM,
    DEFAULT_WORLD_MM,
    GRID_SIZE_PX,
    MAX_WORLD_MM,
    MAX_WORLD_PIXELS,
    SCHEMA_VERSION,
    EditorWorldModel,
    Placement,
    get_asset_spec,
    normalize_asset_key,
)
from simulador_ev3.domain.world.beacon_model import BeaconModel
from simulador_ev3.domain.world.obstacle_model import ObstacleModel
from simulador_ev3.domain.world.surface_model import SurfaceColor, SurfaceModel
from simulador_ev3.domain.world.world_model import WorldModel
from simulador_ev3.persistence.world_repository import WorldRepository

_DEFAULT_WORLD_W = DEFAULT_WORLD_MM
_DEFAULT_WORLD_H = DEFAULT_WORLD_MM
_LINE_ASSET_SIZE_PX = 64.0
_LINE_STROKE_PX = 8.0
_LINE_TILE_WORLD_MM = 2.0 * CELL_SIZE_MM
_LINE_TRACK_WIDTH_MM = _LINE_TILE_WORLD_MM * (_LINE_STROKE_PX / _LINE_ASSET_SIZE_PX)  # 25 mm
_DEFAULT_CELL_SIZE = _LINE_TRACK_WIDTH_MM / 2.0  # 12.5 mm (mejor ajuste visual-fisico)

_SURFACE_COLOR_MAP: dict[str, SurfaceColor] = {
    "WHITE": SurfaceColor.WHITE,
    "BLACK": SurfaceColor.BLACK,
    "RED": SurfaceColor.RED,
    "GREEN": SurfaceColor.GREEN,
}


class WorldEditorService:
    """Facade for world-editor data and persistence."""

    def __init__(self) -> None:
        self._id_counter = 1
        self._validator = ValidationEngine()
        self._formal_world = EditorWorldModel(
            grid_size_px=GRID_SIZE_PX,
            world_width_cells=max(1, int(round(_DEFAULT_WORLD_W / CELL_SIZE_MM))),
            world_height_cells=max(1, int(round(_DEFAULT_WORLD_H / CELL_SIZE_MM))),
            schema_version=SCHEMA_VERSION,
            placements=[],
        )
        self.new_world()

    # ------------------------------------------------------------------
    # Formal SDD API
    # ------------------------------------------------------------------

    def create_world(
        self,
        grid_size: int = GRID_SIZE_PX,
        width_cells: int = 20,
        height_cells: int = 20,
    ) -> EditorWorldModel:
        world = EditorWorldModel(
            grid_size_px=int(grid_size),
            world_width_cells=int(width_cells),
            world_height_cells=int(height_cells),
            schema_version=SCHEMA_VERSION,
            placements=[],
        )
        self._assert_valid_world(world)
        return world

    def place_asset(self, world: EditorWorldModel, p: Placement) -> None:
        candidate = copy.deepcopy(world)
        candidate.placements.append(p.with_normalized_asset())
        self._assert_valid_world(candidate)
        world.placements = candidate.placements

    def remove_asset(self, world: EditorWorldModel, asset_id: str) -> None:
        before = len(world.placements)
        world.placements = [p for p in world.placements if p.id != asset_id]
        if len(world.placements) == before:
            raise ValueError(f"No existe asset_id: {asset_id}")
        self._assert_valid_world(world)

    def move_asset(self, world: EditorWorldModel, asset_id: str, x: int, y: int) -> None:
        candidate = copy.deepcopy(world)
        found = False
        for idx, placement in enumerate(candidate.placements):
            if placement.id != asset_id:
                continue
            candidate.placements[idx] = Placement(
                id=placement.id,
                asset_key=placement.asset_key,
                x_px=int(x),
                y_px=int(y),
                rotation=placement.rotation,
            )
            found = True
            break
        if not found:
            raise ValueError(f"No existe asset_id: {asset_id}")
        self._assert_valid_world(candidate)
        world.placements = candidate.placements

    def validate(self, world: EditorWorldModel) -> list[str]:
        report = self._validator.validate(world)
        return report.messages()

    def save(self, world: EditorWorldModel) -> str:
        self._assert_valid_world(world)
        return json.dumps(world.to_dict(), ensure_ascii=False, indent=2)

    def load(self, data: str) -> EditorWorldModel:
        parsed = json.loads(data)
        world = EditorWorldModel.from_dict(parsed)
        self._assert_valid_world(world)
        return world

    def validate_editor_world(self, world: Optional[EditorWorldModel] = None) -> list[str]:
        target = world if world is not None else self._legacy_to_formal_world()
        return self.validate(target)

    def current_formal_world(self) -> EditorWorldModel:
        return self._formal_world

    def reset_formal_world(
        self,
        width_cells: Optional[int] = None,
        height_cells: Optional[int] = None,
    ) -> EditorWorldModel:
        w = int(width_cells) if width_cells is not None else self._formal_world.world_width_cells
        h = int(height_cells) if height_cells is not None else self._formal_world.world_height_cells
        self._formal_world = self.create_world(grid_size=GRID_SIZE_PX, width_cells=w, height_cells=h)
        self._rebuild_legacy_from_formal()
        return self._formal_world

    def resize_formal_world(self, width_cells: int, height_cells: int) -> bool:
        candidate = copy.deepcopy(self._formal_world)
        candidate.world_width_cells = int(width_cells)
        candidate.world_height_cells = int(height_cells)
        try:
            self._assert_valid_world(candidate)
        except ValueError:
            return False
        self._formal_world = candidate
        self._rebuild_legacy_from_formal()
        return True

    def place_asset_current(
        self,
        asset_key: str,
        x_px: int,
        y_px: int,
        rotation: int = 0,
    ) -> Placement:
        spec = get_asset_spec(asset_key)
        if spec is None:
            raise ValueError(f"Asset no reconocido: {asset_key}")
        placement = Placement(
            id=self._next_id(spec.asset_type),
            asset_key=normalize_asset_key(asset_key),
            x_px=int(x_px),
            y_px=int(y_px),
            rotation=int(rotation),
        )
        self.place_asset(self._formal_world, placement)
        self._rebuild_legacy_from_formal()
        return placement

    def remove_asset_current(self, asset_id: str) -> bool:
        try:
            self.remove_asset(self._formal_world, asset_id)
        except ValueError:
            return False
        self._rebuild_legacy_from_formal()
        return True

    def move_asset_current(self, asset_id: str, x_px: int, y_px: int) -> bool:
        try:
            self.move_asset(self._formal_world, asset_id, int(x_px), int(y_px))
        except ValueError:
            return False
        self._rebuild_legacy_from_formal()
        return True

    def rotate_asset_current(self, asset_id: str, delta_deg: int = 90) -> bool:
        candidate = copy.deepcopy(self._formal_world)
        found = False
        for idx, placement in enumerate(candidate.placements):
            if placement.id != asset_id:
                continue
            candidate.placements[idx] = Placement(
                id=placement.id,
                asset_key=placement.asset_key,
                x_px=placement.x_px,
                y_px=placement.y_px,
                rotation=(int(placement.rotation) + int(delta_deg)) % 360,
            )
            found = True
            break
        if not found:
            return False
        try:
            self._assert_valid_world(candidate)
        except ValueError:
            return False
        self._formal_world = candidate
        self._rebuild_legacy_from_formal()
        return True

    def duplicate_asset_current(
        self,
        asset_id: str,
        dx_px: int = GRID_SIZE_PX,
        dy_px: int = GRID_SIZE_PX,
    ) -> Optional[Placement]:
        src = self.get_placement(asset_id)
        if src is None:
            return None
        clone = Placement(
            id=self._next_id("asset"),
            asset_key=src.asset_key,
            x_px=src.x_px + int(dx_px),
            y_px=src.y_px + int(dy_px),
            rotation=src.rotation,
        )
        try:
            self.place_asset(self._formal_world, clone)
        except ValueError:
            return None
        self._rebuild_legacy_from_formal()
        return clone

    def update_asset_current(
        self,
        asset_id: str,
        *,
        x_px: Optional[int] = None,
        y_px: Optional[int] = None,
        rotation: Optional[int] = None,
        asset_key: Optional[str] = None,
    ) -> bool:
        candidate = copy.deepcopy(self._formal_world)
        found = False
        for idx, placement in enumerate(candidate.placements):
            if placement.id != asset_id:
                continue
            found = True
            candidate.placements[idx] = Placement(
                id=placement.id,
                asset_key=normalize_asset_key(asset_key if asset_key is not None else placement.asset_key),
                x_px=int(x_px if x_px is not None else placement.x_px),
                y_px=int(y_px if y_px is not None else placement.y_px),
                rotation=int(rotation if rotation is not None else placement.rotation),
            )
            break
        if not found:
            return False
        try:
            self._assert_valid_world(candidate)
        except ValueError:
            return False
        self._formal_world = candidate
        self._rebuild_legacy_from_formal()
        return True

    def get_placement(self, asset_id: str) -> Optional[Placement]:
        for placement in self._formal_world.placements:
            if placement.id == asset_id:
                return placement
        return None

    def validate_current_world(self) -> list[str]:
        return self.validate(self._formal_world)

    def _assert_valid_world(self, world: EditorWorldModel) -> None:
        report = self._validator.validate(world)
        if report.has_errors:
            raise ValueError("; ".join(issue.message for issue in report.errors))

    def _assert_world_size_within_limit(self, world: EditorWorldModel) -> None:
        world_width_px = world.world_width_cells * world.grid_size_px
        world_height_px = world.world_height_cells * world.grid_size_px
        if world_width_px > MAX_WORLD_PIXELS or world_height_px > MAX_WORLD_PIXELS:
            raise ValueError(
                f"El mundo excede el maximo permitido de {MAX_WORLD_PIXELS} px por eje "
                f"(actual: {world_width_px}x{world_height_px}px)."
            )

    # ------------------------------------------------------------------
    # World state
    # ------------------------------------------------------------------

    def new_world(self, width_mm: float = _DEFAULT_WORLD_W, height_mm: float = _DEFAULT_WORLD_H) -> None:
        self.width_mm = float(width_mm)
        self.height_mm = float(height_mm)
        self.walls: list[dict[str, Any]] = []
        self.lines: list[dict[str, Any]] = []
        self.zones: list[dict[str, Any]] = []
        self.suitcases: list[dict[str, Any]] = []
        self.beacons: list[BeaconModel] = []
        self._formal_world = EditorWorldModel(
            grid_size_px=GRID_SIZE_PX,
            world_width_cells=max(1, int(round(self.width_mm / CELL_SIZE_MM))),
            world_height_cells=max(1, int(round(self.height_mm / CELL_SIZE_MM))),
            schema_version=SCHEMA_VERSION,
            placements=[],
        )

    def all_objects(self) -> list[dict[str, Any]]:
        return self.walls + self.lines + self.zones + self.suitcases

    def get_object(self, object_id: str) -> Optional[dict[str, Any]]:
        for obj in self.all_objects():
            if obj["id"] == object_id:
                return obj
        return None

    def delete_object(self, object_id: str) -> bool:
        for bucket in (self.walls, self.lines, self.zones, self.suitcases):
            for i, obj in enumerate(bucket):
                if obj["id"] == object_id:
                    bucket.pop(i)
                    self._sync_formal_world_from_legacy()
                    return True
        return False

    def duplicate_object(self, object_id: str, dx_mm: float = 60.0, dy_mm: float = 60.0) -> Optional[dict[str, Any]]:
        src = self.get_object(object_id)
        if src is None:
            return None
        clone = copy.deepcopy(src)
        clone["id"] = self._next_id(src["type"])
        if clone["type"] == "line":
            clone["points"] = [[p[0] + dx_mm, p[1] + dy_mm] for p in clone["points"]]
        else:
            clone["x_mm"] = float(clone.get("x_mm", 0.0)) + dx_mm
            clone["y_mm"] = float(clone.get("y_mm", 0.0)) + dy_mm
        self._bucket_for_type(clone["type"]).append(clone)
        self._sync_formal_world_from_legacy()
        return clone

    def move_object(self, object_id: str, dx_mm: float, dy_mm: float) -> bool:
        obj = self.get_object(object_id)
        if obj is None:
            return False
        if obj["type"] == "line":
            obj["points"] = [[p[0] + dx_mm, p[1] + dy_mm] for p in obj["points"]]
        else:
            obj["x_mm"] = float(obj.get("x_mm", 0.0)) + dx_mm
            obj["y_mm"] = float(obj.get("y_mm", 0.0)) + dy_mm
        self._sync_formal_world_from_legacy()
        return True

    # ------------------------------------------------------------------
    # Object factories
    # ------------------------------------------------------------------

    def add_wall(
        self,
        x_mm: float,
        y_mm: float,
        width_mm: float,
        height_mm: float,
        rotation_deg: float = 0.0,
    ) -> dict[str, Any]:
        x_mm, y_mm, width_mm, height_mm = _normalize_rect(x_mm, y_mm, width_mm, height_mm)
        x_mm = _snap_mm(x_mm, CELL_SIZE_MM)
        y_mm = _snap_mm(y_mm, CELL_SIZE_MM)
        width_mm = _snap_mm(width_mm, 2.0 * CELL_SIZE_MM, min_value=2.0 * CELL_SIZE_MM)
        height_mm = _snap_mm(height_mm, 2.0 * CELL_SIZE_MM, min_value=2.0 * CELL_SIZE_MM)
        rotation_deg = int(round(float(rotation_deg) / 90.0) * 90) % 360
        obj = {
            "id": self._next_id("wall"),
            "type": "wall",
            "x_mm": x_mm,
            "y_mm": y_mm,
            "width_mm": width_mm,
            "height_mm": height_mm,
            "rotation_deg": float(rotation_deg),
        }
        self.walls.append(obj)
        self._sync_formal_world_from_legacy()
        return obj

    def add_line(
        self,
        points: list[list[float]],
        width_mm: float = 20.0,
        color: str = "#000000",
    ) -> dict[str, Any]:
        snapped_points = [[_snap_mm(float(p[0]), CELL_SIZE_MM), _snap_mm(float(p[1]), CELL_SIZE_MM)] for p in points]
        obj = {
            "id": self._next_id("line"),
            "type": "line",
            "color": color,
            "width_mm": _snap_mm(max(1.0, float(width_mm)), CELL_SIZE_MM, min_value=CELL_SIZE_MM),
            "points": snapped_points,
        }
        self.lines.append(obj)
        self._sync_formal_world_from_legacy()
        return obj

    def add_zone(
        self,
        color: str,
        x_mm: float,
        y_mm: float,
        width_mm: float,
        height_mm: float,
    ) -> dict[str, Any]:
        x_mm, y_mm, width_mm, height_mm = _normalize_rect(x_mm, y_mm, width_mm, height_mm)
        x_mm = _snap_mm(x_mm, CELL_SIZE_MM)
        y_mm = _snap_mm(y_mm, CELL_SIZE_MM)
        width_mm = _snap_mm(width_mm, 4.0 * CELL_SIZE_MM, min_value=4.0 * CELL_SIZE_MM)
        height_mm = _snap_mm(height_mm, 4.0 * CELL_SIZE_MM, min_value=4.0 * CELL_SIZE_MM)
        obj = {
            "id": self._next_id("zone"),
            "type": "color_zone",
            "color": str(color).upper(),
            "x_mm": x_mm,
            "y_mm": y_mm,
            "width_mm": width_mm,
            "height_mm": height_mm,
        }
        self.zones.append(obj)
        self._sync_formal_world_from_legacy()
        return obj

    def add_suitcase(
        self,
        x_mm: float,
        y_mm: float,
        width_mm: float = 120.0,
        height_mm: float = 80.0,
        mass: float = 1.2,
        movable: bool = True,
    ) -> dict[str, Any]:
        x_mm, y_mm, width_mm, height_mm = _normalize_rect(x_mm, y_mm, width_mm, height_mm)
        x_mm = _snap_mm(x_mm, CELL_SIZE_MM)
        y_mm = _snap_mm(y_mm, CELL_SIZE_MM)
        width_mm = _snap_mm(width_mm, 2.0 * CELL_SIZE_MM, min_value=2.0 * CELL_SIZE_MM)
        height_mm = _snap_mm(height_mm, 2.0 * CELL_SIZE_MM, min_value=2.0 * CELL_SIZE_MM)
        obj = {
            "id": self._next_id("suitcase"),
            "type": "suitcase",
            "x_mm": x_mm,
            "y_mm": y_mm,
            "width_mm": width_mm,
            "height_mm": height_mm,
            "mass": max(0.0, float(mass)),
            "movable": bool(movable),
        }
        self.suitcases.append(obj)
        self._sync_formal_world_from_legacy()
        return obj

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_json(self, path: str | Path) -> Path:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        self._rebuild_legacy_from_formal()
        data = WorldRepository.to_dict(self.to_world_model())
        data["editor_objects"] = self.to_editor_dict()
        data["editor_spec"] = self._formal_world.to_dict()
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return out

    def load_json(self, path: str | Path) -> tuple[Path, Optional[str]]:
        src = Path(path)
        data = json.loads(src.read_text(encoding="utf-8"))

        if "editor_spec" in data and isinstance(data["editor_spec"], dict):
            self._formal_world = EditorWorldModel.from_dict(data["editor_spec"])
            self._assert_world_size_within_limit(self._formal_world)
            self._rebuild_legacy_from_formal()
            issues = self.validate(self._formal_world)
            note = None
            if issues:
                note = f"Se cargo mundo con advertencias: {issues[0]}"
            return src, note

        if "editor_objects" in data and isinstance(data["editor_objects"], dict):
            self.from_editor_dict(data["editor_objects"])
            return src, None

        # Direct editor format (without wrapper).
        if all(k in data for k in ("world", "walls", "lines", "zones")):
            self.from_editor_dict(data)
            return src, None

        # Legacy repository format.
        world = WorldRepository.from_dict(data)
        self._from_world_model(world)
        return src, (
            "El archivo no tenia metadata del editor. "
            "Se importaron muros/zonas basicos desde el mundo de simulacion."
        )

    def to_editor_dict(self) -> dict[str, Any]:
        return {
            "world": {
                "width_mm": self.width_mm,
                "height_mm": self.height_mm,
            },
            "walls": copy.deepcopy(self.walls),
            "lines": copy.deepcopy(self.lines),
            "zones": copy.deepcopy(self.zones),
            "objects": copy.deepcopy(self.suitcases),
        }

    def from_editor_dict(self, data: dict[str, Any]) -> None:
        world_data = data.get("world", {})
        self.new_world(
            width_mm=float(world_data.get("width_mm", _DEFAULT_WORLD_W)),
            height_mm=float(world_data.get("height_mm", _DEFAULT_WORLD_H)),
        )
        self.walls = [_with_id("wall", item, self._next_id("wall")) for item in data.get("walls", [])]
        self.lines = [_with_id("line", item, self._next_id("line")) for item in data.get("lines", [])]
        self.zones = [_with_id("color_zone", item, self._next_id("zone")) for item in data.get("zones", [])]
        self.suitcases = [
            _with_id("suitcase", item, self._next_id("suitcase"))
            for item in data.get("objects", [])
            if str(item.get("type", "suitcase")).lower() == "suitcase"
        ]
        self._sync_formal_world_from_legacy()
        self._assert_world_size_within_limit(self._formal_world)

    # ------------------------------------------------------------------
    # Conversion to simulation world
    # ------------------------------------------------------------------

    def to_world_model(self) -> WorldModel:
        world_from_formal = self._to_world_model_from_formal()
        # Keep suitcase support from legacy editor objects for compatibility.
        for item in self.suitcases:
            obstacle = _obstacle_from_rect(
                x_mm=float(item.get("x_mm", 0.0)),
                y_mm=float(item.get("y_mm", 0.0)),
                width_mm=float(item.get("width_mm", 120.0)),
                height_mm=float(item.get("height_mm", 80.0)),
                rotation_deg=0.0,
                name=f"suitcase:{item.get('id', 'obj')}",
            )
            world_from_formal.obstacles.append(obstacle)
        return world_from_formal

    def _to_world_model_from_formal(self) -> WorldModel:
        surface = SurfaceModel(cell_size_mm=_DEFAULT_CELL_SIZE, default_color=SurfaceColor.WHITE)
        obstacles: list[ObstacleModel] = []
        world_w_mm = self._formal_world.world_width_cells * CELL_SIZE_MM
        world_h_mm = self._formal_world.world_height_cells * CELL_SIZE_MM

        for placement in self._formal_world.placements:
            spec = get_asset_spec(placement.asset_key)
            if spec is None:
                continue
            x_mm = _px_to_mm(placement.x_px)
            y_mm = _px_to_mm(placement.y_px)
            width_cells = spec.width_cells
            height_cells = spec.height_cells
            if placement.rotation % 180 == 90:
                width_cells, height_cells = height_cells, width_cells
            w_mm = width_cells * CELL_SIZE_MM
            h_mm = height_cells * CELL_SIZE_MM

            if spec.asset_type == "wall":
                wall_key = normalize_asset_key(placement.asset_key)
                obstacles.append(
                    _obstacle_from_rect(
                        x_mm=x_mm,
                        y_mm=y_mm,
                        width_mm=w_mm,
                        height_mm=h_mm,
                        rotation_deg=float(placement.rotation),
                        name=f"wall:{wall_key}:{placement.id}",
                    )
                )
                continue

            if spec.asset_type == "zone":
                zone_color = SurfaceColor.WHITE
                key = normalize_asset_key(placement.asset_key)
                if "red" in key:
                    zone_color = SurfaceColor.RED
                elif "green" in key:
                    zone_color = SurfaceColor.GREEN
                surface.set_rect(
                    x_mm=x_mm,
                    y_mm=y_mm,
                    width_mm=w_mm,
                    height_mm=h_mm,
                    color=zone_color,
                )
                continue

            if spec.asset_type == "line":
                cx = x_mm + w_mm / 2.0
                cy = y_mm + h_mm / 2.0
                connectors = _rotated_connectors(spec.connectors, placement.rotation)
                for direction in connectors:
                    ex, ey = _line_endpoint_mm(direction, x_mm, y_mm, w_mm, h_mm)
                    _paint_segment(
                        surface=surface,
                        x1=cx,
                        y1=cy,
                        x2=ex,
                        y2=ey,
                        width_mm=_LINE_TRACK_WIDTH_MM,
                        color=SurfaceColor.BLACK,
                    )

        return WorldModel(
            width_mm=world_w_mm,
            height_mm=world_h_mm,
            surface=surface,
            obstacles=obstacles,
            beacons=list(self.beacons),
        )

    def _paint_polyline(
        self,
        surface: SurfaceModel,
        points: list[list[float]],
        width_mm: float,
        color: SurfaceColor,
    ) -> None:
        if len(points) == 1:
            p = points[0]
            surface.set_rect(
                x_mm=p[0] - width_mm / 2.0,
                y_mm=p[1] - width_mm / 2.0,
                width_mm=width_mm,
                height_mm=width_mm,
                color=color,
            )
            return

        for p0, p1 in zip(points[:-1], points[1:]):
            _paint_segment(surface, p0[0], p0[1], p1[0], p1[1], width_mm, color)

    def _sync_formal_world_from_legacy(self) -> None:
        self._formal_world = self._legacy_to_formal_world()

    def _legacy_to_formal_world(self) -> EditorWorldModel:
        grid_size = GRID_SIZE_PX
        width_cells = max(1, int(round(self.width_mm / CELL_SIZE_MM)))
        height_cells = max(1, int(round(self.height_mm / CELL_SIZE_MM)))
        placements: list[Placement] = []

        for wall in self.walls:
            placements.append(
                Placement(
                    id=str(wall.get("id", self._next_id("wall"))),
                    asset_key="wall_64x64_a",
                    x_px=_mm_to_px(float(wall.get("x_mm", 0.0))),
                    y_px=_mm_to_px(float(wall.get("y_mm", 0.0))),
                    rotation=int(round(float(wall.get("rotation_deg", 0.0)) / 90.0) * 90),
                )
            )
        for zone in self.zones:
            zone_color = str(zone.get("color", "WHITE")).upper()
            key = {
                "RED": "zone_red_128",
                "GREEN": "zone_green_128",
            }.get(zone_color, "zone_white_128")
            placements.append(
                Placement(
                    id=str(zone.get("id", self._next_id("zone"))),
                    asset_key=key,
                    x_px=_mm_to_px(float(zone.get("x_mm", 0.0))),
                    y_px=_mm_to_px(float(zone.get("y_mm", 0.0))),
                    rotation=0,
                )
            )

        for line in self.lines:
            points = [[float(p[0]), float(p[1])] for p in line.get("points", []) if len(p) >= 2]
            placements.extend(self._line_points_to_formal_placements(points, str(line.get("id", "line"))))

        # Suitcase remains as physical editor-only object; do not include in formal spec model.
        return EditorWorldModel(
            grid_size_px=grid_size,
            world_width_cells=width_cells,
            world_height_cells=height_cells,
            schema_version=SCHEMA_VERSION,
            placements=placements,
        )

    def _line_points_to_formal_placements(self, points: list[list[float]], source_id: str) -> list[Placement]:
        if len(points) < 2:
            return []

        cells = self._trace_polyline_cells(points)
        if not cells:
            return []
        connectors = _connectors_from_cells(cells)
        placements: list[Placement] = []
        for idx, cell in enumerate(sorted(connectors.keys())):
            key = _line_asset_from_connectors(connectors[cell])
            if key is None:
                continue
            placements.append(
                Placement(
                    id=f"{source_id}__tile_{idx:04d}",
                    asset_key=key,
                    x_px=cell[0] * GRID_SIZE_PX,
                    y_px=cell[1] * GRID_SIZE_PX,
                    rotation=0,
                )
            )
        return placements

    def _trace_polyline_cells(self, points: list[list[float]]) -> list[tuple[int, int]]:
        out: set[tuple[int, int]] = set()
        for p0, p1 in zip(points[:-1], points[1:]):
            x0 = _mm_to_cell(p0[0])
            y0 = _mm_to_cell(p0[1])
            x1 = _mm_to_cell(p1[0])
            y1 = _mm_to_cell(p1[1])
            for cell in _bresenham_cells(x0, y0, x1, y1):
                out.add(cell)
        return sorted(out)

    def _rebuild_legacy_from_formal(self) -> None:
        self.width_mm = self._formal_world.world_width_cells * CELL_SIZE_MM
        self.height_mm = self._formal_world.world_height_cells * CELL_SIZE_MM
        self.walls = []
        self.lines = []
        self.zones = []
        self.suitcases = []
        self.beacons = []

        wall_specs = {"wall_64x64_a", "wall_64x64_b", "wall_64x64_c"}
        zone_specs = {"zone_red_128", "zone_green_128", "zone_white_128"}
        line_specs = {
            "line_64_64_hor",
            "line_64_64_ver",
            "line_64x64_cruz",
            "line_64_64_infder",
            "line_64_64_infizq",
            "line_64_64_supder",
            "line_64_64_supizq",
        }

        grouped_lines: list[dict[str, Any]] = []
        for placement in self._formal_world.placements:
            key = normalize_asset_key(placement.asset_key)
            spec = get_asset_spec(key)
            if spec is None:
                continue
            x_mm = _px_to_mm(placement.x_px)
            y_mm = _px_to_mm(placement.y_px)
            if key in wall_specs:
                self.walls.append(
                    {
                        "id": placement.id,
                        "type": "wall",
                        "x_mm": x_mm,
                        "y_mm": y_mm,
                        "width_mm": spec.width_cells * CELL_SIZE_MM,
                        "height_mm": spec.height_cells * CELL_SIZE_MM,
                        "rotation_deg": placement.rotation,
                    }
                )
            elif key in zone_specs:
                zone_color = "WHITE"
                if "red" in key:
                    zone_color = "RED"
                if "green" in key:
                    zone_color = "GREEN"
                self.zones.append(
                    {
                        "id": placement.id,
                        "type": "color_zone",
                        "color": zone_color,
                        "x_mm": x_mm,
                        "y_mm": y_mm,
                        "width_mm": spec.width_cells * CELL_SIZE_MM,
                        "height_mm": spec.height_cells * CELL_SIZE_MM,
                    }
                )
            elif key in line_specs:
                grouped_lines.append(
                    {
                        "id": placement.id,
                        "type": "line",
                        "color": "#000000",
                        "width_mm": CELL_SIZE_MM,
                        "points": [[x_mm, y_mm], [x_mm + CELL_SIZE_MM, y_mm + CELL_SIZE_MM]],
                    }
                )

        self.lines = grouped_lines

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _bucket_for_type(self, obj_type: str) -> list[dict[str, Any]]:
        if obj_type == "wall":
            return self.walls
        if obj_type == "line":
            return self.lines
        if obj_type == "color_zone":
            return self.zones
        if obj_type == "suitcase":
            return self.suitcases
        raise ValueError(f"Tipo no soportado: {obj_type}")

    def _next_id(self, prefix: str) -> str:
        nid = f"{prefix}_{self._id_counter:04d}"
        self._id_counter += 1
        return nid

    def _from_world_model(self, world: WorldModel) -> None:
        self.new_world(width_mm=world.width_mm, height_mm=world.height_mm)
        self.beacons = list(world.beacons)

        for obs in world.obstacles:
            min_x, min_y, max_x, max_y = obs.aabb
            width = max_x - min_x
            height = max_y - min_y
            if obs.name.startswith("suitcase:"):
                self.add_suitcase(
                    x_mm=min_x,
                    y_mm=min_y,
                    width_mm=width,
                    height_mm=height,
                )
            else:
                self.add_wall(
                    x_mm=min_x,
                    y_mm=min_y,
                    width_mm=width,
                    height_mm=height,
                    rotation_deg=0.0,
                )

        # Import de superficie para editor:
        # - Celdas BLACK -> tiles de linea del editor (evita zonas gigantes fuera de limites).
        # - Otros colores se omiten en este fallback para no introducir artefactos.
        cs = float(world.surface.cell_size_mm)
        black_tiles: set[tuple[int, int]] = set()
        max_cols = max(1, self._formal_world.world_width_cells)
        max_rows = max(1, self._formal_world.world_height_cells)
        tile_mm = 2.0 * CELL_SIZE_MM

        for (col, row), cell in world.surface._grid.items():
            if cell.color != SurfaceColor.BLACK:
                continue
            center_x_mm = (float(col) * cs) + (cs / 2.0)
            center_y_mm = (float(row) * cs) + (cs / 2.0)
            tc = int(center_x_mm // tile_mm)
            tr = int(center_y_mm // tile_mm)
            if 0 <= (tc * 2) < max_cols and 0 <= (tr * 2) < max_rows:
                black_tiles.add((tc, tr))

        if black_tiles:
            connectors = _connectors_from_cells(sorted(black_tiles))
            for tc, tr in sorted(connectors.keys()):
                asset_key = _line_asset_from_connectors(connectors[(tc, tr)])
                if asset_key is None:
                    continue
                self._formal_world.placements.append(
                    Placement(
                        id=self._next_id("line"),
                        asset_key=asset_key,
                        x_px=int(tc * (2 * GRID_SIZE_PX)),
                        y_px=int(tr * (2 * GRID_SIZE_PX)),
                        rotation=0,
                    )
                )
            self._rebuild_legacy_from_formal()


def _with_id(expected_type: str, item: dict[str, Any], fallback_id: str) -> dict[str, Any]:
    obj = dict(item)
    obj.setdefault("type", expected_type)
    obj["type"] = expected_type
    obj["id"] = str(obj.get("id", fallback_id))
    return obj


def _mm_to_px(mm_value: float) -> int:
    return int(round(float(mm_value) / CELL_SIZE_MM * GRID_SIZE_PX))


def _px_to_mm(px_value: int | float) -> float:
    return float(px_value) / GRID_SIZE_PX * CELL_SIZE_MM


def _mm_to_cell(mm_value: float) -> int:
    return int(round(float(mm_value) / CELL_SIZE_MM))


def _bresenham_cells(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    points: list[tuple[int, int]] = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    points.append((x1, y1))
    return points


def _connectors_from_cells(cells: list[tuple[int, int]]) -> dict[tuple[int, int], set[str]]:
    cell_set = set(cells)
    out: dict[tuple[int, int], set[str]] = {}
    for cell in cell_set:
        cx, cy = cell
        connectors: set[str] = set()
        if (cx, cy - 1) in cell_set:
            connectors.add("N")
        if (cx, cy + 1) in cell_set:
            connectors.add("S")
        if (cx + 1, cy) in cell_set:
            connectors.add("E")
        if (cx - 1, cy) in cell_set:
            connectors.add("W")
        out[cell] = connectors
    return out


def _line_asset_from_connectors(connectors: set[str]) -> Optional[str]:
    normalized = frozenset(connectors)
    mapping = {
        frozenset({"E", "W"}): "line_64_64_hor",
        frozenset({"N", "S"}): "line_64_64_ver",
        frozenset({"N", "S", "E", "W"}): "line_64x64_cruz",
        frozenset({"N", "W"}): "line_64_64_infder",
        frozenset({"N", "E"}): "line_64_64_infizq",
        frozenset({"S", "W"}): "line_64_64_supder",
        frozenset({"S", "E"}): "line_64_64_supizq",
    }
    if normalized in mapping:
        return mapping[normalized]
    # Endpoints default to straight segments for compatibility.
    if normalized in {frozenset({"E"}), frozenset({"W"})}:
        return "line_64_64_hor"
    if normalized in {frozenset({"N"}), frozenset({"S"})}:
        return "line_64_64_ver"
    return None


def _rotated_connectors(connectors: frozenset[str], rotation_deg: int) -> set[str]:
    return {str(d) for d in rotated_connectors(set(connectors), int(rotation_deg))}


def _line_endpoint_mm(direction: str, x_mm: float, y_mm: float, w_mm: float, h_mm: float) -> tuple[float, float]:
    cx = x_mm + w_mm / 2.0
    cy = y_mm + h_mm / 2.0
    if direction == "N":
        return cx, y_mm
    if direction == "S":
        return cx, y_mm + h_mm
    if direction == "E":
        return x_mm + w_mm, cy
    return x_mm, cy


def _snap_mm(value_mm: float, quantum_mm: float, min_value: float = 0.0) -> float:
    if quantum_mm <= 0:
        raise ValueError("quantum_mm debe ser > 0")
    snapped = round(float(value_mm) / quantum_mm) * quantum_mm
    return max(float(min_value), float(snapped))


def _normalize_rect(
    x_mm: float,
    y_mm: float,
    width_mm: float,
    height_mm: float,
) -> tuple[float, float, float, float]:
    x = float(x_mm)
    y = float(y_mm)
    w = float(width_mm)
    h = float(height_mm)
    if w < 0:
        x += w
        w = -w
    if h < 0:
        y += h
        h = -h
    return x, y, max(1.0, w), max(1.0, h)


def _obstacle_from_rect(
    x_mm: float,
    y_mm: float,
    width_mm: float,
    height_mm: float,
    rotation_deg: float,
    name: str,
) -> ObstacleModel:
    if abs(rotation_deg) < 1e-9:
        return ObstacleModel.from_rect(x_mm, y_mm, width_mm, height_mm, name=name)

    cx = x_mm + width_mm / 2.0
    cy = y_mm + height_mm / 2.0
    half_w = width_mm / 2.0
    half_h = height_mm / 2.0
    th = math.radians(rotation_deg)
    cos_t = math.cos(th)
    sin_t = math.sin(th)

    corners = [
        (-half_w, -half_h),
        (half_w, -half_h),
        (half_w, half_h),
        (-half_w, half_h),
    ]
    vertices = []
    for lx, ly in corners:
        rx = cx + lx * cos_t - ly * sin_t
        ry = cy + lx * sin_t + ly * cos_t
        vertices.append((rx, ry))
    return ObstacleModel(vertices=vertices, name=name)


def _distance_point_to_segment(
    px: float,
    py: float,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> float:
    vx = x2 - x1
    vy = y2 - y1
    wx = px - x1
    wy = py - y1
    c1 = vx * wx + vy * wy
    if c1 <= 0:
        return math.hypot(px - x1, py - y1)
    c2 = vx * vx + vy * vy
    if c2 <= c1:
        return math.hypot(px - x2, py - y2)
    t = c1 / c2
    bx = x1 + t * vx
    by = y1 + t * vy
    return math.hypot(px - bx, py - by)


def _paint_segment(
    surface: SurfaceModel,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    width_mm: float,
    color: SurfaceColor,
) -> None:
    cs = surface.cell_size_mm
    half = width_mm / 2.0
    min_x = min(x1, x2) - half
    max_x = max(x1, x2) + half
    min_y = min(y1, y2) - half
    max_y = max(y1, y2) + half

    col_min = int(math.floor(min_x / cs))
    col_max = int(math.floor(max_x / cs))
    row_min = int(math.floor(min_y / cs))
    row_max = int(math.floor(max_y / cs))

    for col in range(col_min, col_max + 1):
        for row in range(row_min, row_max + 1):
            cell_x0 = col * cs
            cell_y0 = row * cs
            cell_x1 = cell_x0 + cs
            cell_y1 = cell_y0 + cs
            if _segment_intersects_aabb(
                x1,
                y1,
                x2,
                y2,
                cell_x0 - half,
                cell_y0 - half,
                cell_x1 + half,
                cell_y1 + half,
            ):
                surface.set_cell(col, row, color=color)


def _segment_intersects_aabb(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    min_x: float,
    min_y: float,
    max_x: float,
    max_y: float,
) -> bool:
    if min_x <= x1 <= max_x and min_y <= y1 <= max_y:
        return True
    if min_x <= x2 <= max_x and min_y <= y2 <= max_y:
        return True

    dx = x2 - x1
    dy = y2 - y1
    p = (-dx, dx, -dy, dy)
    q = (x1 - min_x, max_x - x1, y1 - min_y, max_y - y1)

    u1 = 0.0
    u2 = 1.0
    for pi, qi in zip(p, q):
        if abs(pi) < 1e-12:
            if qi < 0:
                return False
            continue
        t = qi / pi
        if pi < 0:
            u1 = max(u1, t)
        else:
            u2 = min(u2, t)
        if u1 > u2:
            return False
    return True
