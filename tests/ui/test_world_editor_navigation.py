from pathlib import Path
from unittest.mock import Mock

from simulador_ev3.application.world_editor_service import WorldEditorService
from simulador_ev3.ui.world_editor_window import WorldEditorWindow


def _editor_for_navigation(path: Path, issues: list[str] | None = None) -> WorldEditorWindow:
    editor = object.__new__(WorldEditorWindow)
    service = Mock(spec=WorldEditorService)
    service.validate_current_world.return_value = issues or []
    editor._service = service
    editor._current_path = path
    editor._set_status = Mock()
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
