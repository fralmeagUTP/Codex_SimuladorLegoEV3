"""World preset API routes."""

from __future__ import annotations

import json

from flask import Blueprint, current_app, jsonify, request

from simulador_ev3.web.errors import InvalidPayload
from simulador_ev3.web.routes.helpers import json_body, require_session, safe_child


bp = Blueprint("api_worlds", __name__, url_prefix="/api")


@bp.get("/worlds")
def list_worlds():
    base = current_app.config["WORLDS_DIR"]
    worlds = []
    if base.exists():
        for path in sorted(base.glob("*.json")):
            worlds.append({"name": path.name, "size": path.stat().st_size})
    return jsonify({"worlds": worlds})


@bp.get("/worlds/<name>")
def get_world(name: str):
    path = safe_child(current_app.config["WORLDS_DIR"], name, ".json")
    return jsonify({"name": path.name, "data": json.loads(path.read_text(encoding="utf-8"))})


@bp.post("/sessions/<session_id>/world")
def load_world(session_id: str):
    data = json_body()
    name = str(data.get("name", ""))
    return jsonify(require_session(session_id).load_world_name(name))


@bp.post("/sessions/<session_id>/world/blank")
def load_blank_world(session_id: str):
    data = json_body()
    width_cells = data.get("width_cells")
    height_cells = data.get("height_cells")
    return jsonify(
        require_session(session_id).load_blank_world(
            width_cells=width_cells,
            height_cells=height_cells,
        )
    )


@bp.post("/sessions/<session_id>/world/upload")
def upload_world(session_id: str):
    if request.is_json:
        data = json_body()
    elif "file" in request.files:
        raw = request.files["file"].read()
        max_size = int(current_app.config.get("MAX_WORLD_JSON_SIZE_BYTES", 2 * 1024 * 1024))
        if len(raw) > max_size:
            raise InvalidPayload("El mundo excede el tamano maximo permitido.")
        data = json.loads(raw.decode("utf-8"))
    else:
        raise InvalidPayload("Debe enviar JSON o archivo multipart.")
    return jsonify(require_session(session_id).upload_world_json(data))
