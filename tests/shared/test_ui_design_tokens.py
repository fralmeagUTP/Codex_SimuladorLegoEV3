from simulador_ev3.shared.ui_design_tokens import (
    DARK_TOKENS,
    LIGHT_TOKENS,
    VISUAL_COMPARISON_TOLERANCE_PX,
    WEB_REFERENCE_HEIGHT_PX,
    WEB_REFERENCE_WIDTH_PX,
    scaled_px,
    tokens_for_theme,
)


def test_visual_tokens_are_complete_and_theme_selectable() -> None:
    assert tokens_for_theme("light") == LIGHT_TOKENS
    assert tokens_for_theme("dark") == DARK_TOKENS
    assert LIGHT_TOKENS.primary != LIGHT_TOKENS.surface
    assert DARK_TOKENS.text != DARK_TOKENS.background
    # La cabecera usa los mismos colores que `.menu-bar` de la Web.
    assert (LIGHT_TOKENS.toolbar, LIGHT_TOKENS.toolbar_text) == ("#F8FAFC", "#0F172A")
    assert (DARK_TOKENS.toolbar, DARK_TOKENS.toolbar_text) == ("#111C2D", "#E2E8F0")


def test_reference_metrics_and_dpi_scaling_are_bounded() -> None:
    assert (WEB_REFERENCE_WIDTH_PX, WEB_REFERENCE_HEIGHT_PX) == (1280, 800)
    assert VISUAL_COMPARISON_TOLERANCE_PX == 4
    assert scaled_px(10, 0.1) == 8
    assert scaled_px(10, 3.0) == 20
