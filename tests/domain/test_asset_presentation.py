from simulador_ev3.domain.editor.asset_presentation import (
    CATEGORY_ORDER,
    cells_to_mm,
    pixels_to_cells,
    pixels_to_mm,
    presentation_for_asset,
)


def test_existing_asset_has_spanish_category_name_and_tooltip():
    presentation = presentation_for_asset("wall_64x64_a")

    assert presentation.category == "Obstáculos"
    assert presentation.name == "Muro metálico A"
    assert presentation.tooltip


def test_alias_uses_same_presentation_as_canonical_asset():
    assert presentation_for_asset("line_64_64_cruz").name == "Cruce de líneas"


def test_unknown_asset_remains_understandable():
    presentation = presentation_for_asset("asset_experimental")

    assert presentation.category == "Otros"
    assert presentation.name == "Asset Experimental"


def test_editor_units_are_converted_without_changing_internal_pixels():
    assert pixels_to_cells(64) == 2
    assert pixels_to_mm(64) == 200
    assert cells_to_mm(8) == 800


def test_category_order_reserves_sensor_section_for_future_assets():
    assert CATEGORY_ORDER[-1] == "Sensores"
