from __future__ import annotations

from io import BytesIO
from datetime import timedelta

import pytest

from simulador_ev3.web.app import create_app
from simulador_ev3.web.errors import InvalidPayload, SessionNotFound
from simulador_ev3.web.routes.helpers import safe_child
from simulador_ev3.web.services.simulation_session import asset_catalog_dict
from simulador_ev3.web.session_manager import SessionManager, _hash_token, _utcnow


def make_client(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "WORLDS_DIR": tmp_path / "worlds",
            "EXAMPLES_DIR": tmp_path / "examples",
            "MAX_ACTIVE_SESSIONS": 5,
            "MAX_RUNNING_SIMULATIONS": 5,
            "SCRIPT_MAX_RUNTIME_S": 1.0,
        }
    )
    return app.test_client()


def auth_headers(session_data):
    return {"X-Session-Token": session_data["owner_token"]}


def test_hash_token_is_deterministic_and_not_plain_text():
    token = "owner-token"

    hashed = _hash_token(token)

    assert hashed == _hash_token(token)
    assert hashed != token
    assert len(hashed) == 64


def test_safe_child_accepts_existing_file_with_expected_suffix(tmp_path):
    path = tmp_path / "demo.py"
    path.write_text("print('ok')", encoding="utf-8")

    resolved = safe_child(tmp_path, "demo.py", ".py")

    assert resolved == path


@pytest.mark.parametrize("name", ["", "../demo.py", "sub/demo.py", "sub\\demo.py"])
def test_safe_child_rejects_unsafe_names(tmp_path, name):
    with pytest.raises(InvalidPayload):
        safe_child(tmp_path, name, ".py")


def test_safe_child_rejects_wrong_suffix_and_missing_file(tmp_path):
    (tmp_path / "demo.txt").write_text("x", encoding="utf-8")

    with pytest.raises(InvalidPayload):
        safe_child(tmp_path, "demo.txt", ".py")
    with pytest.raises(InvalidPayload):
        safe_child(tmp_path, "missing.py", ".py")


def test_asset_catalog_serializes_expected_metadata():
    catalog = asset_catalog_dict()
    assets = {item["key"]: item for item in catalog["assets"]}

    assert catalog["grid_size_px"] == 32
    assert catalog["cell_size_mm"] == 100.0
    assert assets["robot_ev3_32x32"]["type"] == "robot"
    assert assets["line_64_64_hor"]["connectors"] == ["E", "W"]
    assert assets["floor_tile_256_c"]["width_cells"] == 8


def test_error_response_for_non_object_json_payload(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()

    res = client.post(
        f"/api/sessions/{session['session_id']}/script",
        json=["not", "an", "object"],
        headers=auth_headers(session),
    )

    assert res.status_code == 400
    assert res.get_json()["error"]["code"] == "INVALID_PAYLOAD"


def test_404_response_uses_json_error_contract(tmp_path):
    client = make_client(tmp_path)

    res = client.get("/no-existe")

    assert res.status_code == 404
    assert res.get_json()["error"]["code"] == "NOT_FOUND"


def test_image_asset_route_rejects_path_traversal_and_bad_extension(tmp_path):
    client = make_client(tmp_path)

    traversal = client.get("/assets/images/..secret.png")
    bad_extension = client.get("/assets/images/robot_ev3_32x32.svg")

    assert traversal.status_code == 400
    assert traversal.get_json()["error"]["code"] == "INVALID_PAYLOAD"
    assert bad_extension.status_code == 400
    assert bad_extension.get_json()["error"]["code"] == "INVALID_PAYLOAD"


def test_examples_and_worlds_are_listed_sorted(tmp_path):
    examples = tmp_path / "examples"
    worlds = tmp_path / "worlds"
    examples.mkdir()
    worlds.mkdir()
    (examples / "b.py").write_text("b = 1", encoding="utf-8")
    (examples / "a.py").write_text("a = 1", encoding="utf-8")
    (worlds / "b.json").write_text("{}", encoding="utf-8")
    (worlds / "a.json").write_text("{}", encoding="utf-8")
    client = make_client(tmp_path)

    listed_examples = client.get("/api/examples").get_json()["examples"]
    listed_worlds = client.get("/api/worlds").get_json()["worlds"]

    assert [item["name"] for item in listed_examples] == ["a.py", "b.py"]
    assert [item["name"] for item in listed_worlds] == ["a.json", "b.json"]


def test_get_example_and_world_reject_wrong_suffix(tmp_path):
    examples = tmp_path / "examples"
    worlds = tmp_path / "worlds"
    examples.mkdir()
    worlds.mkdir()
    (examples / "demo.txt").write_text("x", encoding="utf-8")
    (worlds / "demo.txt").write_text("{}", encoding="utf-8")
    client = make_client(tmp_path)

    example = client.get("/api/examples/demo.txt")
    world = client.get("/api/worlds/demo.txt")

    assert example.status_code == 400
    assert world.status_code == 400


def test_close_session_removes_it_from_manager(tmp_path):
    client = make_client(tmp_path)
    session = client.post("/api/sessions").get_json()

    closed = client.delete(
        f"/api/sessions/{session['session_id']}",
        headers=auth_headers(session),
    )
    info = client.get(
        f"/api/sessions/{session['session_id']}",
        headers=auth_headers(session),
    )

    assert closed.status_code == 200
    assert closed.get_json()["status"] == "closed"
    assert info.status_code == 404


def test_session_manager_expires_session_on_access(tmp_path):
    manager = SessionManager(
        {
            "SESSION_IDLE_TIMEOUT_MIN": 30,
            "MAX_ACTIVE_SESSIONS": 5,
            "MAX_RUNNING_SIMULATIONS": 5,
            "SCRIPT_MAX_RUNTIME_S": 0.5,
            "WORLDS_DIR": tmp_path / "worlds",
            "EXAMPLES_DIR": tmp_path / "examples",
        }
    )
    session_id, _token = manager.create_session()
    record = manager._sessions[session_id]
    record.last_seen_at = _utcnow() - timedelta(minutes=31)

    with pytest.raises(SessionNotFound):
        manager.get_session(session_id)

    assert manager.stats()["active_sessions"] == 0


def test_upload_world_rejects_oversized_multipart_file(tmp_path):
    client = create_app(
        {
            "TESTING": True,
            "WORLDS_DIR": tmp_path / "worlds",
            "EXAMPLES_DIR": tmp_path / "examples",
            "MAX_WORLD_JSON_SIZE_BYTES": 4,
        }
    ).test_client()
    session = client.post("/api/sessions").get_json()

    res = client.post(
        f"/api/sessions/{session['session_id']}/world/upload",
        data={"file": (BytesIO(b'{"too_large": true}'), "world.json")},
        headers=auth_headers(session),
        content_type="multipart/form-data",
    )

    assert res.status_code == 400
    assert res.get_json()["error"]["code"] == "INVALID_PAYLOAD"
