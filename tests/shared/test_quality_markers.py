from pathlib import Path


def test_quality_markers_are_declared_for_targeted_execution() -> None:
    root = Path(__file__).parents[2]
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")

    for marker in ("unit", "integration", "contract", "ui", "e2e", "security", "performance", "release"):
        assert f'"{marker}:' in pyproject
