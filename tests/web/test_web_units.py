from __future__ import annotations

import json
import time
from datetime import timedelta
from io import BytesIO

import pytest

from simulador_ev3.shared.session_status import SessionStatus
from simulador_ev3.web.app import create_app
from simulador_ev3.web.errors import InvalidPayload, SessionNotFound
from simulador_ev3.web.file_session_store import FileSessionStore
from simulador_ev3.web.routes.helpers import safe_child
from simulador_ev3.web.services.simulation_session import SimulationSession, asset_catalog_dict
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


def test_web_session_throttles_snapshot_events_without_stalling_engine(tmp_path):
    session = SimulationSession(
        session_id="perf-session",
        config={
            "WORLDS_DIR": tmp_path / "worlds",
            "EXAMPLES_DIR": tmp_path / "examples",
            "SCRIPT_MAX_RUNTIME_S": 1.0,
            "WEB_SNAPSHOT_MAX_HZ": 10.0,
        },
        max_runtime_s=1.0,
    )

    session.load_script("from pybricks.tools import wait\nwait(500)\n")
    session.start()
    try:
        time.sleep(0.45)
        events = session.events_since(0)
        snapshot_events = [event for event in events if event["type"] == "snapshot"]
        latest = session.snapshot_response()["snapshot"]
    finally:
        session.stop()

    # A 10 Hz, 450 ms de ejecución producen hasta cinco eventos, incluido el
    # inicial; la simulación interna sigue avanzando a 50 Hz.
    assert 2 <= len(snapshot_events) <= 6
    assert latest["tick"] >= snapshot_events[-1]["payload"]["tick"]
    assert latest["snapshot_version"] == 1
    assert latest["snapshot_generation"] == 0


@pytest.mark.parametrize("snapshot_hz", [0, 9, 61, "not-a-number"])
def test_web_rejects_unsafe_snapshot_rate(tmp_path, snapshot_hz):
    with pytest.raises(RuntimeError, match="WEB_SNAPSHOT_MAX_HZ"):
        create_app(
            {
                "TESTING": True,
                "WORLDS_DIR": tmp_path / "worlds",
                "EXAMPLES_DIR": tmp_path / "examples",
                "WEB_SNAPSHOT_MAX_HZ": snapshot_hz,
            }
        )


def test_web_session_discards_late_transition_after_finished(tmp_path):
    session = SimulationSession(
        session_id="state-session",
        config={"WORLDS_DIR": tmp_path / "worlds", "EXAMPLES_DIR": tmp_path / "examples"},
        max_runtime_s=1.0,
    )

    assert session._transition(SessionStatus.READY)
    assert session._transition(SessionStatus.RUNNING)
    assert session._transition(SessionStatus.FINISHED)
    assert not session._transition(SessionStatus.PAUSED)
    assert session.status == "finished"


def test_terminal_status_is_preceded_by_a_snapshot_with_the_same_status(tmp_path):
    """El consumidor SSE nunca debe recibir ``finished`` antes de su DTO final."""

    session = SimulationSession(
        session_id="terminal-snapshot-order",
        config={"WORLDS_DIR": tmp_path / "worlds", "EXAMPLES_DIR": tmp_path / "examples"},
        max_runtime_s=1.0,
    )
    try:
        assert session._transition(SessionStatus.READY)
        assert session._transition(SessionStatus.RUNNING)
        session._latest_snapshot = {
            "tick": 42,
            "sim_time_s": 0.84,
            "robot": {"x_mm": 120.0, "y_mm": 80.0, "theta_deg": 90.0},
        }

        session._on_status("finished")
        events = session.events_since(0)
        terminal_status_index = next(
            index
            for index, event in enumerate(events)
            if event["type"] == "status" and event["payload"]["status"] == "finished"
        )
        final_snapshot = events[terminal_status_index - 1]

        assert final_snapshot["type"] == "snapshot"
        assert final_snapshot["payload"]["status"] == "finished"
        assert final_snapshot["payload"]["tick"] == 42
    finally:
        session.close()


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

    traversal = client.get("/assets/..secret.png")
    bad_extension = client.get("/assets/robot_ev3_32x32.svg")

    assert traversal.status_code == 400
    assert traversal.get_json()["error"]["code"] == "INVALID_PAYLOAD"
    assert bad_extension.status_code == 400
    assert bad_extension.get_json()["error"]["code"] == "INVALID_PAYLOAD"


