from pathlib import Path

from simulador_ev3.shared.interface_catalog import KEYBOARD_SHORTCUTS, NAVIGATION_MENU, NAVIGATION_MENU_ORDER


def test_web_and_tkinter_keep_the_shared_menu_order_and_shortcuts() -> None:
    root = Path(__file__).resolve().parents[2]
    web = (root / "simulador_ev3" / "web" / "templates" / "index.html").read_text(encoding="utf-8")
    tkinter = (root / "simulador_ev3" / "ui" / "main_window.py").read_text(encoding="utf-8")

    for key, label in NAVIGATION_MENU.items():
        assert label in NAVIGATION_MENU_ORDER
        assert f"navigation_menu['{key}']" in web
        assert f'NAVIGATION_MENU["{key}"]' in tkinter
    assert KEYBOARD_SHORTCUTS == {
        "run": "F5",
        "pause_resume": "F6",
        "stop_reset": "Shift+F5",
        "help": "F1",
        "close_dialog": "Escape",
    }
    for binding in ("<F1>", "<F5>", "<F6>", "<Shift-F5>"):
        assert binding in tkinter
    for key in ('"F1"', '"F5"', '"F6"'):
        assert key in (root / "simulador_ev3" / "web" / "static" / "js" / "simulation_app.js").read_text(
            encoding="utf-8"
        )
