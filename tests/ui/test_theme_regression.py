from simulador_ev3.shared.ui_design_tokens import DARK_TOKENS, LIGHT_TOKENS
from simulador_ev3.ui.main_window import EV3SimulatorApp


def test_theme_palette_supports_repeated_dark_and_light_switches() -> None:
    dark_palette = EV3SimulatorApp._theme_palette(DARK_TOKENS)
    light_palette = EV3SimulatorApp._theme_palette(LIGHT_TOKENS)

    assert dark_palette[LIGHT_TOKENS.background.upper()] == DARK_TOKENS.background
    assert light_palette[DARK_TOKENS.background.upper()] == LIGHT_TOKENS.background
    assert light_palette[DARK_TOKENS.toolbar.upper()] == LIGHT_TOKENS.toolbar
