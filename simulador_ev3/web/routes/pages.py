"""Page routes."""

from __future__ import annotations

from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    send_from_directory,
    url_for,
)

from simulador_ev3.shared.paths import resolve_image_assets_dir
from simulador_ev3.web.errors import InvalidPayload
from simulador_ev3.web.redis_support import redis_runtime_state


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
    return jsonify(
        {
            "status": "ok",
            "worker_id": current_app.extensions.get("worker_id"),
            "worker_pid": current_app.extensions.get("worker_pid"),
            "session_manager": manager.diagnostics(),
            "redis": redis_runtime_state(current_app.config),
            **manager.stats(),
        }
    )


@bp.get("/assets/<name>")
def image_asset(name: str):
    if not name or any(part in name for part in ("..", "/", "\\")):
        raise InvalidPayload("Nombre de imagen invalido.")
    if not name.lower().endswith((".png", ".jpg", ".jpeg")):
        raise InvalidPayload("Formato de imagen no permitido.")

    configured_dir = Path(current_app.config["IMAGE_ASSETS_DIR"])
    if (configured_dir / name).is_file():
        return send_from_directory(configured_dir, name)

    fallback_dir = resolve_image_assets_dir()
    if fallback_dir != configured_dir and (fallback_dir / name).is_file():
        return send_from_directory(fallback_dir, name)

    return send_from_directory(configured_dir, name)


@bp.get("/assets/images/<name>")
def image_asset_legacy(name: str):
    return redirect(url_for("pages.image_asset", name=name), code=308)
