from __future__ import annotations

import argparse
import json
import logging
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
DEFAULT_OUTPUT_DIR = ROOT / "Documentos" / "EVIDENCIA_WEB_2026-05-20"
DEFAULT_LAYOUT_VIEWPORTS = [(1280, 800), (1366, 768), (1570, 900)]


def parse_size(value: str) -> tuple[int, int]:
    """Convierte una resolución ``ANCHOxALTO`` para evidencia reproducible."""

    try:
        width_text, height_text = value.lower().split("x", maxsplit=1)
        width, height = int(width_text), int(height_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use ANCHOxALTO, por ejemplo 1280x800.") from exc
    if width < 390 or height < 480:
        raise argparse.ArgumentTypeError("La evidencia requiere al menos 390x480 px.")
    return width, height


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
        "11_siguelineas_basico.py": 'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("linea")\n',
        "15_esquiva_obstaculos.py": 'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("ultra")\n',
        "02_intro_pantalla_altavoz.py": (
            'from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen.print("brick")\n'
        ),
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
    if box["x"] < 0:
        raise AssertionError(f"{selector} queda fuera del viewport horizontal: {box}")
    if box["x"] + box["width"] > viewport["width"] + 1:
        raise AssertionError(f"{selector} excede ancho viewport: {box} vs {viewport}")
    # Las capturas se generan con full_page=True y la aplicación permite
    # desplazamiento vertical. Estar debajo del pliegue no es un recorte ni un
    # defecto responsivo; exigirlo volvía frágil la evidencia a 800 px de alto.


def assert_world_canvas_respects_container(page) -> None:
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
    # La Web adapta el ancho del canvas al panel disponible. A diferencia de
    # Tkinter, no debe exigirse un ancho CSS fijo de 1280 px: eso rompería los
    # viewports responsivos. Sí debe conservar un buffer no vacío y coherente
    # con las dimensiones dibujadas.
    if metrics["canvasWidth"] <= 0 or metrics["canvasHeight"] <= 0:
        raise AssertionError(f"worldCanvas no tiene dimensiones visibles: {metrics}")
    if metrics["attrWidth"] <= 0 or metrics["attrHeight"] <= 0:
        raise AssertionError(f"worldCanvas no tiene buffer: {metrics}")
    if abs(metrics["attrWidth"] - metrics["canvasWidth"]) > 1:
        raise AssertionError(f"buffer horizontal no coincide con canvas: {metrics}")
    if abs(metrics["attrHeight"] - metrics["canvasHeight"]) > 1:
        raise AssertionError(f"buffer vertical no coincide con canvas: {metrics}")
    if metrics["canvasWidth"] > metrics["paneClientWidth"] + 1:
        raise AssertionError(f"canvas excede el ancho de su panel: {metrics}")
    if metrics["paneScrollWidth"] < metrics["canvasWidth"] or metrics["paneScrollHeight"] < metrics["canvasHeight"]:
        raise AssertionError(f"el panel no expone scroll del mapa completo: {metrics}")


def assert_canvas_has_blue_preview(page) -> None:
    metrics = page.locator("#worldCanvas").evaluate(
        """(canvas) => {
            const ctx = canvas.getContext("2d");
            const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
            let bluePixels = 0;
            for (let i = 0; i < data.length; i += 4) {
                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];
                const a = data[i + 3];
                if (a > 180 && r < 20 && g > 80 && g < 140 && b > 220) {
                    bluePixels += 1;
                    if (bluePixels >= 12) break;
                }
            }
            return { bluePixels };
        }"""
    )
    if metrics["bluePixels"] < 12:
        raise AssertionError(f"no se detecto previsualizacion azul: {metrics}")


def capture_layouts(
    browser,
    base_url: str,
    output_dir: Path,
    *,
    viewports: list[tuple[int, int]] | None = None,
    themes: tuple[str, ...] = ("light",),
) -> list[str]:
    files: list[str] = []
    viewports = viewports or DEFAULT_LAYOUT_VIEWPORTS
    pages = [
        ("/", "simulacion", ["#worldCanvas", "#codeEditor", "#telemetry", "#screen"]),
        ("/worlds", "mundos", ["#worldCanvas", "#assetPalette", "#selectedAsset", "#validationStatus"]),
    ]

    for width, height in viewports:
        for theme in themes:
            context = browser.new_context(viewport={"width": width, "height": height})
            page = context.new_page()
            try:
                for path, name, selectors in pages:
                    page.goto(f"{base_url}{path}")
                    expect(page.locator("#sessionStatus")).to_have_text(re.compile("created|ready"))
                    if theme != "light":
                        page.locator(".menu-trigger", has_text="Tema").hover()
                        page.locator(f"[data-theme-choice='{theme}']").click()
                        expect(page.locator("html")).to_have_attribute("data-theme", theme)
                    for selector in selectors:
                        expect(page.locator(selector)).to_be_visible()
                        if selector == "#worldCanvas":
                            assert_world_canvas_respects_container(page)
                        else:
                            assert_box_in_viewport(page, selector)
                    # Los sprites canónicos se cargan de forma asíncrona; el
                    # módulo de canvas redibuja al recibir `ev3-assets-loaded`.
                    # Esperar una vuelta corta del navegador evita registrar
                    # el fallback transitorio como si fuese la escena final.
                    page.wait_for_timeout(180)
                    # Se preservan los nombres históricos para el tema claro
                    # predeterminado; cualquier captura explícita de oscuro
                    # queda identificada y no pisa la evidencia clara.
                    suffix = "" if themes == ("light",) else f"_{theme}"
                    target = output_dir / f"{name}{suffix}_{width}x{height}.png"
                    page.screenshot(path=str(target), full_page=True)
                    files.append(str(target.relative_to(ROOT)))
            finally:
                context.close()
    return files


def capture_feature_flows(browser, base_url: str, output_dir: Path) -> list[str]:
    files: list[str] = []
    context = browser.new_context(viewport={"width": 1366, "height": 768})
    page = context.new_page()
    try:
        page.goto(f"{base_url}/")
        expect(page.locator("#sessionStatus")).to_have_text(re.compile("created|ready"))

        page.locator(".menu-trigger", has_text="Ejemplos").hover()
        expect(page.locator("#examplesMenu")).to_contain_text("qa_menu_example.py")
        page.locator("#examplesMenu button", has_text="qa_menu_example.py").click()
        expect(page.locator("#codeEditor")).to_have_value(re.compile("menu"))
        target = output_dir / "menu_ejemplos_1366x768.png"
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
        target = output_dir / "editor_sintaxis_autocomplete_1366x768.png"
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
        target = output_dir / "brick_altavoz_1366x768.png"
        page.screenshot(path=str(target), full_page=True)
        files.append(str(target.relative_to(ROOT)))

        page.goto(f"{base_url}/worlds")
        expect(page.locator("#sessionStatus")).to_have_text(re.compile("created|ready"))
        page.locator("#assetPalette .asset-tool[data-asset-key='floor_tile_256_a']").click()
        box = page.locator("#worldCanvas").bounding_box()
        if box is None:
            raise AssertionError("worldCanvas no tiene bounding box")
        page.mouse.move(box["x"] + 260, box["y"] + 230)
        expect(page.locator("#cursorReadout")).to_contain_text("Tool: floor_tile_256_a")
        assert_canvas_has_blue_preview(page)
        target = output_dir / "mundos_previsualizacion_1366x768.png"
        page.screenshot(path=str(target), full_page=True)
        files.append(str(target.relative_to(ROOT)))

        page.locator("#assetPalette .asset-tool[data-asset-key='wall_64x64_a']").click()
        page.mouse.click(box["x"] + 120, box["y"] + 120)
        expect(page.locator("#assetPropertiesForm")).to_be_visible()
        page.locator("#assetKeyInput").select_option("line_64_64_hor")
        # El editor actual recibe coordenadas de celda, no píxeles. Mantener
        # estos valores alineados con el flujo E2E de edición de propiedades.
        page.locator("#assetXInput").fill("2")
        page.locator("#assetYInput").fill("3")
        page.locator("#assetRotationInput").fill("180")
        page.locator("#applyAssetPropertiesBtn").click()
        expect(page.locator("#selectedAsset")).to_contain_text("Línea horizontal")
        target = output_dir / "mundos_propiedades_1366x768.png"
        page.screenshot(path=str(target), full_page=True)
        files.append(str(target.relative_to(ROOT)))
    finally:
        context.close()
    return files


def capture_two_profiles(browser, base_url: str, output_dir: Path) -> list[str]:
    files: list[str] = []
    context_a = browser.new_context(viewport={"width": 1366, "height": 768})
    context_b = browser.new_context(viewport={"width": 1366, "height": 768})
    page_a = context_a.new_page()
    page_b = context_b.new_page()
    try:
        page_a.goto(f"{base_url}/")
        page_b.goto(f"{base_url}/")
        expect(page_a.locator("#sessionStatus")).to_have_text(re.compile("created|ready"))
        expect(page_b.locator("#sessionStatus")).to_have_text(re.compile("created|ready"))

        page_a.locator("#codeEditor").fill(
            "from pybricks.hubs import EV3Brick\n"
            "from pybricks.tools import wait\n"
            "ev3 = EV3Brick()\n"
            "ev3.speaker.beep(440, 1000, 40)\n"
            "wait(100)\n"
        )
        page_b.locator("#codeEditor").fill(
            "from pybricks.hubs import EV3Brick\n"
            "from pybricks.tools import wait\n"
            "ev3 = EV3Brick()\n"
            "ev3.speaker.beep(880, 1000, 40)\n"
            "wait(100)\n"
        )
        page_a.locator("#runBtn").click()
        page_b.locator("#runBtn").click()

        # La duración es el tiempo restante y puede contener 440/880; la
        # frecuencia al inicio del texto identifica inequívocamente la sesión.
        expect(page_a.locator("#speaker")).to_have_text(re.compile(r"^440 Hz"))
        expect(page_b.locator("#speaker")).to_have_text(re.compile(r"^880 Hz"))

        for page, name in ((page_a, "perfil_a"), (page_b, "perfil_b")):
            target = output_dir / f"{name}_sesion_independiente.png"
            page.screenshot(path=str(target), full_page=True)
            files.append(str(target.relative_to(ROOT)))
    finally:
        context_a.close()
        context_b.close()
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera evidencia visual reproducible de la interfaz Web.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directorio donde se guardan las capturas.",
    )
    parser.add_argument(
        "--size", type=parse_size, action="append", default=[],
        help="Resolución a capturar; se puede repetir.",
    )
    parser.add_argument(
        "--theme", choices=("light", "dark", "all"), default="light",
        help="Tema para las capturas de composición (predeterminado: light).",
    )
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    themes = ("light", "dark") if args.theme == "all" else (args.theme,)
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    with LiveServer() as server:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                files = capture_layouts(
                    browser,
                    server.url,
                    output_dir,
                    viewports=args.size or None,
                    themes=themes,
                )
                files.extend(capture_feature_flows(browser, server.url, output_dir))
                files.extend(capture_two_profiles(browser, server.url, output_dir))
            finally:
                browser.close()

    print("Evidencia visual generada:")
    for file in files:
        print(f"- {file}")


if __name__ == "__main__":
    main()

