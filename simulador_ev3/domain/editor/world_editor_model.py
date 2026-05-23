"""
world_editor_model.py
=====================
Formal domain model for the EV3 world editor (spec-driven).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Direction = Literal["N", "S", "E", "W"]
AssetType = Literal["robot", "line", "wall", "zone", "floor"]
LayerName = Literal["floor", "zone", "line", "wall", "robot"]

GRID_SIZE_PX = 32
CELL_SIZE_MM = 100.0
SCHEMA_VERSION = 1
SUPPORTED_ROTATIONS = (0, 90, 180, 270)
MAX_WORLD_PIXELS = 5120
MAX_WORLD_CELLS = MAX_WORLD_PIXELS // GRID_SIZE_PX
MAX_WORLD_MM = MAX_WORLD_CELLS * CELL_SIZE_MM
DEFAULT_WORLD_MM = 4000.0
DEFAULT_WORLD_CELLS = int(DEFAULT_WORLD_MM / CELL_SIZE_MM)


@dataclass(frozen=True)
class AssetSpec:
    """Static metadata of a placeable asset."""

    key: str
    asset_type: AssetType
    layer: LayerName
    width_cells: int
    height_cells: int
    connectors: frozenset[Direction] = frozenset()


ASSET_CATALOG: dict[str, AssetSpec] = {
    "robot_ev3_32x32": AssetSpec(
        key="robot_ev3_32x32",
        asset_type="robot",
        layer="robot",
        width_cells=1,
        height_cells=1,
    ),
    "wall_64x64_a": AssetSpec(
        key="wall_64x64_a",
        asset_type="wall",
        layer="wall",
        width_cells=2,
        height_cells=2,
    ),
    "wall_64x64_b": AssetSpec(
        key="wall_64x64_b",
        asset_type="wall",
        layer="wall",
        width_cells=2,
        height_cells=2,
    ),
    "wall_64x64_c": AssetSpec(
        key="wall_64x64_c",
        asset_type="wall",
        layer="wall",
        width_cells=2,
        height_cells=2,
    ),
    "zone_green_128": AssetSpec(
        key="zone_green_128",
        asset_type="zone",
        layer="zone",
        width_cells=4,
        height_cells=4,
    ),
    "zone_red_128": AssetSpec(
        key="zone_red_128",
        asset_type="zone",
        layer="zone",
        width_cells=4,
        height_cells=4,
    ),
    "zone_white_128": AssetSpec(
        key="zone_white_128",
        asset_type="zone",
        layer="zone",
        width_cells=4,
        height_cells=4,
    ),
    "line_64_64_hor": AssetSpec(
        key="line_64_64_hor",
        asset_type="line",
        layer="line",
        width_cells=2,
        height_cells=2,
        connectors=frozenset({"E", "W"}),
    ),
    "line_64_64_ver": AssetSpec(
        key="line_64_64_ver",
        asset_type="line",
        layer="line",
        width_cells=2,
        height_cells=2,
        connectors=frozenset({"N", "S"}),
    ),
    "line_64x64_cruz": AssetSpec(
        key="line_64x64_cruz",
        asset_type="line",
        layer="line",
        width_cells=2,
        height_cells=2,
        connectors=frozenset({"N", "S", "E", "W"}),
    ),
    "line_64_64_infder": AssetSpec(
        key="line_64_64_infder",
        asset_type="line",
        layer="line",
        width_cells=2,
        height_cells=2,
        connectors=frozenset({"N", "W"}),
    ),
    "line_64_64_infizq": AssetSpec(
        key="line_64_64_infizq",
        asset_type="line",
        layer="line",
        width_cells=2,
        height_cells=2,
        connectors=frozenset({"N", "E"}),
    ),
    "line_64_64_supder": AssetSpec(
        key="line_64_64_supder",
        asset_type="line",
        layer="line",
        width_cells=2,
        height_cells=2,
        connectors=frozenset({"S", "W"}),
    ),
    "line_64_64_supizq": AssetSpec(
        key="line_64_64_supizq",
        asset_type="line",
        layer="line",
        width_cells=2,
        height_cells=2,
        connectors=frozenset({"S", "E"}),
    ),
    "floor_tile_256_a": AssetSpec(
        key="floor_tile_256_a",
        asset_type="floor",
        layer="floor",
        width_cells=8,
        height_cells=8,
    ),
    "floor_tile_256_b": AssetSpec(
        key="floor_tile_256_b",
        asset_type="floor",
        layer="floor",
        width_cells=8,
        height_cells=8,
    ),
    "floor_tile_256_c": AssetSpec(
        key="floor_tile_256_c",
        asset_type="floor",
        layer="floor",
        width_cells=8,
        height_cells=8,
    ),
}

ASSET_ALIASES = {
    "line_64_64_cruz": "line_64x64_cruz",
    "line_64_64_infder.png": "line_64_64_infder",
    "line_64_64_infizq.png": "line_64_64_infizq",
    "line_64_64_supder.png": "line_64_64_supder",
    "line_64_64_supizq.png": "line_64_64_supizq",
}


def normalize_asset_key(asset_key: str) -> str:
    key = str(asset_key).strip().lower()
    return ASSET_ALIASES.get(key, key)


def get_asset_spec(asset_key: str) -> AssetSpec | None:
    return ASSET_CATALOG.get(normalize_asset_key(asset_key))


@dataclass
class Placement:
    """Discrete placement in the world."""

    id: str
    asset_key: str
    x_px: int
    y_px: int
    rotation: int = 0

    def canonical_rotation(self) -> int:
        rotation = int(self.rotation) % 360
        return rotation

    def with_normalized_asset(self) -> "Placement":
        return Placement(
            id=str(self.id),
            asset_key=normalize_asset_key(self.asset_key),
            x_px=int(self.x_px),
            y_px=int(self.y_px),
            rotation=int(self.rotation),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "asset_key": normalize_asset_key(self.asset_key),
            "x": int(self.x_px),
            "y": int(self.y_px),
            "rotation": int(self.rotation),
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Placement":
        return Placement(
            id=str(data.get("id", "")),
            asset_key=normalize_asset_key(str(data.get("asset_key", ""))),
            x_px=int(data.get("x", 0)),
            y_px=int(data.get("y", 0)),
            rotation=int(data.get("rotation", 0)),
        )


@dataclass
class EditorWorldModel:
    """Formal world model for editor operations and persistence."""

    grid_size_px: int = GRID_SIZE_PX
    world_width_cells: int = DEFAULT_WORLD_CELLS
    world_height_cells: int = DEFAULT_WORLD_CELLS
    schema_version: int = SCHEMA_VERSION
    placements: list[Placement] = field(default_factory=list)

    @property
    def world_width_px(self) -> int:
        return int(self.world_width_cells) * int(self.grid_size_px)

    @property
    def world_height_px(self) -> int:
        return int(self.world_height_cells) * int(self.grid_size_px)

    def to_dict(self) -> dict[str, Any]:
        ordered = sorted(
            self.placements,
            key=lambda p: (
                _placement_layer_order(p),
                p.y_px,
                p.x_px,
                str(p.id),
            ),
        )
        return {
            "schema_version": int(self.schema_version),
            "grid_size_px": int(self.grid_size_px),
            "world_width_cells": int(self.world_width_cells),
            "world_height_cells": int(self.world_height_cells),
            "placements": [p.to_dict() for p in ordered],
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "EditorWorldModel":
        raw_placements = data.get("placements", [])
        placements = []
        if isinstance(raw_placements, list):
            for item in raw_placements:
                if isinstance(item, dict):
                    placements.append(Placement.from_dict(item))
        return EditorWorldModel(
            grid_size_px=int(data.get("grid_size_px", GRID_SIZE_PX)),
            world_width_cells=int(data.get("world_width_cells", DEFAULT_WORLD_CELLS)),
            world_height_cells=int(data.get("world_height_cells", DEFAULT_WORLD_CELLS)),
            schema_version=int(data.get("schema_version", SCHEMA_VERSION)),
            placements=placements,
        )


def _placement_layer_order(p: Placement) -> int:
    spec = get_asset_spec(p.asset_key)
    layer = spec.layer if spec else "robot"
    return {
        "floor": 0,
        "zone": 1,
        "line": 2,
        "wall": 3,
        "robot": 4,
    }.get(layer, 4)
