"""Flask app factory for the EV3 simulator web UI."""

from __future__ import annotations

import os

from flask import Flask, jsonify

from simulador_ev3.web.config import DefaultWebConfig, apply_env_overrides
from simulador_ev3.web.errors import WebError
from simulador_ev3.web.routes import register_blueprints
from simulador_ev3.web.session_manager import SessionCleanupWorker, SessionManager


def create_app(config: dict | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_object(DefaultWebConfig)
    apply_env_overrides(app.config)
    if config:
        app.config.update(config)

    session_manager = SessionManager(app.config)
    app.extensions["session_manager"] = session_manager
    app.extensions["session_cleanup_worker"] = None
    if (
        app.config.get("ENABLE_SESSION_CLEANUP_THREAD", True)
        and not app.config.get("TESTING", False)
    ):
        cleanup_worker = SessionCleanupWorker(
            session_manager,
            interval_s=float(app.config.get("SESSION_CLEANUP_INTERVAL_S", 60.0)),
        )
        cleanup_worker.start()
        app.extensions["session_cleanup_worker"] = cleanup_worker
    register_blueprints(app)

    @app.after_request
    def _security_headers(response):
        if not app.config.get("ENABLE_SECURITY_HEADERS", True):
            return response
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "connect-src 'self'; "
            "img-src 'self' data:; "
            "script-src 'self'; "
            "style-src 'self'; "
            "base-uri 'self'; "
            "frame-ancestors 'none'",
        )
        return response

    @app.errorhandler(WebError)
    def _handle_web_error(exc: WebError):
        return jsonify({"error": {"code": exc.code, "message": exc.message}}), exc.status_code

    @app.errorhandler(404)
    def _handle_not_found(_exc):
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Recurso no encontrado."}}), 404

    return app


def main() -> None:
    app = create_app()
    host = os.environ.get("EV3_WEB_HOST", "127.0.0.1")
    port = int(os.environ.get("EV3_WEB_PORT", "5050"))
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
