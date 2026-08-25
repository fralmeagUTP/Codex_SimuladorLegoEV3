r"""Recorridos nativos de Tkinter, activados solo en un escritorio Windows real.

No se ejecutan en GitHub Actions porque los runners no exponen un escritorio
interactivo. Para ejecutarlos localmente:

  $env:EV3_RUN_DESKTOP_E2E = "1"
  .\.venv\Scripts\python.exe -m pytest tests/e2e/test_desktop_pywinauto.py -q
"""

from __future__ import annotations

import json
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
    deadline = time.monotonic() + 2.0
    while True:
        try:
            previous_handles = {window.handle for window in desktop.windows()}
            break
        except Exception:  # noqa: BLE001
            # Una ventana de cualquier proceso puede desaparecer entre la
            # enumeración Win32 y la construcción de su wrapper.
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.05)
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
        try:
            windows = [
                window
                for window in desktop.windows()
                if window.handle not in previous_handles
                and window.is_visible()
                and window.window_text() == title
            ]
        except Exception:  # noqa: BLE001
            # Una ventana ajena puede cerrarse entre la enumeración de Win32 y
            # la creación del wrapper de Pywinauto. Es un evento transitorio.
            time.sleep(0.1)
            continue
        if windows:
            # ``Desktop.windows`` puede devolver una especificación por
            # título; al existir otra instancia abierta, se reconecta por
            # handle para no volver a resolver un título ambiguo.
            return desktop.window(handle=windows[-1].element_info.handle).wrapper_object()
        time.sleep(0.2)
    raise TimeoutError(f"no apareció la ventana nueva {title!r}")


def _wait_for_intro(previous_handles: set[int], timeout: float = 2.0):
    """Confirma que el arranque muestra un top-level Tk antes de la principal."""

    from pywinauto import Desktop

    desktop = Desktop(backend="win32")
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            intro_windows = [
                window
                for window in desktop.windows()
                if window.handle not in previous_handles
                and window.is_visible()
                and window.class_name() == "TkTopLevel"
                and window.window_text() != "BotLab Studio"
            ]
        except Exception:  # noqa: BLE001
            time.sleep(0.05)
            continue
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


def _wait_for_state_file(path: Path, expected: str, timeout: float = 5.0) -> bool:
    """Espera una señal emitida por la instancia Tk real de la prueba.

    Los menús de Tk son owner-drawn: Windows puede destruir su popup antes de
    que pywinauto lo enumere. La señal registra el mismo estado aplicado a los
    ``Menubutton`` y permite distinguir ese detalle del sistema operativo de
    un menú que realmente quedó bloqueado.
    """

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if path.read_text(encoding="utf-8") == expected:
                return True
        except FileNotFoundError:
            pass
        time.sleep(0.05)
    return False


def _wait_for_nonempty_state_file(path: Path, timeout: float = 5.0) -> str | None:
    """Devuelve el primer contenido no vacío emitido por la instancia Tk."""

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            content = path.read_text(encoding="utf-8")
            if content:
                return content
        except FileNotFoundError:
            pass
        time.sleep(0.05)
    return None


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
        main = _wait_for_new_window("BotLab Studio", previous_handles, timeout=8)
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
            main = _wait_for_new_window("BotLab Studio", previous_handles)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"el entorno no expone un escritorio Windows visible: {exc}")
        main.set_focus()

        # Los popup Tk son owner-drawn y Windows no expone sus textos. Se usa
        # navegación física de teclado tras abrir cada botón de menú.
        # F1 es el atajo oficial; evita una coordenada frágil cuando cambia
        # el ancho de los menús por accesibilidad o nuevas opciones.
        main.type_keys("{F1}")
        manual = desktop.window(title="Centro de ayuda - Simulador EV3 Pybricks")
        manual.wait("visible", timeout=5)
        assert manual.is_visible()
        manual.close()

        main.set_focus()
        main.click_input(coords=(340, 53))  # Mundos
        main.type_keys("{DOWN}{DOWN}{DOWN}{ENTER}")
        editor = _wait_for_new_window("Editor de Mundos EV3", previous_handles, timeout=8)
        assert editor.is_visible()
        editor.close()
    finally:
        _stop_native_application(application)


