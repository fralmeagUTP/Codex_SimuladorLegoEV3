"""Contrato estable de la sesión compartida del Editor de Mundos."""

from simulador_ev3.application.world_editor_session import WORLD_EDITOR_SESSION_VERSION, WorldEditorSession


def test_session_exposes_serializable_selection_layers_actions_and_dirty_state() -> None:
    session = WorldEditorSession()

    initial = session.snapshot().to_dict()
    assert initial["contract_version"] == WORLD_EDITOR_SESSION_VERSION
    assert initial["selected_placement_id"] is None
    assert initial["actions"]["delete"] is False
    assert initial["dirty"] is False

    changed = session.place("wall_64x64_a", 0, 0).to_dict()
    placement_id = changed["selected_placement_id"]
    assert placement_id is not None
    assert changed["dirty"] is True
    assert changed["actions"]["rotate"] is True
    assert changed["layers"][0]["label"] == "Muro metálico A"
    assert changed["layers"][0]["category"] == "Obstáculos"

    saved = session.mark_saved().to_dict()
    assert saved["dirty"] is False


def test_session_rejects_a_selection_not_in_the_current_world() -> None:
    session = WorldEditorSession()

    try:
        session.select("asset-inexistente")
    except ValueError as error:
        assert "No existe asset_id" in str(error)
    else:
        raise AssertionError("La selección inexistente debe fallar explícitamente.")
