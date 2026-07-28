from simulador_ev3.shared.debug_configuration import normalize_breakpoints, normalize_watches


def test_debug_configuration_normalizes_shared_input_limits() -> None:
    assert normalize_breakpoints([1, "2", 0, "bad", -1]) == {1, 2}
    watches = normalize_watches([" x + 1 ", "", "a" * 201] + ["ok"] * 20)
    assert watches == ["x + 1"] + ["ok"] * 17
