"""Blueprint registration for the web layer."""

from __future__ import annotations

from flask import Flask

from simulador_ev3.web.routes.api_editor import bp as editor_bp
from simulador_ev3.web.routes.api_examples import bp as examples_bp
from simulador_ev3.web.routes.api_simulation import bp as simulation_bp
from simulador_ev3.web.routes.api_worlds import bp as worlds_bp
from simulador_ev3.web.routes.pages import bp as pages_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(pages_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(examples_bp)
    app.register_blueprint(worlds_bp)
    app.register_blueprint(editor_bp)
