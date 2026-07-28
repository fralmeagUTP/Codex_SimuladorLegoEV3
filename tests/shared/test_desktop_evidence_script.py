from pathlib import Path

from scripts.capture_desktop_evidence import display_path


def test_evidence_script_accepts_output_directory_outside_repository(tmp_path: Path) -> None:
    output = tmp_path / "evidence" / "image.png"

    assert display_path(output) == output
