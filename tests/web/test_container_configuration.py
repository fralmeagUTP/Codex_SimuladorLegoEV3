from pathlib import Path


def test_dockerfile_uses_the_documented_web_environment_variable() -> None:
    root = Path(__file__).resolve().parents[2]
    dockerfile = (root / "Dockerfile").read_text(encoding="utf-8")

    assert "EV3_WEB_APP_ENV=production" in dockerfile
    assert "EV3_APP_ENV=production" not in dockerfile
