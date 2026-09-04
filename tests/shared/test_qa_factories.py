from tests.qa_factories import make_editor_world


def test_qa_workspace_uses_isolated_directories(qa_workspace) -> None:
    assert qa_workspace.worlds.is_dir()
    assert qa_workspace.examples.is_dir()
    assert qa_workspace.session_store.is_dir()
    assert qa_workspace.worlds.name == "worlds"


def test_synthetic_world_factory_does_not_require_repository_assets() -> None:
    world = make_editor_world()

    assert world.world_width_cells == 20
    assert [placement.asset_key for placement in world.placements] == ["robot_ev3_32x32"]
