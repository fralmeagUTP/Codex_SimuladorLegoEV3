from simulador_ev3.shared.interface_catalog import (
    INTERFACE_CATALOG_VERSION,
    KEYBOARD_SHORTCUTS,
    RECOVERY_ROUTES,
    SESSION_STATE_MESSAGES,
    VALIDATION_MESSAGES,
    controls_for_status,
)


def test_shared_interface_catalog_covers_controls_messages_validation_and_recovery() -> None:
    assert INTERFACE_CATALOG_VERSION == 1
    assert KEYBOARD_SHORTCUTS["run"] == "F5"
    assert VALIDATION_MESSAGES["script_required"]
    assert RECOVERY_ROUTES["error"]
    assert SESSION_STATE_MESSAGES["finished"]


def test_controls_follow_the_same_state_machine_for_both_adapters() -> None:
    assert controls_for_status("running") == {"run": False, "pause": True, "resume": False, "stop_reset": True}
    assert controls_for_status("paused") == {"run": False, "pause": False, "resume": True, "stop_reset": True}
    assert controls_for_status("finished") == {"run": True, "pause": False, "resume": False, "stop_reset": False}
