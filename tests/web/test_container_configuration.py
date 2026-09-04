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


def test_production_compose_applies_external_worker_boundaries() -> None:
    root = Path(__file__).resolve().parents[2]
    compose = (root / "docker-compose.production.yml").read_text(encoding="utf-8")

    for expected in (
        "read_only: true",
        "pids_limit: 64",
        "mem_limit: 768m",
        "no-new-privileges:true",
        "cap_drop:",
        "- ALL",
        "/tmp/ev3:rw,noexec,nosuid,size=128m,mode=0700,uid=10001,gid=10001",
        "env_file:",
        "expose:",
        "ev3_backend:",
        "internal: true",
        "caddy:2.8-alpine",
        '"${EV3_WEB_HTTP_PORT:-80}:80"',
        '"${EV3_WEB_HTTPS_PORT:-443}:443"',
        "driver: local",
        'max-size: "10m"',
        'max-file: "5"',
    ):
        assert expected in compose
    assert '      - "5050:5050"' not in compose


def test_caddy_production_reference_preserves_tls_and_sse_contract() -> None:
    root = Path(__file__).resolve().parents[2]
    caddyfile = (root / "deploy" / "Caddyfile.production").read_text(encoding="utf-8")

    assert "{$EV3_WEB_PUBLIC_HOST}" in caddyfile
    assert "{$EV3_WEB_TLS_EMAIL}" in caddyfile
    assert "reverse_proxy simulador-ev3:5050" in caddyfile
    assert "flush_interval -1" in caddyfile


def test_vps_operational_scripts_keep_secrets_and_sessions_out_of_backups() -> None:
    root = Path(__file__).resolve().parents[2]
    healthcheck = (root / "scripts" / "vps_healthcheck.sh").read_text(encoding="utf-8")
    backup = (root / "scripts" / "backup_vps_release.sh").read_text(encoding="utf-8")

    assert '"$base_url/healthz" >/dev/null' in healthcheck
    assert '"$base_url/metrics?format=prometheus" >/dev/null' in healthcheck
    assert ".env.production.example" in backup
    assert ".env.production " not in backup
    assert "OPERACION_VPS_WEB.md" in backup


def test_vps_release_gate_checks_proxy_cookie_and_internal_web_port() -> None:
    root = Path(__file__).resolve().parents[2]
    gate = (root / "scripts" / "validate_vps_release.sh").read_text(encoding="utf-8")

    assert "port simulador-ev3 5050" in gate
    assert '"$base_url/healthz"' in gate
    assert '"$base_url/metrics?format=prometheus"' in gate
    assert "SameSite=Lax" in gate
    assert "Compuerta VPS aprobada" in gate


def test_vps_storage_preparation_creates_private_operational_paths() -> None:
    root = Path(__file__).resolve().parents[2]
    script = (root / "scripts" / "prepare_vps_storage.sh").read_text(encoding="utf-8")

    assert "install -d -m 0700" in script
    assert '"$storage_root/backups"' in script
    assert '"$storage_root/logs"' in script


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
