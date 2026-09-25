from simulador_ev3.shared.help_tutorials import HELP_GUIDES, HELP_SAFE_EXAMPLES


def test_safe_examples_are_limited_to_guides_and_do_not_embed_sensitive_data() -> None:
    guide_ids = {guide.identifier for guide in HELP_GUIDES}

    assert set(HELP_SAFE_EXAMPLES) <= guide_ids
    assert "EV3Brick" in HELP_SAFE_EXAMPLES["first-simulation"]
    assert all(
        "token" not in example.casefold() and "password" not in example.casefold()
        for example in HELP_SAFE_EXAMPLES.values()
    )
