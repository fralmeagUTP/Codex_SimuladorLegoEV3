"""Proyecciones seguras del formato de editor de mundos para las UI."""

from __future__ import annotations

from typing import Any


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
