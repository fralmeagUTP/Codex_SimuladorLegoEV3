from pathlib import Path


def test_ci_runs_supported_python_versions_and_platforms() -> None:
    workflow = (Path(__file__).parents[2] / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")

    for expected in (
        "ubuntu-latest",
        "windows-latest",
        '"3.11"',
        '"3.12"',
        "pytest",
        "ruff",
        "mypy",
        "bandit",
        "pip_audit",
        "playwright install --with-deps chromium",
        "runtime-resilience",
        "coverage-core",
    ):
        assert expected in workflow
