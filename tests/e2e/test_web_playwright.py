from __future__ import annotations

import json
import os
import re
import shutil
import socket
import threading
from contextlib import closing
from pathlib import Path

import pytest
from werkzeug.serving import make_server

from simulador_ev3.shared.paths import resolve_examples_dir, resolve_worlds_dir
from simulador_ev3.web.app import create_app


def _failure_evidence_dir() -> Path:
    """Directorio reproducible de evidencia, configurable para CI."""

    return Path(os.environ.get("EV3_E2E_EVIDENCE_DIR", "artifacts/e2e-web"))


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    channels = []
    for component in rgb:
        normalized = component / 255
        channels.append(normalized / 12.92 if normalized <= 0.04045 else ((normalized + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast_ratio(foreground: str, background: str) -> float:
    def parse(value: str) -> tuple[int, int, int]:
        components = [int(component) for component in re.findall(r"\d+", value)[:3]]
        assert len(components) == 3, f"Color CSS no soportado: {value}"
        return tuple(components)  # type: ignore[return-value]

    foreground_luminance = _relative_luminance(parse(foreground))
    background_luminance = _relative_luminance(parse(background))
    lighter, darker = max(foreground_luminance, background_luminance), min(foreground_luminance, background_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def _computed_text_and_background(locator) -> dict[str, str]:
    return locator.evaluate(
        """
        node => {
          const visibleStatusText = node.matches('#sessionStatus[data-label], #telemetryStatus[data-label]')
            ? getComputedStyle(node, '::after').color
            : getComputedStyle(node).color;
          let current = node;
          while (current) {
            const background = getComputedStyle(current).backgroundColor;
            if (background && !background.endsWith(', 0)')) {
              return { foreground: visibleStatusText, background };
            }
            current = current.parentElement;
          }
          return { foreground: visibleStatusText, background: 'rgb(255, 255, 255)' };
        }
        """
    )


def _free_port() -> int:
    # Chromium rechaza una lista de puertos históricos inseguros (por ejemplo
    # 1720). Windows puede asignarlos al pedir el puerto efímero 0, por lo que
    # se descartan los inferiores a 20000 antes de iniciar el servidor E2E.
    while True:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.bind(("127.0.0.1", 0))
            port = int(sock.getsockname()[1])
        if port >= 20000:
            return port


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


@pytest.fixture()
def full_catalog_web_app():
    """Servidor E2E aislado que publica el catálogo real distribuido.

    No reemplaza el fixture mínimo: permite recorrer desde el navegador cada
    recurso que un estudiante verá en los menús de la aplicación instalada.
    """

    app = create_app(
        {
            "TESTING": True,
            "WORLDS_DIR": resolve_worlds_dir(),
            "EXAMPLES_DIR": resolve_examples_dir(),
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
def page(browser, request, tmp_path):
    # El HAR se registra en el directorio temporal de cada caso y solo se
    # conserva como evidencia cuando falla. Asi se obtiene la secuencia real
    # de red sin acumular artefactos de cada prueba aprobada.
    har_path = tmp_path / "network.har"
    context = browser.new_context(
        viewport={"width": 1366, "height": 768},
        record_har_path=har_path,
        record_har_content="omit",
    )
    page = context.new_page()
    console: list[dict[str, str]] = []
    network: list[dict[str, object]] = []

    def capture_console(message):
        console.append({"type": message.type, "text": message.text})

    def capture_response(response):
        if response.status >= 400:
            network.append({"kind": "response", "status": response.status, "url": response.url})

    def capture_request_failed(request_event):
        network.append(
            {
                "kind": "request_failed",
                "url": request_event.url,
                "failure": request_event.failure or "unknown",
            }
        )

    page.on("console", capture_console)
    page.on("response", capture_response)
    page.on("requestfailed", capture_request_failed)
    try:
        yield page
    finally:
        report = getattr(request.node, "rep_call", None)
        failed = report is not None and report.failed
        if failed:
            evidence_dir = _failure_evidence_dir()
            evidence_dir.mkdir(parents=True, exist_ok=True)
            stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.name)
            page.screenshot(path=evidence_dir / f"{stem}.png", full_page=True)
            (evidence_dir / f"{stem}.console.json").write_text(
                json.dumps(console, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (evidence_dir / f"{stem}.network.json").write_text(
                json.dumps(network, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        page.close()
        context.close()
        if failed and har_path.exists():
            shutil.copy2(har_path, evidence_dir / f"{stem}.har")


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


def test_web_startup_screen_closes_after_three_seconds(page, live_web_app, expect):
    """La introducción no puede dejar la aplicación web bloqueada."""

    page.goto(f"{live_web_app}/")
    splash = page.locator("#startupSplash")
    expect(splash).to_be_visible()

    page.wait_for_timeout(2800)
    expect(splash).to_be_visible()
    page.wait_for_timeout(700)
    expect(splash).to_be_hidden()
    expect(page.locator("#worldCanvas")).to_be_visible()


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


def test_ultrasonic_radar_sweep_keeps_canvas_rendering_between_snapshots(page, live_web_app, expect):
    """Un barrido breve ejercita motor, sensor, LCD y el renderizador visual real."""

    page.goto(f"{live_web_app}/")
    page.locator("#codeEditor").fill(
        "from pybricks.hubs import EV3Brick\n"
        "from pybricks.ev3devices import Motor, UltrasonicSensor\n"
        "from pybricks.parameters import Port\n"
        "from pybricks.robotics import DriveBase\n"
        "from pybricks.tools import wait\n"
        "ev3 = EV3Brick()\n"
        "left = Motor(Port.B)\n"
        "right = Motor(Port.C)\n"
        "radar = UltrasonicSensor(Port.S4)\n"
        "robot = DriveBase(left, right, 55.5, 104)\n"
        "robot.settings(turn_rate=180)\n"
        "for step in range(2):\n"
        "    ev3.screen.print('radar', radar.distance())\n"
        "    robot.turn(30)\n"
        "    wait(50)\n"
    )
    page.locator("#runBtn").click()

    expect(page.locator("#sessionStatus")).to_have_text("finished", timeout=7000)
    expect(page.locator("#telemetryStatus")).to_have_text("finished")
    expect(page.locator("#telemetry dd").nth(2)).not_to_have_text("--")
    expect(page.locator("#sensors article").nth(3)).to_contain_text("UltrasonicSensorModel")
    diagnostics = page.evaluate("window.EV3RenderDiagnostics()")
    assert diagnostics["receivedSnapshots"] >= 2
    assert diagnostics["renderedFrames"] >= 1


@pytest.mark.performance
def test_browser_keeps_animation_frames_while_a_simulation_is_running(page, live_web_app, expect):
    """Mide fotogramas reales del navegador durante una simulación corta.

    No define un SLA de producción: detecta que un bloqueo del hilo de UI deje
    el navegador sin animación durante el intervalo de muestreo.
    """

    page.goto(f"{live_web_app}/")
    page.locator("#codeEditor").fill(
        "from pybricks.tools import wait\n"
        "wait(900)\n"
    )
    page.locator("#runBtn").click()
    frame_sample = page.evaluate(
        """
        () => new Promise((resolve) => {
          let frames = 0;
          const startedAt = performance.now();
          const count = () => {
            frames += 1;
            requestAnimationFrame(count);
          };
          requestAnimationFrame(count);
          setTimeout(() => resolve({ frames, elapsedMs: performance.now() - startedAt }), 500);
        })
        """
    )

    expect(page.locator("#sessionStatus")).to_have_text("finished", timeout=7000)
    diagnostics = page.evaluate("window.EV3RenderDiagnostics()")
    assert frame_sample["elapsedMs"] >= 450
    assert frame_sample["frames"] >= 10
    assert diagnostics["renderedFrames"] >= 1


@pytest.mark.performance
def test_wait_duration_remains_close_to_simulated_time_in_the_browser(page, live_web_app, expect):
    """Detecta una degradación que haga que la animación quede muy atrás del runtime."""

    page.goto(f"{live_web_app}/")
    page.locator("#codeEditor").fill("from pybricks.tools import wait\nwait(900)\n")
    page.locator("#runBtn").click()

    expect(page.locator("#sessionStatus")).to_have_text("finished", timeout=7000)
    simulated_s = float(page.locator("#telemetryTime").inner_text().removesuffix("s"))
    render_diagnostics = page.evaluate("window.EV3RenderDiagnostics()")
    timing = render_diagnostics["executionTiming"]
    transitions = timing["transitions"]
    running_at_ms = next(item["atMs"] for item in transitions if item["status"] == "running")
    finished_at_ms = next(item["atMs"] for item in reversed(transitions) if item["status"] == "finished")
    started_at_ms = timing["startedAtMs"]
    assert started_at_ms is not None
    startup_s = (running_at_ms - started_at_ms) / 1000
    runtime_s = (finished_at_ms - running_at_ms) / 1000

    # Separar preparación IPC de ejecución: el usuario debe recibir estado
    # running con rapidez y, desde ese momento, la simulación debe acompasar
    # su reloj y renderizado con el reloj de pared. Un límite único desde el
    # clic mezclaba ambos contratos y diagnosticaba erróneamente un problema
    # de renderizado cuando el runtime ya iba a tiempo real.
    assert simulated_s >= 0.86
    assert startup_s <= 0.75, (startup_s, render_diagnostics)
    assert runtime_s <= max(1.2, simulated_s * 1.25), (runtime_s, simulated_s, render_diagnostics)


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
    expect(page.locator("#executionSuccessToast")).to_have_attribute("role", "status")
    expect(page.locator("#executionSuccessToast")).to_have_attribute("aria-live", "polite")
    expect(page.locator("#executionSuccessToast")).to_have_attribute("aria-atomic", "true")
    expect(page.locator("#executionSuccessToastClose")).to_have_attribute(
        "aria-label", "Cerrar notificación de ejecución finalizada"
    )
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
@pytest.mark.parametrize(
    "selector",
    ["#runBtn", "#sessionStatus", "#telemetryStatus", "#telemetryTick", "#telemetryCollision"],
)
def test_critical_web_text_keeps_wcag_aa_contrast_in_each_theme(page, live_web_app, theme, selector):
    page.goto(f"{live_web_app}/")
    page.locator(".menu-trigger", has_text="Configuración").hover()
    page.locator(f"[data-theme-choice='{theme}']").click()

    colors = _computed_text_and_background(page.locator(selector))
    ratio = _contrast_ratio(colors["foreground"], colors["background"])
    assert ratio >= 4.5, (
        f"{selector} en {theme}: contraste {ratio:.2f}:1 "
        f"(texto {colors['foreground']}, fondo {colors['background']})"
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_success_toast_fits_mobile_viewport_in_both_themes(page, live_web_app, expect, theme):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{live_web_app}/")
    page.locator(".menu-trigger", has_text="Configuración").hover()
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


@pytest.mark.parametrize("viewport", [(1920, 1080), (1280, 800), (1024, 768), (390, 844)])
def test_critical_simulation_panels_stay_inside_viewport(page, live_web_app, viewport):
    """El punto de ruptura debe contener editor, telemetría y Brick."""

    page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    page.goto(f"{live_web_app}/")
    layout = page.evaluate(
        """() => ({
            mediaMatches: window.matchMedia('(max-width: 1120px)').matches,
            viewport: window.innerWidth,
            documentWidth: document.documentElement.scrollWidth,
            mainColumns: getComputedStyle(document.querySelector('.sim-main-area')).gridTemplateColumns,
        })"""
    )

    for selector in (".sim-map-pane", "#codeEditor", "#telemetry", "#screen"):
        box = page.locator(selector).bounding_box()
        assert box is not None, f"{selector} no es visible en {viewport}"
        assert box["x"] >= 0, f"{selector} inicia fuera del viewport: {box}"
        assert box["x"] + box["width"] <= viewport[0] + 1, (
            f"{selector} excede el viewport {viewport}: {box}; layout={layout}"
        )

    if viewport[0] <= 1120:
        canvas_box = page.locator("#worldCanvas").bounding_box()
        pane_box = page.locator(".sim-map-pane").bounding_box()
        assert canvas_box is not None and pane_box is not None
        # El panel conserva 12 px de padding horizontal; el canvas no debe
        # añadir el margen de seguimiento de escritorio sobre ese espacio.
        assert canvas_box["x"] <= pane_box["x"] + 16, (
            f"el canvas inicia desplazado en la composición compacta: "
            f"canvas={canvas_box}, panel={pane_box}"
        )


def test_web_exposes_and_loads_the_canonical_robot_asset(page, live_web_app):
    """El primer render no debe quedar permanentemente en el fallback verde."""

    page.goto(f"{live_web_app}/")
    page.wait_for_function("() => Boolean(window.EV3Canvas?.isAssetReady('robot_ev3_32x32'))")
    assert page.evaluate("window.EV3Canvas.isAssetReady('robot_ev3_32x32')")


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
    expect(page.locator("#telemetryStatus")).to_have_text(re.compile(r"paused", re.IGNORECASE), timeout=5000)
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


def test_execution_locks_mutating_menus_and_restores_them_after_reset(page, live_web_app, expect):
    """Los menús que cambian la sesión no deben competir con una ejecución."""

    page.goto(f"{live_web_app}/")
    lockable_buttons = page.locator("[data-execution-lockable] button")
    lockable_links = page.locator("[data-execution-lockable] a")
    assert lockable_buttons.count() > 0

    page.locator("#codeEditor").fill("from pybricks.tools import wait\nwhile True:\n    wait(100)\n")
    page.locator("#runBtn").press("Enter")
    expect(page.locator("#sessionStatus")).to_have_text(re.compile(r"running"), timeout=5000)

    for index in range(lockable_buttons.count()):
        expect(lockable_buttons.nth(index)).to_be_disabled()
        expect(lockable_buttons.nth(index)).to_have_attribute("aria-disabled", "true")
    for index in range(lockable_links.count()):
        expect(lockable_links.nth(index)).to_have_attribute("aria-disabled", "true")
        expect(lockable_links.nth(index)).to_have_attribute("tabindex", "-1")

    page.locator("#stopBtn").press("Enter")
    expect(page.locator("#sessionStatus")).to_have_text("created", timeout=5000)

    for index in range(lockable_buttons.count()):
        expect(lockable_buttons.nth(index)).to_be_enabled()
        assert lockable_buttons.nth(index).get_attribute("aria-disabled") is None
    for index in range(lockable_links.count()):
        assert lockable_links.nth(index).get_attribute("aria-disabled") is None


def test_simulation_menus_load_examples_worlds_and_scenarios(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    expect(page.locator("#examplesMenu")).to_contain_text("menu_example.py")
    page.locator(".menu-trigger", has_text="Aprender").hover()
    page.locator("#examplesMenu button", has_text="menu_example.py").click()
    expect(page.locator("#codeEditor")).to_have_value(re.compile("menu"))

    expect(page.locator("#worldsMenu")).to_contain_text("menu_world.json")
    page.locator(".menu-trigger", has_text="Mundos").hover()
    page.locator("#worldsMenu .menu-subtoggle", has_text="Mundos preestablecidos").click()
    page.locator("#worldsMenu .menu-sublist button", has_text="menu_world.json").click()
    expect(page.locator("#statusWorld")).to_have_text("menu_world.json")

    page.locator(".menu-trigger", has_text="Prácticas guiadas").hover()
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("#scenariosMenu button[data-scenario='line']").click()
    expect(page.locator("#codeEditor")).to_have_value(re.compile("linea"), timeout=5000)
    expect(page.locator("#statusWorld")).to_have_text("01_linea_negra_basica.json")
    expect(page.locator("#console")).to_contain_text("Práctica guiada cargada: Seguidor de línea")

    page.locator(".menu-trigger", has_text="Ayuda").hover()
    page.locator("#aboutMenuBtn").click()
    expect(page.locator("#console")).to_contain_text("Simulador EV3 Web")


def test_real_catalog_loads_every_example_world_scenario_and_evaluated_practice(
    page, full_catalog_web_app, expect
):
    """Recorre con Chromium todos los recursos realmente distribuidos.

    El oráculo es la actualización visible del editor, mundo o consola. Así se
    detectan recursos rotos que una comprobación de lectura de archivos no
    descubriría en los menús de la interfaz real.
    """

    page.goto(f"{full_catalog_web_app}/")

    examples = page.locator("#examplesMenu button")
    expected_example_count = len(list(resolve_examples_dir().glob("*.py")))
    expect(examples).to_have_count(expected_example_count, timeout=5000)
    example_names = examples.all_inner_texts()
    assert len(example_names) >= 20
    for name in example_names:
        page.locator(".menu-trigger", has_text="Aprender").hover()
        page.locator("#examplesMenu").get_by_role("button", name=name, exact=True).click()
        expected_source = (resolve_examples_dir() / name).read_text(encoding="utf-8")
        expect(page.locator("#codeEditor")).to_have_value(expected_source, timeout=3000)

    worlds_menu = page.locator(".menu-trigger", has_text="Mundos")
    presets_menu = page.locator("#worldsMenu .menu-subtoggle", has_text="Mundos preestablecidos")
    worlds = page.locator("#worldsMenu .menu-sublist button")
    expect(worlds).to_have_count(len(list(resolve_worlds_dir().glob("*.json"))), timeout=5000)
    world_names = worlds.all_inner_texts()
    assert len(world_names) >= 10
    for name in world_names:
        worlds_menu.click()
        if presets_menu.get_attribute("aria-expanded") != "true":
            presets_menu.click()
        expect(page.locator("#worldsMenu .menu-sublist")).to_be_visible()
        page.locator("#worldsMenu .menu-sublist").get_by_role("button", name=name, exact=True).click()
        expect(page.locator("#statusWorld")).to_have_text(name)

    for scenario in ("line", "ultrasonic", "brick", "radar"):
        page.locator(".menu-trigger", has_text="Prácticas guiadas").hover()
        page.once("dialog", lambda dialog: dialog.accept())
        page.locator(f"#scenariosMenu button[data-scenario='{scenario}']").click()
        expect(page.locator("#console")).to_contain_text("Práctica guiada cargada:")

    page.locator(".menu-trigger", has_text="Prácticas guiadas").hover()
    mission_names = page.locator("#scenariosMenu button[data-mission]").all_inner_texts()
    assert mission_names
    for name in mission_names:
        page.locator(".menu-trigger", has_text="Prácticas guiadas").hover()
        page.locator("#scenariosMenu").get_by_role("button", name=name, exact=True).click()
        expect(page.locator("#console")).to_contain_text("Misión cargada:")


def test_legacy_obstacle_world_renders_the_canonical_wall_texture(
    page, full_catalog_web_app, expect
):
    """Las cajas de un mundo histórico se pintan con el PNG, no como rectángulos grises."""

    page.goto(f"{full_catalog_web_app}/")
    page.locator(".menu-trigger", has_text="Mundos").click()
    presets = page.locator("#worldsMenu .menu-subtoggle", has_text="Mundos preestablecidos")
    presets.click()
    page.locator("#worldsMenu .menu-sublist").get_by_role(
        "button", name="12_radar_ultrasonido_360.json", exact=True
    ).click()
    expect(page.locator("#statusWorld")).to_have_text("12_radar_ultrasonido_360.json")

    # El asset se solicita y queda disponible desde el navegador real sólo si
    # ``drawObstacles`` resolvió el nombre histórico al asset canónico.
    page.wait_for_function(
        "() => window.EV3Canvas.isAssetReady('wall_64x64_b')",
        timeout=5000,
    )


def test_world_presets_remain_open_when_activated_by_click(page, live_web_app, expect):
    """El submenú debe funcionar sin depender del hover del puntero."""

    page.goto(f"{live_web_app}/")
    worlds_trigger = page.get_by_role("button", name="Mundos", exact=True)
    worlds_trigger.click()
    presets = page.locator("#worldsMenu .menu-subtoggle", has_text="Mundos preestablecidos")
    presets.click()

    expect(page.locator("#worldsMenu")).to_be_visible()
    expect(page.locator("#worldsMenu .menu-sublist")).to_be_visible()
    first_world = page.locator("#worldsMenu .menu-sublist button").first
    expect(first_world).to_be_visible()
    first_world.click()
    expect(page.locator("#statusWorld")).to_have_text(first_world.inner_text())


def test_reset_hides_the_terminal_mission_result(page, live_web_app, expect):
    """Una misión terminada no puede dejar resultado visible tras reiniciar."""

    page.goto(f"{live_web_app}/")
    page.locator(".menu-trigger", has_text="Prácticas guiadas").hover()
    mission = page.locator("#scenariosMenu button[data-mission]").first
    expect(mission).to_be_visible()
    mission.click()
    expect(page.locator("#console")).to_contain_text("Misión cargada")

    page.locator("#runBtn").click()
    expect(page.locator("#sessionStatus")).to_have_text("finished", timeout=7000)
    expect(page.locator("#missionResult")).to_be_visible(timeout=5000)

    page.locator("#stopBtn").click()
    expect(page.locator("#sessionStatus")).to_have_text("created", timeout=5000)
    expect(page.locator("#missionResult")).to_be_hidden()


def test_reset_recovers_the_ultrasonic_obstacle_scenario(page, live_web_app, expect):
    """El reinicio de un escenario normal no puede quedar bloqueado en resetting."""
    page.goto(f"{live_web_app}/")
    page.locator(".menu-trigger", has_text="Prácticas guiadas").hover()
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("#scenariosMenu button[data-scenario='ultrasonic']").click()
    expect(page.locator("#codeEditor")).to_have_value(re.compile("ultra"), timeout=5000)

    page.locator("#runBtn").click()
    expect(page.locator("#sessionStatus")).to_have_text(re.compile(r"running|finished"), timeout=5000)
    page.locator("#stopBtn").click()

    expect(page.locator("#sessionStatus")).to_have_text("created", timeout=5000)
    expect(page.locator("#telemetryStatus")).to_have_text(re.compile(r"created", re.IGNORECASE), timeout=5000)
    expect(page.locator("#runBtn")).to_be_enabled()
    expect(page.locator("#stopBtn")).to_be_disabled()


def test_menu_keyboard_opens_items_and_escape_restores_trigger_focus(page, live_web_app, expect):
    """La barra de menús debe ser utilizable sin ratón."""

    page.goto(f"{live_web_app}/")
    file_menu = page.get_by_role("button", name="Archivo", exact=True)
    new_script = page.locator("#newScriptMenuBtn")

    file_menu.press("ArrowDown")
    expect(file_menu).to_have_attribute("aria-expanded", "true")
    expect(new_script).to_be_visible()
    assert page.evaluate("document.activeElement.id") == "newScriptMenuBtn"

    new_script.press("Escape")
    expect(file_menu).to_have_attribute("aria-expanded", "false")
    expect(new_script).to_be_hidden()
    assert page.evaluate("document.activeElement.textContent.trim()") == "Archivo"


def test_activity_guide_replaces_the_fixed_learning_panel(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    expect(page.locator("#learningPanel")).to_have_count(0)
    page.get_by_role("button", name="Ayuda", exact=True).click()
    guide = page.locator("#activityGuideLink")
    expect(guide).to_be_visible()
    expect(guide).to_have_attribute("href", re.compile(r"#guide-first-simulation$"))


def test_primary_menu_has_a_predictable_tab_order(page, live_web_app):
    """Los controles principales deben seguir un orden de foco utilizable."""
    page.goto(f"{live_web_app}/")

    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.textContent.trim()") == "Archivo"
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.textContent.trim()") == "Aprender"
    page.keyboard.press("Shift+Tab")
    assert page.evaluate("document.activeElement.textContent.trim()") == "Archivo"
    page.keyboard.press("Enter")
    assert page.locator(".menu-trigger", has_text="Archivo").get_attribute("aria-expanded") == "true"


def test_all_primary_menu_triggers_are_reachable_in_tab_order(page, live_web_app):
    """La barra completa no debe dejar menús inaccesibles por teclado."""
    page.goto(f"{live_web_app}/")
    expected_labels = [
        "Archivo",
        "Aprender",
        "Mundos",
        "Prácticas guiadas",
        "Configuración",
        "Diagnóstico",
        "Ayuda",
    ]

    for label in expected_labels:
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.textContent.trim()") == label


def test_settings_menu_updates_theme_profile_and_runtime_with_visible_state(page, live_web_app, expect):
    """Configuración agrupa ajustes técnicos y confirma su estado actual."""

    page.goto(f"{live_web_app}/")
    settings = page.get_by_role("button", name="Configuración", exact=True)
    settings.click()

    page.get_by_role("button", name="Tema oscuro", exact=True).click()
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")

    settings.click()
    realistic = page.get_by_role("button", name=re.compile(r"^Realista"))
    realistic.click()
    expect(realistic).to_have_attribute("aria-pressed", "true")

    settings.click()
    limit = page.get_by_role("button", name="30 s", exact=True)
    limit.click()
    expect(limit).to_have_attribute("aria-pressed", "true")


def test_evaluated_practices_expose_requirements_and_visible_progress(page, live_web_app, expect):
    """Los retos evaluables se integran en Prácticas guiadas sin perder sus requisitos."""

    page.goto(f"{live_web_app}/")
    practices = page.get_by_role("button", name="Prácticas guiadas", exact=True)
    practices.click()
    mission = page.locator("#scenariosMenu button[data-mission]").first
    expect(mission).to_have_attribute("aria-description", re.compile(r"Objetivo:|Requisitos"))
    mission.click()
    expect(page.locator("#missionProgress")).to_be_visible()
    expect(page.locator("#missionProgress")).to_contain_text(re.compile(r"Progreso: 0/\d+ requisitos"))


def test_help_menu_opens_the_help_center(page, live_web_app, expect):
    """El Centro de ayuda debe abrir contenido real desde el menú Ayuda."""
    page.goto(f"{live_web_app}/")
    page.locator(".menu-trigger", has_text="Ayuda").hover()
    with page.context.expect_page() as new_page_info:
        page.locator(".menu-dropdown a", has_text="Centro de ayuda").click()
    manual_page = new_page_info.value
    manual_page.wait_for_load_state()
    expect(manual_page).to_have_url(re.compile(r"/help"))
    expect(manual_page.locator("body")).to_contain_text("¿Qué quieres hacer hoy?")


def test_help_diagnostics_has_its_own_title_and_exports_safe_json(page, live_web_app, expect):
    """Diagnóstico y Acerca de no comparten semántica ni contenido visual."""

    page.goto(f"{live_web_app}/")
    page.get_by_role("button", name="Diagnóstico", exact=True).click()
    page.get_by_role("button", name="Diagnóstico de sesión", exact=True).click()

    dialog = page.get_by_role("dialog")
    expect(dialog).to_be_visible()
    expect(dialog.locator("#aboutDialogTitle")).to_have_text("Diagnóstico de sesión")
    expect(dialog.locator(".about-groups")).to_be_hidden()
    dialog.press("Escape")
    expect(dialog).to_be_hidden()

    page.get_by_role("button", name="Diagnóstico", exact=True).click()
    with page.expect_download() as download_info:
        page.get_by_role("button", name="Exportar diagnóstico JSON", exact=True).click()
    download = download_info.value
    assert download.suggested_filename.startswith("diagnostico-sesion-")
    assert download.suggested_filename.endswith(".json")

    page.get_by_role("button", name="Ayuda", exact=True).click()
    page.get_by_role("button", name="Acerca de", exact=True).click()
    expect(dialog.locator("#aboutDialogTitle")).to_have_text("Acerca de")
    expect(dialog.locator(".about-groups")).to_be_visible()


def test_help_menu_offers_the_lego_ev3_book_in_a_new_secure_tab(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")
    page.get_by_role("button", name="Ayuda", exact=True).click()

    book = page.get_by_role("link", name="Libro: Programación en Python para robótica (LEGO EV3)", exact=True)
    expect(book).to_have_attribute("target", "_blank")
    expect(book).to_have_attribute("rel", re.compile(r"noopener"))
    expect(book).to_have_attribute(
        "href",
        re.compile(r"repositorio\.utp\.edu\.co/entities/publication/2cb3c888-47b1-4653-8b05-46c27a87ae81"),
    )


def test_secondary_web_controls_are_operable_with_keyboard(page, live_web_app, expect):
    """Ayuda y herramientas de mapa conservan un recorrido de teclado útil."""

    page.goto(f"{live_web_app}/")
    help_menu = page.get_by_role("button", name="Ayuda", exact=True)
    assert help_menu.count() == 1
    help_menu.press("ArrowDown")

    about_button = page.get_by_role("button", name="Acerca de", exact=True)
    assert about_button.count() == 1
    about_button.press("Enter")
    dialog = page.get_by_role("dialog")
    assert dialog.count() == 1
    expect(dialog).to_be_visible()
    dialog.press("Escape")
    expect(dialog).to_be_hidden()

    beams_button = page.get_by_role("button", name="Mostrar haces de sensores", exact=True)
    assert beams_button.count() == 1
    beams_button.press("Enter")
    expect(beams_button).to_have_text("Haces OFF")
    beams_button.press("Enter")
    expect(beams_button).to_have_text("Haces ON")

    robot_placement = page.get_by_role("button", name="Ubicar robot", exact=True)
    assert robot_placement.count() == 1
    robot_placement.press("Enter")
    expect(page.get_by_text("Haz clic en el canvas para fijar la pose.", exact=True)).to_be_visible()
    robot_placement.press("Enter")


def test_trace_tick_advances_the_visible_authoritative_snapshot(page, live_web_app, expect):
    """Trazas no puede confirmar un tick que el panel aún no haya recibido."""

    page.goto(f"{live_web_app}/")
    page.locator("#codeEditor").fill("from pybricks.tools import wait\nwait(1)\n")

    traces_menu = page.get_by_role("button", name="Diagnóstico", exact=True)
    traces_menu.hover()
    page.get_by_role("button", name="Iniciar registro", exact=True).click()
    expect(page.locator("#console")).to_contain_text("Registro de traza iniciado.")

    before = int(page.locator("#telemetryTick").inner_text())
    traces_menu.hover()
    page.get_by_role("button", name="Avanzar un tick", exact=True).click()
    expect(page.locator("#telemetryTick")).not_to_have_text(str(before), timeout=5000)
    after = int(page.locator("#telemetryTick").inner_text())

    assert after > before
    expect(page.locator("#console")).to_contain_text("Se avanzo un tick de simulacion.")


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


def test_reset_recovers_a_session_paused_at_a_debug_breakpoint(page, live_web_app, expect):
    """Detener y reiniciar debe recuperar una sesión pausada por el depurador."""
    page.goto(f"{live_web_app}/")

    page.locator("#codeEditor").fill("from pybricks.tools import wait\nx = 1\nwait(10000)\n")
    page.locator("#breakpointsInput").fill("3")
    page.locator("#debugRunBtn").click()

    expect(page.locator("#debugState")).to_contain_text("pausado en linea 3", timeout=5000)
    expect(page.locator("#sessionStatus")).to_have_text(re.compile(r"paused"), timeout=5000)
    page.locator("#stopBtn").click()

    expect(page.locator("#sessionStatus")).to_have_text("created", timeout=5000)
    expect(page.locator("#runBtn")).to_be_enabled()
    expect(page.locator("#debugRunBtn")).to_be_enabled()
    expect(page.locator("#telemetryStatus")).to_have_text(re.compile(r"created", re.IGNORECASE), timeout=5000)


def test_loading_new_example_clears_stale_breakpoints(page, live_web_app, expect):
    page.goto(f"{live_web_app}/")

    page.locator(".gutter-line[data-line='12']").click()
    expect(page.locator("#breakpointsInput")).to_have_value("12")

    page.locator(".menu-trigger", has_text="Aprender").hover()
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

    expect(page.locator("#selectedAsset")).to_contain_text("Robot EV3", timeout=5000)
    expect(page.locator("#validationStatus")).to_contain_text("Validacion", timeout=5000)

    page.on("dialog", lambda dialog: dialog.accept("world_editor_smoke"))
    page.locator("#saveWorldBtn").click()

    expect(page.locator("#console")).to_contain_text("Mundo")
    expect(page.locator("#console")).to_contain_text(".json")
    expect(page.locator("#simulateSavedWorldLink")).to_be_visible()


def test_world_editor_blank_canvas_does_not_attempt_an_unselected_placement(page, live_web_app, expect):
    """Crear/cargar un mundo vacío no debe generar un error al pulsar el lienzo."""
    page.goto(f"{live_web_app}/worlds")
    expect(page.locator("#worldCanvas")).to_be_visible()
    expect(page.locator("#selectedAsset")).to_contain_text("Selecciona un elemento")
    expect(page.locator("#console")).to_have_text("Mundo valido.")
    previous_console = page.locator("#console").inner_text()
    box = page.locator("#worldCanvas").bounding_box()
    assert box is not None

    page.mouse.click(box["x"] + 160, box["y"] + 160)

    expect(page.locator("#selectedAsset")).to_contain_text("Selecciona un elemento")
    expect(page.locator("#console")).to_have_text(previous_console)


def test_world_editor_updates_selected_asset_properties(page, live_web_app, expect):
    page.goto(f"{live_web_app}/worlds")

    page.locator("#assetPalette .asset-tool[data-asset-key='wall_64x64_a']").click()
    box = page.locator("#worldCanvas").bounding_box()
    assert box is not None
    page.mouse.click(box["x"] + 120, box["y"] + 120)

    expect(page.locator("#assetPropertiesForm")).to_be_visible()
    page.locator("#assetKeyInput").select_option("line_64_64_hor")
    page.locator("#assetXInput").fill("2")
    page.locator("#assetYInput").fill("3")
    page.locator("#assetRotationInput").fill("180")
    page.locator("#applyAssetPropertiesBtn").click()

    expect(page.locator("#selectedAsset")).to_contain_text("Línea horizontal", timeout=5000)
    expect(page.locator("#assetProperties")).to_contain_text("2")
    expect(page.locator("#assetProperties")).to_contain_text("3")
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
    expect(page.locator("#selectedAsset")).to_contain_text("Muro A", timeout=5000)

    page.mouse.move(start_x, start_y)
    page.mouse.down()
    page.mouse.move(end_x, end_y, steps=8)
    page.mouse.up()

    expect(page.locator("#assetProperties")).to_contain_text("X")
    expect(page.locator("#selectedAsset")).to_contain_text("Muro A", timeout=5000)
    expect(page.locator("#console")).to_contain_text("Mundo valido.", timeout=5000)


def test_world_editor_preserves_assets_when_resizing_and_docks_panels(page, live_web_app, expect):
    """Recorrido visible de la protección contra pérdida y el diseño portátil."""

    page.set_viewport_size({"width": 1024, "height": 768})
    page.goto(f"{live_web_app}/worlds")
    expect(page.locator("#worldCanvas")).to_be_visible()

    page.locator("#assetPalette .asset-tool[data-asset-key='wall_64x64_a']").click()
    box = page.locator("#worldCanvas").bounding_box()
    assert box is not None
    page.mouse.click(box["x"] + 160, box["y"] + 160)
    expect(page.locator("#worldDirtyIndicator")).to_be_visible()

    page.locator("#worldWidthInput").fill("50")
    page.locator("#worldHeightInput").fill("40")
    page.locator("#applyWorldSizeBtn").click()
    expect(page.locator("#selectedAsset")).to_contain_text("Muro A", timeout=5000)
    expect(page.locator("#worldDirtyIndicator")).to_be_visible()

    page.locator("#toggleLibraryPanelBtn").click()
    expect(page.locator(".world-editor-shell")).to_have_class(re.compile(r"\bis-library-collapsed\b"))
    expect(page.locator("#worldCanvas")).to_be_visible()
    page.locator("#toggleInspectorPanelBtn").click()
    expect(page.locator(".world-editor-shell")).to_have_class(
        re.compile(r"(?=.*\bis-library-collapsed\b)(?=.*\bis-inspector-collapsed\b)")
    )
    expect(page.locator("#worldCanvas")).to_be_visible()


def test_help_page_is_available_from_browser(page, live_web_app, expect):
    page.goto(f"{live_web_app}/help")

    expect(page.get_by_role("heading", name="¿Qué quieres hacer hoy?")).to_be_visible()
    search = page.get_by_role("searchbox", name="Buscar una guía, control o error")
    expect(search).to_be_visible()
    expect(page.locator("[data-help-guide]")).to_have_count(11)

    search.fill("ultrasónico")
    expect(page.locator("#helpSearchStatus")).to_have_text("1 guía disponible.")
    expect(page.locator("[data-help-guide]:not([hidden])")).to_have_count(1)
    expect(page.locator("#guide-use-sensors")).to_be_visible()

    search.fill("")
    page.get_by_role("button", name="Resolver problemas").click()
    expect(page.locator("[data-help-guide]:not([hidden])")).to_have_count(3)
    expect(page.locator("#guide-recover-script-error")).to_be_visible()
    expect(page.locator("#guide-session-diagnostics")).to_be_visible()

    page.locator("#helpThemeSelect").select_option("light")
    expect(page.locator("html")).to_have_attribute("data-theme", "light")
    page.locator("#helpThemeSelect").select_option("dark")
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")

    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def test_help_progress_teacher_mode_and_keyboard_are_accessible(page, live_web_app, expect):
    """El recorrido guiado conserva el avance y funciona sin ratÃ³n."""

    page.goto(f"{live_web_app}/help")
    page.evaluate("localStorage.removeItem('ev3-help-guide-progress-v1')")
    page.evaluate("localStorage.removeItem('ev3-help-teacher-mode-v1')")
    page.reload()

    first_step = page.locator("[data-guide-step]").first
    first_step.focus()
    first_step.press("Space")
    expect(first_step).to_be_checked()
    progress = page.locator("[data-guide-progress]").first
    expect(progress).to_have_attribute("aria-live", "polite")
    expect(progress.locator("progress")).to_have_attribute("value", "1")

    page.reload()
    expect(page.locator("[data-guide-step]").first).to_be_checked()

    teacher_mode = page.locator("[data-teacher-mode]")
    teacher_mode.focus()
    teacher_mode.press("Enter")
    expect(teacher_mode).to_have_attribute("aria-pressed", "true")
    expect(page.locator("[data-teacher-route]")).to_be_visible()


def test_help_page_respects_dark_mobile_and_reduced_motion(page, live_web_app, expect):
    """La ayuda mantiene contenido utilizable con preferencias de accesibilidad."""

    page.emulate_media(reduced_motion="reduce")
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{live_web_app}/help")
    page.locator("#helpThemeSelect").select_option("dark")

    expect(page.locator("html")).to_have_attribute("data-theme", "dark")
    expect(page.locator("[data-help-guide]").first).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert page.evaluate(
        "getComputedStyle(document.querySelector('.help-teacher-route')).animationName"
    ) in {"none", ""}


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
