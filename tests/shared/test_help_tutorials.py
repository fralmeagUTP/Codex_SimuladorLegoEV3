from simulador_ev3.shared.help_tutorials import HELP_TUTORIALS, tutorial_by_id


def test_help_tutorials_cover_world_simulation_and_debugging() -> None:
    assert [tutorial.identifier for tutorial in HELP_TUTORIALS] == [
        "create-world",
        "run-simulation",
        "debug-script",
    ]
    for tutorial in HELP_TUTORIALS:
        assert tutorial.steps
        assert tutorial.expected_result
        assert tutorial.recovery


def test_help_tutorials_have_stable_destinations() -> None:
    assert tutorial_by_id("create-world").destination == "worlds"
    assert tutorial_by_id("run-simulation").destination == "simulation"
    assert tutorial_by_id("debug-script").destination == "debug"
