from pathlib import Path

from scripts import capture_desktop_evidence
from scripts.capture_desktop_evidence import display_path


def test_evidence_script_accepts_output_directory_outside_repository(tmp_path: Path) -> None:
    output = tmp_path / "evidence" / "image.png"

    assert display_path(output) == output


def test_evidence_capture_prefers_the_native_window_handle(monkeypatch) -> None:
    class Target:
        def winfo_id(self) -> int:
            return 42

    captured: dict[str, object] = {}
    image = object()

    def fake_grab(**kwargs):
        captured.update(kwargs)
        return image

    monkeypatch.setattr(capture_desktop_evidence.ImageGrab, "grab", fake_grab)

    assert capture_desktop_evidence._capture_window(Target(), (1, 2, 3, 4)) is image
    assert captured == {"window": 42}
