from simulador_ev3.domain.world.world_model import WorldModel
from simulador_ev3.shared.world_editor_projection import editor_placements
from simulador_ev3.web.services.world_dto import world_to_dict


def test_editor_placements_normalizes_supported_visual_fields() -> None:
    result = editor_placements(
        {
            "placements": [
                {"asset_key": " wall ", "x": 4, "y_px": 8, "rotation": 90},
                {"asset_key": ""},
                "invalid",
            ]
        }
    )

    assert result == [{"asset_key": "wall", "x_px": 4, "y_px": 8, "rotation": 90}]


def test_web_world_dto_uses_the_shared_editor_projection() -> None:
    payload = world_to_dict(
        WorldModel(width_mm=1000, height_mm=1000),
        {"placements": [{"asset_key": " robot ", "x": 1, "y": 2}]},
    )

    assert payload["editor_spec"]["placements"] == [{"asset_key": "robot", "x_px": 1, "y_px": 2, "rotation": 0}]
