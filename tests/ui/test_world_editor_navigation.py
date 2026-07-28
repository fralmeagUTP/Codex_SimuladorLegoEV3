from pathlib import Path
from unittest.mock import Mock, patch

from simulador_ev3.application.world_editor_service import WorldEditorService
from simulador_ev3.ui.world_editor_window import WorldEditorWindow


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

    with patch("simulador_ev3.ui.world_editor_window.messagebox.askyesno", return_value=True):
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
    with patch.object(WorldEditorWindow, "_is_builtin_world_path", return_value=True), patch(
        "simulador_ev3.ui.world_editor_window.messagebox.showwarning"
    ) as show_warning:
        editor._cmd_delete_world_file()

    show_warning.assert_called_once()
    editor._service.reset_formal_world.assert_not_called()
