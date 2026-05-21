from __future__ import annotations

import json
import re
import socket
import tempfile
import threading
from contextlib import closing
from pathlib import Path

from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import make_server

from simulador_ev3.web.app import create_app


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "Documentos" / "EVIDENCIA_WEB_2026-05-20"


def prepare_evidence_data(base_dir: Path) -> tuple[Path, Path]:
    worlds_dir = base_dir / "worlds"
    examples_dir = base_dir / "examples"
    worlds_dir.mkdir(parents=True, exist_ok=True)
    examples_dir.mkdir(parents=True, exist_ok=True)
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
    for name in ("01_linea_negra.json", "02_obstaculos_beacon.json", "qa_menu_world.json"):
        (worlds_dir / name).write_text(json.dumps(world), encoding="utf-8")
    examples = {
        "06_siguelineas_basico.py": 'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("linea")\n',
        "05_esquiva_obstaculos.py": 'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("ultra")\n',
        "12_pantalla_altavoz_test.py": 'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("brick")\n',
        "qa_menu_example.py": 'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("menu")\n',
    }
    for name, source in examples.items():
        (examples_dir / name).write_text(source, encoding="utf-8")
    return worlds_dir, examples_dir


def free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class LiveServer:
    def __init__(self) -> None:
        self.port = free_port()
        self._tmp = tempfile.TemporaryDirectory(prefix="ev3_web_evidence_")
        worlds_dir, examples_dir = prepare_evidence_data(Path(self._tmp.name))
        self.app = create_app(
            {
                "TESTING": True,
                "WORLDS_DIR": worlds_dir,
                "EXAMPLES_DIR": examples_dir,
                "MAX_ACTIVE_SESSIONS": 10,
                "MAX_RUNNING_SIMULATIONS": 4,
                "SCRIPT_MAX_RUNTIME_S": 3.0,
                "SSE_HEARTBEAT_S": 0.1,
                "ENABLE_SESSION_CLEANUP_THREAD": False,
            }
        )
        self.server = make_server("127.0.0.1", self.port, self.app, threaded=True)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def __enter__(self) -> "LiveServer":
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.server.shutdown()
        self.thread.join(timeout=2)
        self._tmp.cleanup()


def assert_box_in_viewport(page, selector: str) -> None:
    box = page.locator(selector).bounding_box()
    viewport = page.viewport_size
    if box is None or viewport is None:
        raise AssertionError(f"{selector} no tiene bounding box visible")
    if box["x"] < 0 or box["y"] < 0:
        raise AssertionError(f"{selector} queda fuera del viewport: {box}")
    if box["x"] + box["width"] > viewport["width"] + 1:
        raise AssertionError(f"{selector} excede ancho viewport: {box} vs {viewport}")
    if box["y"] + box["height"] > viewport["height"] + 1:
        raise AssertionError(f"{selector} excede alto viewport: {box} vs {viewport}")


def assert_world_canvas_matches_tkinter_size(page) -> None:
    metrics = page.locator("#worldCanvas").evaluate(
        """(canvas) => {
            const pane = canvas.parentElement;
            return {
                canvasWidth: Math.round(canvas.getBoundingClientRect().width),
                canvasHeight: Math.round(canvas.getBoundingClientRect().height),
                attrWidth: canvas.width,
                attrHeight: canvas.height,
                paneClientWidth: pane ? pane.clientWidth : 0,
                paneClientHeight: pane ? pane.clientHeight : 0,
                paneScrollWidth: pane ? pane.scrollWidth : 0,
                paneScrollHeight: pane ? pane.scrollHeight : 0,
            };
        }"""
    )
    # Tkinter usa 32 px por cada 100 mm. El mundo base de 16000x16000 mm debe medir 5120x5120 px.
    expected_px = 5120
    if metrics["canvasWidth"] != expected_px or metrics["canvasHeight"] != expected_px:
        raise AssertionError(f"worldCanvas no coincide con tamano Tkinter: {metrics}")
    if metrics["attrWidth"] != expected_px or metrics["attrHeight"] != expected_px:
        raise AssertionError(f"buffer del canvas no coincide con tamano Tkinter: {metrics}")
    if metrics["paneScrollWidth"] < metrics["canvasWidth"] or metrics["paneScrollHeight"] < metrics["canvasHeight"]:
        raise AssertionError(f"el panel no expone scroll del mapa completo: {metrics}")


def capture_layouts(browser, base_url: str) -> list[str]:
    files: list[str] = []
    viewports = [(1366, 768), (1570, 900)]
    pages = [
        ("/", "simulacion", ["#worldCanvas", "#codeEditor", "#telemetry", "#screen"]),
        ("/worlds", "mundos", ["#worldCanvas", "#assetSelect", "#selectedAsset", "#validationStatus"]),
    ]

    for width, height in viewports:
        context = browser.new_context(viewport={"width": width, "height": height})
        page = context.new_page()
        try:
            for path, name, selectors in pages:
                page.goto(f"{base_url}{path}")
                expect(page.locator("#sessionStatus")).to_have_text("created")
                for selector in selectors:
                    expect(page.locator(selector)).to_be_visible()
                    if selector == "#worldCanvas":
                        assert_world_canvas_matches_tkinter_size(page)
                    else:
                        assert_box_in_viewport(page, selector)
                target = OUTPUT_DIR / f"{name}_{width}x{height}.png"
                page.screenshot(path=str(target), full_page=True)
                files.append(str(target.relative_to(ROOT)))
        finally:
            context.close()
    return files


