"""World editor API routes."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, current_app, jsonify

from simulador_ev3.domain.editor.world_editor_model import DEFAULT_WORLD_CELLS
from simulador_ev3.web.errors import InvalidPayload
from simulador_ev3.web.routes.helpers import get_manager, json_body, require_session, safe_child
from simulador_ev3.web.services.simulation_session import asset_catalog_dict

bp = Blueprint("api_editor", __name__, url_prefix="/api")

_BUILTIN_WORLD_FILENAMES = frozenset(
    {
        "01_linea_negra_basica.json", "02_linea_negra_v1.json", "03_linea_negra_v2.json",
        "04_linea_negra_v3.json", "05_obstaculos_baliza_ir.json", "06_pasillo_gyro_rumbo.json",
        "07_laberinto_v1.json", "08_laberinto_v2.json", "09_laberinto_v3.json",
        "10_laberinto_v4.json", "11_laberinto_v5.json", "12_radar_ultrasonido_360.json",
    }
)


def _sync_metadata(session_id: str) -> None:
    get_manager().sync_session_metadata(session_id)


@bp.get("/editor/assets")
def assets():
    return jsonify(asset_catalog_dict())


@bp.get("/sessions/<session_id>/editor/world")
def get_editor_world(session_id: str):
    return jsonify(require_session(session_id).editor_response())


@bp.post("/sessions/<session_id>/editor/world")
def create_editor_world(session_id: str):
    data = json_body()
    if (
        ("schema_version" in data and "placements" in data)
        or isinstance(data.get("editor_spec"), dict)
        or isinstance(data.get("editor_objects"), dict)
        or (isinstance(data.get("world"), dict) and "version" in data)
        or all(key in data for key in ("world", "walls", "lines", "zones"))
    ):
        result = require_session(session_id).import_editor_world_payload(data)
        _sync_metadata(session_id)
        return jsonify(result)
    result = require_session(session_id).create_editor_world(
        data.get("width_cells", DEFAULT_WORLD_CELLS),
        data.get("height_cells", DEFAULT_WORLD_CELLS),
    )
    _sync_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/editor/world/resize")
def resize_editor_world(session_id: str):
    data = json_body()
    result = require_session(session_id).resize_editor_world(
        data.get("width_cells", DEFAULT_WORLD_CELLS),
        data.get("height_cells", DEFAULT_WORLD_CELLS),
    )
    _sync_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/editor/world/place")
def place_asset(session_id: str):
    result = require_session(session_id).place_asset(json_body())
    _sync_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/editor/world/move")
def move_asset(session_id: str):
    result = require_session(session_id).move_asset(json_body())
    _sync_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/editor/world/rotate")
def rotate_asset(session_id: str):
    result = require_session(session_id).rotate_asset(json_body())
    _sync_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/editor/world/update")
def update_asset(session_id: str):
    result = require_session(session_id).update_asset(json_body())
    _sync_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/editor/world/duplicate")
def duplicate_asset(session_id: str):
    result = require_session(session_id).duplicate_asset(json_body())
    _sync_metadata(session_id)
    return jsonify(result)


@bp.delete("/sessions/<session_id>/editor/world/placements/<asset_id>")
def remove_asset(session_id: str, asset_id: str):
    result = require_session(session_id).remove_asset(asset_id)
    _sync_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/editor/world/validate")
def validate_world(session_id: str):
    return jsonify(require_session(session_id).validate_editor_world())


@bp.post("/sessions/<session_id>/editor/world/apply-to-simulation")
def apply_world(session_id: str):
    result = require_session(session_id).apply_editor_world()
    _sync_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/editor/world/save")
def save_world(session_id: str):
    data = json_body()
    result = require_session(session_id).save_editor_world(str(data.get("name", "")))
    _sync_metadata(session_id)
    return jsonify(result)


@bp.delete("/sessions/<session_id>/editor/world/save/<name>")
def delete_saved_world(session_id: str, name: str):
    """Elimina un mundo guardado por el usuario, nunca un preestablecido."""
    require_session(session_id)
    if name in _BUILTIN_WORLD_FILENAMES:
        raise InvalidPayload("Los mundos preestablecidos no se pueden eliminar.")
    path = safe_child(Path(current_app.config["WORLDS_DIR"]), name, ".json")
    try:
        path.unlink()
    except OSError as exc:
        raise InvalidPayload(f"No se pudo eliminar el mundo: {exc}") from exc
    _sync_metadata(session_id)
    return jsonify({"status": "deleted", "name": path.name})
