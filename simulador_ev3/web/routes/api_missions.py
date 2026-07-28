"""API del catálogo de misiones locales."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from simulador_ev3.shared.mission_catalog import MissionCatalog

bp = Blueprint("api_missions", __name__, url_prefix="/api/missions")


def _catalog() -> MissionCatalog:
    return MissionCatalog(current_app.config["EXAMPLES_DIR"], current_app.config["WORLDS_DIR"])


@bp.get("")
def list_missions():
    return jsonify({"missions": [mission.to_dict() for mission in _catalog().list_missions()]})


@bp.get("/<identifier>")
def get_mission(identifier: str):
    mission = _catalog().get(identifier)
    if mission is None:
        return jsonify({"error": "Misión no encontrada."}), 404
    return jsonify(mission.to_dict())
