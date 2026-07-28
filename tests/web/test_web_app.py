from __future__ import annotations

import json
import re
import threading
import time
from io import BytesIO
from pathlib import Path

import pytest

from simulador_ev3 import __version__
from simulador_ev3.application.world_editor_service import WorldEditorService
from simulador_ev3.web.app import create_app
from simulador_ev3.web.errors import CapacityExceeded
from simulador_ev3.web.session_manager import SessionCleanupWorker, SessionManager
from simulador_ev3.web.wsgi import app as wsgi_app

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def make_client(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "WORLDS_DIR": tmp_path,
            "EXAMPLES_DIR": tmp_path,
            "MAX_ACTIVE_SESSIONS": 5,
            "MAX_RUNNING_SIMULATIONS": 5,
            "SCRIPT_MAX_RUNTIME_S": 2.0,
        }
    )
    return app.test_client()


def make_client_with_config(tmp_path, **config):
    base_config = {
        "TESTING": True,
        "WORLDS_DIR": tmp_path,
        "EXAMPLES_DIR": tmp_path,
        "MAX_ACTIVE_SESSIONS": 5,
        "MAX_RUNNING_SIMULATIONS": 5,
        "SCRIPT_MAX_RUNTIME_S": 2.0,
    }
    base_config.update(config)
    return create_app(base_config).test_client()


def auth_headers(session_data):
    return {"X-Session-Token": session_data["owner_token"]}


def test_index_page_references_existing_static_assets(tmp_path):
    client = make_client(tmp_path)

    res = client.get("/")
    html = res.get_data(as_text=True)
    static_paths = re.findall(r'/(static/[^"\']+)', html)

    assert res.status_code == 200
    assert f'data-ev3-app-version="{__version__}"' in html
    assert static_paths
    for path in static_paths:
        asset = client.get(f"/{path}")
        assert asset.status_code == 200, path


def test_wsgi_entrypoint_exposes_flask_app():
    assert wsgi_app.name == "simulador_ev3.web.app"
    assert "session_manager" in wsgi_app.extensions


def test_testing_app_does_not_start_cleanup_thread(tmp_path):
    client = make_client(tmp_path)

    assert client.application.extensions["session_cleanup_worker"] is None


def test_cleanup_worker_closes_expired_sessions(tmp_path):
    manager = SessionManager(
        {
            "SESSION_IDLE_TIMEOUT_MIN": 0,
            "MAX_ACTIVE_SESSIONS": 5,
            "MAX_RUNNING_SIMULATIONS": 5,
            "SCRIPT_MAX_RUNTIME_S": 0.5,
            "WORLDS_DIR": tmp_path,
            "EXAMPLES_DIR": tmp_path,
        }
    )
    worker = SessionCleanupWorker(manager, interval_s=0.05)
    manager.create_session()

    try:
        worker.start()
        for _ in range(20):
            if manager.stats()["active_sessions"] == 0:
                break
            time.sleep(0.05)
    finally:
        worker.stop()

    assert manager.stats()["active_sessions"] == 0
    assert worker.is_running is False


def test_smoke_web_script_covers_critical_routes():
    script = (PROJECT_ROOT / "scripts" / "smoke_web.ps1").read_text(encoding="utf-8")
    wrapper = (PROJECT_ROOT / "scripts" / "smoke_web.cmd").read_text(encoding="utf-8")

    for expected in (
        "/healthz",
        "/worlds",
        "/static/js/simulation_app.js",
        "/static/js/world_editor_app.js",
        "/api/sessions",
        "/snapshot",
        "/debug/breakpoints",
        "/debug/watches",
        "/debug/step",
        "/debug/continue",
    ):
        assert expected in script
    assert "ExecutionPolicy Bypass" in wrapper


def test_web_scripts_use_safe_default_runtime_limit(tmp_path):
    app = create_app({"TESTING": True, "WORLDS_DIR": tmp_path, "EXAMPLES_DIR": tmp_path})

    assert app.config["SCRIPT_MAX_RUNTIME_S"] == 120.0


def test_production_configuration_rejects_unsafe_defaults(tmp_path):
    with pytest.raises(RuntimeError, match="Configuracion de produccion invalida"):
        create_app(
            {
                "TESTING": True,
                "APP_ENV": "production",
                "WORLDS_DIR": tmp_path,
                "EXAMPLES_DIR": tmp_path,
            }
        )


def test_production_configuration_accepts_required_security_values(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "APP_ENV": "production",
            "SECRET_KEY": "clave-de-produccion-segura-con-32-caracteres",
            "SCRIPT_MAX_RUNTIME_S": 30.0,
            "SESSION_COOKIE_SECURE": True,
            "WORLDS_DIR": tmp_path,
            "EXAMPLES_DIR": tmp_path,
        }
    )

    assert app.config["APP_ENV"] == "production"


def test_environment_config_overrides_defaults(monkeypatch, tmp_path):
    worlds_dir = tmp_path / "worlds_env"
    examples_dir = tmp_path / "examples_env"
    monkeypatch.setenv("EV3_WEB_SECRET_KEY", "secret-from-env")
    monkeypatch.setenv("EV3_WEB_APP_ENV", "development")
    monkeypatch.setenv("EV3_WEB_WORLDS_DIR", str(worlds_dir))
    monkeypatch.setenv("EV3_WEB_EXAMPLES_DIR", str(examples_dir))
    monkeypatch.setenv("EV3_WEB_MAX_ACTIVE_SESSIONS", "7")
    monkeypatch.setenv("EV3_WEB_SCRIPT_MAX_RUNTIME_S", "4.5")
    monkeypatch.setenv("EV3_WEB_SESSION_CLEANUP_INTERVAL_S", "12.5")
    monkeypatch.setenv("EV3_WEB_ENABLE_SESSION_CLEANUP_THREAD", "false")
    monkeypatch.setenv("EV3_WEB_ENABLE_SECURITY_HEADERS", "false")
    monkeypatch.setenv("EV3_WEB_SESSION_COOKIE_SECURE", "true")
    monkeypatch.setenv("EV3_WEB_SESSION_BACKEND", "redis")
    monkeypatch.setenv("EV3_WEB_REDIS_ENABLED", "true")
    monkeypatch.setenv("EV3_WEB_REDIS_URL", "redis://127.0.0.1:6379/0")
    monkeypatch.setenv("EV3_WEB_REDIS_PREFIX", "ev3test")
    monkeypatch.setenv("EV3_WEB_REDIS_CONNECT_TIMEOUT_S", "0.4")
    monkeypatch.setenv("EV3_WEB_REDIS_SOCKET_TIMEOUT_S", "0.4")
    monkeypatch.setenv("EV3_WEB_REDIS_HEALTHCHECK_PING", "true")

    app = create_app({"TESTING": True})

    assert app.config["SECRET_KEY"] == "secret-from-env"
    assert app.config["APP_ENV"] == "development"
    assert app.config["WORLDS_DIR"] == worlds_dir
    assert app.config["EXAMPLES_DIR"] == examples_dir
    assert app.config["MAX_ACTIVE_SESSIONS"] == 7
    assert app.config["SCRIPT_MAX_RUNTIME_S"] == 4.5
    assert app.config["SESSION_CLEANUP_INTERVAL_S"] == 12.5
    assert app.config["ENABLE_SESSION_CLEANUP_THREAD"] is False
    assert app.config["ENABLE_SECURITY_HEADERS"] is False
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.config["SESSION_BACKEND"] == "redis"
    assert app.config["REDIS_ENABLED"] is True
    assert app.config["REDIS_URL"] == "redis://127.0.0.1:6379/0"
    assert app.config["REDIS_PREFIX"] == "ev3test"
    assert app.config["REDIS_CONNECT_TIMEOUT_S"] == 0.4
    assert app.config["REDIS_SOCKET_TIMEOUT_S"] == 0.4
    assert app.config["REDIS_HEALTHCHECK_PING"] is True


def test_healthz_includes_worker_session_and_redis_diagnostics(tmp_path):
    client = make_client(tmp_path)

    res = client.get("/healthz")

    assert res.status_code == 200
    payload = res.get_json()
    assert payload["status"] == "ok"
    assert payload["version"] == __version__
    assert str(payload["worker_id"]).startswith("pid-")
    assert str(payload["worker_pid"]).isdigit()
    assert payload["session_manager"]["session_backend"] == "memory"
    assert payload["session_manager"]["is_redis_primary"] is False
    assert payload["session_manager"]["degraded_to_memory"] is False
    assert payload["session_manager"]["redis_enabled"] is False
    assert "metadata_mirror" in payload["session_manager"]
    assert payload["session_manager"]["metadata_mirror"]["enabled"] is True
    assert payload["session_manager"]["metadata_mirror"]["driver"] == "file"
    assert payload["redis"]["backend"] == "memory"
    assert payload["redis"]["enabled"] is False


