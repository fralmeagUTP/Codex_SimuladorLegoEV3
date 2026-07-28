from __future__ import annotations

from pathlib import Path

from simulador_ev3.web.app import create_app


def _client(tmp_path: Path):
    app = create_app(
        {
            "TESTING": True,
            "WORLDS_DIR": tmp_path,
            "EXAMPLES_DIR": tmp_path,
            "MAX_ACTIVE_SESSIONS": 2,
            "MAX_RUNNING_SIMULATIONS": 2,
            "SCRIPT_MAX_RUNTIME_S": 2.0,
        }
    )
    return app.test_client()


def _session(client):
    payload = client.post("/api/sessions").get_json()
    return payload["session_id"], {"X-Session-Token": payload["owner_token"]}


def test_custom_saved_world_can_be_deleted(tmp_path: Path) -> None:
    client = _client(tmp_path)
    session_id, headers = _session(client)
    world = tmp_path / "practica.json"
    world.write_text("{}", encoding="utf-8")

    response = client.delete(f"/api/sessions/{session_id}/editor/world/save/practica.json", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == {"status": "deleted", "name": "practica.json"}
    assert not world.exists()


def test_builtin_world_cannot_be_deleted(tmp_path: Path) -> None:
    client = _client(tmp_path)
    session_id, headers = _session(client)
    world = tmp_path / "01_linea_negra_basica.json"
    world.write_text("{}", encoding="utf-8")

    response = client.delete(
        f"/api/sessions/{session_id}/editor/world/save/{world.name}", headers=headers
    )

    assert response.status_code == 400
    assert world.exists()
