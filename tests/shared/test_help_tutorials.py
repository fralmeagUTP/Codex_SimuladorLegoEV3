from simulador_ev3.shared.help_tutorials import (
    HELP_CATEGORIES,
    HELP_GUIDES,
    HELP_MENU_ACTIONS,
    HELP_REFERENCES,
    PYBRICKS_GLOSSARY,
    guides_for_category,
    help_menu_action,
    search_guides,
    tutorial_by_id,
)


def test_help_menu_actions_have_a_shared_order_and_specific_quick_guide() -> None:
    assert [action.identifier for action in HELP_MENU_ACTIONS] == [
        "help-center",
        "quick-first-simulation",
        "session-diagnostics",
        "export-diagnostics",
        "lego-ev3-book",
        "about",
    ]
    quick_guide = help_menu_action("quick-first-simulation")
    assert quick_guide.label == "Guía rápida: primera simulación"
    assert quick_guide.guide_id == "first-simulation"
    book = help_menu_action("lego-ev3-book")
    assert book.external_url == (
        "https://repositorio.utp.edu.co/entities/publication/2cb3c888-47b1-4653-8b05-46c27a87ae81"
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
        "missions",
        "traces",
        "runtime-limit",
        "session-diagnostics",
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
        assert guide.image_name.startswith("web/")
        assert guide.image_name.endswith(".png")


def test_help_guides_have_stable_destinations_and_categories() -> None:
    categories = {identifier for identifier, _ in HELP_CATEGORIES}

    assert tutorial_by_id("create-world").destination == "worlds"
    assert tutorial_by_id("run-simulation").destination == "simulation"
    assert tutorial_by_id("debug-script").destination == "debug"
    assert {guide.category for guide in HELP_GUIDES} <= categories
    assert [guide.identifier for guide in guides_for_category("resolver")] == [
        "recover-script-error",
        "recover-world-validation",
        "session-diagnostics",
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
