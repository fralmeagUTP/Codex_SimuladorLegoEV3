from simulador_ev3.shared.ui_design_tokens import (
    APP_OUTER_PADDING_PX,
    BRICK_MIN_WIDTH_PX,
    COMPACT_GAP_PX,
    DARK_TOKENS,
    EDITOR_MIN_WIDTH_PX,
    LIGHT_TOKENS,
    PANEL_GAP_PX,
    STATUS_STRIP_HEIGHT_PX,
    VISUAL_COMPARISON_TOLERANCE_PX,
    WEB_REFERENCE_HEIGHT_PX,
    WEB_REFERENCE_WIDTH_PX,
    scaled_px,
    tokens_for_theme,
)


def test_web_theme_variables_match_the_shared_semantic_tokens() -> None:
    """La Web consume el mismo vocabulario de tema que Tkinter."""

    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    css = (root / "simulador_ev3" / "web" / "static" / "css" / "app.css").read_text(encoding="utf-8")

    for token in (LIGHT_TOKENS, DARK_TOKENS):
        for name, value in token.__dict__.items():
            css_name = f"--ev3-{name.replace('_', '-')}"
            assert css_name in css
            assert value.lower() in css.lower()


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


def test_web_and_tkinter_share_composition_metrics() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    css = (root / "simulador_ev3" / "web" / "static" / "css" / "app.css").read_text(encoding="utf-8")

    assert (APP_OUTER_PADDING_PX, COMPACT_GAP_PX, PANEL_GAP_PX) == (12, 6, 10)
    assert (BRICK_MIN_WIDTH_PX, EDITOR_MIN_WIDTH_PX, STATUS_STRIP_HEIGHT_PX) == (340, 430, 30)
    for variable in (
        "--ev3-space-page", "--ev3-space-compact", "--ev3-space-panel",
        "--ev3-brick-min-width", "--ev3-editor-min-width", "--ev3-status-strip-height",
    ):
        assert variable in css


def test_syntax_colours_match_between_web_and_tkinter() -> None:
    from pathlib import Path

    from simulador_ev3.ui.editor_panel import _DARK_SYNTAX_COLORS, _LIGHT_SYNTAX_COLORS

    root = Path(__file__).resolve().parents[2]
    css = (root / "simulador_ev3" / "web" / "static" / "css" / "app.css").read_text(encoding="utf-8").lower()

    for colors in (_LIGHT_SYNTAX_COLORS, _DARK_SYNTAX_COLORS):
        for color in colors.values():
            assert color.lower() in css
