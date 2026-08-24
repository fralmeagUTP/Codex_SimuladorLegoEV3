from simulador_ev3.shared.help_tutorials import (
    HELP_CATEGORIES,
    HELP_GUIDES,
    HELP_REFERENCES,
    PYBRICKS_GLOSSARY,
    guides_for_category,
    search_guides,
    tutorial_by_id,
)


def test_help_catalog_covers_the_primary_learning_paths() -> None:
    identifiers = [guide.identifier for guide in HELP_GUIDES]

    assert identifiers == [
        "first-simulation",
        "create-world",
        "run-simulation",
        "use-sensors",
        "debug-script",
        "recover-script-error",
        "recover-world-validation",
    ]
    for guide in HELP_GUIDES:
        assert guide.title
        assert guide.summary
        assert guide.minutes > 0
        assert guide.prerequisites
        assert guide.steps
        assert guide.expected_result
        assert guide.recovery
        assert guide.audience


def test_help_guides_have_stable_destinations_and_categories() -> None:
    categories = {identifier for identifier, _ in HELP_CATEGORIES}

    assert tutorial_by_id("create-world").destination == "worlds"
    assert tutorial_by_id("run-simulation").destination == "simulation"
    assert tutorial_by_id("debug-script").destination == "debug"
    assert {guide.category for guide in HELP_GUIDES} <= categories
    assert [guide.identifier for guide in guides_for_category("resolver")] == [
        "recover-script-error",
        "recover-world-validation",
    ]
    for guide in HELP_GUIDES:
        assert guide.destination in {"simulation", "worlds", "debug"}
        assert all("http://" not in text and "https://" not in text for text in (*guide.steps, guide.recovery))


def test_help_references_and_glossary_are_stable_and_educational() -> None:
    assert {reference.identifier for reference in HELP_REFERENCES} == {
        "user-manual",
        "learning-guide",
        "pybricks-limits",
        "technical-manual-web",
        "technical-manual-desktop",
    }
    assert all(reference.filename.endswith((".md", ".html")) for reference in HELP_REFERENCES)
    identifiers = {term.identifier for term in PYBRICKS_GLOSSARY}
    assert identifiers >= {"ev3brick", "port", "motor", "drivebase", "wait", "timeout"}
    assert all(term.definition for term in PYBRICKS_GLOSSARY)


def test_help_search_matches_visible_task_content() -> None:
    assert [guide.identifier for guide in search_guides("ultrasónico")] == ["use-sensors"]
    assert [guide.identifier for guide in search_guides("breakpoint")] == ["debug-script"]
    assert search_guides("término inexistente") == ()
