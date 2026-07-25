from pathlib import Path


def test_quality_tooling_is_declared_in_project_configuration() -> None:
    root = Path(__file__).parents[2]
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    hooks = (root / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    for tool in ("ruff", "mypy", "bandit", "pip-audit", "pre-commit"):
        assert tool in pyproject
    assert "ruff-format" in hooks
    assert "bandit" in hooks
