from simulador_ev3.shared.help_tutorials import HELP_GUIDES, TEACHER_ROUTE


def test_teacher_route_uses_existing_guides_and_declares_safe_evidence() -> None:
    guide_ids = {guide.identifier for guide in HELP_GUIDES}

    assert TEACHER_ROUTE.minutes > 0
    assert set(TEACHER_ROUTE.guide_ids) <= guide_ids
    assert "ev3" in TEACHER_ROUTE.physical_robot_warning.casefold()
    assert "captura" in TEACHER_ROUTE.suggested_evidence.casefold()
