"""Flask app factory for the EV3 simulator web UI."""

from __future__ import annotations

import os

from flask import Flask, jsonify

from simulador_ev3.web.config import DefaultWebConfig, apply_env_overrides
from simulador_ev3.web.errors import WebError
from simulador_ev3.web.file_session_store import FileSessionStore
from simulador_ev3.web.redis_session_store import RedisSessionStore
from simulador_ev3.web.routes import register_blueprints
from simulador_ev3.web.session_manager import SessionCleanupWorker, SessionManager


def _create_metadata_store(config: dict) -> object | None:
    redis_enabled = bool(config.get("REDIS_ENABLED", False))
    if redis_enabled:
        return RedisSessionStore(config)
    if bool(config.get("FILE_MIRROR_ENABLED", True)):
        return FileSessionStore(config)
    return None


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
    worker_id = os.environ.get("EV3_WEB_WORKER_ID") or f"pid-{os.getpid()}"
    worker_pid = str(os.getpid())
    app.extensions["worker_id"] = worker_id
    app.extensions["worker_pid"] = worker_pid

    metadata_store = _create_metadata_store(app.config)
    app.extensions["session_metadata_store"] = metadata_store
    session_manager = SessionManager(app.config, metadata_store=metadata_store)
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

    @app.context_processor
    def _asset_version_context():
        return {
            "asset_version": app.config.get("STATIC_ASSET_VERSION", "dev"),
            "fit_padding_ratio": app.config.get("UI_FIT_PADDING_RATIO", 0.05),
        }

    @app.after_request
    def _response_headers(response):
        response.headers.setdefault("X-Worker-Id", worker_id)
        response.headers.setdefault("X-Worker-Pid", worker_pid)
        if app.config.get("ENABLE_SECURITY_HEADERS", True):
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
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=False)


if __name__ == "__main__":
    main()
