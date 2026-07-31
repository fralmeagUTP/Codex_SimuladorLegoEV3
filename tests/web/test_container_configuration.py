from pathlib import Path


def test_dockerfile_uses_the_documented_web_environment_variable() -> None:
    root = Path(__file__).resolve().parents[2]
    dockerfile = (root / "Dockerfile").read_text(encoding="utf-8")

    assert "EV3_WEB_APP_ENV=production" in dockerfile
    assert "EV3_WEB_HOST=0.0.0.0" in dockerfile
    assert "EV3_APP_ENV=production" not in dockerfile


def test_dockerfile_runs_the_web_server_without_root() -> None:
    root = Path(__file__).resolve().parents[2]
    dockerfile = (root / "Dockerfile").read_text(encoding="utf-8")

    assert "FROM python:3.12-slim" in dockerfile
    assert "useradd --create-home --uid 10001 ev3" in dockerfile
    assert "USER ev3" in dockerfile
    assert "EXPOSE 5050" in dockerfile
    assert 'CMD ["python", "-m", "simulador_ev3.web.waitress_server"]' in dockerfile


def test_docker_smoke_provides_required_production_configuration() -> None:
    root = Path(__file__).resolve().parents[2]
    workflow = (root / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")

    assert "EV3_WEB_SECRET_KEY=ci-only-secret-key-at-least-32-characters" in workflow
    assert "EV3_WEB_SESSION_COOKIE_SECURE=true" in workflow


def test_windows_release_script_preserves_the_custom_pyinstaller_spec() -> None:
    root = Path(__file__).resolve().parents[2]
    script = (root / "scripts" / "build_release_windows.ps1").read_text(encoding="utf-8")
    spec = root / "SimuladorEV3.spec"

    assert spec.is_file()
    assert 'Remove-Item -Force "SimuladorEV3.spec"' not in script
    assert "SimuladorEV3.spec" in script
