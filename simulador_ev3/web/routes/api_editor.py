"""World editor API routes."""

from __future__ import annotations

from flask import Blueprint, jsonify

from simulador_ev3.domain.editor.world_editor_model import MAX_WORLD_CELLS
from simulador_ev3.web.routes.helpers import json_body, require_session
from simulador_ev3.web.services.simulation_session import asset_catalog_dict


bp = Blueprint("api_editor", __name__, url_prefix="/api")


@bp.get("/editor/assets")
def assets():
    return jsonify(asset_catalog_dict())


@bp.get("/sessions/<session_id>/editor/world")
def get_editor_world(session_id: str):
    return jsonify(require_session(session_id).editor_response())


@bp.post("/sessions/<session_id>/editor/world")
def create_editor_world(session_id: str):
    data = json_body()
    if "schema_version" in data and "placements" in data:
        return jsonify(require_session(session_id).load_editor_world(data))
    return jsonify(
        require_session(session_id).create_editor_world(
            data.get("width_cells", MAX_WORLD_CELLS),
            data.get("height_cells", MAX_WORLD_CELLS),
        )
    )


@bp.post("/sessions/<session_id>/editor/world/place")
def place_asset(session_id: str):
    return jsonify(require_session(session_id).place_asset(json_body()))


@bp.post("/sessions/<session_id>/editor/world/move")
def move_asset(session_id: str):
    return jsonify(require_session(session_id).move_asset(json_body()))


@bp.post("/sessions/<session_id>/editor/world/rotate")
def rotate_asset(session_id: str):
    return jsonify(require_session(session_id).rotate_asset(json_body()))


@bp.post("/sessions/<session_id>/editor/world/update")
def update_asset(session_id: str):
    return jsonify(require_session(session_id).update_asset(json_body()))


@bp.post("/sessions/<session_id>/editor/world/duplicate")
def duplicate_asset(session_id: str):
    return jsonify(require_session(session_id).duplicate_asset(json_body()))


@bp.delete("/sessions/<session_id>/editor/world/placements/<asset_id>")
def remove_asset(session_id: str, asset_id: str):
    return jsonify(require_session(session_id).remove_asset(asset_id))


@bp.post("/sessions/<session_id>/editor/world/validate")
def validate_world(session_id: str):
    return jsonify(require_session(session_id).validate_editor_world())


@bp.post("/sessions/<session_id>/editor/world/apply-to-simulation")
def apply_world(session_id: str):
    return jsonify(require_session(session_id).apply_editor_world())


@bp.post("/sessions/<session_id>/editor/world/save")
def save_world(session_id: str):
    data = json_body()
    return jsonify(require_session(session_id).save_editor_world(str(data.get("name", ""))))
