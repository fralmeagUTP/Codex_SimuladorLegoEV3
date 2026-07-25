from pathlib import Path

from simulador_ev3.shared.ui_control_catalog import REQUIRED_CONTROL_AREAS, REQUIRED_SIMULATION_ACTIONS


def test_web_and_tkinter_expose_required_visual_control_catalog() -> None:
    root = Path(__file__).resolve().parents[2]
    web = (root / "simulador_ev3" / "web" / "templates" / "index.html").read_text(encoding="utf-8")
    desktop = (root / "simulador_ev3" / "ui" / "main_window.py").read_text(encoding="utf-8")

    matrix = (root / "Documentos" / "MATRIZ_PARIDAD_VISUAL_WEB_TKINTER.md").read_text(encoding="utf-8").lower()
    for area in REQUIRED_CONTROL_AREAS:
        assert area.lower() in matrix
    for action in REQUIRED_SIMULATION_ACTIONS:
        assert action in web
        assert action in desktop
