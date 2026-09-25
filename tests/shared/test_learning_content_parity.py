"""Contratos de contenido que impiden divergencias didácticas entre interfaces."""

from __future__ import annotations

from simulador_ev3.shared.help_tutorials import HELP_GUIDES, HELP_REFERENCES, PYBRICKS_GLOSSARY
from simulador_ev3.shared.learning_catalog import LEARNING_ROUTES
from simulador_ev3.ui.main_window import EV3SimulatorApp


def test_desktop_accessible_help_contains_the_shared_guides_references_and_glossary() -> None:
    app = object.__new__(EV3SimulatorApp)

    text = app._read_manual_text()

    for guide in HELP_GUIDES:
        assert guide.title in text
        assert all(step in text for step in guide.steps)
        assert guide.expected_result in text
    for reference in HELP_REFERENCES:
        assert reference.title in text
        assert reference.filename in text
    for term in PYBRICKS_GLOSSARY:
        assert term.term in text
        assert term.definition in text


def test_learning_routes_reference_existing_help_and_evaluable_content() -> None:
    guide_ids = {guide.identifier for guide in HELP_GUIDES}

    for route in LEARNING_ROUTES:
        assert set(route.guide_ids) <= guide_ids
        assert route.practice
        assert route.success_criteria
        assert route.recovery
