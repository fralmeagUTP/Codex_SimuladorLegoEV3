from pathlib import Path
from unittest.mock import Mock, patch

from simulador_ev3.application.world_editor_service import WorldEditorService
from simulador_ev3.ui.world_editor_window import WorldEditorWindow

_EDITOR_GLOBALS = WorldEditorWindow._cmd_delete_world_file.__globals__
_EDITOR_MESSAGEBOX = _EDITOR_GLOBALS["messagebox"]


def _editor_for_navigation(path: Path, issues: list[str] | None = None) -> WorldEditorWindow:
    editor = object.__new__(WorldEditorWindow)
    service = Mock(spec=WorldEditorService)
    service.validate_current_world.return_value = issues or []
    editor._service = service
    editor._current_path = path
    editor._set_status = Mock()
    editor._toolbar = Mock()
    editor._props = Mock()
    editor._sync_world_size_inputs = Mock()
    editor._refresh_canvas = Mock()
    editor._selected_id = None
    return editor


def test_simulate_saved_world_calls_public_navigation_callback(tmp_path: Path) -> None:
    callback = Mock()
    editor = _editor_for_navigation(tmp_path / "mundo.json")
    editor._on_simulate_saved = callback

    editor._cmd_simulate_saved()

    callback.assert_called_once_with(str(tmp_path / "mundo.json"))
    assert "Mundo aplicado a simulación" in editor._set_status.call_args.args[0]


def test_invalid_world_is_not_applied_to_simulation(tmp_path: Path) -> None:
    callback = Mock()
    editor = _editor_for_navigation(tmp_path / "mundo.json", issues=["Robot fuera de límites"])
    editor._on_simulate_saved = callback
    editor._refresh_validation_status = Mock()

    editor._cmd_simulate_saved()

    callback.assert_not_called()
    editor._refresh_validation_status.assert_called_once()


def test_delete_current_custom_world_resets_editor_after_confirmation(tmp_path: Path) -> None:
    world_path = tmp_path / "practica.json"
    world_path.write_text("{}", encoding="utf-8")
    editor = _editor_for_navigation(world_path)

    with patch.dict(_EDITOR_GLOBALS, {"_WORLDS_DIR": tmp_path}), patch.object(
        _EDITOR_MESSAGEBOX, "askyesno", return_value=True
    ):
        editor._cmd_delete_world_file()

    assert not world_path.exists()
    editor._service.reset_formal_world.assert_called_once()
    editor._props.set_object.assert_called_once_with(None)
    editor._sync_world_size_inputs.assert_called_once()
    editor._refresh_canvas.assert_called_once()
    editor._toolbar.set_delete_world_file_enabled.assert_called_once_with(False)
    editor._toolbar.set_simulate_saved_enabled.assert_called_once_with(False)
    assert "Mundo eliminado: practica.json" in editor._set_status.call_args.args[0]


def test_builtin_world_cannot_be_deleted(tmp_path: Path) -> None:
    editor = _editor_for_navigation(tmp_path / "01_linea_negra_basica.json")
    with patch.object(WorldEditorWindow, "_is_builtin_world_path", return_value=True), patch.object(
        _EDITOR_MESSAGEBOX, "showwarning", create=True
    ) as show_warning:
        editor._cmd_delete_world_file()

    show_warning.assert_called_once()
    editor._service.reset_formal_world.assert_not_called()


def test_world_outside_configured_directory_cannot_be_deleted(tmp_path: Path) -> None:
    external = tmp_path / "externo"
    external.mkdir()
    path = external / "practica.json"
    path.write_text("{}", encoding="utf-8")
    editor = _editor_for_navigation(path)

    with patch.dict(_EDITOR_GLOBALS, {"_WORLDS_DIR": tmp_path}), patch.object(
        _EDITOR_MESSAGEBOX, "showwarning", create=True
    ) as show_warning:
        editor._cmd_delete_world_file()

    assert path.exists()
    show_warning.assert_called_once()
    editor._service.reset_formal_world.assert_not_called()


def test_desktop_world_editor_declares_equivalent_shortcuts_and_empty_canvas_guide() -> None:
    source = Path(WorldEditorWindow.__module__.replace(".", "/") + ".py")
    # Se consulta el archivo real del módulo sin requerir una ventana gráfica.
    editor_source = (Path(__file__).parents[2] / "simulador_ev3" / "ui" / "world_editor_window.py").read_text(
        encoding="utf-8"
    )

    assert source.name == "world_editor_window.py"
    assert "def _bind_shortcuts" in editor_source
    shortcuts = (
        "<Control-n>",
        "<Control-o>",
        "<Control-s>",
        "<Control-Shift-S>",
        "<Control-d>",
        "<Delete>",
        "<Escape>",
    )
    for shortcut in shortcuts:
        assert shortcut in editor_source
    canvas_source = (Path(__file__).parents[2] / "simulador_ev3" / "ui" / "world_canvas_editor.py").read_text(
        encoding="utf-8"
    )
    assert "Comienza a crear tu mundo" in canvas_source
    assert "def _draw_empty_world_guide" in canvas_source
