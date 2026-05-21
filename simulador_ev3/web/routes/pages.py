"""Page routes."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template, send_from_directory

from simulador_ev3.web.errors import InvalidPayload


bp = Blueprint("pages", __name__)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/worlds")
def worlds_page():
    return render_template("worlds.html")


@bp.get("/help")
def help_page():
    return render_template("help.html")


@bp.get("/healthz")
def healthz():
    manager = current_app.extensions["session_manager"]
    return jsonify({"status": "ok", **manager.stats()})


@bp.get("/assets/images/<name>")
def image_asset(name: str):
    if not name or any(part in name for part in ("..", "/", "\\")):
        raise InvalidPayload("Nombre de imagen invalido.")
    if not name.lower().endswith((".png", ".jpg", ".jpeg")):
        raise InvalidPayload("Formato de imagen no permitido.")
    return send_from_directory(current_app.config["IMAGE_ASSETS_DIR"], name)