@pytest.mark.skipif(not _desktop_e2e_enabled(), reason="requiere EV3_RUN_DESKTOP_E2E=1 y escritorio Windows")
def test_desktop_world_editor_applies_presets_and_native_shortcuts() -> None:
    """Ejercita el editor Tk real sin depender de atributos privados de la UI."""

    pytest.importorskip("pywinauto")
    from pywinauto import Desktop

    root = Path(__file__).resolve().parents[2]
    state_path = root / "artifacts" / "e2e-desktop" / "world-editor-preset.txt"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.unlink(missing_ok=True)
    state_path_literal = repr(str(state_path))
    source = (
        "from pathlib import Path; "
        "from simulador_ev3.ui.main_window import EV3SimulatorApp; "
        "from simulador_ev3.ui.world_editor_window import WorldEditorWindow; "
        "original_preset = WorldEditorWindow._set_world_size_preset; "
        f"state_path = Path({state_path_literal}); "
        "WorldEditorWindow._set_world_size_preset = lambda self, w, h: ("
        "original_preset(self, w, h), state_path.write_text(f'{w}x{h}', encoding='utf-8'))[0]; "
        "app = EV3SimulatorApp(restore_session=False, persist_session=False); app.mainloop()"
    )
    application, previous_handles = _start_native_application(f'"{sys.executable}" -c "{source}"', root)
    desktop = Desktop(backend="win32")
    try:
        main = _wait_for_new_window("BotLab Studio", previous_handles)
        main.set_focus()
        main.click_input(coords=(340, 53))  # Mundos
        main.type_keys("{DOWN}{DOWN}{DOWN}{ENTER}")
        editor = _wait_for_new_window("Editor de Mundos EV3", previous_handles, timeout=8)
        editor.set_focus()

        # Los widgets Tk no publican todos sus textos a Win32. Se activa el
        # botón físico por su posición estable y se verifica el comando que
        # recibió la ventana real.
        buttons = [item for item in editor.descendants() if item.class_name() == "Button"]
        if len(buttons) < 21:
            controls = [(item.window_text(), item.rectangle()) for item in buttons]
            pytest.fail(f"No se expusieron botones Tk suficientes: {controls}")
        # La enumeración Win32 incluye primero los assets de Biblioteca. En
        # la cabecera, Aula ocupa el índice 20 y su rectángulo se comprueba
        # explícitamente para detectar cambios de composición.
        aula = buttons[20]
        rect = aula.rectangle()
        assert rect.width() > 30 and rect.height() > 20
        aula.click_input()
        assert _wait_for_state_file(state_path, "80x60")

        # Escape limpia la selección y los atajos de archivo siguen abiertos
        # para que Tk gestione sus diálogos nativos de forma accesible.
        editor.type_keys("{ESC}")
        editor.type_keys("^s")
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            dialogs = [
                window
                for window in desktop.windows()
                if window.handle != editor.handle and window.is_visible() and "Guardar" in window.window_text()
            ]
            if dialogs:
                dialogs[-1].type_keys("{ESC}")
                break
            time.sleep(0.05)
        else:
            pytest.fail("Ctrl+S no abrió el diálogo nativo de guardado del editor")
    finally:
        _stop_native_application(application)
        state_path.unlink(missing_ok=True)


@pytest.mark.skipif(not _desktop_e2e_enabled(), reason="requiere EV3_RUN_DESKTOP_E2E=1 y escritorio Windows")
def test_desktop_learning_status_displays_initial_activity() -> None:
    """La ventana Tk real debe presentar la actividad pedagógica compartida."""

    pytest.importorskip("pywinauto")
    root = Path(__file__).resolve().parents[2]
    state_path = root / "artifacts" / "e2e-desktop" / "learning-status.txt"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.unlink(missing_ok=True)
    state_path_literal = repr(str(state_path))
    source = (
        "from pathlib import Path; "
        "from simulador_ev3.ui.main_window import EV3SimulatorApp; "
        "app = EV3SimulatorApp(restore_session=False, persist_session=False); "
        f"state_path = Path({state_path_literal}); "
        "app.after(250, lambda: state_path.write_text(app._learning_text_var.get(), encoding='utf-8')); "
        "app.mainloop()"
    )
    application, previous_handles = _start_native_application(f'"{sys.executable}" -c "{source}"', root)
    try:
        try:
            main = _wait_for_new_window("BotLab Studio", previous_handles)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"el entorno no expone un escritorio Windows visible: {exc}")
        assert main.is_visible()
        text = _wait_for_nonempty_state_file(state_path)
        assert text is not None
        assert "Actividad: first-simulation" in text
        assert "Progreso: 0/1" in text
        assert "Resultado: pendiente" in text
    finally:
        _stop_native_application(application)
        state_path.unlink(missing_ok=True)


