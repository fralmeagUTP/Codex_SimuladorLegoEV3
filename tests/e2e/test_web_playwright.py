from __future__ import annotations

import json
import re
import socket
import threading
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
    for name in (
        "01_linea_negra.json",
        "01_linea_negra_basica.json",
        "02_obstaculos_beacon.json",
        "05_obstaculos_baliza_ir.json",
        "12_radar_ultrasonido_360.json",
        "menu_world.json",
    ):
        (worlds_dir / name).write_text(json.dumps(world), encoding="utf-8")
    examples = {
        "11_siguelineas_basico.py": 'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("linea")\n',
        "15_esquiva_obstaculos.py": 'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("ultra")\n',
        "02_intro_pantalla_altavoz.py": (
            'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("brick")\n'
        ),
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

    expect(page.locator("#sessionStatus")).to_have_text(re.compile("running|finished"), timeout=5000)
    expect(page.locator("#sessionStatus")).to_have_text("finished", timeout=7000)
    expect(page.locator("#runBtn")).to_be_enabled()
    expect(page.locator("#telemetryTick")).not_to_have_text("--", timeout=5000)


def test_terminal_snapshot_synchronizes_status_telemetry_and_lcd(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")
    page.locator("#codeEditor").fill(
        "from pybricks.hubs import EV3Brick\n"
        "from pybricks.tools import wait\n"
        "ev3 = EV3Brick()\n"
        "ev3.screen.print('QA F001')\n"
        "wait(100)\n"
    )
    page.locator("#runBtn").click()

    expect(page.locator("#sessionStatus")).to_have_text("finished", timeout=7000)
    expect(page.locator("#telemetryStatus")).to_have_text("finished", timeout=7000)
    expect(page.locator("#telemetryTime")).not_to_have_text("--")
    expect(page.locator("#telemetryTick")).not_to_have_text("--")
    has_lcd_pixels = page.locator("#screen").evaluate(
        "canvas => canvas.getContext('2d').getImageData(0, 0, 178, 128).data.some(x => x !== 0)"
    )
    assert has_lcd_pixels


def test_successful_execution_shows_one_accessible_toast_after_terminal_snapshot(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")
    page.locator("#codeEditor").fill(
        "from pybricks.hubs import EV3Brick\n"
        "from pybricks.tools import wait\n"
        "ev3 = EV3Brick()\n"
        "ev3.screen.print('FIN OK')\n"
        "wait(80)\n"
    )
    page.locator("#runBtn").click()

    expect(page.locator("#sessionStatus")).to_have_text("finished", timeout=7000)
    expect(page.locator("#telemetryStatus")).to_have_text("finished", timeout=7000)
    expect(page.locator("#executionSuccessToast")).to_be_visible(timeout=3000)
    expect(page.locator("#executionSuccessToast")).to_contain_text("El programa se ejecutó correctamente.")
    assert page.locator("#executionSuccessToast").count() == 1
    page.locator("#executionSuccessToastClose").click()
    expect(page.locator("#executionSuccessToast")).to_be_hidden()


def test_success_toast_is_not_emitted_for_error_or_manual_stop(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")
    page.locator("#codeEditor").fill("raise RuntimeError('fallo de QA')\n")
    page.locator("#runBtn").click()
    expect(page.locator("#sessionStatus")).to_have_text("error", timeout=7000)
    expect(page.locator("#executionSuccessToast")).to_be_hidden()

    page.locator("#codeEditor").fill("from pybricks.tools import wait\nwhile True:\n    wait(50)\n")
    page.locator("#runBtn").click()
    expect(page.locator("#sessionStatus")).to_have_text(re.compile("running"), timeout=5000)
    page.locator("#stopBtn").click()
    expect(page.locator("#sessionStatus")).to_have_text("created", timeout=5000)
    expect(page.locator("#executionSuccessToast")).to_be_hidden()


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_success_toast_fits_mobile_viewport_in_both_themes(page, live_web_app, expect, theme):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{live_web_app}/")
    page.locator(".menu-trigger", has_text="Tema").hover()
    page.locator(f"[data-theme-choice='{theme}']").click()
    expect(page.locator("html")).to_have_attribute("data-theme", theme)
    page.locator("#codeEditor").fill("from pybricks.tools import wait\nwait(50)\n")
    page.locator("#runBtn").click()
    expect(page.locator("#executionSuccessToast")).to_be_visible(timeout=7000)
    box = page.locator("#executionSuccessToast").bounding_box()
    assert box is not None
    assert box["x"] >= 0
    assert box["x"] + box["width"] <= 390


def test_reset_replaces_terminal_snapshot_without_late_updates(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")
    expect(page.locator("#telemetryTick")).not_to_have_text("--", timeout=5000)
    page.locator("#codeEditor").fill("from pybricks.tools import wait\nwhile True:\n    wait(100)\n")
    page.locator("#runBtn").click()
    expect(page.locator("#sessionStatus")).to_have_text(re.compile("running"), timeout=5000)
    page.locator("#stopBtn").click()

    expect(page.locator("#sessionStatus")).to_have_text("created", timeout=5000)
    expect(page.locator("#telemetryStatus")).to_have_text("created", timeout=5000)
    # Esperar a que termine el refresco explícito que realiza el controlador
    # después de recibir la respuesta de reset.
    page.wait_for_timeout(300)
    # El endpoint inicial puede avanzar un tick para construir el primer DTO;
    # tras reset solo se admite ese snapshot inicial, nunca el de la ejecución.
    tick = int(page.locator("#telemetryTick").inner_text())
    simulated_time = float(page.locator("#telemetryTime").inner_text().removesuffix("s"))
    assert tick <= 1
    assert simulated_time <= 0.02


@pytest.mark.parametrize("viewport", [(1920, 1080), (1280, 800), (1024, 768), (390, 844)])
def test_map_canvas_and_tools_stay_inside_viewport(page, live_web_app, viewport):
    page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    page.goto(f"{live_web_app}/")

    canvas_box = page.locator("#worldCanvas").bounding_box()
    beam_box = page.locator("#toggleSensorBeamsBtn").bounding_box()

    assert canvas_box is not None
    assert beam_box is not None
    assert canvas_box["width"] <= viewport[0]
    assert beam_box["x"] >= 0
    assert beam_box["x"] + beam_box["width"] <= viewport[0]


def test_simulation_controls_follow_execution_state(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    expect(page.locator("#runBtn")).to_be_enabled()
    expect(page.locator("#debugRunBtn")).to_be_enabled()
    expect(page.locator("#debugStepBtn")).to_be_enabled()
    expect(page.locator("#pauseBtn")).to_be_disabled()
    expect(page.locator("#resumeBtn")).to_be_disabled()
    expect(page.locator("#stopBtn")).to_be_disabled()
    expect(page.locator("#placeRobotStartBtn")).to_be_enabled()

    page.locator("#codeEditor").fill("from pybricks.tools import wait\nwhile True:\n    wait(100)\n")
    page.locator("#runBtn").click()

    expect(page.locator("#sessionStatus")).to_have_text(re.compile(r"running"), timeout=5000)
    expect(page.locator("#runBtn")).to_be_disabled()
    expect(page.locator("#debugRunBtn")).to_be_disabled()
    expect(page.locator("#pauseBtn")).to_be_enabled()
    expect(page.locator("#resumeBtn")).to_be_disabled()
    expect(page.locator("#stopBtn")).to_be_enabled()
    expect(page.locator("#placeRobotStartBtn")).to_be_disabled()

    page.locator("#pauseBtn").click()

    expect(page.locator("#sessionStatus")).to_have_text(re.compile(r"paused"), timeout=5000)
    expect(page.locator("#pauseBtn")).to_be_disabled()
    expect(page.locator("#resumeBtn")).to_be_enabled()
    expect(page.locator("#debugContinueBtn")).to_be_enabled()
    expect(page.locator("#debugStepBtn")).to_be_enabled()

    page.locator("#resumeBtn").click()
    expect(page.locator("#sessionStatus")).to_have_text(re.compile(r"running"), timeout=5000)

    page.locator("#stopBtn").click()
    expect(page.locator("#sessionStatus")).to_have_text("created", timeout=5000)
    expect(page.locator("#runBtn")).to_be_enabled()
    expect(page.locator("#pauseBtn")).to_be_disabled()
    expect(page.locator("#resumeBtn")).to_be_disabled()
    expect(page.locator("#stopBtn")).to_be_disabled()
    expect(page.locator("#placeRobotStartBtn")).to_be_enabled()


def test_simulation_menus_load_examples_worlds_and_scenarios(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    expect(page.locator("#examplesMenu")).to_contain_text("menu_example.py")
    page.locator(".menu-trigger", has_text="Ejemplos").hover()
    page.locator("#examplesMenu button", has_text="menu_example.py").click()
    expect(page.locator("#codeEditor")).to_have_value(re.compile("menu"))

    expect(page.locator("#worldsMenu")).to_contain_text("menu_world.json")
    page.locator(".menu-trigger", has_text="Mundos").hover()
    page.locator("#worldsMenu .menu-subtoggle", has_text="Mundos preestablecidos").click()
    page.locator("#worldsMenu .menu-sublist button", has_text="menu_world.json").click()
    expect(page.locator("#statusWorld")).to_have_text("menu_world.json")

    page.locator(".menu-trigger", has_text="Escenarios").hover()
    page.locator("#scenariosMenu button[data-scenario='line']").click()
    expect(page.locator("#codeEditor")).to_have_value(re.compile("linea"), timeout=5000)
    expect(page.locator("#statusWorld")).to_have_text("01_linea_negra_basica.json")
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


def test_debug_breakpoint_pause_enables_debug_controls(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    page.locator("#codeEditor").fill("from pybricks.tools import wait\nx = 1\nwait(2000)\nx = 2\n")
    page.locator("#breakpointsInput").fill("3")
    page.locator("#debugRunBtn").click()

    expect(page.locator("#debugState")).to_contain_text("pausado en linea 3", timeout=5000)
    expect(page.locator(".gutter-line.current-debug-line")).to_have_attribute("data-line", "3")
    expect(page.locator("#debugContinueBtn")).to_be_enabled()
    expect(page.locator("#debugStepBtn")).to_be_enabled()
    expect(page.locator("#pauseBtn")).to_be_disabled()

    page.locator("#debugContinueBtn").click()
    expect(page.locator("#debugState")).to_contain_text("debug continue")


def test_loading_new_example_clears_stale_breakpoints(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    page.locator(".gutter-line[data-line='12']").click()
    expect(page.locator("#breakpointsInput")).to_have_value("12")

    page.locator(".menu-trigger", has_text="Ejemplos").hover()
    page.locator("#examplesMenu button", has_text="menu_example.py").click()

    expect(page.locator("#codeEditor")).to_have_value(re.compile("menu"))
    expect(page.locator("#breakpointsInput")).to_have_value("")
    expect(page.locator(".gutter-line.has-breakpoint")).to_have_count(0)


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


def test_simulation_editor_tabs_indent_and_outdent_without_losing_focus(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    editor = page.locator("#codeEditor")
    editor.fill("if True:\nprint('x')\n")
    page.evaluate(
        """
        () => {
          const editor = document.getElementById("codeEditor");
          const start = editor.value.indexOf("print");
          editor.focus();
          editor.setSelectionRange(start, start);
        }
        """
    )

    editor.press("Tab")
    expect(editor).to_have_value("if True:\n    print('x')\n")
    assert page.evaluate("document.activeElement.id") == "codeEditor"

    editor.press("Shift+Tab")
    expect(editor).to_have_value("if True:\nprint('x')\n")
    assert page.evaluate("document.activeElement.id") == "codeEditor"

    editor.fill("a = 1\nb = 2\n")
    page.evaluate(
        """
        () => {
          const editor = document.getElementById("codeEditor");
          editor.focus();
          editor.setSelectionRange(0, editor.value.length);
        }
        """
    )
    editor.press("Tab")
    expect(editor).to_have_value("    a = 1\n    b = 2\n")
    editor.press("Shift+Tab")
    expect(editor).to_have_value("a = 1\nb = 2\n")


def test_simulation_editor_wraps_selected_text_with_pairs(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    editor = page.locator("#codeEditor")
    editor.fill("ev3.screen.print")
    page.evaluate(
        """
        () => {
          const editor = document.getElementById("codeEditor");
          editor.focus();
          editor.setSelectionRange(0, editor.value.length);
        }
        """
    )
    editor.press("(")

    expect(editor).to_have_value("(ev3.screen.print)")
    assert page.evaluate("document.activeElement.id") == "codeEditor"


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


def test_simulation_editor_autocomplete_accepts_tab_without_leaving_editor(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    editor = page.locator("#codeEditor")
    editor.fill("from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.")
    editor.press("Control+Space")

    expect(page.locator("#autocompletePopup")).to_be_visible()
    editor.press("Tab")

    expect(editor).to_have_value(re.compile(r"ev3\.screen$"))
    expect(page.locator("#autocompletePopup")).to_be_hidden()
    assert page.evaluate("document.activeElement.id") == "codeEditor"


def test_simulation_editor_highlights_python_syntax(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    page.locator("#codeEditor").fill(
        "from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print('hola')  # comentario\n"
    )

    expect(page.locator("#syntaxHighlight .syntax-kw", has_text="from")).to_be_visible()
    expect(page.locator("#syntaxHighlight .syntax-builtin", has_text="EV3Brick").first).to_be_visible()
    expect(page.locator("#syntaxHighlight .syntax-string", has_text="'hola'")).to_be_visible()
    expect(page.locator("#syntaxHighlight .syntax-comment", has_text="# comentario")).to_be_visible()


def test_simulation_editor_scroll_synchronizes_highlight_and_gutter(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    long_line = "valor = '" + ("x" * 220) + "'"
    page.locator("#codeEditor").fill("\n".join([f"linea_{index} = {index}" for index in range(40)]) + f"\n{long_line}")
    page.evaluate(
        """
        () => {
          const editor = document.getElementById("codeEditor");
          editor.scrollTop = 180;
          editor.scrollLeft = 260;
          editor.dispatchEvent(new Event("scroll"));
        }
        """
    )

    sync = page.evaluate(
        """
        () => {
          const editor = document.getElementById("codeEditor");
          const highlight = document.getElementById("syntaxHighlight");
          const gutter = document.getElementById("editorGutter");
          return {
            editorTop: editor.scrollTop,
            editorLeft: editor.scrollLeft,
            highlightTop: highlight.scrollTop,
            highlightLeft: highlight.scrollLeft,
            gutterTop: gutter.scrollTop,
            canScrollHorizontal: editor.scrollWidth > editor.clientWidth,
          };
        }
        """
    )

    assert sync["canScrollHorizontal"]
    assert sync["highlightTop"] == sync["editorTop"]
    assert sync["highlightLeft"] == sync["editorLeft"]
    assert sync["gutterTop"] == sync["editorTop"]


def test_simulation_editor_last_line_can_be_clicked_at_line_end(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    lines = [f"linea_{index} = {index}" for index in range(1, 60)]
    last_line = "wait(20)  # Iteracion de Control 50Hz"
    source = "\n".join(lines + [last_line])
    editor = page.locator("#codeEditor")
    editor.fill(source)
    editor.evaluate("(node) => { node.scrollTop = node.scrollHeight; }")

    position = page.evaluate(
        """
        () => {
          const editor = document.getElementById("codeEditor");
          const style = window.getComputedStyle(editor);
          const lineHeight = Number.parseFloat(style.lineHeight);
          const paddingTop = Number.parseFloat(style.paddingTop);
          const paddingLeft = Number.parseFloat(style.paddingLeft);
          const paddingBottom = Number.parseFloat(style.paddingBottom);
          const lines = editor.value.split("\\n");
          const context = document.createElement("canvas").getContext("2d");
          context.font = `${style.fontSize} ${style.fontFamily}`;
          const textWidth = context.measureText(lines.at(-1)).width;
          const lineTop = paddingTop + (lines.length - 1) * lineHeight - editor.scrollTop;
          const rect = editor.getBoundingClientRect();
          return {
            x: rect.left + paddingLeft + textWidth + 4,
            y: rect.top + lineTop + lineHeight / 2,
            freeBottom: editor.clientHeight - (lineTop + lineHeight),
            paddingBottom,
          };
        }
        """
    )

    assert position["paddingBottom"] >= 60
    assert position["freeBottom"] >= 40
    page.mouse.click(position["x"], position["y"])

    assert page.evaluate("document.activeElement.id") == "codeEditor"
    assert page.evaluate("document.getElementById('codeEditor').selectionStart") == len(source)
    assert page.evaluate("document.getElementById('codeEditor').selectionEnd") == len(source)


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
    expect(page.locator("#assetPalette")).to_be_visible()
    expect(page.locator("#worldCanvas")).to_be_visible()

    page.locator("#assetPalette .asset-tool[data-asset-key='robot_ev3_32x32']").click()
    box = page.locator("#worldCanvas").bounding_box()
    assert box is not None
    page.mouse.click(box["x"] + 120, box["y"] + 120)

    expect(page.locator("#selectedAsset")).to_contain_text("robot_ev3_32x32", timeout=5000)
    expect(page.locator("#validationStatus")).to_contain_text("Validacion", timeout=5000)

    page.on("dialog", lambda dialog: dialog.accept("world_editor_smoke"))
    page.locator("#saveWorldBtn").click()

    expect(page.locator("#console")).to_contain_text("Mundo")
    expect(page.locator("#console")).to_contain_text(".json")
    expect(page.locator("#simulateSavedWorldLink")).to_be_visible()


def test_world_editor_updates_selected_asset_properties(page, live_web_app, expect):
    page.goto(f"{live_web_app}/worlds")

    page.locator("#assetPalette .asset-tool[data-asset-key='wall_64x64_a']").click()
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

    page.locator("#assetPalette .asset-tool[data-asset-key='wall_64x64_a']").click()
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
    expect(page.locator(".tutorial-card")).to_have_count(3)
    expect(page.locator(".tutorial-card").nth(0)).to_contain_text("Crear tu primer mundo")
    expect(page.locator(".tutorial-card").nth(1)).to_contain_text("Ejecutar un script")
    expect(page.locator(".tutorial-card").nth(2)).to_contain_text("Depurar por pasos")

    page.locator(".help-nav a", has_text="Crear mundos").click()
    expect(page.locator("#assetPalette")).to_be_visible()

    page.locator("nav a", has_text="Simulacion").click()
    expect(page.locator("#runBtn")).to_be_visible()


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
            "from pybricks.parameters import Color\n"
            "ev3 = EV3Brick()\n"
            "ev3.light.on(Color.RED)\n"
            "wait(900)\n"
        )
        page_b.locator("#codeEditor").fill(
            "from pybricks.hubs import EV3Brick\n"
            "from pybricks.tools import wait\n"
            "from pybricks.parameters import Color\n"
            "ev3 = EV3Brick()\n"
            "ev3.light.on(Color.GREEN)\n"
            "wait(900)\n"
        )

        page_a.locator("#runBtn").click()
        page_b.locator("#runBtn").click()

        expect(page_a.locator("#ledText")).to_have_text("RED", timeout=5000)
        expect(page_b.locator("#ledText")).to_have_text("GREEN", timeout=5000)
    finally:
        context_a.close()
        context_b.close()
