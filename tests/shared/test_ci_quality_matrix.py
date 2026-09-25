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
        "coverage.xml",
        "cobertura-${{ matrix.os }}-py${{ matrix.python }}",
        "evidencia-e2e-web",
        "docker-smoke",
        "docker build --tag simulador-ev3:ci .",
        "http://127.0.0.1:5050/healthz",
        "windows-release-smoke",
        "build_release_windows.ps1 -PythonExe python",
        "SimuladorEV3.exe",
    ):
        assert expected in workflow