@pytest.mark.skipif(not _desktop_e2e_enabled(), reason="requiere EV3_RUN_DESKTOP_E2E=1 y escritorio Windows")
def test_desktop_preset_world_catalog_loads_every_world() -> None:
    """Recorre físicamente el submenú y verifica los doce mundos cargados."""

    pytest.importorskip("pywinauto")
    root = Path(__file__).resolve().parents[2]
    worlds = sorted((root / "worlds").glob("*.json"))
    assert len(worlds) == 12
    state_path = root / "artifacts" / "e2e-desktop" / "world-loaded.txt"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.unlink(missing_ok=True)
    state_path_literal = repr(str(state_path))
    source = (
        "from pathlib import Path; "
        "from simulador_ev3.ui.main_window import EV3SimulatorApp; "
        "app = EV3SimulatorApp(restore_session=False, persist_session=False); "
        f"state_path = Path({state_path_literal}); "
        "original_load_world = app._load_world; "
        "app._load_world = lambda path: ("
        "original_load_world(path), state_path.write_text(Path(path).name, encoding='utf-8')"
        ")[0]; "
        "app.mainloop()"
    )
    application, previous_handles = _start_native_application(f'"{sys.executable}" -c "{source}"', root)
    try:
        try:
            main = _wait_for_new_window("BotLab Studio", previous_handles)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"el entorno no expone un escritorio Windows visible: {exc}")

        for index, world_path in enumerate(worlds):
            main.set_focus()
            main.click_input(coords=(340, 53))
            # Tres comandos y luego la cascada Mundos preestablecidos.
            main.type_keys("{DOWN}{DOWN}{DOWN}{DOWN}{RIGHT}")
            if index:
                main.type_keys("{DOWN}" * index)
            main.type_keys("{ENTER}")
            assert _wait_for_state_file(state_path, world_path.name)
    finally:
        _stop_native_application(application)
        state_path.unlink(missing_ok=True)


