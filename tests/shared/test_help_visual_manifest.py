from pathlib import Path

from simulador_ev3.shared.help_tutorials import HELP_GUIDES
from simulador_ev3.shared.help_visual_manifest import (
    HELP_VISUAL_MANIFEST_VERSION,
    HELP_VISUALS,
    validate_visual_manifest,
    visual_for,
)


def test_every_help_guide_uses_a_real_web_capture_with_accessible_metadata() -> None:
    root = Path(__file__).resolve().parents[2]
    help_assets = root / "simulador_ev3" / "web" / "static" / "images" / "help"

    assert HELP_VISUAL_MANIFEST_VERSION == 1
    assert validate_visual_manifest(help_assets) == ()
    assert {visual.guide_id for visual in HELP_VISUALS if visual.platform == "web"} == {
        guide.identifier for guide in HELP_GUIDES
    }


def test_visual_lookup_is_stable_and_uses_catalog_asset_path() -> None:
    visual = visual_for("first-simulation")

    assert visual.filename == "web/primera_simulacion.png"
    assert visual.filename == HELP_GUIDES[0].image_name
    assert visual.alt and visual.transcript and visual.ui_version