def capture_feature_flows(browser, base_url: str) -> list[str]:
    files: list[str] = []
    context = browser.new_context(viewport={"width": 1366, "height": 768})
    page = context.new_page()
    try:
        page.goto(f"{base_url}/")
        expect(page.locator("#sessionStatus")).to_have_text("created")

        page.locator(".menu-trigger", has_text="Ejemplos").hover()
        expect(page.locator("#examplesMenu")).to_contain_text("qa_menu_example.py")
        page.locator("#examplesMenu button", has_text="qa_menu_example.py").click()
        expect(page.locator("#codeEditor")).to_have_value(re.compile("menu"))
        target = OUTPUT_DIR / "menu_ejemplos_1366x768.png"
        page.screenshot(path=str(target), full_page=True)
        files.append(str(target.relative_to(ROOT)))

        page.locator("#worldCanvas").click(position={"x": 20, "y": 20})
        expect(page.locator("#examplesMenu")).not_to_be_visible()
        page.locator("#codeEditor").fill(
            "from pybricks.hubs import EV3Brick\n"
            "ev3 = EV3Brick()\n"
            "ev3.screen.print('hola')  # comentario\n"
        )
        expect(page.locator("#syntaxHighlight .syntax-kw", has_text="from")).to_be_visible()
        page.locator("#codeEditor").press("End")
        page.locator("#codeEditor").press("Control+Space")
        expect(page.locator("#autocompletePopup")).to_be_visible()
        target = OUTPUT_DIR / "editor_sintaxis_autocomplete_1366x768.png"
        page.screenshot(path=str(target), full_page=True)
        files.append(str(target.relative_to(ROOT)))

        page.locator("#codeEditor").fill(
            "from pybricks.hubs import EV3Brick\n"
            "from pybricks.tools import wait\n"
            "ev3 = EV3Brick()\n"
            "ev3.speaker.beep(880, 1000, 70)\n"
            "wait(100)\n"
        )
        page.locator("#runBtn").click()
        expect(page.locator("#speaker")).to_contain_text("880")
        target = OUTPUT_DIR / "brick_altavoz_1366x768.png"
        page.screenshot(path=str(target), full_page=True)
        files.append(str(target.relative_to(ROOT)))

        page.goto(f"{base_url}/worlds")
        expect(page.locator("#sessionStatus")).to_have_text("created")
        page.locator("#assetSelect").select_option("wall_64x64_a")
        box = page.locator("#worldCanvas").bounding_box()
        if box is None:
            raise AssertionError("worldCanvas no tiene bounding box")
        page.mouse.click(box["x"] + 120, box["y"] + 120)
        expect(page.locator("#assetPropertiesForm")).to_be_visible()
        page.locator("#assetKeyInput").select_option("line_64_64_hor")
        page.locator("#assetXInput").fill("64")
        page.locator("#assetYInput").fill("96")
        page.locator("#assetRotationInput").fill("180")
        page.locator("#applyAssetPropertiesBtn").click()
        expect(page.locator("#selectedAsset")).to_contain_text("line_64_64_hor")
        target = OUTPUT_DIR / "mundos_propiedades_1366x768.png"
        page.screenshot(path=str(target), full_page=True)
        files.append(str(target.relative_to(ROOT)))
    finally:
        context.close()
    return files


def capture_two_profiles(browser, base_url: str) -> list[str]:
    files: list[str] = []
    context_a = browser.new_context(viewport={"width": 1366, "height": 768})
    context_b = browser.new_context(viewport={"width": 1366, "height": 768})
    page_a = context_a.new_page()
    page_b = context_b.new_page()
    try:
        page_a.goto(f"{base_url}/")
        page_b.goto(f"{base_url}/")
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

        expect(page_a.locator("#screen")).to_contain_text("perfil A")
        expect(page_b.locator("#screen")).to_contain_text("perfil B")
        expect(page_a.locator("#screen")).not_to_contain_text("perfil B")
        expect(page_b.locator("#screen")).not_to_contain_text("perfil A")

        for page, name in ((page_a, "perfil_a"), (page_b, "perfil_b")):
            target = OUTPUT_DIR / f"{name}_sesion_independiente.png"
            page.screenshot(path=str(target), full_page=True)
            files.append(str(target.relative_to(ROOT)))
    finally:
        context_a.close()
        context_b.close()
    return files


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with LiveServer() as server:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                files = capture_layouts(browser, server.url)
                files.extend(capture_feature_flows(browser, server.url))
                files.extend(capture_two_profiles(browser, server.url))
            finally:
                browser.close()

    print("Evidencia visual generada:")
    for file in files:
        print(f"- {file}")


if __name__ == "__main__":
    main()
