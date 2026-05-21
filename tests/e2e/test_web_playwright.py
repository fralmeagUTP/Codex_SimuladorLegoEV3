from __future__ import annotations

import socket
import threading
import json
import re
from contextlib import closing

import pytest
from werkzeug.serving import make_server

from simulador_ev3.web.app import create_app


def _free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture()
def live_web_app(tmp_path):
    worlds_dir = tmp_path / "worlds"
    examples_dir = tmp_path / "examples"
    worlds_dir.mkdir()
    examples_dir.mkdir()
    editor_spec = {
        "schema_version": 1,
        "grid_size_px": 32,
        "world_width_cells": 20,
        "world_height_cells": 20,
        "placements": [
            {
                "id": "robot_0001",
                "asset_key": "robot_ev3_32x32",
                "x": 64,
                "y": 96,
                "rotation": 0,
            }
        ],
    }
    world = {"editor_spec": editor_spec}
    for name in ("01_linea_negra.json", "02_obstaculos_beacon.json", "menu_world.json"):
        (worlds_dir / name).write_text(json.dumps(world), encoding="utf-8")
    examples = {
        "06_siguelineas_basico.py": 'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("linea")\n',
        "05_esquiva_obstaculos.py": 'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("ultra")\n',
        "12_pantalla_altavoz_test.py": 'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("brick")\n',
        "menu_example.py": 'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("menu")\n',
    }
    for name, source in examples.items():
        (examples_dir / name).write_text(source, encoding="utf-8")
    app = create_app(
        {
            "TESTING": True,
            "WORLDS_DIR": worlds_dir,
            "EXAMPLES_DIR": examples_dir,
            "MAX_ACTIVE_SESSIONS": 5,
            "MAX_RUNNING_SIMULATIONS": 3,
            "SCRIPT_MAX_RUNTIME_S": 2.0,
            "SSE_HEARTBEAT_S": 0.1,
            "ENABLE_SESSION_CLEANUP_THREAD": False,
        }
    )
    port = _free_port()
    server = make_server("127.0.0.1", port, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=2)


@pytest.fixture(scope="module")
def playwright_api():
    return pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def browser(playwright_api):
    with playwright_api.sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except playwright_api.Error as exc:
            pytest.skip(f"Playwright Chromium no esta instalado: {exc}")
        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture()
def page(browser):
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        yield page
    finally:
        page.close()


@pytest.fixture()
def expect(playwright_api):
    return playwright_api.expect