def test_metrics_exposes_request_and_latency_counters(tmp_path):
    client = make_client(tmp_path)

    client.get("/healthz")
    response = client.get("/metrics")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["requests_total"] >= 1
    assert payload["responses_5xx"] == 0
    assert payload["average_duration_ms"] >= 0


def test_metrics_supports_prometheus_text_format(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/metrics?format=prometheus")

    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert "ev3_http_requests_total" in response.get_data(as_text=True)
    assert "ev3_active_sessions" in response.get_data(as_text=True)
    assert "ev3_worker_memory_bytes" in response.get_data(as_text=True)


def test_request_trace_id_is_propagated_to_response(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/healthz", headers={"X-Trace-Id": "trace-contract-1"})

    assert response.headers["X-Trace-Id"] == "trace-contract-1"


def test_operations_dashboard_is_available(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/operations")

    assert response.status_code == 200
    assert b"Estado operativo" in response.data


def test_explicit_config_wins_over_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("EV3_WEB_MAX_ACTIVE_SESSIONS", "7")

    app = create_app({"TESTING": True, "MAX_ACTIVE_SESSIONS": 3, "WORLDS_DIR": tmp_path})

    assert app.config["MAX_ACTIVE_SESSIONS"] == 3


def test_security_headers_are_enabled_by_default(tmp_path):
    client = make_client(tmp_path)

    res = client.get("/")

    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert res.headers["Referrer-Policy"] == "same-origin"
    assert "default-src 'self'" in res.headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in res.headers["Content-Security-Policy"]
    assert res.headers["X-Worker-Id"].startswith("pid-")
    assert res.headers["X-Worker-Pid"].isdigit()


def test_security_headers_can_be_disabled(tmp_path):
    client = make_client_with_config(tmp_path, ENABLE_SECURITY_HEADERS=False)

    res = client.get("/")

    assert "X-Content-Type-Options" not in res.headers
    assert "Content-Security-Policy" not in res.headers
    assert res.headers["X-Worker-Id"].startswith("pid-")
    assert res.headers["X-Worker-Pid"].isdigit()


def test_simulation_and_world_editor_pages_are_separate(tmp_path):
    client = make_client(tmp_path)

    simulation = client.get("/").get_data(as_text=True)
    worlds = client.get("/worlds").get_data(as_text=True)
    world_editor_js = client.get("/static/js/world_editor_app.js").get_data(as_text=True)

    assert "simulation_app.js" in simulation
    assert "simulation_app.js?v=" in simulation
    assert "api.js?v=" in simulation
    assert "app.css?v=" in simulation
    assert "world_editor_app.js" not in simulation
    assert 'id="runBtn"' in simulation
    assert 'id="codeEditor"' in simulation
    assert 'id="assetSelect"' not in simulation
    assert 'id="saveWorldBtn"' not in simulation
    assert 'class="window-actions"' not in simulation
    assert 'id="openScriptMenuBtnTop"' not in simulation
    assert 'id="saveScriptMenuBtnTop"' not in simulation
    assert 'class="sim-control-group load-controls"' not in simulation
    assert 'id="exampleSelect"' not in simulation
    assert 'id="worldSelect"' not in simulation
    assert 'id="loadWorldBtn"' not in simulation
    assert 'id="loadWorldFromFileMenuBtn"' in simulation
    assert simulation.index('id="debugRunBtn"') > simulation.index('class="debug-panel"')
    assert simulation.index('id="debugRunBtn"') < simulation.index('for="breakpointsInput"')
    assert simulation.index('id="runBtn"') < simulation.index('id="pauseBtn"')
    assert simulation.index('id="pauseBtn"') < simulation.index('id="resumeBtn"')
    assert simulation.index('id="resumeBtn"') < simulation.index('id="stopBtn"')
    assert 'id="resetBtn"' not in simulation

    assert "world_editor_app.js" in worlds
    assert "world_editor_app.js?v=" in worlds
    assert "api.js?v=" in worlds
    assert "app.css?v=" in worlds
    assert "simulation_app.js" not in worlds
    assert 'id="assetSelect"' in worlds
    assert 'id="assetPropertiesForm"' in worlds
    assert 'id="assetKeyInput"' in worlds
    assert 'id="saveWorldBtn"' in worlds
    assert 'id="exportWorldBtn"' in worlds
    assert 'id="simulateSavedWorldLink"' in worlds
    assert 'id="worldMapZoomInBtn"' in worlds
    assert 'id="worldMapZoomOutBtn"' in worlds
    assert 'id="worldMapZoomResetBtn"' in worlds
    assert 'id="runBtn"' not in worlds
    assert 'id="codeEditor"' not in worlds
    assert "window.EV3Canvas.zoomIn(canvas)" in world_editor_js
    assert "window.EV3Canvas.zoomOut(canvas)" in world_editor_js
    assert "window.EV3Canvas.fitToView(canvas, currentWorld)" in world_editor_js


def test_simulation_page_exposes_tk_style_menus(tmp_path):
    client = make_client(tmp_path)

    html = client.get("/").get_data(as_text=True)

    for expected in (
        'id="newScriptMenuBtn"',
        'id="openScriptMenuBtn"',
        'id="saveScriptMenuBtn"',
        'id="loadWorldFromFileMenuBtn"',
        'id="statusProgram"',
        'id="statusSavePath"',
        'id="editorGutter"',
        'id="syntaxHighlight"',
        'id="autocompletePopup"',
        'class="code-editor-shell"',
        'id="placeRobotStartBtn"',
        'id="robotThetaInput"',
        'id="robotStartReadout"',
        'id="watchesInput"',
        'class="sim-control-group robot-location-controls"',
        'id="speaker"',
        'id="examplesMenu"',
        'id="worldsMenu"',
        'id="scenariosMenu"',
        'data-scenario="line"',
        'data-scenario="ultrasonic"',
        'data-scenario="brick"',
        'id="aboutMenuBtn"',
        'id="scriptFileInput"',
    ):
        assert expected in html

    assert 'class="window-actions"' not in html
    assert 'class="sim-control-group load-controls"' not in html
    assert 'id="exampleSelect"' not in html
    assert 'id="worldSelect"' not in html
    assert 'id="loadWorldBtn"' not in html
    assert html.index('id="debugRunBtn"') > html.index('class="debug-panel"')
    assert html.index('id="debugStepBtn"') < html.index('for="breakpointsInput"')
    assert html.index('id="debugContinueBtn"') < html.index('for="breakpointsInput"')
    assert html.index('id="runBtn"') < html.index('id="pauseBtn"')
    assert html.index('id="pauseBtn"') < html.index('id="resumeBtn"')
    assert html.index('id="resumeBtn"') < html.index('id="stopBtn"')
    assert 'id="resetBtn"' not in html


def test_theme_controls_and_assets_are_available_across_pages(tmp_path):
    client = make_client(tmp_path)

    simulation = client.get("/").get_data(as_text=True)
    worlds = client.get("/worlds").get_data(as_text=True)
    help_page = client.get("/help").get_data(as_text=True)
    css = client.get("/static/css/app.css").get_data(as_text=True)
    theme_js = client.get("/static/js/theme_manager.js")
    menu_js = client.get("/static/js/menu_controller.js")

    assert theme_js.status_code == 200
    assert menu_js.status_code == 200
    assert "data-theme-choice" in simulation
    assert "data-theme-choice" in worlds
    assert "data-theme-select" in help_page
    assert "theme_manager.js?v=" in simulation
    assert "theme_manager.js?v=" in worlds
    assert "theme_manager.js?v=" in help_page
    assert "menu_controller.js?v=" in simulation
    assert "menu_controller.js?v=" in worlds
    assert "closeAll(groups)" in menu_js.get_data(as_text=True)
    assert 'document.addEventListener("click"' in menu_js.get_data(as_text=True)
    assert 'html[data-theme="dark"] body' in css


def test_simulation_js_wires_file_and_scenario_menus(tmp_path):
    client = make_client(tmp_path)

    js = client.get("/static/js/simulation_app.js").get_data(as_text=True)
    api_js = client.get("/static/js/api.js").get_data(as_text=True)
    speaker_audio = client.get("/static/js/speaker_audio.js").get_data(as_text=True)

    for expected in (
        "11_siguelineas_basico.py",
        "15_esquiva_obstaculos.py",
        "02_intro_pantalla_altavoz.py",
        "23_radar_ultrasonido_5grados.py",
        "01_linea_negra_basica.json",
        "05_obstaculos_baliza_ir.json",
        "12_radar_ultrasonido_360.json",
        "downloadScript",
        "showSaveFilePicker",
        "worldFileInput",
        "uploadWorld(file)",
        "Cargar mundo desde tu equipo",
        "scenariosMenu",
        "loadScenario",
        "renderEditorGutter",
        "toggleBreakpoint",
        "currentDebugLine",
        "setRobotStartMode",
        "robotStartPreview",
        "showRobotStartMarker",
        "hideRobotStartMarker",
        "robotStart: robotStartMode ? robotStartPreview : (showRobotStartMarker ? robotStart : null)",
        "window.EV3Canvas.resetTrail(pose)",
        "canvasToWorld",
        "api.setRobotStart",
        "handleEditorEnter",
        "handleEditorTab",
        "indentSelection",
        "unindentSelection",
        "selectedLineRange",
        "handleEditorPairs",
        "insertAtCursor",
        "speaker.duration_ms",
        "autocompleteCandidates",
        "inferVariableTypes",
        "showAutocomplete",
        "applyAutocomplete",
        "updateSyntaxHighlight",
        "handleGlobalShortcuts",
        "event.ctrlKey || event.metaKey",
        'window.addEventListener("keydown", handleGlobalShortcuts, true)',
        "syntax-kw",
        "function updateControlStates()",
        "if (data.debug)",
        "handleDebug(data.debug)",
        "debugPaused",
        "runBtn.disabled = !canStart",
        "pauseBtn.disabled = !isRunning",
        "resumeBtn.disabled = !isEffectivelyPaused",
        'stopBtn.disabled = status === "created"',
        "placeRobotStartBtn.disabled = isBusy",
        "window.EV3Canvas.resetTrail();",
        "latestSnapshot = null",
        "function clearBreakpoints()",
        "function clearDebugState()",
        "watchesInput",
        "setWatches",
        "let executionMenuLocked = false",
        "function updateMenuLockState()",
        "function guardMenuAction()",
        "MENU_LOCK_MESSAGE",
        "executionMenuLocked = true;",
        "executionMenuLocked = false;",
        "if (guardMenuAction()) return;",
    ):
        assert expected in js
    file_input_js = client.get("/static/js/file_input_controller.js").get_data(as_text=True)
    assert "EV3FileInputController.bind" in js
    assert 'input?.addEventListener("change"' in file_input_js
    for expected in ("AudioContext || window.webkitAudioContext", "handleSpeaker", "bindUnlockGesture"):
        assert expected in speaker_audio
    assert "api.createSession()" in js
    lifecycle_js = client.get("/static/js/page_lifecycle_controller.js").get_data(as_text=True)
    assert "EV3PageLifecycleController.bind" in js
    assert "closeSession();" in lifecycle_js
    assert "recoveryFailures" in js
    assert "const configuredPollingIntervalMs = Number.parseInt(" in js
    assert "const POLLING_INTERVAL_MS = Number.isFinite(configuredPollingIntervalMs)" in js
    assert "const SSE_ENABLED =" in js
    assert "setInterval(refreshSnapshot, POLLING_INTERVAL_MS)" in js
    assert "scheduleStreamRetry()" in js
    assert "api.createSession({ reuse: true })" in js
    assert "setInterval(refreshSnapshot, 120)" not in js
    assert "api.openSnapshotStream" in js
    assert "STREAM_BOOTSTRAP_TIMEOUT_MS" in js
    assert "connectionError" in js
    assert "openScriptMenuBtnTop" not in js
    assert "saveScriptMenuBtnTop" not in js
    assert "exampleSelect" not in js
    assert "worldSelect" not in js
    assert "loadWorldBtn" not in js
    assert "closeSessionOnUnload" in api_js
    assert "keepalive: true" in api_js
    assert "SESSION_NOT_FOUND" in api_js
    assert "recoverSession" in api_js
    assert "withSessionPath" in api_js
    assert "MAX_SESSION_RECOVERY_ATTEMPTS = 4" in api_js
    assert "MAX_SESSION_FORBIDDEN_RECOVERY_ATTEMPTS = 1" in api_js
    assert "SESSION_FORBIDDEN" in api_js
    assert "DEFAULT_SESSION_CREATE_WAIT_MS" in api_js
    assert "wait_ms: Math.floor(createWaitMs)" in api_js
    assert "singleFlight(" in api_js
    assert "requestWithPolicy(" in api_js
    assert "timeoutMs: 1200" in api_js
    assert "NETWORK_TIMEOUT" in api_js
    assert "TRANSIENT_HTTP_STATUS" in api_js
    assert "request_id: randomRequestId()" in api_js
    assert "ev3-session-recovered" in api_js
    assert "X-Worker-Id" in api_js
    assert "X-Worker-Pid" in api_js
    assert "lastWorkerInfo" in api_js
    assert 'window.addEventListener("ev3-session-recovered"' in lifecycle_js


def test_simulation_canvas_preserves_physical_world_scale(tmp_path):
    client = make_client(tmp_path)

    js = client.get("/static/js/canvas_world.js").get_data(as_text=True)

    assert "view.widthMm * view.scale" in js
    assert "view.heightMm * view.scale" in js
    assert "scale: BASE_PX_PER_MM * zoom" in js
    assert "const MIN_ZOOM = 0.5" in js
    assert "const MAX_ZOOM = 3.0" in js
    assert "staticLayerCache" in js
    assert "staticWorldLayer" in js
    assert "resetTrail" in js
    assert "trail.length = 0" in js
    assert "TRAIL_TELEPORT_THRESHOLD_MM" in js
    assert "distanceMm(previous, point)" in js
    assert "pane.clientWidth - 24" not in js


def test_world_editor_can_link_saved_world_to_simulation(tmp_path):
    client = make_client(tmp_path)

    worlds = client.get("/worlds").get_data(as_text=True)
    simulation_js = client.get("/static/js/simulation_app.js").get_data(as_text=True)
    editor_js = client.get("/static/js/world_editor_app.js").get_data(as_text=True)

    assert 'id="simulateSavedWorldLink"' in worlds
    assert 'id="saveWorldBtn"' in worlds
    assert 'id="worldNameLabel"' in worlds
    assert "URLSearchParams(window.location.search)" in simulation_js
    assert 'params.get("world")' in simulation_js
    assert "api.saveEditorWorld" in editor_js
    assert "setSimulateSavedWorldLink(savedFileName)" in editor_js
    assert "setActiveWorldName(inferredName)" in editor_js
    assert "api.updateAsset" in editor_js
    assert "dragPlacement" in editor_js
    assert "mousedown" in editor_js
    assert "mouseup" in editor_js
    assert "showSaveFilePicker" in editor_js
    assert "createWritable" in editor_js


def test_canvas_renderer_matches_tkinter_world_scale(tmp_path):
    client = make_client(tmp_path)

    canvas_js = client.get("/static/js/canvas_world.js").get_data(as_text=True)

    assert "const CELL_SIZE_MM = 100" in canvas_js
    assert "const GRID_SIZE_PX = 32" in canvas_js
    assert "const BASE_PX_PER_MM = GRID_SIZE_PX / CELL_SIZE_MM" in canvas_js
    assert "scale: BASE_PX_PER_MM * zoom" in canvas_js
    assert "function syncCanvasWorldSize" in canvas_js
    assert "view.widthMm * view.scale" in canvas_js
    assert "view.heightMm * view.scale" in canvas_js
    assert "function zoomIn(canvas)" in canvas_js
    assert "function zoomOut(canvas)" in canvas_js
    assert "function resetZoom(canvas)" in canvas_js
    assert "function fitToView(canvas, world)" in canvas_js
    assert "canvas.style.width = cssWidth" in canvas_js
    assert "canvas.style.height = cssHeight" in canvas_js
    assert "devicePixelRatio" not in canvas_js
    assert "const DEFAULT_WORLD_MM = 4000" in canvas_js
    assert "ROBOT_WIDTH_MM = 110" in canvas_js
    assert "ROBOT_HEIGHT_MM = 70" in canvas_js
    assert 'getAssetImage("robot_ev3_32x32")' in canvas_js


def test_world_editor_defaults_to_four_meter_world(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    res = client.post(
        f"/api/sessions/{session['session_id']}/editor/world",
        json={},
        headers=headers,
    )

    assert res.status_code == 200


def test_load_blank_world_endpoint_resets_to_empty_editor_spec(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    res = client.post(
        f"/api/sessions/{session['session_id']}/world/blank",
        json={"width_cells": 40, "height_cells": 40},
        headers=headers,
    )

    assert res.status_code == 200
    payload = res.get_json()
    world = payload["world"]
    assert world["width_mm"] == 4000.0
    assert world["height_mm"] == 4000.0
    assert world["editor_spec"]["world_width_cells"] == 40
    assert world["editor_spec"]["world_height_cells"] == 40
    assert world["editor_spec"]["placements"] == []


def test_web_simulation_session_defaults_to_four_meter_world(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    res = client.get(
        f"/api/sessions/{session['session_id']}/stream",
        headers=headers,
        buffered=False,
    )
    stream_iter = iter(res.response)

    world_event = ""
    try:
        for _ in range(8):
            chunk = next(stream_iter).decode("utf-8")
            if "event: world" in chunk:
                world_event = chunk
                break
    finally:
        res.close()

    assert world_event
    assert '"width_mm": 4000.0' in world_event
    assert '"height_mm": 4000.0' in world_event


def test_loading_legacy_oversized_editor_world_keeps_authored_simulation_size(tmp_path):
    legacy_world = {
        "version": 1,
        "world": {
            "width_mm": 8000.0,
            "height_mm": 8000.0,
            "surface": {"cell_size_mm": 12.5, "default_color": "WHITE", "cells": []},
            "obstacles": [],
            "beacons": [],
        },
        "editor_spec": {
            "grid_size_px": 32,
            "world_width_cells": 160,
            "world_height_cells": 160,
            "schema_version": 1,
            "placements": [],
        },
    }
    (tmp_path / "legacy_8m.json").write_text(json.dumps(legacy_world), encoding="utf-8")
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()

    res = client.post(
        f"/api/sessions/{session['session_id']}/world",
        json={"name": "legacy_8m.json"},
        headers=auth_headers(session),
    )

    assert res.status_code == 200
    world = res.get_json()["world"]
    assert world["width_mm"] == 16000.0
    assert world["height_mm"] == 16000.0


def test_ev3_lcd_keeps_original_screen_ratio(tmp_path):
    client = make_client(tmp_path)

    css = client.get("/static/css/app.css").get_data(as_text=True)

    assert ".sim-brick-pane .brick-screen" in css
    assert "width: min(260px, calc(100% - 24px));" in css
    assert "@media (min-height: 940px)" in css
    assert "width: min(356px, calc(100% - 24px));" in css
    assert "@media (max-height: 820px)" in css
    assert "width: min(240px, calc(100% - 24px));" in css
    assert "aspect-ratio: 178 / 128;" in css
    assert "grid-template-columns: minmax(430px, 1.18fr) minmax(300px, 0.82fr);" in css
    assert "grid-template-columns: minmax(220px, 34fr)" in css


def test_simulation_toolbar_groups_are_compact_with_separator(tmp_path):
    client = make_client(tmp_path)

    css = client.get("/static/css/app.css").get_data(as_text=True)

    assert ".sim-control-bar" in css
    assert "justify-content: flex-start;" in css
    assert ".sim-control-bar .robot-location-controls" in css
    assert "border-left: 1px solid #cfd9e6;" in css
    toolbar_block = re.search(
        r"\.sim-control-bar \.robot-location-controls \{(?P<body>.*?)\n\}",
        css,
        re.DOTALL,
    )
    assert toolbar_block is not None
    assert "margin-left: auto;" not in toolbar_block.group("body")


def test_code_panel_header_and_debug_bar_are_compact(tmp_path):
    client = make_client(tmp_path)

    css = client.get("/static/css/app.css").get_data(as_text=True)

    assert ".sim-code-pane .code-header" in css
    assert "min-height: 25px;" in css
    assert "padding: 3px 10px;" in css
    assert ".sim-code-pane .debug-panel" in css
    assert "padding: 4px 10px;" in css
    assert "min-height: 24px;" in css


def test_code_editor_uses_horizontal_scroll_instead_of_wrapping(tmp_path):
    client = make_client(tmp_path)

    css = client.get("/static/css/app.css").get_data(as_text=True)
    editor_block = re.search(
        r"\.syntax-highlight,\n\.sim-code-pane #codeEditor \{(?P<body>.*?)\n\}",
        css,
        re.DOTALL,
    )

    assert editor_block is not None
    body = editor_block.group("body")
    assert "overflow: auto;" in body
    assert "padding: 12px 12px 72px;" in body
    assert "white-space: pre;" in body
    assert "white-space: pre-wrap;" not in body


def test_simulation_workspace_uses_compact_vertical_spacing(tmp_path):
    client = make_client(tmp_path)

    css = client.get("/static/css/app.css").get_data(as_text=True)

    workspace_block = re.search(r"\.sim-workspace \{(?P<body>.*?)\n\}", css, re.DOTALL)
    assert workspace_block is not None
    body = workspace_block.group("body")
    assert "gap: 6px;" in body
    assert "padding: 4px 12px 0;" in body
    assert "grid-template-rows: minmax(0, 1fr) 36px;" in body
    assert "gap: 10px;" not in body
    assert "padding: 8px 12px 0;" not in body


def test_simulation_controls_live_inside_left_column_so_code_starts_top(tmp_path):
    client = make_client(tmp_path)

    html = client.get("/").get_data(as_text=True)
    css = client.get("/static/css/app.css").get_data(as_text=True)

    assert html.index('class="sim-left-column"') < html.index('class="sim-control-bar"')
    assert html.index('class="sim-control-bar"') < html.index('class="sim-panel sim-map-panel"')
    assert html.index('class="sim-panel sim-code-pane"') > html.index('class="sim-panel sim-map-panel"')
    assert "grid-template-rows: auto minmax(300px, 1fr) minmax(230px, 0.62fr);" in css


def test_map_zoom_buttons_are_present_and_wired(tmp_path):
    client = make_client(tmp_path)

    html = client.get("/").get_data(as_text=True)
    js = client.get("/static/js/simulation_app.js").get_data(as_text=True)
    world_controller_js = client.get("/static/js/world_view_controller.js").get_data(as_text=True)
    canvas_js = client.get("/static/js/canvas_world.js").get_data(as_text=True)

    assert 'id="mapZoomInBtn"' in html
    assert 'id="mapZoomOutBtn"' in html
    assert 'id="mapZoomResetBtn"' in html
    assert "EV3WorldViewController.create" in js
    assert "window.EV3Canvas.zoomIn(canvas)" in world_controller_js
    assert "window.EV3Canvas.zoomOut(canvas)" in world_controller_js
    assert "window.EV3Canvas.fitToView(canvas, state.world)" in world_controller_js
    assert "function zoomIn(canvas)" in canvas_js
    assert "function zoomOut(canvas)" in canvas_js
    assert "function resetZoom(canvas)" in canvas_js
    assert "function fitToView(canvas, world)" in canvas_js


def test_telemetry_panel_uses_three_columns_and_brick_robot_state(tmp_path):
    client = make_client(tmp_path)

    html = client.get("/").get_data(as_text=True)
    css = client.get("/static/css/app.css").get_data(as_text=True)
    js = client.get("/static/js/simulation_app.js").get_data(as_text=True)

    assert "TELEMETRÍA DEL ROBOT" in html
    assert "Motores A-B (28%)" in html
    assert "Motores C-D (28%)" in html
    assert "Sensores S1-S4 (26%)" in html
    assert "ROBOT / ESTADO" in html
    assert 'id="motorsAB"' in html
    assert 'id="motorsCD"' in html
    assert "grid-template-columns: minmax(220px, 34fr)" in css
    assert ".telemetry-section:last-child" in css
    assert "renderMotorTelemetry" in js
    assert "renderSensorTelemetry" in js
    assert "readableSensorKey" in js
    assert "JSON.stringify(s.value)" not in js


def test_web_editor_places_assets_like_tkinter_tool_origin(tmp_path):
    client = make_client(tmp_path)

    canvas_js = client.get("/static/js/canvas_world.js").get_data(as_text=True)
    editor_js = client.get("/static/js/world_editor_app.js").get_data(as_text=True)

    assert "function placementOriginForAsset" in canvas_js
    assert "Math.floor(size.w / 2) * gridSize" in canvas_js
    assert "Math.floor(size.h / 2) * gridSize" in canvas_js
    assert "worldWidthPx - widthPx" in canvas_js
    assert "worldHeightPx - heightPx" in canvas_js
    assert "function placementMoveTarget" in canvas_js
    assert "function drawPlacementPreview" in canvas_js
    assert "ctx.setLineDash([2, 2])" in canvas_js
    assert 'ctx.strokeStyle = "#006CFF"' in canvas_js
    assert "placementMoveTarget," in canvas_js
    assert "placementOriginForAsset(assetSelect.value" in editor_js
    assert "placementOriginForAsset(\n        selectedPlacement.asset_key" in editor_js
    assert "placementPreview" in editor_js
    assert "canPreviewPlacement" in editor_js
    assert "offset: { x: x0 - editorPoint.x, y: y0 - editorPoint.y }" in editor_js
    assert "placementMoveTarget(" in editor_js


def test_world_editor_page_references_existing_static_assets(tmp_path):
    client = make_client(tmp_path)

    res = client.get("/worlds")
    html = res.get_data(as_text=True)
    static_paths = re.findall(r'/(static/[^"\']+)', html)

    assert res.status_code == 200
    assert static_paths
    for path in static_paths:
        asset = client.get(f"/{path}")
        assert asset.status_code == 200, path


def test_world_editor_uses_jpg_for_floor_tile_c(tmp_path):
    client = make_client(tmp_path)

    editor_js = client.get("/static/js/world_editor_app.js").get_data(as_text=True)
    image = client.get("/assets/floor_tile_256_c.jpg")

    assert 'floor_tile_256_c: "floor_tile_256_c.jpg"' in editor_js
    assert image.status_code == 200
    assert image.content_type.startswith("image/")


def test_help_page_documents_web_workflows(tmp_path):
    client = make_client(tmp_path)

    res = client.get("/help")
    html = res.get_data(as_text=True)

    assert res.status_code == 200
    for expected in (
        "nyquist.app/simuladorlego",
        "Simulacion del robot",
        "Creacion de mundos",
        "Escenarios",
        "sin escribir nombres ni rutas",
        "no necesitas ejecutar scripts locales",
        "Ctrl+Space",
        "Ubicar robot",
        "altavoz EV3",
        "panel de propiedades",
        "Cargar mundo desde tu equipo",
    ):
        assert expected in html


def test_create_session_returns_id_and_token(tmp_path):
    client = make_client(tmp_path)

    res = client.post("/api/sessions")

    assert res.status_code == 201
    data = res.get_json()
    assert data["session_id"]
    assert data["owner_token"]
    assert data["status"] == "created"


def test_create_session_can_reuse_cookie_session(tmp_path):
    client = make_client(tmp_path)

    first = client.post("/api/sessions").get_json()
    reused = client.post("/api/sessions", json={"reuse": True})

    assert reused.status_code == 200
    assert reused.get_json()["session_id"] == first["session_id"]
    assert client.application.extensions["session_manager"].stats()["active_sessions"] == 1


def test_session_cookie_is_httponly_lax_and_not_secure_by_default(tmp_path):
    client = make_client(tmp_path)

    res = client.post("/api/sessions")
    cookie = res.headers["Set-Cookie"]

    assert "ev3_owner_token=" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert "Secure" not in cookie
    assert any("ev3_session_id=" in item for item in res.headers.getlist("Set-Cookie"))


def test_session_cookie_can_be_marked_secure(tmp_path):
    client = make_client_with_config(tmp_path, SESSION_COOKIE_SECURE=True)

    res = client.post("/api/sessions")

    assert "Secure" in res.headers["Set-Cookie"]


def test_session_token_is_required_for_wrong_token(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()

    res = client.get(
        f"/api/sessions/{session['session_id']}",
        headers={"X-Session-Token": "wrong"},
    )

    assert res.status_code == 403


def test_two_sessions_are_independent(tmp_path):
    client = make_client(tmp_path)
    a = client.post("/api/sessions").get_json()
    b = client.post("/api/sessions").get_json()

    assert a["session_id"] != b["session_id"]

    client.post(
        f"/api/sessions/{a['session_id']}/script",
        json={"source": "x = 1"},
        headers=auth_headers(a),
    )
    info_b = client.get(
        f"/api/sessions/{b['session_id']}",
        headers=auth_headers(b),
    ).get_json()

    assert info_b["has_script"] is False


def test_session_cannot_modify_another_session_with_own_token(tmp_path):
    client = make_client(tmp_path)
    a = client.post("/api/sessions").get_json()
    b = client.post("/api/sessions").get_json()

    res = client.post(
        f"/api/sessions/{a['session_id']}/script",
        json={"source": "x = 1"},
        headers=auth_headers(b),
    )

    assert res.status_code == 403
    assert res.get_json()["error"]["code"] == "SESSION_FORBIDDEN"


def test_active_session_limit_is_enforced(tmp_path):
    manager = SessionManager(
        {
            "SESSION_IDLE_TIMEOUT_MIN": 30,
            "MAX_ACTIVE_SESSIONS": 2,
            "MAX_RUNNING_SIMULATIONS": 5,
            "SCRIPT_MAX_RUNTIME_S": 0.5,
            "WORLDS_DIR": tmp_path,
            "EXAMPLES_DIR": tmp_path,
        }
    )

    manager.create_session()
    manager.create_session()
    with pytest.raises(CapacityExceeded):
        manager.create_session()


def test_api_session_creation_returns_429_at_capacity_without_eviction(tmp_path):
    client = make_client_with_config(tmp_path, MAX_ACTIVE_SESSIONS=2)

    first = client.post("/api/sessions").get_json()
    second = client.post("/api/sessions").get_json()
    third = client.post("/api/sessions")
    manager = client.application.extensions["session_manager"]

    assert third.status_code == 429
    assert third.get_json()["error"]["code"] == "CAPACITY_EXCEEDED"
    assert third.headers.get("Retry-After") == "2"
    assert manager.stats()["active_sessions"] == 2
    assert (
        client.get(
            f"/api/sessions/{first['session_id']}",
            headers=auth_headers(first),
        ).status_code
        == 200
    )
    assert (
        client.get(
            f"/api/sessions/{second['session_id']}",
            headers=auth_headers(second),
        ).status_code
        == 200
    )


def test_api_session_creation_wait_ms_can_queue_until_capacity_frees(tmp_path):
    client = make_client_with_config(tmp_path, MAX_ACTIVE_SESSIONS=1)
    first = client.post("/api/sessions").get_json()
    manager = client.application.extensions["session_manager"]

    def delayed_release():
        time.sleep(0.08)
        manager.close_session(first["session_id"], first["owner_token"])

    releaser = threading.Thread(target=delayed_release, daemon=True)
    releaser.start()
    started_at = time.monotonic()
    second = client.post("/api/sessions", json={"wait_ms": 1200})
    elapsed_s = time.monotonic() - started_at
    releaser.join(timeout=1.0)

    assert second.status_code == 201
    assert elapsed_s >= 0.05
    assert manager.stats()["active_sessions"] == 1


def test_api_session_creation_wait_ms_invalid_payload_returns_400(tmp_path):
    client = make_client_with_config(tmp_path, MAX_ACTIVE_SESSIONS=1)
    client.post("/api/sessions")
    res = client.post("/api/sessions", json={"wait_ms": "abc"})

    assert res.status_code == 400
    assert res.get_json()["error"]["code"] == "INVALID_PAYLOAD"


def test_running_simulation_limit_is_enforced(tmp_path):
    client = make_client_with_config(
        tmp_path,
        MAX_ACTIVE_SESSIONS=3,
        MAX_RUNNING_SIMULATIONS=1,
        SCRIPT_MAX_RUNTIME_S=0.5,
    )
    a = client.post("/api/sessions").get_json()
    b = client.post("/api/sessions").get_json()
    long_script = "from pybricks.tools import wait\nwait(1000)"

    for session in (a, b):
        load = client.post(
            f"/api/sessions/{session['session_id']}/script",
            json={"source": long_script},
            headers=auth_headers(session),
        )
        assert load.status_code == 200

    first_start = client.post(
        f"/api/sessions/{a['session_id']}/start",
        json={},
        headers=auth_headers(a),
    )
    second_start = client.post(
        f"/api/sessions/{b['session_id']}/start",
        json={},
        headers=auth_headers(b),
    )

    try:
        assert first_start.status_code == 200
        assert second_start.status_code == 429
        assert second_start.get_json()["error"]["code"] == "CAPACITY_EXCEEDED"
        assert second_start.headers.get("Retry-After") == "2"
        # Politica actual: no se desaloja otra sesion; se devuelve capacidad excedida.
        assert (
            client.get(
                f"/api/sessions/{a['session_id']}",
                headers=auth_headers(a),
            ).status_code
            == 200
        )
        assert (
            client.get(
                f"/api/sessions/{b['session_id']}",
                headers=auth_headers(b),
            ).status_code
            == 200
        )
    finally:
        client.post(f"/api/sessions/{a['session_id']}/stop", headers=auth_headers(a))
        client.post(f"/api/sessions/{b['session_id']}/stop", headers=auth_headers(b))


def test_load_script_start_and_snapshot(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    res = client.post(
        f"/api/sessions/{session['session_id']}/script",
        json={"source": "x = 1 + 1"},
        headers=headers,
    )
    assert res.status_code == 200

    res = client.post(
        f"/api/sessions/{session['session_id']}/start",
        json={},
        headers=headers,
    )
    assert res.status_code == 200

    time.sleep(0.1)
    snap = client.get(
        f"/api/sessions/{session['session_id']}/snapshot",
        headers=headers,
    ).get_json()
    assert snap["snapshot"]["robot"]

    client.post(f"/api/sessions/{session['session_id']}/stop", headers=headers)


def test_start_endpoint_is_idempotent_per_request_id(tmp_path, monkeypatch):
    client = make_client(tmp_path)
    session_data = client.post("/api/sessions").get_json()
    headers = auth_headers(session_data)
    sid = session_data["session_id"]

    loaded = client.post(
        f"/api/sessions/{sid}/script",
        json={"source": "from pybricks.tools import wait\nwait(200)\n"},
        headers=headers,
    )
    assert loaded.status_code == 200

    manager = client.application.extensions["session_manager"]
    session = manager.get_session(sid, session_data["owner_token"])
    original_start = session.start
    call_count = {"value": 0}

    def counted_start(*, debug=False, step_mode=False):
        call_count["value"] += 1
        return original_start(debug=debug, step_mode=step_mode)

    monkeypatch.setattr(session, "start", counted_start)
    payload = {"request_id": "start-req-001"}

    first = client.post(f"/api/sessions/{sid}/start", json=payload, headers=headers)
    second = client.post(f"/api/sessions/{sid}/start", json=payload, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.get_json()["status"] == "running"
    assert second.get_json()["status"] == "running"
    assert call_count["value"] == 1

    client.post(f"/api/sessions/{sid}/stop", headers=headers)


def test_snapshot_endpoint_accepts_post_for_proxy_compatibility(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    snap_response = client.post(
        f"/api/sessions/{session['session_id']}/snapshot",
        json={},
        headers=headers,
    )

    assert snap_response.status_code == 200
    assert "no-store" in snap_response.headers.get("Cache-Control", "")
    snap = snap_response.get_json()
    assert snap["session_id"] == session["session_id"]


def test_snapshot_contract_has_sequence_and_new_generation_after_reset(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)
    sid = session["session_id"]

    before = client.get(f"/api/sessions/{sid}/snapshot", headers=headers).get_json()
    reset = client.post(f"/api/sessions/{sid}/reset", headers=headers)
    after = client.get(f"/api/sessions/{sid}/snapshot", headers=headers).get_json()

    assert reset.status_code == 200
    assert before["sequence"] >= 0
    assert before["snapshot"]["snapshot_version"] == 1
    assert before["snapshot"]["snapshot_generation"] == 0
    assert after["snapshot"]["snapshot_generation"] == 1


def test_reset_snapshot_is_a_complete_created_state(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)
    sid = session["session_id"]

    client.post(f"/api/sessions/{sid}/reset", headers=headers)
    payload = client.get(f"/api/sessions/{sid}/snapshot", headers=headers).get_json()

    assert payload["status"] == "created"
    assert payload["snapshot"]["status"] == "created"
    assert payload["snapshot"]["tick"] <= 1
    assert payload["snapshot"]["sim_time_s"] <= 0.02


def test_pause_does_not_consume_runtime_timeout_budget(tmp_path):
    client = make_client_with_config(tmp_path, SCRIPT_MAX_RUNTIME_S=1.0)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)
    sid = session["session_id"]

    client.post(
        f"/api/sessions/{sid}/script",
        json={"source": "from pybricks.tools import wait\nwhile True:\n    wait(100)\n"},
        headers=headers,
    )
    start = client.post(f"/api/sessions/{sid}/start", json={}, headers=headers)
    assert start.status_code == 200
    assert start.get_json()["status"] == "running"

    paused = client.post(f"/api/sessions/{sid}/pause", headers=headers)
    assert paused.status_code == 200
    assert paused.get_json()["status"] == "paused"

    time.sleep(1.4)
    snapshot = client.get(f"/api/sessions/{sid}/snapshot", headers=headers).get_json()
    assert snapshot["status"] == "paused"
    assert snapshot["error"] is None

    resumed = client.post(f"/api/sessions/{sid}/resume", headers=headers)
    assert resumed.status_code == 200
    assert resumed.get_json()["status"] == "running"
    client.post(f"/api/sessions/{sid}/stop", headers=headers)


def test_finished_script_updates_web_status_and_preserves_final_brick_state(tmp_path):
    client = make_client_with_config(tmp_path, SCRIPT_MAX_RUNTIME_S=2.0)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    client.post(
        f"/api/sessions/{session['session_id']}/script",
        json={
            "source": (
                "from pybricks.hubs import EV3Brick\n"
                "from pybricks.tools import wait\n"
                "ev3 = EV3Brick()\n"
                "ev3.speaker.beep(880, 1000, 70)\n"
                "wait(100)\n"
            )
        },
        headers=headers,
    )
    client.post(f"/api/sessions/{session['session_id']}/start", json={}, headers=headers)

    status = "running"
    for _ in range(30):
        time.sleep(0.1)
        payload = client.get(
            f"/api/sessions/{session['session_id']}/snapshot",
            headers=headers,
        ).get_json()
        status = payload["status"]
        if status == "finished":
            break

    assert status == "finished"
    assert payload["snapshot"]["brick"]["speaker"]["freq"] == 880


def test_runtime_timeout_is_reported_as_terminal_timed_out_state(tmp_path):
    client = make_client_with_config(tmp_path, SCRIPT_MAX_RUNTIME_S=0.1)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    client.post(
        f"/api/sessions/{session['session_id']}/script",
        json={"source": "from pybricks.tools import wait\nwhile True:\n    wait(10)\n"},
        headers=headers,
    )
    client.post(f"/api/sessions/{session['session_id']}/start", json={}, headers=headers)

    status = "running"
    for _ in range(30):
        time.sleep(0.05)
        payload = client.get(
            f"/api/sessions/{session['session_id']}/snapshot",
            headers=headers,
        ).get_json()
        status = payload["status"]
        if status == "timed_out":
            break

    assert status == "timed_out"
    assert "tiempo maximo" in payload["error"]["error"].lower()


def test_editor_assets_and_validation(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()

    assets = client.get("/api/editor/assets").get_json()
    assert any(item["key"] == "robot_ev3_32x32" for item in assets["assets"])

    res = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/place",
        json={"asset_key": "robot_ev3_32x32", "x": 0, "y": 0, "rotation": 0},
        headers=auth_headers(session),
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["validation"]["valid"] is True


def test_editor_move_rotate_duplicate_and_delete_asset(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    placed = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/place",
        json={"asset_key": "wall_64x64_a", "x": 0, "y": 0, "rotation": 0},
        headers=headers,
    ).get_json()["placement"]

    moved = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/move",
        json={"id": placed["id"], "x": 96, "y": 128},
        headers=headers,
    ).get_json()
    moved_placement = next(item for item in moved["world"]["placements"] if item["id"] == placed["id"])
    assert moved_placement["x"] == 96
    assert moved_placement["y"] == 128

    rotated = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/rotate",
        json={"id": placed["id"], "delta_deg": 90},
        headers=headers,
    ).get_json()
    rotated_placement = next(item for item in rotated["world"]["placements"] if item["id"] == placed["id"])
    assert rotated_placement["rotation"] == 90

    updated = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/update",
        json={
            "id": placed["id"],
            "asset_key": "line_64_64_hor",
            "x": 32,
            "y": 64,
            "rotation": 180,
        },
        headers=headers,
    ).get_json()
    updated_placement = updated["placement"]
    assert updated_placement["asset_key"] == "line_64_64_hor"
    assert updated_placement["x"] == 32
    assert updated_placement["y"] == 64
    assert updated_placement["rotation"] == 180

    duplicated = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/duplicate",
        json={"id": placed["id"]},
        headers=headers,
    ).get_json()
    assert len(duplicated["world"]["placements"]) == 2
    clone = duplicated["placement"]
    assert clone["id"] != placed["id"]

    deleted = client.delete(
        f"/api/sessions/{session['session_id']}/editor/world/placements/{clone['id']}",
        headers=headers,
    ).get_json()
    assert [item["id"] for item in deleted["world"]["placements"]] == [placed["id"]]


def test_editor_rejects_invalid_asset_payloads(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    bad_asset = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/place",
        json={"asset_key": "no_existe", "x": 0, "y": 0},
        headers=headers,
    )
    bad_dimensions = client.post(
        f"/api/sessions/{session['session_id']}/editor/world",
        json={"width_cells": "abc", "height_cells": 20},
        headers=headers,
    )

    assert bad_asset.status_code == 400
    assert bad_dimensions.status_code == 400

    bad_update = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/update",
        json={"id": "missing", "x": 0, "y": 0},
        headers=headers,
    )
    assert bad_update.status_code == 400


def test_apply_editor_world_sets_robot_start(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    client.post(
        f"/api/sessions/{session['session_id']}/editor/world/place",
        json={"asset_key": "robot_ev3_32x32", "x": 64, "y": 96, "rotation": 90},
        headers=headers,
    )
    res = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/apply-to-simulation",
        headers=headers,
    )
    assert res.status_code == 200

    snap = client.get(
        f"/api/sessions/{session['session_id']}/snapshot",
        headers=headers,
    ).get_json()
    assert snap["snapshot"]["robot"]["x_mm"] == 250.0
    assert snap["snapshot"]["robot"]["y_mm"] == 350.0
    assert snap["snapshot"]["robot"]["theta_deg"] == 90.0


def test_import_editor_world(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)
    world = {
        "schema_version": 1,
        "grid_size_px": 32,
        "world_width_cells": 20,
        "world_height_cells": 20,
        "placements": [
            {
                "id": "robot_0001",
                "asset_key": "robot_ev3_32x32",
                "x": 0,
                "y": 0,
                "rotation": 0,
            }
        ],
    }

    res = client.post(
        f"/api/sessions/{session['session_id']}/editor/world",
        json=world,
        headers=headers,
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["world"]["placements"][0]["id"] == "robot_0001"
    assert data["validation"]["valid"] is True


def test_import_wrapped_editor_spec_world(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)
    wrapped_world = {
        "version": 1,
        "world": {"width_mm": 4000.0, "height_mm": 4000.0},
        "editor_spec": {
            "schema_version": 1,
            "grid_size_px": 32,
            "world_width_cells": 40,
            "world_height_cells": 40,
            "placements": [
                {
                    "id": "wall_0001",
                    "asset_key": "wall_64x64_a",
                    "x_px": 0,
                    "y_px": 0,
                    "rotation": 0,
                }
            ],
        },
    }

    res = client.post(
        f"/api/sessions/{session['session_id']}/editor/world",
        json=wrapped_world,
        headers=headers,
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["world"]["world_width_cells"] == 40
    assert data["world"]["world_height_cells"] == 40
    assert data["world"]["placements"][0]["asset_key"] == "wall_64x64_a"
    assert data["validation"]["valid"] is True


def test_import_simulation_world_repository_format_into_editor(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)
    sim_world = {
        "version": 1,
        "world": {
            "width_mm": 2000.0,
            "height_mm": 2000.0,
            "surface": {
                "cell_size_mm": 50.0,
                "default_color": "WHITE",
                "cells": [],
            },
            "obstacles": [
                {
                    "name": "wall_demo",
                    "vertices": [[200, 200], [400, 200], [400, 400], [200, 400]],
                }
            ],
            "beacons": [],
        },
    }

    res = client.post(
        f"/api/sessions/{session['session_id']}/editor/world",
        json=sim_world,
        headers=headers,
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["world"]["world_width_cells"] == 20
    assert data["world"]["world_height_cells"] == 20
    assert data["world"]["placements"]
    assert data["validation"]["valid"] is True


def test_import_line_surface_world_into_editor_without_out_of_bounds(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    cells = [{"col": col, "row": 4, "color": "BLACK", "reflectance": 5.0} for col in range(40)]
    sim_world = {
        "version": 1,
        "world": {
            "width_mm": 2000.0,
            "height_mm": 2000.0,
            "surface": {
                "cell_size_mm": 50.0,
                "default_color": "WHITE",
                "cells": cells,
            },
            "obstacles": [],
            "beacons": [],
        },
    }

    res = client.post(
        f"/api/sessions/{session['session_id']}/editor/world",
        json=sim_world,
        headers=headers,
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["validation"]["valid"] is True
    assert data["validation"]["errors"] == []
    assert len(data["world"]["placements"]) == 10
    assert all(p["asset_key"] == "line_64_64_hor" for p in data["world"]["placements"])


def test_save_editor_world_to_worlds_dir(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    client.post(
        f"/api/sessions/{session['session_id']}/editor/world/place",
        json={"asset_key": "robot_ev3_32x32", "x": 0, "y": 0, "rotation": 0},
        headers=headers,
    )
    res = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/save",
        json={"name": "mundo_prueba"},
        headers=headers,
    )

    assert res.status_code == 200
    assert (tmp_path / "mundo_prueba.json").exists()
    assert res.get_json()["name"] == "mundo_prueba.json"


def test_save_editor_world_rejects_unsafe_name(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()

    res = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/save",
        json={"name": "../bad"},
        headers=auth_headers(session),
    )

    assert res.status_code == 400


def test_save_editor_world_preserves_human_friendly_name(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    client.post(
        f"/api/sessions/{session['session_id']}/editor/world/place",
        json={"asset_key": "robot_ev3_32x32", "x": 0, "y": 0, "rotation": 0},
        headers=headers,
    )
    raw_name = "09 Laberinto v3 Ñ"
    res = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/save",
        json={"name": raw_name},
        headers=headers,
    )

    assert res.status_code == 200
    assert res.get_json()["name"] == f"{raw_name}.json"
    assert (tmp_path / f"{raw_name}.json").exists()


def test_set_robot_start_endpoint_updates_snapshot(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    initial = client.get(
        f"/api/sessions/{session['session_id']}/snapshot",
        headers=headers,
    ).get_json()
    assert initial["snapshot"]["robot"]["x_mm"] != 321.5

    res = client.post(
        f"/api/sessions/{session['session_id']}/robot/start",
        json={"x_mm": 321.5, "y_mm": 654.0, "theta_deg": 45},
        headers=headers,
    )
    assert res.status_code == 200

    snap = client.get(
        f"/api/sessions/{session['session_id']}/snapshot",
        headers=headers,
    ).get_json()
    assert snap["snapshot"]["robot"]["x_mm"] == 321.5
    assert snap["snapshot"]["robot"]["y_mm"] == 654.0
    assert snap["snapshot"]["robot"]["theta_deg"] == 45.0


def test_stream_emits_initial_status_snapshot_and_world(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)
    client.post(
        f"/api/sessions/{session['session_id']}/editor/world",
        headers=headers,
    )

    res = client.get(
        f"/api/sessions/{session['session_id']}/stream",
        headers=headers,
        buffered=False,
    )
    stream_iter = iter(res.response)

    try:
        first = next(stream_iter).decode("utf-8")
        second = next(stream_iter).decode("utf-8")
        third = next(stream_iter).decode("utf-8")
        fourth = next(stream_iter).decode("utf-8")
    finally:
        res.close()

    assert res.status_code == 200
    assert "event: status" in first
    assert '"status": "created"' in first
    assert "event: snapshot" in second
    assert '"robot"' in second
    assert "event: debug_state" in third
    assert '"debug_state": "idle"' in third
    assert "event: world" in fourth
    assert '"editor_spec"' in fourth


def test_stream_uses_configured_heartbeat_interval(tmp_path):
    client = make_client_with_config(tmp_path, SSE_HEARTBEAT_S=0.05)
    session = client.post("/api/sessions").get_json()

    res = client.get(
        f"/api/sessions/{session['session_id']}/stream",
        headers=auth_headers(session),
        buffered=False,
    )
    stream_iter = iter(res.response)

    try:
        first = next(stream_iter).decode("utf-8")
        second = next(stream_iter).decode("utf-8")
        third = next(stream_iter).decode("utf-8")
        fourth = next(stream_iter).decode("utf-8")
        fifth = next(stream_iter).decode("utf-8")
    finally:
        res.close()

    assert res.status_code == 200
    assert "event: status" in first
    assert "event: snapshot" in second
    assert "event: debug_state" in third
    assert "event: world" in fourth
    assert "event: heartbeat" in fifth


def test_debug_breakpoint_pause_and_continue(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    sid = session["session_id"]
    headers = auth_headers(session)

    loaded = client.post(
        f"/api/sessions/{sid}/script",
        json={"source": "x = 1\nx = 2\nx = 3\n"},
        headers=headers,
    )
    breakpoints = client.post(
        f"/api/sessions/{sid}/debug/breakpoints",
        json={"breakpoints": [2]},
        headers=headers,
    )
    started = client.post(
        f"/api/sessions/{sid}/start",
        json={"debug": True},
        headers=headers,
    )

    paused = None
    for _ in range(20):
        payload = client.get(f"/api/sessions/{sid}/snapshot", headers=headers).get_json()
        if payload["debug"] and payload["debug"].get("type") == "paused":
            paused = payload["debug"]
            break
        time.sleep(0.02)

    continued = client.post(f"/api/sessions/{sid}/debug/continue", headers=headers)
    client.post(f"/api/sessions/{sid}/stop", headers=headers)

    assert loaded.status_code == 200
    assert breakpoints.status_code == 200
    assert breakpoints.get_json()["breakpoints"] == [2]
    assert started.status_code == 200
    assert paused is not None
    assert paused["debug_state"] == "paused_breakpoint"
    assert paused["can_continue"] is True
    assert paused["can_step"] is True
    assert paused["line"] == 2
    assert paused["reason"] == "breakpoint"
    assert continued.status_code == 200
    assert continued.get_json()["action"] == "continue"
    assert continued.get_json()["type"] == "command"

    after_continue = client.get(f"/api/sessions/{sid}/snapshot", headers=headers).get_json()
    assert after_continue["debug"].get("type") != "paused"
    assert after_continue["debug"]["debug_state"] in {"running", "stopped"}


def test_debug_step_starts_in_step_mode(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    sid = session["session_id"]
    headers = auth_headers(session)

    client.post(
        f"/api/sessions/{sid}/script",
        json={"source": "x = 1\nx = 2\n"},
        headers=headers,
    )
    started = client.post(
        f"/api/sessions/{sid}/start",
        json={"debug": True, "step_mode": True},
        headers=headers,
    )

    paused = None
    for _ in range(20):
        payload = client.get(f"/api/sessions/{sid}/snapshot", headers=headers).get_json()
        if payload["debug"] and payload["debug"].get("type") == "paused":
            paused = payload["debug"]
            break
        time.sleep(0.02)

    step = client.post(f"/api/sessions/{sid}/debug/step", headers=headers)
    client.post(f"/api/sessions/{sid}/stop", headers=headers)

    assert started.status_code == 200
    assert paused is not None
    assert paused["debug_state"] == "paused_step"
    assert paused["can_continue"] is True
    assert paused["can_step"] is True
    assert paused["reason"] == "step"
    assert step.status_code == 200
    assert step.get_json()["action"] == "step"


def test_snapshot_debug_state_includes_capabilities_and_breakpoints(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    sid = session["session_id"]
    headers = auth_headers(session)

    client.post(
        f"/api/sessions/{sid}/script",
        json={"source": "x = 1\nx = 2\nx = 3\n"},
        headers=headers,
    )
    client.post(
        f"/api/sessions/{sid}/debug/breakpoints",
        json={"breakpoints": [2, 3]},
        headers=headers,
    )
    client.post(
        f"/api/sessions/{sid}/debug/watches",
        json={"watches": ["x + 1", "x * 2", "z_no_existe + 1"]},
        headers=headers,
    )
    client.post(
        f"/api/sessions/{sid}/start",
        json={"debug": True},
        headers=headers,
    )

    payload = None
    debug_context = None
    for _ in range(30):
        snapshot = client.get(f"/api/sessions/{sid}/snapshot", headers=headers).get_json()
        debug = snapshot.get("debug") or {}
        if debug.get("debug_state") == "paused_breakpoint":
            payload = debug
            debug_context = snapshot.get("debug_context") or {}
            break
        time.sleep(0.02)
    client.post(f"/api/sessions/{sid}/stop", headers=headers)

    assert payload is not None
    assert payload["breakpoints"] == [2, 3]
    assert payload["watches"] == ["x + 1", "x * 2", "z_no_existe + 1"]
    assert payload["can_continue"] is True
    assert payload["can_step"] is True
    assert isinstance(payload.get("timestamp"), str)
    assert debug_context.get("line") == payload["line"]
    assert isinstance(debug_context.get("stack"), list)
    assert isinstance(debug_context.get("locals"), dict)
    assert isinstance(debug_context.get("watches"), list)
    watch_values = {item["expr"]: item for item in debug_context["watches"]}
    assert watch_values["x + 1"]["value"] == 2
    assert watch_values["x * 2"]["value"] == 2
    assert watch_values["z_no_existe + 1"]["error"]


def test_debug_breakpoints_reject_invalid_payload(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()

    res = client.post(
        f"/api/sessions/{session['session_id']}/debug/breakpoints",
        json={"breakpoints": "2,3"},
        headers=auth_headers(session),
    )

    assert res.status_code == 400
    assert res.get_json()["error"]["code"] == "INVALID_PAYLOAD"


def test_debug_watches_endpoint_and_validation(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    sid = session["session_id"]
    headers = auth_headers(session)

    valid = client.post(
        f"/api/sessions/{sid}/debug/watches",
        json={"watches": ["distancia < 300", "velocidad * 2"]},
        headers=headers,
    )
    invalid = client.post(
        f"/api/sessions/{sid}/debug/watches",
        json={"watches": "distancia < 300"},
        headers=headers,
    )

    assert valid.status_code == 200
    assert valid.get_json()["watches"] == ["distancia < 300", "velocidad * 2"]
    assert invalid.status_code == 400
    assert invalid.get_json()["error"]["code"] == "INVALID_PAYLOAD"


def test_image_asset_route_serves_robot(tmp_path):
    client = make_client(tmp_path)

    res = client.get("/assets/robot_ev3_32x32.png")

    assert res.status_code == 200
    assert res.content_type.startswith("image/png")


def test_browser_like_world_build_save_load_apply_and_run_flow(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)
    sid = session["session_id"]

    created = client.post(
        f"/api/sessions/{sid}/editor/world",
        json={"width_cells": 20, "height_cells": 20},
        headers=headers,
    )
    assert created.status_code == 200

    for payload in (
        {"asset_key": "floor_tile_256_a", "x": 0, "y": 0, "rotation": 0},
        {"asset_key": "zone_green_128", "x": 160, "y": 0, "rotation": 0},
        {"asset_key": "line_64_64_hor", "x": 0, "y": 224, "rotation": 0},
        {"asset_key": "wall_64x64_a", "x": 320, "y": 320, "rotation": 0},
        {"asset_key": "robot_ev3_32x32", "x": 64, "y": 96, "rotation": 90},
    ):
        placed = client.post(
            f"/api/sessions/{sid}/editor/world/place",
            json=payload,
            headers=headers,
        )
        assert placed.status_code == 200, placed.get_json()

    validation = client.post(
        f"/api/sessions/{sid}/editor/world/validate",
        headers=headers,
    ).get_json()
    assert validation["valid"] is True

    saved = client.post(
        f"/api/sessions/{sid}/editor/world/save",
        json={"name": "flujo_visual"},
        headers=headers,
    )
    assert saved.status_code == 200

    worlds = client.get("/api/worlds").get_json()["worlds"]
    assert any(item["name"] == "flujo_visual.json" for item in worlds)

    loaded = client.post(
        f"/api/sessions/{sid}/world",
        json={"name": "flujo_visual.json"},
        headers=headers,
    )
    assert loaded.status_code == 200
    assert loaded.get_json()["world"]["editor_spec"]["placements"]

    applied = client.post(
        f"/api/sessions/{sid}/editor/world/apply-to-simulation",
        headers=headers,
    )
    assert applied.status_code == 200

    script = (
        "from pybricks.hubs import EV3Brick\n"
        "from pybricks.tools import wait\n"
        "ev3 = EV3Brick()\n"
        "ev3.screen.print('flujo web')\n"
        "wait(20)\n"
    )
    loaded_script = client.post(
        f"/api/sessions/{sid}/script",
        json={"source": script},
        headers=headers,
    )
    started = client.post(
        f"/api/sessions/{sid}/start",
        json={},
        headers=headers,
    )
    time.sleep(0.05)
    snapshot = client.get(f"/api/sessions/{sid}/snapshot", headers=headers).get_json()

    assert loaded_script.status_code == 200
    assert started.status_code == 200
    assert snapshot["snapshot"]["robot"]["theta_deg"] == 90.0
    assert "flujo web" in "\n".join(snapshot["snapshot"]["brick"]["screen"]["lines"])


def test_upload_world_file_loads_user_world_into_session(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    client.post(
        f"/api/sessions/{session['session_id']}/editor/world",
        json={"width_cells": 20, "height_cells": 20},
        headers=headers,
    )
    client.post(
        f"/api/sessions/{session['session_id']}/editor/world/place",
        json={
            "asset_key": "robot_ev3_32x32",
            "x": 64,
            "y": 64,
            "rotation": 90,
        },
        headers=headers,
    )
    saved = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/save",
        json={"name": "mundo_usuario"},
        headers=headers,
    )
    assert saved.status_code == 200

    world_path = tmp_path / "mundo_usuario.json"
    assert world_path.exists()

    res = client.post(
        f"/api/sessions/{session['session_id']}/world/upload",
        data={"file": (BytesIO(world_path.read_bytes()), "mundo_usuario.json")},
        headers=headers,
        content_type="multipart/form-data",
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ready"
    assert data["world"]["editor_spec"]["placements"]


def test_upload_raw_editor_world_file_loads_into_session(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    editor = WorldEditorService()
    editor.reset_formal_world(20, 20)
    raw_editor_world = editor.to_editor_dict()
    world_path = tmp_path / "raw_editor_world.json"
    world_path.write_text(json.dumps(raw_editor_world, ensure_ascii=False, indent=2), encoding="utf-8")

    res = client.post(
        f"/api/sessions/{session['session_id']}/world/upload",
        data={"file": (BytesIO(world_path.read_bytes()), "raw_editor_world.json")},
        headers=headers,
        content_type="multipart/form-data",
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ready"
    assert data["world"]["width_mm"] == 2000.0


def test_load_saved_world_in_new_session_keeps_editor_spec_for_rendering(tmp_path):
    client = make_client(tmp_path)

    author = client.post("/api/sessions").get_json()
    author_headers = auth_headers(author)
    sid_author = author["session_id"]

    client.post(
        f"/api/sessions/{sid_author}/editor/world",
        json={"width_cells": 20, "height_cells": 20},
        headers=author_headers,
    )
    client.post(
        f"/api/sessions/{sid_author}/editor/world/place",
        json={"asset_key": "line_64_64_hor", "x": 0, "y": 0, "rotation": 0},
        headers=author_headers,
    )
    saved = client.post(
        f"/api/sessions/{sid_author}/editor/world/save",
        json={"name": "render_editor_spec"},
        headers=author_headers,
    )
    assert saved.status_code == 200

    viewer = client.post("/api/sessions").get_json()
    viewer_headers = auth_headers(viewer)
    loaded = client.post(
        f"/api/sessions/{viewer['session_id']}/world",
        json={"name": "render_editor_spec.json"},
        headers=viewer_headers,
    )

    assert loaded.status_code == 200
    data = loaded.get_json()
    assert data["world"]["editor_spec"]["placements"]
    assert data["world"]["editor_spec"]["placements"][0]["asset_key"] == "line_64_64_hor"
