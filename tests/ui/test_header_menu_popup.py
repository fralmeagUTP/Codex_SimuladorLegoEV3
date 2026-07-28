import tkinter as tk
from unittest.mock import Mock

from simulador_ev3.ui.main_window import EV3SimulatorApp


def test_header_menu_posts_below_enabled_button() -> None:
    button = Mock()
    button.cget.return_value = tk.NORMAL
    button.winfo_rootx.return_value = 120
    button.winfo_rooty.return_value = 40
    button.winfo_height.return_value = 28
    menu = Mock()

    result = EV3SimulatorApp._post_header_menu(button, menu)

    assert result == "break"
    button.focus_set.assert_called_once()
    menu.tk_popup.assert_called_once_with(120, 68)


def test_header_menu_does_not_post_when_button_is_disabled() -> None:
    button = Mock()
    button.cget.return_value = tk.DISABLED
    menu = Mock()

    assert EV3SimulatorApp._post_header_menu(button, menu) == "break"
    menu.tk_popup.assert_not_called()
