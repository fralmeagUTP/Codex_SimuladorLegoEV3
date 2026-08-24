"""Proyecciones seguras del formato de editor de mundos para las UI."""

from __future__ import annotations

from typing import Any

from simulador_ev3.domain.editor.world_editor_model import (
    CELL_SIZE_MM,
    GRID_SIZE_PX,
    get_asset_spec,
    normalize_asset_key,
)


def editor_placements(editor_spec: object) -> list[dict[str, Any]]:
    """Normaliza colocaciones visuales sin exponer el JSON crudo a una UI."""

    if not isinstance(editor_spec, dict):
        return []
    raw_placements = editor_spec.get("placements")
    if not isinstance(raw_placements, list):
        return []
    result: list[dict[str, Any]] = []
    for item in raw_placements:
        if not isinstance(item, dict):
            continue
        asset_key = item.get("asset_key")
        if not isinstance(asset_key, str) or not asset_key.strip():
            continue
        result.append(
            {
                "asset_key": asset_key.strip(),
                "x_px": int(item.get("x_px", item.get("x", 0)) or 0),
                "y_px": int(item.get("y_px", item.get("y", 0)) or 0),
                "rotation": int(item.get("rotation", 0) or 0),
            }
        )
    return result


def placement_geometry(
    placement: dict[str, Any], *, grid_size_px: int = GRID_SIZE_PX
) -> dict[str, Any] | None:
    """Proyecta una colocación a geometría canónica del mundo.

    El archivo de mundo conserva posiciones en píxeles del editor. Las UI no
    deben interpretar esos píxeles como coordenadas de pantalla: esta función
    entrega milímetros, dimensiones lógicas, capa y rotación bajo el mismo
    contrato que se publica en ``editor_asset_manifest`` para la Web.
    """

    asset_key = normalize_asset_key(str(placement.get("asset_key", "")))
    spec = get_asset_spec(asset_key)
    if spec is None:
        return None
    rotation = int(placement.get("rotation", 0) or 0) % 360
    width_cells, height_cells = spec.width_cells, spec.height_cells
    if rotation % 180 == 90:
        width_cells, height_cells = height_cells, width_cells
    safe_grid = max(1, int(grid_size_px or GRID_SIZE_PX))
    x_px = int(placement.get("x_px", placement.get("x", 0)) or 0)
    y_px = int(placement.get("y_px", placement.get("y", 0)) or 0)
    mm_per_px = CELL_SIZE_MM / safe_grid
    return {
        "asset_key": asset_key,
        "layer": spec.layer,
        "asset_type": spec.asset_type,
        "rotation": rotation,
        "x_px": x_px,
        "y_px": y_px,
        "x_mm": x_px * mm_per_px,
        "y_mm": y_px * mm_per_px,
        "width_cells": width_cells,
        "height_cells": height_cells,
        "width_mm": width_cells * CELL_SIZE_MM,
        "height_mm": height_cells * CELL_SIZE_MM,
    }
