"""Simulation session API routes."""

from __future__ import annotations

import json
import time

from flask import Blueprint, Response, current_app, jsonify, make_response, request, stream_with_context

from simulador_ev3.shared.mission_catalog import MissionCatalog
from simulador_ev3.web.errors import CapacityExceeded, InvalidPayload
from simulador_ev3.web.routes.helpers import get_manager, json_body, request_token, require_session

bp = Blueprint("api_simulation", __name__, url_prefix="/api")


@bp.post("/sessions")
def create_session():
    manager = get_manager()
    data = json_body()
    wait_ms_raw = data.get("wait_ms", 0)
    try:
        wait_ms = int(wait_ms_raw)
    except (TypeError, ValueError) as exc:
        raise InvalidPayload("wait_ms debe ser un entero >= 0.") from exc
    wait_ms = max(0, min(wait_ms, 120000))
    if data.get("reuse", False):
        session_id = request.cookies.get("ev3_session_id")
        owner_token = request_token()
        if session_id and owner_token:
            try:
                session = manager.get_session(session_id, owner_token)
                response = _session_response(
                    session_id=session_id,
                    owner_token=owner_token,
                    status=session.status,
                )
                return response, 200
            except Exception:  # noqa: BLE001
                pass

    try:
        session_id, owner_token = manager.create_session(
            evict_inactive=False,
            wait_timeout_s=float(wait_ms) / 1000.0,
        )
    except CapacityExceeded as exc:
        stats = manager.stats()
        raise CapacityExceeded(
            (
                "Se alcanzo el limite de sesiones activas. "
                f"Activas: {stats['active_sessions']}/{stats['max_active_sessions']}."
            ),
            retry_after_s=2,
        ) from exc
    return (
        _session_response(
            session_id=session_id,
            owner_token=owner_token,
            status="created",
        ),
        201,
    )


def _session_response(*, session_id: str, owner_token: str, status: str):
    response = make_response(
        jsonify(
            {
                "session_id": session_id,
                "owner_token": owner_token,
                "status": status,
            }
        )
    )
    cookie_secure = bool(current_app.config.get("SESSION_COOKIE_SECURE", False))
    response.set_cookie(
        "ev3_owner_token",
        owner_token,
        httponly=True,
        samesite="Lax",
        secure=cookie_secure,
    )
    response.set_cookie(
        "ev3_session_id",
        session_id,
        httponly=True,
        samesite="Lax",
        secure=cookie_secure,
    )
    return response


@bp.delete("/sessions/<session_id>")
def close_session(session_id: str):
    get_manager().close_session(session_id, request_token())
    return jsonify({"status": "closed"})


@bp.get("/sessions/<session_id>")
def session_info(session_id: str):
    session = require_session(session_id)
    return jsonify(session.summary())


@bp.post("/sessions/<session_id>/mission")
def select_mission(session_id: str):
    identifier = str(json_body().get("id", "")).strip()
    mission = MissionCatalog(current_app.config["EXAMPLES_DIR"], current_app.config["WORLDS_DIR"]).get(identifier)
    if mission is None:
        raise InvalidPayload("La misión solicitada no existe.")
    return jsonify(require_session(session_id).select_mission(mission))


@bp.post("/sessions/<session_id>/simulation-profile")
def set_simulation_profile(session_id: str):
    data = json_body()
    profile = data.get("profile")
    calibration = data.get("calibration")
    if not isinstance(profile, str):
        raise InvalidPayload("profile debe ser texto.")
    if calibration is not None and not isinstance(calibration, dict):
        raise InvalidPayload("calibration debe ser un objeto.")
    try:
        result = require_session(session_id).set_simulation_profile(profile, calibration)
    except ValueError as exc:
        raise InvalidPayload(str(exc)) from exc
    return jsonify(result)


@bp.post("/sessions/<session_id>/trace/start")
def start_trace(session_id: str):
    require_session(session_id).start_trace()
    return jsonify({"recording": True})


@bp.post("/sessions/<session_id>/trace/stop")
def stop_trace(session_id: str):
    require_session(session_id).stop_trace()
    return jsonify({"recording": False})


@bp.post("/sessions/<session_id>/tick-step")
def step_tick(session_id: str):
    return jsonify(require_session(session_id).step_tick())


@bp.get("/sessions/<session_id>/trace")
def export_trace(session_id: str):
    format = request.args.get("format", "json").lower()
    try:
        payload = require_session(session_id).export_trace(format)
    except ValueError as exc:
        raise InvalidPayload(str(exc)) from exc
    mimetype = "application/json" if format == "json" else "text/csv"
    return Response(
        payload, mimetype=mimetype, headers={"Content-Disposition": f"attachment; filename=ev3-trace.{format}"}
    )


@bp.post("/sessions/<session_id>/script")
def load_script(session_id: str):
    data = json_body()
    session = require_session(session_id)
    result = session.load_script(str(data.get("source", "")))
    get_manager().sync_session_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/start")
def start(session_id: str):
    manager = get_manager()
    manager.cleanup_expired()
    if not manager.can_start():
        stats = manager.stats()
        raise CapacityExceeded(
            "Se alcanzo el limite de simulaciones activas. "
            f"Activas: {stats['running_simulations']}/{stats['max_running_simulations']}.",
            retry_after_s=2,
        )
    session = require_session(session_id)
    data = json_body()
    request_id = str(data.get("request_id", "")).strip()
    if request_id:
        cached = session.get_start_idempotency(request_id)
        if cached is not None:
            return jsonify(cached)
    result = session.start(
        debug=bool(data.get("debug", False)),
        step_mode=bool(data.get("step_mode", False)),
    )
    if request_id:
        session.remember_start_idempotency(request_id, result)
    manager.sync_session_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/pause")