def test_image_asset_legacy_route_is_kept_for_compatibility(tmp_path):
    client = make_client(tmp_path)

    res = client.get("/assets/images/robot_ev3_32x32.png")

    assert res.status_code == 308
    assert res.headers["Location"].endswith("/assets/robot_ev3_32x32.png")


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


def test_session_manager_mirrors_metadata_lifecycle(tmp_path):
    class FakeMirror:
        def __init__(self):
            self.upserts = []
            self.touches = []
            self.deletes = []

        def upsert_metadata(self, session_id, metadata, ttl_s):
            self.upserts.append((session_id, metadata, ttl_s))
            return True

        def touch(self, session_id, last_seen_at, ttl_s):
            self.touches.append((session_id, last_seen_at, ttl_s))
            return True

        def delete(self, session_id):
            self.deletes.append(session_id)
            return True

        def diagnostics(self):
            return {"enabled": True}

    mirror = FakeMirror()
    manager = SessionManager(
        {
            "SESSION_IDLE_TIMEOUT_MIN": 30,
            "MAX_ACTIVE_SESSIONS": 5,
            "MAX_RUNNING_SIMULATIONS": 5,
            "SCRIPT_MAX_RUNTIME_S": 0.5,
            "WORLDS_DIR": tmp_path / "worlds",
            "EXAMPLES_DIR": tmp_path / "examples",
        },
        metadata_store=mirror,
    )
    session_id, token = manager.create_session()
    manager.get_session(session_id, token)
    manager.close_session(session_id, token)

    assert mirror.upserts
    assert mirror.touches
    assert mirror.deletes == [session_id]


def test_session_manager_recovers_session_from_metadata_mirror(tmp_path):
    session_id = "recovered-session"
    owner_token = "owner-secret"
    owner_hash = _hash_token(owner_token)

    class RecoverMirror:
        def upsert_metadata(self, _session_id, _metadata, ttl_s):
            return True

        def touch(self, _session_id, _last_seen_at, ttl_s):
            return True

        def delete(self, _session_id):
            return True

        def fetch_metadata(self, requested_id):
            if requested_id != session_id:
                return None
            return {
                "session_id": session_id,
                "owner_token_hash": owner_hash,
                "created_at": _utcnow().isoformat(),
            }

        def diagnostics(self):
            return {"enabled": True}

    manager = SessionManager(
        {
            "SESSION_IDLE_TIMEOUT_MIN": 30,
            "MAX_ACTIVE_SESSIONS": 5,
            "MAX_RUNNING_SIMULATIONS": 5,
            "SCRIPT_MAX_RUNTIME_S": 0.5,
            "WORLDS_DIR": tmp_path / "worlds",
            "EXAMPLES_DIR": tmp_path / "examples",
        },
        metadata_store=RecoverMirror(),
    )

    recovered = manager.get_session(session_id, owner_token)

    assert recovered.session_id == session_id
    assert manager.stats()["sessions_recovered_from_mirror"] == 1


def test_session_manager_recovery_fails_with_invalid_owner_token(tmp_path):
    session_id = "recovered-session"
    owner_hash = _hash_token("correct-token")

    class RecoverMirror:
        def upsert_metadata(self, _session_id, _metadata, ttl_s):
            return True

        def touch(self, _session_id, _last_seen_at, ttl_s):
            return True

        def delete(self, _session_id):
            return True

        def fetch_metadata(self, requested_id):
            if requested_id != session_id:
                return None
            return {
                "session_id": session_id,
                "owner_token_hash": owner_hash,
                "created_at": _utcnow().isoformat(),
            }

        def diagnostics(self):
            return {"enabled": True}

    manager = SessionManager(
        {
            "SESSION_IDLE_TIMEOUT_MIN": 30,
            "MAX_ACTIVE_SESSIONS": 5,
            "MAX_RUNNING_SIMULATIONS": 5,
            "SCRIPT_MAX_RUNTIME_S": 0.5,
            "WORLDS_DIR": tmp_path / "worlds",
            "EXAMPLES_DIR": tmp_path / "examples",
        },
        metadata_store=RecoverMirror(),
    )

    with pytest.raises(SessionNotFound):
        manager.get_session(session_id, "wrong-token")

    assert manager.stats()["session_recovery_failures"] == 1


