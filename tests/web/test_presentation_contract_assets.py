from pathlib import Path


def test_web_session_controller_synchronizes_the_shared_presentation_contract() -> None:
    root = Path(__file__).resolve().parents[2]
    api = (root / "simulador_ev3" / "web" / "static" / "js" / "api.js").read_text(encoding="utf-8")
    controller_path = root / "simulador_ev3" / "web" / "static" / "js" / "session_controller.js"
    controller = controller_path.read_text(encoding="utf-8")
    app = (root / "simulador_ev3" / "web" / "static" / "js" / "simulation_app.js").read_text(encoding="utf-8")

    assert "presentationState" in api
    assert "synchronizePresentation" in controller
    assert "onPresentation: applyPresentationState" in app
    assert "Number(presentation.version) !== 1" in app
