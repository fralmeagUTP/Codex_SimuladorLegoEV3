from __future__ import annotations

import re
import time
from pathlib import Path

from simulador_ev3.web.app import create_app
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
        "/debug/step",
        "/debug/continue",
    ):
        assert expected in script
    assert "ExecutionPolicy Bypass" in wrapper


def test_environment_config_overrides_defaults(monkeypatch, tmp_path):
    worlds_dir = tmp_path / "worlds_env"
    examples_dir = tmp_path / "examples_env"
    monkeypatch.setenv("EV3_WEB_SECRET_KEY", "secret-from-env")
    monkeypatch.setenv("EV3_WEB_WORLDS_DIR", str(worlds_dir))
    monkeypatch.setenv("EV3_WEB_EXAMPLES_DIR", str(examples_dir))
    monkeypatch.setenv("EV3_WEB_MAX_ACTIVE_SESSIONS", "7")
    monkeypatch.setenv("EV3_WEB_SCRIPT_MAX_RUNTIME_S", "4.5")
    monkeypatch.setenv("EV3_WEB_SESSION_CLEANUP_INTERVAL_S", "12.5")
    monkeypatch.setenv("EV3_WEB_ENABLE_SESSION_CLEANUP_THREAD", "false")
    monkeypatch.setenv("EV3_WEB_ENABLE_SECURITY_HEADERS", "false")
    monkeypatch.setenv("EV3_WEB_SESSION_COOKIE_SECURE", "true")

    app = create_app({"TESTING": True})

    assert app.config["SECRET_KEY"] == "secret-from-env"
    assert app.config["WORLDS_DIR"] == worlds_dir
    assert app.config["EXAMPLES_DIR"] == examples_dir
    assert app.config["MAX_ACTIVE_SESSIONS"] == 7
    assert app.config["SCRIPT_MAX_RUNTIME_S"] == 4.5
    assert app.config["SESSION_CLEANUP_INTERVAL_S"] == 12.5
    assert app.config["ENABLE_SESSION_CLEANUP_THREAD"] is False
    assert app.config["ENABLE_SECURITY_HEADERS"] is False
    assert app.config["SESSION_COOKIE_SECURE"] is True


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


def test_security_headers_can_be_disabled(tmp_path):
    client = make_client_with_config(tmp_path, ENABLE_SECURITY_HEADERS=False)

    res = client.get("/")

    assert "X-Content-Type-Options" not in res.headers
    assert "Content-Security-Policy" not in res.headers


def test_simulation_and_world_editor_pages_are_separate(tmp_path):
    client = make_client(tmp_path)

    simulation = client.get("/").get_data(as_text=True)
    worlds = client.get("/worlds").get_data(as_text=True)

    assert "simulation_app.js" in simulation
    assert "world_editor_app.js" not in simulation
    assert 'id="runBtn"' in simulation
    assert 'id="codeEditor"' in simulation
    assert 'id="assetSelect"' not in simulation
    assert 'id="saveWorldBtn"' not in simulation

    assert "world_editor_app.js" in worlds
    assert "simulation_app.js" not in worlds
    assert 'id="assetSelect"' in worlds
    assert 'id="assetPropertiesForm"' in worlds
    assert 'id="assetKeyInput"' in worlds
    assert 'id="saveWorldBtn"' in worlds
    assert 'id="simulateSavedWorldLink"' in worlds
    assert 'id="runBtn"' not in worlds
    assert 'id="codeEditor"' not in worlds


