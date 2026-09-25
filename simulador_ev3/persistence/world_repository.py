"""
world_repository.py — Persistencia JSON para el mundo del simulador EV3.

Formato JSON estable:
{
  "version": 1,
  "world": {
    "width_mm": 2000.0,
    "height_mm": 2000.0,
    "surface": {
      "cell_size_mm": 50.0,
      "default_color": "WHITE",
      "cells": [
        {"col": 0, "row": 0, "color": "BLACK", "reflectance": 5.0}
      ]
    },
    "obstacles": [
      {"name": "wall", "vertices": [[100, 100], [200, 100], [200, 200], [100, 200]]}
    ],
    "beacons": [
      {"name": "beacon1", "x_mm": 500.0, "y_mm": 800.0, "channel": 1}
    ]
  }
}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from simulador_ev3.domain.world.beacon_model import BeaconModel
from simulador_ev3.domain.world.obstacle_model import ObstacleModel
from simulador_ev3.domain.world.surface_model import SurfaceColor, SurfaceModel
from simulador_ev3.domain.world.world_model import WorldModel
from simulador_ev3.shared.local_file_security import MAX_WORLD_FILE_BYTES, read_text_limited, write_text_atomically


class WorldRepository:
    """Guarda y carga `WorldModel` desde JSON."""

    FORMAT_VERSION = 1

    @classmethod
    def save(cls, world: WorldModel, path: str | Path) -> Path:
        data = cls.to_dict(world)
        return write_text_atomically(
            path,
            json.dumps(data, indent=2, ensure_ascii=False),
            allowed_suffixes=(".json",),
            max_bytes=MAX_WORLD_FILE_BYTES,
        )

    @classmethod
    def load(cls, path: str | Path) -> WorldModel:
        _, source = read_text_limited(path, allowed_suffixes=(".json",), max_bytes=MAX_WORLD_FILE_BYTES)
        data = json.loads(source)
        return cls.from_dict(data)

    @classmethod
    def to_dict(cls, world: WorldModel) -> dict[str, Any]:
        return {
            "version": cls.FORMAT_VERSION,
            "world": {
                "width_mm": world.width_mm,
                "height_mm": world.height_mm,
                "surface": cls._surface_to_dict(world.surface),
                "obstacles": [cls._obstacle_to_dict(o) for o in world.obstacles],
                "beacons": [cls._beacon_to_dict(b) for b in world.beacons],
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorldModel:
        version = data.get("version")
        if version != cls.FORMAT_VERSION:
            raise ValueError(f"Versión JSON no soportada: {version}")

        world_data = data.get("world") or {}
        surface = cls._surface_from_dict(world_data.get("surface") or {})
        obstacles = [cls._obstacle_from_dict(o) for o in world_data.get("obstacles", [])]
        beacons = [cls._beacon_from_dict(b) for b in world_data.get("beacons", [])]
        return WorldModel(
            width_mm=world_data.get("width_mm", 2000.0),
            height_mm=world_data.get("height_mm", 2000.0),
            surface=surface,
            obstacles=obstacles,
            beacons=beacons,
        )

    @staticmethod
    def _surface_to_dict(surface: SurfaceModel) -> dict[str, Any]:
        cells: list[dict[str, Any]] = []
        for col, row, cell in sorted(surface.iter_defined_cells()):
            cells.append(
                {
                    "col": col,
                    "row": row,
                    "color": cell.color.name,
                    "reflectance": cell.reflectance,
                }
            )
        return {
            "cell_size_mm": surface.cell_size_mm,
            "default_color": surface.default_color.name,
            "cells": cells,
        }

    @staticmethod
    def _surface_from_dict(data: dict[str, Any]) -> SurfaceModel:
        default_color = SurfaceColor[data.get("default_color", "WHITE")]
        surface = SurfaceModel(
            cell_size_mm=data.get("cell_size_mm", 50.0),
            default_color=default_color,
        )
        for item in data.get("cells", []):
            surface.set_cell(
                col=item["col"],
                row=item["row"],
                color=SurfaceColor[item["color"]],
                reflectance=item.get("reflectance"),
            )
        return surface

    @staticmethod
    def _obstacle_to_dict(obstacle: ObstacleModel) -> dict[str, Any]:
        return {
            "name": obstacle.name,
            "vertices": [[x, y] for x, y in obstacle.vertices],
        }

    @staticmethod
    def _obstacle_from_dict(data: dict[str, Any]) -> ObstacleModel:
        vertices = [tuple(v) for v in data.get("vertices", [])]
        return ObstacleModel(vertices=vertices, name=data.get("name", "obstacle"))

    @staticmethod
    def _beacon_to_dict(beacon: BeaconModel) -> dict[str, Any]:
        return {
            "name": beacon.name,
            "x_mm": beacon.x_mm,
            "y_mm": beacon.y_mm,
            "channel": beacon.channel,
        }

    @staticmethod
    def _beacon_from_dict(data: dict[str, Any]) -> BeaconModel:
        return BeaconModel(
            x_mm=data["x_mm"],
            y_mm=data["y_mm"],
            channel=data.get("channel", 1),
            name=data.get("name", "beacon"),
        )
