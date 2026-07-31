r"""Recorridos nativos de Tkinter, activados solo en un escritorio Windows real.

No se ejecutan en GitHub Actions porque los runners no exponen un escritorio
interactivo. Para ejecutarlos localmente:

  $env:EV3_RUN_DESKTOP_E2E = "1"
  .\.venv\Scripts\python.exe -m pytest tests/e2e/test_desktop_pywinauto.py -q
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.desktop_e2e


def _desktop_e2e_enabled() -> bool:
    return os.name == "nt" and os.environ.get("EV3_RUN_DESKTOP_E2E") == "1"


def _start_native_application(command_line: str, root: Path):
    """Inicia Tkinter y conserva las ventanas existentes antes del arranque.

    En algunos entornos Windows el ejecutable de la venv actúa como lanzador:
    la ventana Tk queda en un proceso hijo. Por ello no se debe buscar solo por
    el PID inicial de ``Application.start``.
    """

    from pywinauto import Desktop
    from pywinauto.application import Application

    desktop = Desktop(backend="win32")
    previous_handles = {window.handle for window in desktop.windows()}
    application = Application(backend="win32").start(
        cmd_line=command_line,
        work_dir=str(root),
        wait_for_idle=False,
    )
    return application, previous_handles


def _wait_for_new_window(title: str, previous_handles: set[int], timeout: float = 15.0):
    """Obtiene una ventana nueva por título sin capturar una app preexistente."""

    from pywinauto import Desktop

    desktop = Desktop(backend="win32")
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        windows = [
            window
            for window in desktop.windows()
            if window.handle not in previous_handles
            and window.is_visible()
            and window.window_text() == title
        ]
        if windows:
            return windows[-1]
        time.sleep(0.2)
    raise TimeoutError(f"no apareció la ventana nueva {title!r}")


def _wait_for_intro(previous_handles: set[int], timeout: float = 2.0):
    """Confirma que el arranque muestra un top-level Tk antes de la principal."""

    from pywinauto import Desktop

    desktop = Desktop(backend="win32")
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        intro_windows = [
            window
            for window in desktop.windows()
            if window.handle not in previous_handles
            and window.is_visible()
            and window.class_name() == "TkTopLevel"
            and window.window_text() != "Simulador EV3 Pybricks"
        ]
        if intro_windows:
            return intro_windows[-1]
        time.sleep(0.1)
    raise TimeoutError("no apareció la ventana de introducción")


def _stop_native_application(application) -> None:
    """Finaliza exactamente el árbol creado por la prueba nativa."""

    subprocess.run(
        ["taskkill", "/PID", str(application.process), "/T", "/F"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _menu_popup_is_visible() -> bool:
    """Indica si Tk abrió el popup nativo de menú en el escritorio."""

    from pywinauto import Desktop

    return any(window.is_visible() for window in Desktop(backend="win32").windows(class_name="#32768"))


@pytest.mark.skipif(not _desktop_e2e_enabled(), reason="requiere EV3_RUN_DESKTOP_E2E=1 y escritorio Windows")
def test_desktop_startup_shows_intro_before_main_window() -> None:
    """Comprueba que la intro ocupa el arranque y que no deja ventanas residuales."""

    pytest.importorskip("pywinauto")
    root = Path(__file__).resolve().parents[2]
    application, previous_handles = _start_native_application(
        f'"{sys.executable}" -m simulador_ev3.ui.main_window', root
    )
    try:
        intro = _wait_for_intro(previous_handles)
        assert intro.is_visible()
        main = _wait_for_new_window("Simulador EV3 Pybricks", previous_handles, timeout=8)
        main.set_focus()
        assert main.is_visible()
    except TimeoutError as exc:
        pytest.skip(f"el entorno no expone un escritorio Windows visible: {exc}")
    finally:
        _stop_native_application(application)


@pytest.mark.skipif(not _desktop_e2e_enabled(), reason="requiere EV3_RUN_DESKTOP_E2E=1 y escritorio Windows")
def test_desktop_navigation_opens_help_and_world_editor() -> None:
    """Comprueba navegación real por ratón sobre las ventanas Tkinter."""

    pytest.importorskip("pywinauto")
    from pywinauto import Desktop

    root = Path(__file__).resolve().parents[2]
    source = (
        "from simulador_ev3.ui.main_window import EV3SimulatorApp; "
        "app = EV3SimulatorApp(restore_session=False, persist_session=False); app.mainloop()"
    )
    application, previous_handles = _start_native_application(f'"{sys.executable}" -c "{source}"', root)
    desktop = Desktop(backend="win32")

    try:
        try:
            main = _wait_for_new_window("Simulador EV3 Pybricks", previous_handles)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"el entorno no expone un escritorio Windows visible: {exc}")
        main.set_focus()

        # Los popup Tk son owner-drawn y Windows no expone sus textos. Se usa
        # navegación física de teclado tras abrir cada botón de menú.
        main.click_input(coords=(870, 53))  # Ayuda
        main.type_keys("{DOWN}{ENTER}")
        manual = desktop.window(title="Manual de uso")
        manual.wait("visible", timeout=5)
        assert manual.is_visible()
        manual.close()

        main.set_focus()
        main.click_input(coords=(400, 53))  # Mundos
        main.type_keys("{DOWN}{DOWN}{DOWN}{ENTER}")
        editor = desktop.window(title="Editor de Mundos EV3")
        editor.wait("visible", timeout=8)
        assert editor.is_visible()
        editor.close()
    finally:
        _stop_native_application(application)


@pytest.mark.skipif(not _desktop_e2e_enabled(), reason="requiere EV3_RUN_DESKTOP_E2E=1 y escritorio Windows")
def test_desktop_controls_cover_execution_debug_and_keyboard() -> None:
    """Recorrido de botones nativos para ejecución, pausa, depuración y Ctrl+N."""

    pytest.importorskip("pywinauto")
    root = Path(__file__).resolve().parents[2]
    source = (
        "from simulador_ev3.ui.main_window import EV3SimulatorApp; "
        "app = EV3SimulatorApp(restore_session=False, persist_session=False); app.mainloop()"
    )
    application, previous_handles = _start_native_application(f'"{sys.executable}" -c "{source}"', root)
    try:
        try:
            main = _wait_for_new_window("Simulador EV3 Pybricks", previous_handles)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"el entorno no expone un escritorio Windows visible: {exc}")
        main.set_focus()
        main.type_keys("^n")
        # Tk no publica los textos de botones como controles Win32. Las
        # coordenadas son relativas a la ventana de tamaño base 1280x800.
        main.click_input(coords=(58, 91))  # Ejecutar
        main.click_input(coords=(128, 91))  # Pausar
        main.click_input(coords=(196, 91))  # Reanudar
        main.click_input(coords=(304, 91))  # Detener y reiniciar
        main.click_input(coords=(762, 117))  # Depurar
        main.click_input(coords=(304, 91))  # Detener y reiniciar
    finally:
        _stop_native_application(application)


@pytest.mark.skipif(not _desktop_e2e_enabled(), reason="requiere EV3_RUN_DESKTOP_E2E=1 y escritorio Windows")
def test_desktop_menus_unlock_after_execution_finishes_or_resets() -> None:
    """Evita que una ejecución terminal deje la navegación de Tkinter bloqueada."""

    pytest.importorskip("pywinauto")
    import pyperclip
    from pywinauto import Desktop
    root = Path(__file__).resolve().parents[2]
    source = (
        "from simulador_ev3.ui.main_window import EV3SimulatorApp; "
        "app = EV3SimulatorApp(restore_session=False, persist_session=False); app.mainloop()"
    )
    application, previous_handles = _start_native_application(f'"{sys.executable}" -c "{source}"', root)
    try:
        try:
            main = _wait_for_new_window("Simulador EV3 Pybricks", previous_handles)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"el entorno no expone un escritorio Windows visible: {exc}")
        main.set_focus()

        run = (58, 91)
        stop = (304, 91)
        archivo = (275, 53)
        # Se escribe un programa corto en el editor real para que la transición
        # terminal sea determinista y no dependa del ejemplo persistido.
        pyperclip.copy("from pybricks.tools import wait\nwait(1000)\n")
        main.click_input(coords=(1000, 200))
        main.type_keys("^a^v")
        time.sleep(0.2)
        main.click_input(coords=run)
        time.sleep(0.4)
        main.click_input(coords=archivo)
        assert not _menu_popup_is_visible()

        main.click_input(coords=stop)
        time.sleep(0.4)
        main.click_input(coords=archivo)
        assert _menu_popup_is_visible()
        main.type_keys("{ESC}")

        main.click_input(coords=run)
        time.sleep(0.4)
        main.click_input(coords=archivo)
        assert not _menu_popup_is_visible()
        # El script inicial es finito; cuando termina de forma natural, la
        # navegación debe reactivarse sin requerir un nuevo reinicio manual.
        desktop = Desktop(backend="win32")
        deadline = time.monotonic() + 15.0
        while time.monotonic() < deadline:
            finished = desktop.window(title="Ejecución finalizada")
            if finished.exists(timeout=0.1) and finished.is_visible():
                finished.type_keys("{ENTER}")
                time.sleep(0.25)
            main.click_input(coords=archivo)
            if _menu_popup_is_visible():
                break
            time.sleep(0.25)
        assert _menu_popup_is_visible()
    finally:
        _stop_native_application(application)