def test_simulation_page_exposes_tk_style_menus(tmp_path):
    client = make_client(tmp_path)

    html = client.get("/").get_data(as_text=True)

    for expected in (
        'id="newScriptMenuBtn"',
        'id="openScriptMenuBtn"',
        'id="saveScriptMenuBtn"',
        'id="editorGutter"',
        'id="syntaxHighlight"',
        'id="autocompletePopup"',
        'class="code-editor-shell"',
        'id="placeRobotStartBtn"',
        'id="robotThetaInput"',
        'id="robotStartReadout"',
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


def test_simulation_js_wires_file_and_scenario_menus(tmp_path):
    client = make_client(tmp_path)

    js = client.get("/static/js/simulation_app.js").get_data(as_text=True)

    for expected in (
        "06_siguelineas_basico.py",
        "05_esquiva_obstaculos.py",
        "12_pantalla_altavoz_test.py",
        "01_linea_negra.json",
        "02_obstaculos_beacon.json",
        "downloadScript",
        "scriptFileInput.addEventListener",
        "scenariosMenu",
        "loadScenario",
        "renderEditorGutter",
        "toggleBreakpoint",
        "currentDebugLine",
        "setRobotStartMode",
        "robotStartPreview",
        "canvasToWorld",
        "api.setRobotStart",
        "handleEditorEnter",
        "handleEditorPairs",
        "insertAtCursor",
        "speaker.duration_ms",
        "autocompleteCandidates",
        "inferVariableTypes",
        "showAutocomplete",
        "applyAutocomplete",
        "updateSyntaxHighlight",
        "syntax-kw",
    ):
        assert expected in js


def test_world_editor_can_link_saved_world_to_simulation(tmp_path):
    client = make_client(tmp_path)

    worlds = client.get("/worlds").get_data(as_text=True)
    simulation_js = client.get("/static/js/simulation_app.js").get_data(as_text=True)
    editor_js = client.get("/static/js/world_editor_app.js").get_data(as_text=True)

    assert 'id="simulateSavedWorldLink"' in worlds
    assert "URLSearchParams(window.location.search)" in simulation_js
    assert 'params.get("world")' in simulation_js
    assert "`/?world=${encodeURIComponent(result.name)}`" in editor_js
    assert "api.updateAsset" in editor_js
    assert "dragPlacement" in editor_js
    assert "mousedown" in editor_js
    assert "mouseup" in editor_js


def test_canvas_renderer_matches_tkinter_world_scale(tmp_path):
    client = make_client(tmp_path)

    canvas_js = client.get("/static/js/canvas_world.js").get_data(as_text=True)

    assert "const CELL_SIZE_MM = 100" in canvas_js
    assert "const GRID_SIZE_PX = 32" in canvas_js
    assert "const PX_PER_MM = GRID_SIZE_PX / CELL_SIZE_MM" in canvas_js
    assert "scale: PX_PER_MM" in canvas_js
    assert "function syncCanvasWorldSize" in canvas_js
    assert "view.widthMm * PX_PER_MM" in canvas_js
    assert "view.heightMm * PX_PER_MM" in canvas_js
    assert "canvas.style.width = cssWidth" in canvas_js
    assert "canvas.style.height = cssHeight" in canvas_js
    assert "devicePixelRatio" not in canvas_js
    assert "ROBOT_WIDTH_MM = 32 / PX_PER_MM" in canvas_js
    assert "ROBOT_HEIGHT_MM = 23 / PX_PER_MM" in canvas_js


def test_ev3_lcd_keeps_original_screen_ratio(tmp_path):
    client = make_client(tmp_path)

    css = client.get("/static/css/app.css").get_data(as_text=True)

    assert ".sim-brick-pane .brick-screen" in css
    assert "width: min(260px, calc(100% - 24px));" in css
    assert "@media (min-height: 940px)" in css
    assert "width: min(356px, calc(100% - 24px));" in css
    assert "aspect-ratio: 178 / 128;" in css
    assert "grid-template-columns: minmax(430px, 1.18fr) minmax(300px, 0.82fr);" in css
    assert "grid-template-columns: repeat(3, minmax(120px, 1fr));" in css


def test_telemetry_panel_uses_three_readable_columns(tmp_path):
    client = make_client(tmp_path)

    html = client.get("/").get_data(as_text=True)
    css = client.get("/static/css/app.css").get_data(as_text=True)

    assert "<h3>Robot</h3>" in html
    assert "<h3>Motores</h3>" in html
    assert "<h3>Sensores</h3>" in html
    assert "grid-template-columns: repeat(3, minmax(120px, 1fr));" in css
    assert ".telemetry-section:last-child" in css


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
    assert "placementMoveTarget," in canvas_js
    assert "placementOriginForAsset(assetSelect.value" in editor_js
    assert "placementOriginForAsset(\n        selectedPlacement.asset_key" in editor_js
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
    image = client.get("/assets/images/floor_tile_256_c.jpg")

    assert 'floor_tile_256_c: "floor_tile_256_c.jpg"' in editor_js
    assert image.status_code == 200
    assert image.content_type.startswith("image/")


def test_help_page_documents_web_workflows(tmp_path):
    client = make_client(tmp_path)

    res = client.get("/help")
    html = res.get_data(as_text=True)

    assert res.status_code == 200
    for expected in (
        "Simulacion del robot",
        "Creacion de mundos",
        "Escenarios",
        "Ctrl+Space",
        "Ubicar robot",
        "altavoz EV3",
        "panel de propiedades",
        "/?world=prueba_lineas.json",
        "start_web.cmd",
        "restart_web.cmd",
        "stop_web.cmd",
        "smoke_web.cmd",
        "start_web_waitress.cmd",
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


def test_session_cookie_is_httponly_lax_and_not_secure_by_default(tmp_path):
    client = make_client(tmp_path)

    res = client.post("/api/sessions")
    cookie = res.headers["Set-Cookie"]

    assert "ev3_owner_token=" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert "Secure" not in cookie


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
    client = make_client_with_config(tmp_path, MAX_ACTIVE_SESSIONS=2)

    assert client.post("/api/sessions").status_code == 201
    assert client.post("/api/sessions").status_code == 201
    res = client.post("/api/sessions")

    assert res.status_code == 429
    assert res.get_json()["error"]["code"] == "CAPACITY_EXCEEDED"


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
    finally:
        client.post(f"/api/sessions/{a['session_id']}/stop", headers=auth_headers(a))


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


def test_finished_script_updates_web_status_to_stopped(tmp_path):
    client = make_client_with_config(tmp_path, SCRIPT_MAX_RUNTIME_S=2.0)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

    client.post(
        f"/api/sessions/{session['session_id']}/script",
        json={"source": "from pybricks.tools import wait\nwait(100)\n"},
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
        if status == "stopped":
            break

    assert status == "stopped"


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
    moved_placement = next(
        item for item in moved["world"]["placements"] if item["id"] == placed["id"]
    )
    assert moved_placement["x"] == 96
    assert moved_placement["y"] == 128

    rotated = client.post(
        f"/api/sessions/{session['session_id']}/editor/world/rotate",
        json={"id": placed["id"], "delta_deg": 90},
        headers=headers,
    ).get_json()
    rotated_placement = next(
        item for item in rotated["world"]["placements"] if item["id"] == placed["id"]
    )
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


def test_set_robot_start_endpoint_updates_snapshot(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()
    headers = auth_headers(session)

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
    finally:
        res.close()

    assert res.status_code == 200
    assert "event: status" in first
    assert '"status": "created"' in first
    assert "event: snapshot" in second
    assert '"robot"' in second
    assert "event: world" in third
    assert '"editor_spec"' in third


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
    finally:
        res.close()

    assert res.status_code == 200
    assert "event: status" in first
    assert "event: snapshot" in second
    assert "event: world" in third
    assert "event: heartbeat" in fourth


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
    assert paused["line"] == 2
    assert paused["reason"] == "breakpoint"
    assert continued.status_code == 200
    assert continued.get_json()["action"] == "continue"


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
    assert paused["reason"] == "step"
    assert step.status_code == 200
    assert step.get_json()["action"] == "step"


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


def test_image_asset_route_serves_robot(tmp_path):
    client = make_client(tmp_path)

    res = client.get("/assets/images/robot_ev3_32x32.png")

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