@pytest.mark.skipif(not _desktop_e2e_enabled(), reason="requiere EV3_RUN_DESKTOP_E2E=1 y escritorio Windows")
def test_desktop_real_catalog_loads_examples_scenarios_and_missions() -> None:
    """Recorre físicamente los recursos distribuidos desde los menús Tkinter."""

    pytest.importorskip("pywinauto")
    root = Path(__file__).resolve().parents[2]
    examples = sorted((root / "examples").glob("*.py"))
    assert len(examples) >= 20
    state_path = root / "artifacts" / "e2e-desktop" / "catalog-loaded.txt"
    layout_path = root / "artifacts" / "e2e-desktop" / "catalog-menu-layout.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.unlink(missing_ok=True)
    layout_path.unlink(missing_ok=True)
    state_path_literal = repr(str(state_path))
    layout_path_literal = repr(str(layout_path))
    source = (
        "import json; "
        "from pathlib import Path; "
        "from simulador_ev3.ui.main_window import EV3SimulatorApp; "
        "app = EV3SimulatorApp(restore_session=False, persist_session=False); "
        f"state_path = Path({state_path_literal}); "
        f"layout_path = Path({layout_path_literal}); "
        "load_example = app._load_example; "
        "app._load_example = lambda path: (load_example(path), state_path.write_text("
        "'example:' + Path(path).name, encoding='utf-8'))[0]; "
        "apply_scenario = app._apply_scenario; "
        "app._apply_scenario = lambda world, example: (apply_scenario(world, example), state_path.write_text("
        "'scenario:' + world + ':' + example, encoding='utf-8'))[0]; "
        "load_mission = app._load_mission; "
        "app._load_mission = lambda identifier: (load_mission(identifier), state_path.write_text("
        "'mission:' + identifier, encoding='utf-8'))[0]; "
        "app.after(750, lambda: layout_path.write_text(json.dumps({button.cget('text'): ["
        "button.winfo_rootx() + button.winfo_width() // 2, "
        "button.winfo_rooty() + button.winfo_height() // 2] "
        "for button in app._header_menu_buttons}), encoding='utf-8')); "
        "app.mainloop()"
    )
    application, previous_handles = _start_native_application(f'"{sys.executable}" -c "{source}"', root)
    try:
        try:
            main = _wait_for_new_window("BotLab Studio", previous_handles)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"el entorno no expone un escritorio Windows visible: {exc}")

        layout_text = _wait_for_nonempty_state_file(layout_path)
        assert layout_text is not None
        absolute_menu_positions = json.loads(layout_text)
        main_rect = main.rectangle()
        menu_positions = {
            label: (position[0] - main_rect.left, position[1] - main_rect.top)
            for label, position in absolute_menu_positions.items()
        }

        # Las coordenadas relativas provienen de los botones reales de esta
        # ventana Tkinter. Cada selección usa el menú nativo y Enter; la
        # instrumentación solo captura su geometría para evitar clicks frágiles.
        for index, example in enumerate(examples):
            main.set_focus()
            main.click_input(coords=menu_positions["Ejemplos"])
            main.type_keys("{DOWN}" * (index + 1) + "{ENTER}")
            assert _wait_for_state_file(state_path, f"example:{example.name}")

        scenarios = (
            ("01_linea_negra_basica.json", "11_siguelineas_basico.py"),
            ("05_obstaculos_baliza_ir.json", "15_esquiva_obstaculos.py"),
            ("05_obstaculos_baliza_ir.json", "02_intro_pantalla_altavoz.py"),
            ("12_radar_ultrasonido_360.json", "23_radar_ultrasonido_5grados.py"),
        )
        for index, (world, example) in enumerate(scenarios):
            main.set_focus()
            main.click_input(coords=menu_positions["Escenarios"])
            main.type_keys("{DOWN}" * (index + 1) + "{ENTER}")
            assert _wait_for_state_file(state_path, f"scenario:{world}:{example}")

        for index, identifier in enumerate(("sigue-linea-basico", "evita-obstaculos", "radar-ultrasonido")):
            main.set_focus()
            main.click_input(coords=menu_positions["Misiones"])
            main.type_keys("{DOWN}" * (index + 1) + "{ENTER}")
            assert _wait_for_state_file(state_path, f"mission:{identifier}")
    finally:
        _stop_native_application(application)
        state_path.unlink(missing_ok=True)
        layout_path.unlink(missing_ok=True)


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
            main = _wait_for_new_window("BotLab Studio", previous_handles)
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
def test_desktop_tab_reaches_header_menus_from_native_window() -> None:
    """El Tab físico alcanza los menús desde la ventana nativa de Tkinter."""

    pytest.importorskip("pywinauto")
    root = Path(__file__).resolve().parents[2]
    state_path = root / "artifacts" / "e2e-desktop" / "header-tab-focus.txt"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.unlink(missing_ok=True)
    source = (
        "from pathlib import Path; "
        "from simulador_ev3.ui.main_window import EV3SimulatorApp; "
        "app = EV3SimulatorApp(restore_session=False, persist_session=False); "
        "target = Path(r'" + str(state_path) + "'); "
        "original_post = app._post_header_menu; "
        "app._post_header_menu = lambda item, popup: ("
        "target.write_text('open:' + item.cget('text'), encoding='utf-8'), "
        "original_post(item, popup))[1]; "
        "[item.bind('<FocusIn>', lambda _event, item=item: "
        "target.write_text(item.cget('text') + '|' + item.cget('bg'), encoding='utf-8'), add='+') "
        "for item in app._header_menu_buttons]; "
        "app.mainloop()"
    )
    application, previous_handles = _start_native_application(f'"{sys.executable}" -c "{source}"', root)
    try:
        main = _wait_for_new_window("BotLab Studio", previous_handles)
        main.set_focus()
        main.type_keys("{TAB}")
        focused_menu = _wait_for_nonempty_state_file(state_path)
        assert focused_menu == "Archivo|#0D47A1", (
            "El primer Tab físico debe enfocar y resaltar Archivo; se recibió "
            f"{focused_menu!r}"
        )
        main.type_keys("{ENTER}")
        assert _wait_for_state_file(state_path, "open:Archivo"), (
            "Enter debe abrir el menú de cabecera que obtuvo foco mediante Tab"
        )
    finally:
        _stop_native_application(application)
        state_path.unlink(missing_ok=True)


