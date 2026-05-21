"""Example script API routes."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from simulador_ev3.web.routes.helpers import safe_child


bp = Blueprint("api_examples", __name__, url_prefix="/api")


@bp.get("/examples")
def list_examples():
    base = current_app.config["EXAMPLES_DIR"]
    examples = []
    if base.exists():
        for path in sorted(base.glob("*.py")):
            examples.append({"name": path.name, "size": path.stat().st_size})
    return jsonify({"examples": examples})


@bp.get("/examples/<name>")
def get_example(name: str):
    path = safe_child(current_app.config["EXAMPLES_DIR"], name, ".py")
    return jsonify({"name": path.name, "source": path.read_text(encoding="utf-8")})
