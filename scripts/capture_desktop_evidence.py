"""Genera capturas reproducibles de la interfaz de escritorio Tkinter.

Requiere una sesión gráfica activa de Windows. La ventana es temporal y no
persiste el tema ni la sesión del usuario.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Literal

from PIL import ImageGrab

from simulador_ev3.shared.ui_design_tokens import WEB_REFERENCE_HEIGHT_PX, WEB_REFERENCE_WIDTH_PX
from simulador_ev3.ui.main_window import EV3SimulatorApp

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "Documentos" / "EVIDENCIA_PARIDAD_2026-07-24" / "tkinter"
ThemeName = Literal["light", "dark"]


def display_path(path: Path) -> Path:
    """Devuelve una ruta relativa si es posible, sin fallar para artefactos temporales."""
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def _parse_size(value: str) -> tuple[int, int]:
    """Convierte ``ANCHOxALTO`` y rechaza tamaños ambiguos."""
    try:
        width_text, height_text = value.lower().split("x", maxsplit=1)
        width, height = int(width_text), int(height_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use el formato ANCHOxALTO, por ejemplo 1280x800.") from exc
    if width < 640 or height < 480:
        raise argparse.ArgumentTypeError("La captura debe tener al menos 640x480 px.")
    return width, height


def capture_theme(
    theme: ThemeName, output_dir: Path, size: tuple[int, int], *, verify_layout: bool = False
) -> Path:
    """Abre una ventana temporal, captura su área cliente y la cierra."""

    width, height = size
    app = EV3SimulatorApp(restore_session=False, persist_session=False)
    app.geometry(f"{width}x{height}+20+20")
    app._theme_name = theme
    app._apply_theme(theme)
    app.update_idletasks()
    app.deiconify()
    # ImageGrab captura el escritorio real: asegurar que la ventana temporal
    # esté delante de VS Code u otra aplicación antes de registrar evidencia.
    app.attributes("-topmost", True)
    app.lift()
    app.focus_force()
    measurement: dict[str, object] = {}

    captured_target: Path | None = None

    def save_and_close() -> None:
        nonlocal captured_target
        try:
            app.update_idletasks()
            left = app.winfo_rootx()
            top = app.winfo_rooty()
            width = app.winfo_width()
            height = app.winfo_height()
            measurement.update({
                "window": f"{width}x{height}",
                "dpi": round(float(app.winfo_fpixels("1i")), 1),
                "telemetry": f"{app._telemetry_panel.winfo_width()}x{app._telemetry_panel.winfo_height()}",
                "brick": f"{app._brick_panel.winfo_width()}x{app._brick_panel.winfo_height()}",
                "lcd": (
                    f"{app._brick_panel._screen_canvas.winfo_width()}x"
                    f"{app._brick_panel._screen_canvas.winfo_height()}"
                ),
            })
            if verify_layout:
                _verify_layout(app, width)
            captured_target = output_dir / f"simulacion_{theme}_{width}x{height}.png"
            ImageGrab.grab(bbox=(left, top, left + width, top + height), all_screens=True).save(captured_target)
        finally:
            app._on_close()

    app.after(900, save_and_close)
    app.mainloop()
    print(
        f"  {theme} {measurement.get('window')} dpi={measurement.get('dpi')} "
        f"telemetría={measurement.get('telemetry')} Brick={measurement.get('brick')} "
        f"LCD={measurement.get('lcd')}"
    )
    if captured_target is None:
        raise RuntimeError("La captura de Tkinter no produjo un archivo de evidencia")
    return captured_target


def _verify_layout(app: EV3SimulatorApp, window_width: int) -> None:
    """Falla la captura si una regresión vuelve a ocultar paneles críticos."""
    telemetry = app._telemetry_panel
    brick = app._brick_panel
    errors: list[str] = []
    if telemetry.winfo_width() <= 0 or brick.winfo_width() <= 0:
        errors.append("telemetría o Brick no recibió ancho visible")
    if brick._screen_canvas.winfo_width() <= 0 or brick._screen_canvas.winfo_height() <= 0:
        errors.append("la LCD no recibió geometría visible")
    if telemetry.winfo_width() < 560 and not telemetry._compact_layout:
        errors.append("la telemetría estrecha no activó el modo compacto")
    if telemetry.winfo_width() >= 560 and telemetry._compact_layout:
        errors.append("la telemetría ancha no restauró sus tres columnas")
    robot_bottom = brick._robot_state_section.winfo_y() + brick._robot_state_section.winfo_height()
    content_bottom = brick._scroll_canvas.canvasy(brick._scroll_canvas.winfo_height())
    if robot_bottom > content_bottom and brick._scroll_canvas.yview()[1] >= 1.0:
        errors.append("Robot/Estado está fuera de la vista y Brick no permite desplazamiento")
    if errors:
        raise RuntimeError(f"Layout inválido a {window_width}px: {'; '.join(errors)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera evidencia visual de la interfaz Tkinter.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--theme", choices=("light", "dark", "all"), default="all")
    parser.add_argument(
        "--size", type=_parse_size, action="append", default=[],
        help="Resolución a capturar; puede repetirse (predeterminado: 1280x800).",
    )
    parser.add_argument(
        "--verify-layout", action="store_true",
        help="Comprueba geometría y alcanzabilidad de Robot/Estado durante cada captura.",
    )
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    themes: tuple[ThemeName, ...] = ("light", "dark") if args.theme == "all" else (args.theme,)

    try:
        sizes = args.size or [(WEB_REFERENCE_WIDTH_PX, WEB_REFERENCE_HEIGHT_PX)]
        files = [
            capture_theme(theme, output_dir, size, verify_layout=args.verify_layout)
            for size in sizes for theme in themes
        ]
    except OSError as exc:
        print(f"No fue posible capturar Tkinter: {exc}", file=sys.stderr)
        return 1

    print("Evidencia Tkinter generada:")
    for file in files:
        print(f"- {display_path(file)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
