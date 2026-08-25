"""Flask app factory for the EV3 simulator web UI."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid

from flask import Flask, jsonify
from opentelemetry import trace

from simulador_ev3 import __version__
from simulador_ev3.runtime.isolated_worker import cleanup_worker_temp_dirs
from simulador_ev3.web.config import (
    DefaultWebConfig,
    apply_env_overrides,
    validate_runtime_config,
)
from simulador_ev3.web.errors import WebError
from simulador_ev3.web.file_session_store import FileSessionStore
from simulador_ev3.web.redis_session_store import RedisSessionStore
from simulador_ev3.web.routes import register_blueprints
from simulador_ev3.web.security import ClientRateLimiter, enforce_operational_access, enforce_origin, enforce_rate_limit
from simulador_ev3.web.session_manager import SessionCleanupWorker, SessionManager

logger = logging.getLogger("simulador_ev3.web")
tracer = trace.get_tracer("simulador_ev3.web")


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
    validate_runtime_config(app.config)
    worker_id = os.environ.get("EV3_WEB_WORKER_ID") or f"pid-{os.getpid()}"
    worker_pid = str(os.getpid())
    app.extensions["worker_id"] = worker_id
    app.extensions["worker_pid"] = worker_pid
    app.extensions["operational_metrics"] = {"requests_total": 0, "responses_5xx": 0, "total_duration_ms": 0.0}
    app.extensions["client_rate_limiter"] = ClientRateLimiter(max_keys=int(app.config["RATE_LIMIT_MAX_CLIENTS"]))
    app.extensions["worker_temp_cleanup"] = cleanup_worker_temp_dirs(
        app.config.get("WORKER_TEMP_ROOT"),
        max_age_s=float(app.config.get("WORKER_TEMP_MAX_AGE_S", 3_600)),
    )

    @app.before_request
    def _request_started():
        from flask import g, request

        g.ev3_request_started = time.perf_counter()
        g.ev3_trace_id = request.headers.get("X-Trace-Id") or uuid.uuid4().hex
        span = tracer.start_span("ev3.http_request")
        span.set_attribute("ev3.trace_id", g.ev3_trace_id)
        span.set_attribute("http.request.method", request.method)
        span.set_attribute("url.path", request.path)
        if request.view_args and request.view_args.get("session_id"):
            span.set_attribute("ev3.session_id", request.view_args["session_id"])
        if request.headers.get("X-EV3-Command-Id"):
            span.set_attribute("ev3.command_id", request.headers["X-EV3-Command-Id"])
        g.ev3_span = span

    @app.before_request
    def _security_controls():
        from flask import request

        enforce_operational_access(request, app.config)
        enforce_origin(request)
        enforce_rate_limit(request, app.config, app.extensions["client_rate_limiter"])

    metadata_store = _create_metadata_store(app.config)
    app.extensions["session_metadata_store"] = metadata_store
    session_manager = SessionManager(app.config, metadata_store=metadata_store)
    app.extensions["session_manager"] = session_manager
    app.extensions["shutdown_sessions"] = session_manager.close_all
    app.extensions["session_cleanup_worker"] = None
    if app.config.get("ENABLE_SESSION_CLEANUP_THREAD", True) and not app.config.get("TESTING", False):
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
            "app_version": __version__,
            "fit_padding_ratio": app.config.get("UI_FIT_PADDING_RATIO", 0.05),
            "sensor_beams_enabled": app.config.get("SENSOR_BEAMS_ENABLED", True),
            "sse_enabled": app.config.get("WEB_SSE_ENABLED", True),
            "polling_interval_ms": int(app.config.get("WEB_POLLING_INTERVAL_MS", 250)),
            "session_create_wait_ms": int(app.config.get("WEB_SESSION_CREATE_WAIT_MS", 0)),
        }

    @app.after_request
    def _response_headers(response):
        from flask import g, request

        metrics = app.extensions["operational_metrics"]
        duration_ms = round((time.perf_counter() - getattr(g, "ev3_request_started", time.perf_counter())) * 1000, 3)
        metrics["requests_total"] += 1
        metrics["total_duration_ms"] += duration_ms
        if response.status_code >= 500:
            metrics["responses_5xx"] += 1
        span = getattr(g, "ev3_span", None)
        if span is not None:
            span.set_attribute("http.response.status_code", response.status_code)
            span.end()
        logger.info(
            json.dumps(
                {
                    "event": "http_request",
                    "trace_id": g.ev3_trace_id,
                    "session_id": request.view_args.get("session_id") if request.view_args else None,
                    "command_id": request.headers.get("X-EV3-Command-Id"),
                    "method": request.method,
                    "path": request.path,
                    "status": response.status_code,
                    "duration_ms": duration_ms,
                },
                ensure_ascii=False,
            )
        )
        response.headers.setdefault("X-Worker-Id", worker_id)
        response.headers.setdefault("X-Worker-Pid", worker_pid)
        response.headers.setdefault("X-Trace-Id", g.ev3_trace_id)
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
                "object-src 'none'; "
                "form-action 'self'; "
                "frame-ancestors 'none'",
            )
            if app.config.get("ENABLE_HSTS", False):
                response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response

    @app.errorhandler(WebError)
    def _handle_web_error(exc: WebError):
        response = jsonify({"error": {"code": exc.code, "message": exc.message}})
        retry_after_s = getattr(exc, "retry_after_s", None)
        if retry_after_s is not None:
            try:
                retry_after_int = int(retry_after_s)
            except (TypeError, ValueError):
                retry_after_int = None
            if retry_after_int is not None and retry_after_int > 0:
                response.headers["Retry-After"] = str(retry_after_int)
        return response, exc.status_code

    @app.errorhandler(404)
    def _handle_not_found(_exc):
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Recurso no encontrado."}}), 404

    return app


def main() -> None:
    app = create_app()
    host = os.environ.get("EV3_WEB_HOST", "127.0.0.1")
    port = int(os.environ.get("EV3_WEB_PORT", "5050"))
    # La página abre un stream SSE al iniciar. El servidor de desarrollo debe
    # atenderlo en paralelo a los comandos HTTP (ejecutar, depurar y reiniciar);
    # un único hilo dejaba la UI en ``ready`` con los menús bloqueados.
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
