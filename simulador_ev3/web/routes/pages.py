"""Page routes."""

from __future__ import annotations

from pathlib import Path

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from simulador_ev3 import __version__
from simulador_ev3.shared.asset_catalog import asset_filename, editor_asset_manifest
from simulador_ev3.shared.help_tutorials import (
    HELP_CATEGORIES,
    HELP_GUIDES,
    HELP_MENU_ACTIONS,
    HELP_REFERENCES,
    HELP_SAFE_EXAMPLES,
    PYBRICKS_GLOSSARY,
    TEACHER_ROUTE,
)
from simulador_ev3.shared.help_visual_manifest import visual_for
from simulador_ev3.shared.interface_catalog import SESSION_STATUS_LABELS
from simulador_ev3.shared.paths import resolve_documentation_path, resolve_image_assets_dir
from simulador_ev3.web.errors import InvalidPayload
from simulador_ev3.web.redis_support import redis_runtime_state

bp = Blueprint("pages", __name__)


@bp.get("/")
def index():
    asset_manifest = editor_asset_manifest()
    return render_template(
        "index.html",
        asset_files={str(item["asset_id"]): str(item["filename"]) for item in asset_manifest},
        asset_manifest=asset_manifest,
        status_labels=SESSION_STATUS_LABELS,
        brand_assets={
            "nyquist": asset_filename("logo-nyquist"),
            "robotica_aplicada": asset_filename("logo-robotica-aplicada"),
            "utp": asset_filename("logo-utp"),
        },
        help_menu_actions={action.identifier: action for action in HELP_MENU_ACTIONS},
    )


@bp.get("/worlds")
def worlds_page():
    return render_template("worlds.html")


@bp.get("/help")
def help_page():
    return render_template(
        "help.html",
        categories=HELP_CATEGORIES,
        guides=HELP_GUIDES,
        guides_by_id={guide.identifier: guide for guide in HELP_GUIDES},
        guide_visuals={guide.identifier: visual_for(guide.identifier) for guide in HELP_GUIDES},
        safe_examples=HELP_SAFE_EXAMPLES,
        references=HELP_REFERENCES,
        glossary=PYBRICKS_GLOSSARY,
        teacher_route=TEACHER_ROUTE,
        destinations={
            "simulation": url_for("pages.index"),
            "worlds": url_for("pages.worlds_page"),
            "debug": url_for("pages.index", help="debug"),
        },
    )


@bp.get("/documentation/<reference_id>")
def documentation_resource(reference_id: str):
    """Entrega únicamente documentos canónicos anunciados por la ayuda compartida."""

    filenames = {reference.identifier: reference.filename for reference in HELP_REFERENCES}
    filename = filenames.get(reference_id)
    if filename is None:
        raise InvalidPayload("Referencia de documentación desconocida.")
    path = resolve_documentation_path(filename)
    return send_from_directory(path.parent, path.name, as_attachment=False)


@bp.get("/operations")
def operations_page():
    return render_template("operations.html")


@bp.get("/healthz")
def healthz():
    if str(current_app.config.get("OPERATIONS_ACCESS_POLICY", "public")).strip().lower() == "public":
        # El healthcheck público confirma disponibilidad sin revelar PIDs,
        # capacidad, almacenes ni topología interna del proceso.
        return jsonify({"status": "ok", "version": __version__})
    manager = current_app.extensions["session_manager"]
    return jsonify(
        {
            "status": "ok",
            "version": __version__,
            "worker_id": current_app.extensions.get("worker_id"),
            "worker_pid": current_app.extensions.get("worker_pid"),
            "session_manager": manager.diagnostics(),
            "redis": redis_runtime_state(current_app.config),
            **manager.stats(),
        }
    )


@bp.get("/metrics")
def metrics():
    values = dict(current_app.extensions["operational_metrics"])
    total = values["requests_total"]
    values["average_duration_ms"] = round(values["total_duration_ms"] / total, 3) if total else 0.0
    if str(current_app.config.get("OPERATIONS_ACCESS_POLICY", "public")).strip().lower() == "public":
        return jsonify(values)
    session_stats = current_app.extensions["session_manager"].stats()
    worker_stats = current_app.extensions["session_manager"].worker_stats()
    wants_prometheus = request.args.get("format") == "prometheus" or "text/plain" in request.headers.get("Accept", "")
    if wants_prometheus:
        payload = "\n".join(
            (
                "# TYPE ev3_http_requests_total counter",
                f"ev3_http_requests_total {values['requests_total']}",
                "# TYPE ev3_http_responses_5xx_total counter",
                f"ev3_http_responses_5xx_total {values['responses_5xx']}",
                "# TYPE ev3_http_request_duration_milliseconds gauge",
                f"ev3_http_request_duration_milliseconds {values['average_duration_ms']}",
                "# TYPE ev3_active_sessions gauge",
                f"ev3_active_sessions {session_stats['active_sessions']}",
                "# TYPE ev3_running_sessions gauge",
                f"ev3_running_sessions {session_stats['running_simulations']}",
                "# TYPE ev3_active_workers gauge",
                f"ev3_active_workers {worker_stats['active_workers']}",
                "# TYPE ev3_worker_memory_bytes gauge",
                f"ev3_worker_memory_bytes {worker_stats['worker_memory_bytes']}",
                "# TYPE ev3_worker_peak_memory_bytes gauge",
                f"ev3_worker_peak_memory_bytes {worker_stats['worker_peak_memory_bytes']}",
                "# TYPE ev3_worker_cpu_seconds gauge",
                f"ev3_worker_cpu_seconds {worker_stats['worker_cpu_seconds']}",
                "# TYPE ev3_worker_event_queue_depth gauge",
                f"ev3_worker_event_queue_depth {worker_stats['worker_event_queue_depth']}",
                "# TYPE ev3_worker_last_tick_total gauge",
                f"ev3_worker_last_tick_total {worker_stats['worker_last_tick_total']}",
                "",
            )
        )
        return Response(payload, mimetype="text/plain; version=0.0.4")
    values.update(session_stats)
    values.update(worker_stats)
    return jsonify(values)


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
