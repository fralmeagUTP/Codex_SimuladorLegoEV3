r"""Recorridos nativos de Tkinter, activados solo en un escritorio Windows real.

No se ejecutan en GitHub Actions porque los runners no exponen un escritorio
interactivo. Para ejecutarlos localmente:

  $env:EV3_RUN_DESKTOP_E2E = "1"
  .\.venv\Scripts\python.exe -m pytest tests/e2e/test_desktop_pywinauto.py -q
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.desktop_e2e


def _desktop_e2e_enabled() -> bool:
    return os.name == "nt" and os.environ.get("EV3_RUN_DESKTOP_E2E") == "1"


@pytest.mark.skipif(not _desktop_e2e_enabled(), reason="requiere EV3_RUN_DESKTOP_E2E=1 y escritorio Windows")
def test_desktop_navigation_opens_help_and_world_editor() -> None:
    """Comprueba navegación real por ratón sobre las ventanas Tkinter."""

    pytest.importorskip("pywinauto")
    from pywinauto import Desktop
    from pywinauto.application import Application

    root = Path(__file__).resolve().parents[2]
    source = (
        "from simulador_ev3.ui.main_window import EV3SimulatorApp; "
        "app = EV3SimulatorApp(restore_session=False, persist_session=False); app.mainloop()"
    )
    application = Application(backend="win32").start(
        cmd_line=f'"{sys.executable}" -c "{source}"',
        work_dir=str(root),
        wait_for_idle=False,
    )
    desktop = Desktop(backend="win32")
    main = application.window(title="Simulador EV3 Pybricks")

    try:
        try:
            main.wait("visible", timeout=15)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"el entorno no expone un escritorio Windows visible: {exc}")
        main.set_focus()

        # Los menús Tk clásicos no publican etiquetas UI Automation fiables;
        # se usan coordenadas relativas de la barra común de referencia 1280x800.
        main.click_input(coords=(372, 53))  # Ayuda
        help_menu = desktop.window(class_name="#32768")
        help_menu.wait("visible", timeout=5)
        help_menu.menu_item("Manual de uso...").click_input()
        manual = desktop.window(title="Manual de uso")
        manual.wait("visible", timeout=5)
        assert manual.is_visible()
        manual.close()

        main.set_focus()
        main.click_input(coords=(185, 53))  # Mundos
        worlds_menu = desktop.window(class_name="#32768")
        worlds_menu.wait("visible", timeout=5)
        worlds_menu.menu_item("Editor de mundos...").click_input()
        editor = desktop.window(title="Editor de Mundos EV3")
        editor.wait("visible", timeout=8)
        assert editor.is_visible()
        editor.close()
    finally:
        try:
            application.kill()
        except Exception:  # noqa: BLE001
            pass


@pytest.mark.skipif(not _desktop_e2e_enabled(), reason="requiere EV3_RUN_DESKTOP_E2E=1 y escritorio Windows")
def test_desktop_controls_cover_execution_debug_and_keyboard() -> None:
    """Recorrido de botones nativos para ejecución, pausa, depuración y Ctrl+N."""

    pytest.importorskip("pywinauto")
    from pywinauto.application import Application

    root = Path(__file__).resolve().parents[2]
    source = (
        "from simulador_ev3.ui.main_window import EV3SimulatorApp; "
        "app = EV3SimulatorApp(restore_session=False, persist_session=False); app.mainloop()"
    )
    application = Application(backend="win32").start(
        cmd_line=f'"{sys.executable}" -c "{source}"', work_dir=str(root), wait_for_idle=False
    )
    main = application.window(title="Simulador EV3 Pybricks")
    try:
        try:
            main.wait("visible", timeout=15)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"el entorno no expone un escritorio Windows visible: {exc}")
        main.set_focus()
        main.type_keys("^n")
        run = main.child_window(title="Ejecutar", control_type="Button")
        pause = main.child_window(title="Pausar", control_type="Button")
        resume = main.child_window(title="Reanudar", control_type="Button")
        stop = main.child_window(title="Detener y reiniciar", control_type="Button")
        debug = main.child_window(title="Depurar", control_type="Button")
        for control in (run, pause, resume, stop, debug):
            control.wait("enabled", timeout=8)
        run.click_input()
        pause.click_input()
        resume.click_input()
        stop.click_input()
        debug.click_input()
        stop.click_input()
    finally:
        try:
            application.kill()
        except Exception:  # noqa: BLE001
            pass
