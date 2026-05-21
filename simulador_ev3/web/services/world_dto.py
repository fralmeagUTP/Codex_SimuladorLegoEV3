"""JSON serializers for world objects consumed by the web frontend."""

from __future__ import annotations

from typing import Any

from simulador_ev3.domain.world.world_model import WorldModel


def world_to_dict(world: WorldModel, editor_spec: dict[str, Any] | None = None) -> dict[str, Any]:
    surface_cells: list[dict[str, Any]] = []
    for (col, row), cell in sorted(world.surface._grid.items()):
        surface_cells.append(
            {
                "col": col,
                "row": row,
                "color": cell.color.name,
                "reflectance": cell.reflectance,
            }
        )

    return {
        "width_mm": world.width_mm,
        "height_mm": world.height_mm,
        "surface": {
            "cell_size_mm": world.surface.cell_size_mm,
            "default_color": world.surface.default_color.name,
            "cells": surface_cells,
        },
        "obstacles": [
            {"name": obstacle.name, "vertices": [[x, y] for x, y in obstacle.vertices]}
            for obstacle in world.obstacles
        ],
        "beacons": [
            {
                "name": beacon.name,
                "x_mm": beacon.x_mm,
                "y_mm": beacon.y_mm,
                "channel": beacon.channel,
            }
            for beacon in world.beacons
        ],
        "editor_spec": editor_spec,
    }
