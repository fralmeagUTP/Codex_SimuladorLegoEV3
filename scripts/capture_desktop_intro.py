"""Captura la secuencia real de inicio de la aplicación Tkinter.

Genera una imagen durante la introducción y otra después de que la ventana
principal se revele. No utiliza pywinauto ni modifica la sesión del usuario.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import ImageGrab

from simulador_ev3.ui.main_window import EV3SimulatorApp, _launch_after_intro


def _capture_widget(widget, target: Path) -> None:
    widget.update_idletasks()
    left, top = widget.winfo_rootx(), widget.winfo_rooty()
    width, height = widget.winfo_width(), widget.winfo_height()
    if width <= 1 or height <= 1:
        raise RuntimeError("La ventana no recibió geometría visible para la captura.")
    ImageGrab.grab(bbox=(left, top, left + width, top + height), all_screens=True).save(target)


def capture_sequence(output_dir: Path) -> tuple[Path, Path]:
    """Ejecuta el mismo flujo de ``main()`` y cierra la instancia temporal."""
    output_dir.mkdir(parents=True, exist_ok=True)
    intro_target = output_dir / "intro.png"
    main_target = output_dir / "ventana_principal.png"

    def on_intro_ready(splash) -> None:
        splash.after(500, lambda: _capture_widget(splash, intro_target))

    def on_main_ready(app: EV3SimulatorApp) -> None:
        def capture_and_close() -> None:
            try:
                _capture_widget(app, main_target)
            finally:
                app._on_close()

        app.after(900, capture_and_close)

    _launch_after_intro(
        on_intro_ready=on_intro_ready,
        on_main_ready=on_main_ready,
        app_factory=lambda: EV3SimulatorApp(restore_session=False, persist_session=False),
    )
    if not intro_target.is_file() or not main_target.is_file():
        raise RuntimeError("No se generaron ambas capturas de la secuencia de inicio.")
    return intro_target, main_target


def main() -> int:
    parser = argparse.ArgumentParser(description="Captura intro y ventana principal de Tkinter.")
    parser.add_argument("--output-dir", type=Path, default=Path("Documentos") / "EVIDENCIA_INTRO")
    args = parser.parse_args()
    intro, main_window = capture_sequence(args.output_dir.resolve())
    print(f"Intro: {intro}")
    print(f"Ventana principal: {main_window}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
