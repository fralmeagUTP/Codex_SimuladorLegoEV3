"""Flujo CRUD aislado para asegurar persistencia de mundos sin datos de usuario."""

from __future__ import annotations

from simulador_ev3.web.app import create_app


def _client_and_session(qa_workspace):
    app = create_app(
        {
            "TESTING": True,
            **qa_workspace.web_config(),
            "MAX_ACTIVE_SESSIONS": 2,
            "MAX_RUNNING_SIMULATIONS": 2,
            "SCRIPT_MAX_RUNTIME_S": 2.0,
        }
    )
    client = app.test_client()
    created = client.post("/api/sessions").get_json()
    return client, created["session_id"], {"X-Session-Token": created["owner_token"]}


def test_isolated_world_crud_preserves_saved_version_until_explicit_save(qa_workspace) -> None:
    client, session_id, headers = _client_and_session(qa_workspace)
    editor_url = f"/api/sessions/{session_id}/editor/world"

    created = client.post(editor_url, json={"width_cells": 10, "height_cells": 10}, headers=headers)
    robot = client.post(
        f"{editor_url}/place",
        json={"asset_key": "robot_ev3_32x32", "x": 0, "y": 0, "rotation": 90},
        headers=headers,
    )
    saved = client.post(f"{editor_url}/save", json={"name": "qa_temporal"}, headers=headers)

    assert created.status_code == robot.status_code == saved.status_code == 200
    path = qa_workspace.worlds / "qa_temporal.json"
    baseline = path.read_bytes()
    assert path.is_file()

    # La edición no confirmada modifica solo la sesión: no persiste hasta Guardar.
    changed = client.post(
        f"{editor_url}/place",
        json={"asset_key": "wall_64x64_a", "x": 64, "y": 64, "rotation": 0},
        headers=headers,
    )
    assert changed.status_code == 200
    assert path.read_bytes() == baseline

    viewer = client.post("/api/sessions").get_json()
    viewer_headers = {"X-Session-Token": viewer["owner_token"]}
    loaded = client.post(
        f"/api/sessions/{viewer['session_id']}/world",
        json={"name": "qa_temporal.json"},
        headers=viewer_headers,
    )
    placements = loaded.get_json()["world"]["editor_spec"]["placements"]
    assert loaded.status_code == 200
    assert [item["asset_key"] for item in placements] == ["robot_ev3_32x32"]

    deleted = client.delete(f"{editor_url}/save/qa_temporal.json", headers=headers)
    assert deleted.status_code == 200
    assert not path.exists()