def test_session_manager_recovers_script_world_and_debug_state_from_mirror(tmp_path):
    shared: dict[str, dict[str, str]] = {}

    class SharedMirror:
        def __init__(self, state: dict[str, dict[str, str]]):
            self._state = state

        def upsert_metadata(self, session_id, metadata, ttl_s):
            self._state[session_id] = {str(k): str(v) for k, v in metadata.items()}
            return True

        def touch(self, session_id, last_seen_at, ttl_s):
            if session_id in self._state:
                self._state[session_id]["last_seen_at"] = last_seen_at.isoformat()
            return True

        def delete(self, session_id):
            self._state.pop(session_id, None)
            return True

        def fetch_metadata(self, session_id):
            data = self._state.get(session_id)
            return dict(data) if data is not None else None

        def diagnostics(self):
            return {"enabled": True}

    config = {
        "SESSION_IDLE_TIMEOUT_MIN": 30,
        "MAX_ACTIVE_SESSIONS": 5,
        "MAX_RUNNING_SIMULATIONS": 5,
        "SCRIPT_MAX_RUNTIME_S": 1.0,
        "WORLDS_DIR": tmp_path / "worlds",
        "EXAMPLES_DIR": tmp_path / "examples",
    }

    manager_a = SessionManager(config, metadata_store=SharedMirror(shared))
    session_id, owner_token = manager_a.create_session()
    session_a = manager_a.get_session(session_id, owner_token)
    session_a.load_script("x = 1\nx = x + 1\n")
    session_a.load_blank_world(width_cells=20, height_cells=20)
    session_a.set_debug_breakpoints({2, 5})
    session_a.set_debug_watches(["x + 1"])
    manager_a.sync_session_metadata(session_id)

    manager_b = SessionManager(config, metadata_store=SharedMirror(shared))
    session_b = manager_b.get_session(session_id, owner_token)
    summary = session_b.summary()
    world = session_b.current_world()

    assert summary["has_script"] is True
    assert summary["breakpoints"] == [2, 5]
    assert summary["watches"] == ["x + 1"]
    assert world is not None
    assert world["width_mm"] == 2000.0
    assert world["height_mm"] == 2000.0
    assert manager_b.stats()["sessions_recovered_from_mirror"] == 1


def test_session_manager_redis_primary_degrades_to_memory_when_mirror_write_fails(tmp_path):
    class FailingMirror:
        def upsert_metadata(self, session_id, metadata, ttl_s):
            return False

        def touch(self, session_id, last_seen_at, ttl_s):
            return False

        def delete(self, session_id):
            return False

        def fetch_metadata(self, session_id):
            return None

        def diagnostics(self):
            return {"enabled": True, "client_ready": False}

    manager = SessionManager(
        {
            "SESSION_BACKEND": "redis",
            "REDIS_ENABLED": True,
            "SESSION_IDLE_TIMEOUT_MIN": 30,
            "MAX_ACTIVE_SESSIONS": 5,
            "MAX_RUNNING_SIMULATIONS": 5,
            "SCRIPT_MAX_RUNTIME_S": 1.0,
            "WORLDS_DIR": tmp_path / "worlds",
            "EXAMPLES_DIR": tmp_path / "examples",
        },
        metadata_store=FailingMirror(),
    )

    session_id, token = manager.create_session()
    session = manager.get_session(session_id, token)
    diag = manager.diagnostics()

    assert session.session_id == session_id
    assert diag["is_redis_primary"] is True
    assert diag["degraded_to_memory"] is True
    assert diag["degraded_reason"] == "redis_mirror_touch_failed"


def test_session_manager_redis_primary_not_degraded_when_mirror_ok(tmp_path):
    class HealthyMirror:
        def upsert_metadata(self, session_id, metadata, ttl_s):
            return True

        def touch(self, session_id, last_seen_at, ttl_s):
            return True

        def delete(self, session_id):
            return True

        def fetch_metadata(self, session_id):
            return None

        def diagnostics(self):
            return {"enabled": True, "client_ready": True}

    manager = SessionManager(
        {
            "SESSION_BACKEND": "redis",
            "REDIS_ENABLED": True,
            "SESSION_IDLE_TIMEOUT_MIN": 30,
            "MAX_ACTIVE_SESSIONS": 5,
            "MAX_RUNNING_SIMULATIONS": 5,
            "SCRIPT_MAX_RUNTIME_S": 1.0,
            "WORLDS_DIR": tmp_path / "worlds",
            "EXAMPLES_DIR": tmp_path / "examples",
        },
        metadata_store=HealthyMirror(),
    )

    session_id, token = manager.create_session()
    manager.get_session(session_id, token)
    diag = manager.diagnostics()

    assert diag["is_redis_primary"] is True
    assert diag["degraded_to_memory"] is False
    assert diag["degraded_reason"] is None


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