def test_simulation_page_runs_default_script(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    expect(page.locator("#sessionStatus")).to_have_text("created")
    expect(page.locator("#worldCanvas")).to_be_visible()
    expect(page.locator("#codeEditor")).to_contain_text("EV3 Web")

    page.locator("#runBtn").click()

    expect(page.locator("#screen")).to_contain_text("EV3 Web", timeout=5000)
    expect(page.locator("#telemetry")).to_contain_text("Tick", timeout=5000)


def test_simulation_menus_load_examples_worlds_and_scenarios(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    expect(page.locator("#examplesMenu")).to_contain_text("menu_example.py")
    page.locator(".menu-trigger", has_text="Ejemplos").hover()
    page.locator("#examplesMenu button", has_text="menu_example.py").click()
    expect(page.locator("#codeEditor")).to_have_value(re.compile("menu"))

    expect(page.locator("#worldsMenu")).to_contain_text("menu_world.json")
    page.locator(".menu-trigger", has_text="Mundos").hover()
    page.locator("#worldsMenu button", has_text="menu_world.json").click()
    expect(page.locator("#worldSelect")).to_have_value("menu_world.json")

    page.locator(".menu-trigger", has_text="Escenarios").hover()
    page.locator("#scenariosMenu button[data-scenario='line']").click()
    expect(page.locator("#codeEditor")).to_have_value(re.compile("linea"), timeout=5000)
    expect(page.locator("#worldSelect")).to_have_value("01_linea_negra.json")
    expect(page.locator("#console")).to_contain_text("Escenario cargado: Seguidor de linea")

    page.locator(".menu-trigger", has_text="Ayuda").hover()
    page.locator("#aboutMenuBtn").click()
    expect(page.locator("#console")).to_contain_text("Simulador EV3 Web")


def test_simulation_gutter_breakpoints_and_robot_start(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    page.locator(".gutter-line[data-line='3']").click()
    expect(page.locator("#breakpointsInput")).to_have_value("3")
    expect(page.locator(".gutter-line[data-line='3']")).to_have_class(re.compile(r"\bhas-breakpoint\b"))

    page.locator("#robotThetaInput").fill("45")
    page.locator("#placeRobotStartBtn").click()
    box = page.locator("#worldCanvas").bounding_box()
    assert box is not None
    page.mouse.move(box["x"] + 180, box["y"] + 150)
    expect(page.locator("#robotStartReadout")).to_contain_text("theta 45")
    page.mouse.click(box["x"] + 180, box["y"] + 150)
    expect(page.locator("#robotStartReadout")).to_contain_text("theta 45")
    expect(page.locator("#console")).to_contain_text("Pose inicial actualizada.")


def test_simulation_editor_auto_pairs_and_indents(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    editor = page.locator("#codeEditor")
    editor.fill("if True:")
    editor.press("End")
    editor.press("Enter")
    editor.type("ev3.screen.print")
    editor.press("(")

    expect(editor).to_have_value(re.compile(r"if True:\n    ev3\.screen\.print\(\)"))
    expect(page.locator("#editorGutter .gutter-line")).to_have_count(2)


def test_simulation_editor_autocomplete_pybricks_context(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    editor = page.locator("#codeEditor")
    editor.fill("from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.")
    editor.press("Control+Space")

    expect(page.locator("#autocompletePopup")).to_be_visible()
    expect(page.locator("#autocompletePopup")).to_contain_text("screen")
    page.locator("#autocompletePopup .autocomplete-item", has_text="screen").click()
    expect(editor).to_have_value(re.compile(r"ev3\.screen$"))

    editor.type(".")
    expect(page.locator("#autocompletePopup")).to_be_visible()
    expect(page.locator("#autocompletePopup")).to_contain_text("print")
    page.locator("#autocompletePopup .autocomplete-item", has_text="print").click()
    expect(editor).to_have_value(re.compile(r"ev3\.screen\.print$"))


def test_simulation_editor_highlights_python_syntax(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    page.locator("#codeEditor").fill(
        "from pybricks.hubs import EV3Brick\n"
        "ev3 = EV3Brick()\n"
        "ev3.screen.print('hola')  # comentario\n"
    )

    expect(page.locator("#syntaxHighlight .syntax-kw", has_text="from")).to_be_visible()
    expect(page.locator("#syntaxHighlight .syntax-builtin", has_text="EV3Brick").first).to_be_visible()
    expect(page.locator("#syntaxHighlight .syntax-string", has_text="'hola'")).to_be_visible()
    expect(page.locator("#syntaxHighlight .syntax-comment", has_text="# comentario")).to_be_visible()


def test_simulation_brick_panel_shows_speaker_state(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    page.locator("#codeEditor").fill(
        "from pybricks.hubs import EV3Brick\n"
        "from pybricks.tools import wait\n"
        "ev3 = EV3Brick()\n"
        "ev3.speaker.beep(880, 1000, 70)\n"
        "wait(100)\n"
    )
    page.locator("#runBtn").click()

    expect(page.locator("#speaker")).to_contain_text("880", timeout=5000)
    expect(page.locator("#speaker")).to_contain_text("vol 70")


def test_world_editor_builds_valid_world_and_exposes_simulation_link(page, live_web_app, expect):
    page.goto(f"{live_web_app}/worlds")

    expect(page.locator("#sessionStatus")).to_have_text("created")
    expect(page.locator("#assetSelect")).to_be_visible()
    expect(page.locator("#worldCanvas")).to_be_visible()

    page.locator("#assetSelect").select_option("robot_ev3_32x32")
    box = page.locator("#worldCanvas").bounding_box()
    assert box is not None
    page.mouse.click(box["x"] + 120, box["y"] + 120)

    expect(page.locator("#selectedAsset")).to_contain_text("robot_ev3_32x32", timeout=5000)
    expect(page.locator("#validationStatus")).to_contain_text("Validacion", timeout=5000)

    page.locator("#saveWorldName").fill("e2e_world")
    page.locator("#saveWorldBtn").click()

    expect(page.locator("#console")).to_contain_text("Mundo guardado: e2e_world.json")
    expect(page.locator("#simulateSavedWorldLink")).to_be_visible()


def test_world_editor_updates_selected_asset_properties(page, live_web_app, expect):
    page.goto(f"{live_web_app}/worlds")

    page.locator("#assetSelect").select_option("wall_64x64_a")
    box = page.locator("#worldCanvas").bounding_box()
    assert box is not None
    page.mouse.click(box["x"] + 120, box["y"] + 120)

    expect(page.locator("#assetPropertiesForm")).to_be_visible()
    page.locator("#assetKeyInput").select_option("line_64_64_hor")
    page.locator("#assetXInput").fill("64")
    page.locator("#assetYInput").fill("96")
    page.locator("#assetRotationInput").fill("180")
    page.locator("#applyAssetPropertiesBtn").click()

    expect(page.locator("#selectedAsset")).to_contain_text("line_64_64_hor", timeout=5000)
    expect(page.locator("#assetProperties")).to_contain_text("64")
    expect(page.locator("#assetProperties")).to_contain_text("96")
    expect(page.locator("#assetProperties")).to_contain_text("180")


def test_world_editor_drags_selected_asset(page, live_web_app, expect):
    page.goto(f"{live_web_app}/worlds")

    page.locator("#assetSelect").select_option("wall_64x64_a")
    box = page.locator("#worldCanvas").bounding_box()
    assert box is not None
    start_x = box["x"] + 120
    start_y = box["y"] + 120
    end_x = box["x"] + 260
    end_y = box["y"] + 190

    page.mouse.click(start_x, start_y)
    expect(page.locator("#selectedAsset")).to_contain_text("wall_64x64_a", timeout=5000)

    page.mouse.move(start_x, start_y)
    page.mouse.down()
    page.mouse.move(end_x, end_y, steps=8)
    page.mouse.up()

    expect(page.locator("#assetProperties")).to_contain_text("X")
    expect(page.locator("#selectedAsset")).to_contain_text("wall_64x64_a", timeout=5000)
    expect(page.locator("#console")).to_contain_text("Mundo valido.", timeout=5000)


def test_help_page_is_available_from_browser(page, live_web_app, expect):
    page.goto(f"{live_web_app}/help")

    expect(page.locator("body")).to_contain_text("Simulacion del robot")
    expect(page.locator("body")).to_contain_text("Creacion de mundos")


def test_two_browser_contexts_keep_sessions_independent(browser, live_web_app, expect):
    context_a = browser.new_context(viewport={"width": 1366, "height": 768})
    context_b = browser.new_context(viewport={"width": 1366, "height": 768})
    page_a = context_a.new_page()
    page_b = context_b.new_page()

    try:
        page_a.goto(f"{live_web_app}/")
        page_b.goto(f"{live_web_app}/")

        expect(page_a.locator("#sessionStatus")).to_have_text("created")
        expect(page_b.locator("#sessionStatus")).to_have_text("created")

        page_a.locator("#codeEditor").fill(
            "from pybricks.hubs import EV3Brick\n"
            "from pybricks.tools import wait\n"
            "ev3 = EV3Brick()\n"
            "ev3.screen.print('perfil A')\n"
            "wait(20)\n"
        )
        page_b.locator("#codeEditor").fill(
            "from pybricks.hubs import EV3Brick\n"
            "from pybricks.tools import wait\n"
            "ev3 = EV3Brick()\n"
            "ev3.screen.print('perfil B')\n"
            "wait(20)\n"
        )

        page_a.locator("#runBtn").click()
        page_b.locator("#runBtn").click()

        expect(page_a.locator("#screen")).to_contain_text("perfil A", timeout=5000)
        expect(page_b.locator("#screen")).to_contain_text("perfil B", timeout=5000)
        expect(page_a.locator("#screen")).not_to_contain_text("perfil B")
        expect(page_b.locator("#screen")).not_to_contain_text("perfil A")
    finally:
        context_a.close()
        context_b.close()
