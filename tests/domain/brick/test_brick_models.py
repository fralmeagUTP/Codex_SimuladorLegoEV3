"""
test_led_model.py
=================
Tests unitarios para LedModel y EV3BrickModel.
"""

from simulador_ev3.domain.brick.buttons_model import Button, ButtonsModel
from simulador_ev3.domain.brick.ev3brick_model import EV3BrickModel
from simulador_ev3.domain.brick.led_model import LedColor, LedModel
from simulador_ev3.domain.brick.screen_buffer import (
    MAX_LINES,
    SCREEN_HEIGHT_PX,
    SCREEN_WIDTH_PX,
    ScreenBuffer,
)

# ------------------------------------------------------------------ #
# LedModel
# ------------------------------------------------------------------ #


class TestLedModel:
    def test_initial_state_is_off(self) -> None:
        led = LedModel()
        assert not led.is_on
        assert led.color == LedColor.OFF

    def test_cmd_on_turns_led_on(self) -> None:
        led = LedModel()
        led.cmd_on(LedColor.RED)
        assert led.is_on
        assert led.color == LedColor.RED

    def test_cmd_off_turns_led_off(self) -> None:
        led = LedModel()
        led.cmd_on(LedColor.GREEN)
        led.cmd_off()
        assert not led.is_on
        assert led.color == LedColor.OFF

    def test_cmd_on_with_off_color_turns_off(self) -> None:
        led = LedModel()
        led.cmd_on(LedColor.RED)
        led.cmd_on(LedColor.OFF)  # pasar OFF como color apaga el LED
        assert not led.is_on

    def test_to_dict_structure(self) -> None:
        led = LedModel()
        led.cmd_on(LedColor.ORANGE)
        d = led.to_dict()
        assert d["is_on"] is True
        assert d["color"] == "ORANGE"


# ------------------------------------------------------------------ #
# ButtonsModel
# ------------------------------------------------------------------ #


class TestButtonsModel:
    def test_no_buttons_pressed_initially(self) -> None:
        buttons = ButtonsModel()
        assert not buttons.is_pressed(Button.CENTER)

    def test_press_and_release(self) -> None:
        buttons = ButtonsModel()
        buttons.press(Button.UP)
        assert buttons.is_pressed(Button.UP)
        buttons.release(Button.UP)
        assert not buttons.is_pressed(Button.UP)

    def test_release_all(self) -> None:
        buttons = ButtonsModel()
        buttons.press(Button.UP)
        buttons.press(Button.DOWN)
        buttons.release_all()
        assert buttons.pressed_buttons() == set()

    def test_pressed_buttons_returns_copy(self) -> None:
        buttons = ButtonsModel()
        buttons.press(Button.LEFT)
        result = buttons.pressed_buttons()
        result.add(Button.RIGHT)  # no debe afectar al modelo
        assert not buttons.is_pressed(Button.RIGHT)


# ------------------------------------------------------------------ #
# ScreenBuffer
# ------------------------------------------------------------------ #


class TestScreenBuffer:
    def test_initial_screen_empty(self) -> None:
        screen = ScreenBuffer()
        assert screen.lines == []

    def test_print_adds_line(self) -> None:
        screen = ScreenBuffer()
        screen.cmd_print("Hola EV3")
        assert "Hola EV3" in screen.lines

    def test_screen_scrolls_after_max_lines(self) -> None:
        screen = ScreenBuffer()
        for i in range(MAX_LINES + 2):
            screen.cmd_print(f"Linea {i}")
        assert len(screen.lines) == MAX_LINES

    def test_clear_empties_screen(self) -> None:
        screen = ScreenBuffer()
        screen.cmd_print("texto")
        screen.cmd_clear()
        assert screen.lines == []

    def test_line_truncation(self) -> None:
        screen = ScreenBuffer()
        long_text = "A" * 100
        screen.cmd_print(long_text)
        assert len(screen.lines[0]) <= 22

    def test_to_dict_contains_physical_spec_metadata(self) -> None:
        screen = ScreenBuffer()
        d = screen.to_dict()
        assert d["width_px"] == SCREEN_WIDTH_PX
        assert d["height_px"] == SCREEN_HEIGHT_PX
        assert d["monochrome"] is True


# ------------------------------------------------------------------ #
# EV3BrickModel
# ------------------------------------------------------------------ #


class TestEV3BrickModel:
    def test_default_construction(self) -> None:
        brick = EV3BrickModel()
        assert not brick.light.is_on
        assert not brick.buttons.is_pressed(Button.CENTER)
        assert brick.screen.lines == []

    def test_to_dict_contains_all_keys(self) -> None:
        brick = EV3BrickModel()
        d = brick.to_dict()
        assert "led" in d
        assert "speaker" in d
        assert "screen" in d
        assert "buttons" in d

    def test_update_advances_speaker(self) -> None:
        brick = EV3BrickModel()
        brick.speaker.cmd_beep(frequency=440.0, duration_ms=40.0)
        # update con dt=0.02 s → 20 ms consumidos, quedan 20 ms
        brick.update(dt=0.02)
        from simulador_ev3.domain.brick.speaker_model import SpeakerState

        assert brick.speaker.state == SpeakerState.BEEPING
        # segundo update → queda en 0 ms → IDLE
        brick.update(dt=0.02)
        assert brick.speaker.state == SpeakerState.IDLE