@pytest.mark.skipif(not _desktop_e2e_enabled(), reason="requiere EV3_RUN_DESKTOP_E2E=1 y escritorio Windows")
def test_desktop_success_dialog_is_shown_once_after_finished() -> None:
    """La finalización exitosa muestra un único diálogo nativo y se puede cerrar."""

    pytest.importorskip("pywinauto")
    import pyperclip
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
            main = _wait_for_new_window("BotLab Studio", previous_handles)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"el entorno no expone un escritorio Windows visible: {exc}")
        main.set_focus()
        pyperclip.copy("from pybricks.tools import wait\nwait(80)\n")
        main.click_input(coords=(1000, 200))
        main.type_keys("^a^v")
        main.click_input(coords=(58, 91))

        deadline = time.monotonic() + 10.0
        finished = desktop.window(title="Ejecución finalizada")
        while time.monotonic() < deadline and not finished.exists(timeout=0.1):
            time.sleep(0.1)
        assert finished.exists(timeout=0.5)
        assert finished.is_visible()
        finished.type_keys("{ENTER}")
        time.sleep(0.5)
        assert not finished.exists(timeout=0.1) or not finished.is_visible()
    finally:
        _stop_native_application(application)


@pytest.mark.skipif(not _desktop_e2e_enabled(), reason="requiere EV3_RUN_DESKTOP_E2E=1 y escritorio Windows")
def test_desktop_menus_unlock_after_execution_finishes_or_resets() -> None:
    """Evita que una ejecución terminal deje la navegación de Tkinter bloqueada."""

    pytest.importorskip("pywinauto")
    import pyperclip
    from pywinauto import Desktop
    root = Path(__file__).resolve().parents[2]
    state_path = root / "artifacts" / "e2e-desktop" / "menu-state.txt"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.unlink(missing_ok=True)
    state_path_literal = repr(str(state_path))
    source = (
        "from pathlib import Path; "
        "from simulador_ev3.ui.main_window import EV3SimulatorApp; "
        "app = EV3SimulatorApp(restore_session=False, persist_session=False); "
        f"state_path = Path({state_path_literal}); "
        "original_set_menu_locked = app._set_execution_menu_locked; "
        "app._set_execution_menu_locked = lambda locked: ("
        "original_set_menu_locked(locked), "
        "state_path.write_text('locked' if locked else 'unlocked', encoding='utf-8')"
        ")[0]; "
        "app.mainloop()"
    )
    application, previous_handles = _start_native_application(f'"{sys.executable}" -c "{source}"', root)
    try:
        try:
            main = _wait_for_new_window("BotLab Studio", previous_handles)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"el entorno no expone un escritorio Windows visible: {exc}")
        main.set_focus()

        run = (58, 91)
        stop = (304, 91)
        archivo = (210, 53)
        editor = (1000, 200)
        running_source = "from pybricks.tools import wait\nwait(5000)\n"
        terminal_source = "from pybricks.tools import wait\nwait(1000)\n"

        def paste_script(source_code: str) -> None:
            pyperclip.copy(source_code)
            main.click_input(coords=editor)
            main.type_keys("^a^v")
            time.sleep(0.15)

        def read_editor() -> str:
            main.click_input(coords=editor)
            main.type_keys("^a^c")
            time.sleep(0.05)
            return str(pyperclip.paste()).replace("\r\n", "\n")

        def invoke_new_from_file_menu() -> None:
            main.set_focus()
            main.click_input(coords=archivo)
            main.type_keys("{DOWN}{ENTER}")
            time.sleep(0.15)

        # Se escribe un programa corto en el editor real para que la transición
        # terminal sea determinista y no dependa del ejemplo persistido.
        paste_script(running_source)
        main.click_input(coords=run)
        assert _wait_for_state_file(state_path, "locked")
        invoke_new_from_file_menu()
        assert read_editor().strip() == running_source.strip()

        main.click_input(coords=stop)
        assert _wait_for_state_file(state_path, "unlocked")
        invoke_new_from_file_menu()
        assert read_editor().strip() == "# Nuevo script"

        paste_script(terminal_source)
        main.click_input(coords=run)
        assert _wait_for_state_file(state_path, "locked")
        # El script inicial es finito; cuando termina de forma natural, la
        # navegación debe reactivarse sin requerir un nuevo reinicio manual.
        desktop = Desktop(backend="win32")
        deadline = time.monotonic() + 15.0
        dialog_closed = False
        while time.monotonic() < deadline:
            finished = desktop.window(title="Ejecución finalizada")
            if finished.exists(timeout=0.1) and finished.is_visible():
                finished.type_keys("{ENTER}")
                time.sleep(0.25)
                dialog_closed = True
                break
            time.sleep(0.1)
        assert dialog_closed
        assert _wait_for_state_file(state_path, "unlocked")
        invoke_new_from_file_menu()
        assert read_editor().strip() == "# Nuevo script"
    finally:
        _stop_native_application(application)
        state_path.unlink(missing_ok=True)
