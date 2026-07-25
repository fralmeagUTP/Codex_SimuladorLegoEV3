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


def capture_theme(theme: ThemeName, output_dir: Path) -> Path:
    """Abre una ventana temporal, captura su área cliente y la cierra."""

    target = output_dir / f"simulacion_{theme}_{WEB_REFERENCE_WIDTH_PX}x{WEB_REFERENCE_HEIGHT_PX}.png"
    app = EV3SimulatorApp(restore_session=False, persist_session=False)
    app.geometry(f"{WEB_REFERENCE_WIDTH_PX}x{WEB_REFERENCE_HEIGHT_PX}+20+20")
    app._theme_name = theme
    app._apply_theme(theme)
    app.update_idletasks()
    app.deiconify()
    app.lift()

    def save_and_close() -> None:
        try:
            app.update_idletasks()
            left = app.winfo_rootx()
            top = app.winfo_rooty()
            width = app.winfo_width()
            height = app.winfo_height()
            ImageGrab.grab(bbox=(left, top, left + width, top + height), all_screens=True).save(target)
        finally:
            app._on_close()

    app.after(900, save_and_close)
    app.mainloop()
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera evidencia visual de la interfaz Tkinter.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--theme", choices=("light", "dark", "all"), default="all")
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    themes: tuple[ThemeName, ...] = ("light", "dark") if args.theme == "all" else (args.theme,)

    try:
        files = [capture_theme(theme, output_dir) for theme in themes]
    except OSError as exc:
        print(f"No fue posible capturar Tkinter: {exc}", file=sys.stderr)
        return 1

    print("Evidencia Tkinter generada:")
    for file in files:
        print(f"- {display_path(file)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
