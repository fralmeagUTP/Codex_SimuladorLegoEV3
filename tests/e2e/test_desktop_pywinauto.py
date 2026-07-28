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
def test_desktop_startup_shows_intro_before_main_window() -> None:
    """Comprueba que la intro ocupa el arranque y que no deja ventanas residuales."""

    pytest.importorskip("pywinauto")
    from pywinauto import Desktop
    from pywinauto.application import Application

    root = Path(__file__).resolve().parents[2]
    application = Application(backend="win32").start(
        cmd_line=f'"{sys.executable}" -m simulador_ev3.ui.main_window',
        work_dir=str(root),
        wait_for_idle=False,
    )
    desktop = Desktop(backend="win32")
    main = application.window(title="Simulador EV3 Pybricks")
    try:
        # Durante la intro existe una sola ventana visible del proceso y la
        # ventana principal aún no debe ser interactuable.
        assert not main.exists(timeout=1)
        visible = [window for window in application.windows() if window.is_visible()]
        if not visible:
            pytest.skip("el entorno no expone la ventana de introducción en un escritorio Windows visible")
        assert len(visible) == 1

        main.wait("visible", timeout=8)
        main.set_focus()
        visible_main = [
            window for window in desktop.windows(process=application.process)
            if window.is_visible() and window.window_text() == "Simulador EV3 Pybricks"
        ]
        assert len(visible_main) == 1
    finally:
        try:
            application.kill()
        except Exception:  # noqa: BLE001
            pass


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


@pytest.mark.skipif(not _desktop_e2e_enabled(), reason="requiere EV3_RUN_DESKTOP_E2E=1 y escritorio Windows")
def test_desktop_menus_unlock_after_execution_finishes_or_resets() -> None:
    """Evita que una ejecución terminal deje la navegación de Tkinter bloqueada."""

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

        archivo = main.child_window(title="Archivo", class_name="Menubutton")
        run = main.child_window(title="Ejecutar", control_type="Button")
        stop = main.child_window(title="Detener y reiniciar", control_type="Button")
        for control in (archivo, run):
            control.wait("enabled", timeout=8)

        run.click_input()
        archivo.wait_not("enabled", timeout=5)

        stop.wait("enabled", timeout=8)
        stop.click_input()
        archivo.wait("enabled", timeout=8)

        run.click_input()
        archivo.wait_not("enabled", timeout=5)
        # El script inicial es finito; cuando termina de forma natural, la
        # navegación debe reactivarse sin requerir un nuevo reinicio manual.
        archivo.wait("enabled", timeout=15)
    finally:
        try:
            application.kill()
        except Exception:  # noqa: BLE001
            pass