def pause(session_id: str):
    result = require_session(session_id).pause()
    get_manager().sync_session_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/resume")
def resume(session_id: str):
    result = require_session(session_id).resume()
    get_manager().sync_session_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/stop")
def stop(session_id: str):
    result = require_session(session_id).stop()
    get_manager().sync_session_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/reset")
def reset(session_id: str):
    result = require_session(session_id).reset()
    get_manager().sync_session_metadata(session_id)
    return jsonify(result)


@bp.post("/sessions/<session_id>/runtime-limit")
def set_runtime_limit(session_id: str):
    data = json_body()
    try:
        max_runtime_s = float(data["max_runtime_s"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidPayload("max_runtime_s debe ser un numero valido.") from exc
    return jsonify(require_session(session_id).set_max_runtime_s(max_runtime_s))


@bp.post("/sessions/<session_id>/debug/breakpoints")
def set_debug_breakpoints(session_id: str):
    data = json_body()
    raw_breakpoints = data.get("breakpoints", [])
    if not isinstance(raw_breakpoints, list):
        raise InvalidPayload("breakpoints debe ser una lista de numeros de linea.")
    try:
        breakpoints = {int(line) for line in raw_breakpoints if int(line) > 0}
    except (TypeError, ValueError) as exc:
        raise InvalidPayload("breakpoints debe contener numeros de linea validos.") from exc
    return jsonify(require_session(session_id).set_debug_breakpoints(breakpoints))


@bp.post("/sessions/<session_id>/debug/watches")
def set_debug_watches(session_id: str):
    data = json_body()
    raw_watches = data.get("watches", [])
    if not isinstance(raw_watches, list):
        raise InvalidPayload("watches debe ser una lista de expresiones.")
    watches: list[str] = []
    for item in raw_watches:
        if not isinstance(item, str):
            raise InvalidPayload("watches debe contener solo expresiones de texto.")
        expr = item.strip()
        if not expr:
            continue
        if len(expr) > 200:
            raise InvalidPayload("Cada watch debe tener maximo 200 caracteres.")
        watches.append(expr)
    return jsonify(require_session(session_id).set_debug_watches(watches))


@bp.post("/sessions/<session_id>/debug/continue")
def debug_continue(session_id: str):
    return jsonify(require_session(session_id).debug_continue())


@bp.post("/sessions/<session_id>/debug/step")
def debug_step(session_id: str):
    return jsonify(require_session(session_id).debug_step())


@bp.post("/sessions/<session_id>/robot/start")
def robot_start(session_id: str):
    data = json_body()
    try:
        x_mm = float(data["x_mm"])
        y_mm = float(data["y_mm"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidPayload("x_mm y y_mm son requeridos.") from exc
    theta = data.get("theta_deg")
    theta_deg = float(theta) if theta is not None else None
    result = require_session(session_id).set_robot_start(x_mm, y_mm, theta_deg)
    get_manager().sync_session_metadata(session_id)
    return jsonify(result)


@bp.get("/sessions/<session_id>/snapshot")
@bp.post("/sessions/<session_id>/snapshot")
def snapshot(session_id: str):
    response = jsonify(require_session(session_id).snapshot_response())
    response.headers.setdefault("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
    response.headers.setdefault("Pragma", "no-cache")
    response.headers.setdefault("Expires", "0")
    return response


@bp.get("/sessions/<session_id>/stream")
def stream(session_id: str):
    session = require_session(session_id)
    heartbeat_s = float(current_app.config.get("SSE_HEARTBEAT_S", 15))

    def generate():
        last_sequence = 0
        last_heartbeat = time.monotonic()
        initial = session.snapshot_response()
        yield (f"event: status\ndata: {json.dumps({'status': initial['status']}, ensure_ascii=False)}\n\n")
        if initial.get("snapshot") is not None:
            yield (f"event: snapshot\ndata: {json.dumps(initial['snapshot'], ensure_ascii=False)}\n\n")
        if initial.get("debug") is not None:
            yield (f"event: debug_state\ndata: {json.dumps(initial['debug'], ensure_ascii=False)}\n\n")
        if initial.get("debug_context") is not None:
            yield (f"event: debug_context\ndata: {json.dumps(initial['debug_context'], ensure_ascii=False)}\n\n")
        current_world = session.current_world()
        if current_world is not None:
            yield (f"event: world\ndata: {json.dumps(current_world, ensure_ascii=False)}\n\n")
        while True:
            now = time.monotonic()
            heartbeat_remaining = max(0.0, heartbeat_s - (now - last_heartbeat))
            # Los eventos del worker llegan por una cola multiproceso y no
            # pueden despertar directamente esta condición. Una espera de un
            # segundo retrasaba en la UI el estado terminal y hacía que el
            # reloj de pared pareciera más lento que la simulación. Limitar el
            # sondeo del stream a 50 ms mantiene la entrega fluida sin busy
            # waiting: la condición sigue bloqueada entre comprobaciones.
            wait_timeout = min(heartbeat_remaining, 0.05) if heartbeat_remaining > 0 else 0.0
            events = session.wait_for_events_since(last_sequence, timeout_s=wait_timeout)
            if events:
                for event in events:
                    last_sequence = max(last_sequence, int(event["sequence"]))
                    yield (f"event: {event['type']}\ndata: {json.dumps(event['payload'], ensure_ascii=False)}\n\n")
                continue
            if time.monotonic() - last_heartbeat >= heartbeat_s:
                last_heartbeat = time.monotonic()
                yield "event: heartbeat\ndata: {}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")