def test_loading_plain_world_clears_stale_editor_overlays(tmp_path):
    worlds_dir = tmp_path / "worlds"
    examples_dir = tmp_path / "examples"
    worlds_dir.mkdir()
    examples_dir.mkdir()

    plain_world = {
        "version": 1,
        "world": {
            "width_mm": 2000.0,
            "height_mm": 2000.0,
            "surface": {"cell_size_mm": 50.0, "default_color": "WHITE", "cells": []},
            "obstacles": [],
            "beacons": [],
        },
    }
    (worlds_dir / "plain.json").write_text(
        json.dumps(plain_world, ensure_ascii=False),
        encoding="utf-8",
    )

    session = SimulationSession(
        session_id="overlay-reset",
        config={
            "WORLDS_DIR": worlds_dir,
            "EXAMPLES_DIR": examples_dir,
            "SCRIPT_MAX_RUNTIME_S": 1.0,
        },
        max_runtime_s=1.0,
    )

    # Simula estado previo con overlays del editor.
    session.create_editor_world(width_cells=20, height_cells=20)
    session.place_asset(
        {
            "asset_key": "line_64_64_hor",
            "x": 0,
            "y": 0,
            "rotation": 0,
        }
    )
    assert session.editor_response()["world"]["placements"]

    loaded = session.load_world_name("plain.json")

    assert loaded["world"]["editor_spec"] is None


def test_loading_large_editor_world_keeps_original_dimensions(tmp_path):
    worlds_dir = tmp_path / "worlds"
    examples_dir = tmp_path / "examples"
    worlds_dir.mkdir()
    examples_dir.mkdir()

    editor_world = {
        "schema_version": 1,
        "grid_size_px": 32,
        "world_width_cells": 160,
        "world_height_cells": 160,
        "placements": [
            {
                "id": "robot_0001",
                "asset_key": "robot_ev3_32x32",
                "x": 3008,
                "y": 3008,
                "rotation": 0,
            }
        ],
    }
    (worlds_dir / "large_editor_world.json").write_text(
        json.dumps(editor_world, ensure_ascii=False),
        encoding="utf-8",
    )

    session = SimulationSession(
        session_id="large-world",
        config={
            "WORLDS_DIR": worlds_dir,
            "EXAMPLES_DIR": examples_dir,
            "SCRIPT_MAX_RUNTIME_S": 1.0,
        },
        max_runtime_s=1.0,
    )

    loaded = session.load_world_name("large_editor_world.json")
    world = loaded["world"]

    assert world["width_mm"] == 16000.0
    assert world["height_mm"] == 16000.0
    assert world["editor_spec"]["world_width_cells"] == 160
    assert world["editor_spec"]["world_height_cells"] == 160


def test_file_session_store_lifecycle(tmp_path):
    store = FileSessionStore(
        {
            "FILE_MIRROR_ENABLED": True,
            "FILE_MIRROR_DIR": tmp_path / "mirror",
            "REDIS_PREFIX": "ev3test",
        }
    )

    assert store.upsert_metadata("sid-1", {"status": "ready", "owner_token_hash": "abc"}, ttl_s=30)
    fetched = store.fetch_metadata("sid-1")
    assert fetched is not None
    assert fetched["status"] == "ready"
    assert fetched["owner_token_hash"] == "abc"

    assert store.touch("sid-1", _utcnow(), ttl_s=30)
    fetched2 = store.fetch_metadata("sid-1")
    assert fetched2 is not None
    assert "last_seen_at" in fetched2

    assert store.delete("sid-1")
    assert store.fetch_metadata("sid-1") is None


def test_file_session_store_expires_records(tmp_path):
    store = FileSessionStore(
        {
            "FILE_MIRROR_ENABLED": True,
            "FILE_MIRROR_DIR": tmp_path / "mirror",
        }
    )

    assert store.upsert_metadata("sid-exp", {"status": "ready"}, ttl_s=1)
    time.sleep(1.1)
    assert store.fetch_metadata("sid-exp") is None
