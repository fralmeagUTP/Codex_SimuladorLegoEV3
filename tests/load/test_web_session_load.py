"""Carga acotada para detectar regresiones de concurrencia en sesiones web."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from simulador_ev3.web.app import create_app


def test_web_accepts_parallel_session_creation(tmp_path) -> None:
    app = create_app(
        {
            "TESTING": True,
            "EXAMPLES_DIR": tmp_path / "examples",
            "WORLDS_DIR": tmp_path / "worlds",
            "MAX_ACTIVE_SESSIONS": 16,
            "MAX_RUNNING_SIMULATIONS": 16,
            "ENABLE_SESSION_CLEANUP_THREAD": False,
        }
    )

    def create_and_load(index: int) -> tuple[int, str]:
        with app.test_client() as client:
            created = client.post("/api/sessions")
            payload = created.get_json()
            assert payload is not None
            response = client.post(
                f"/api/sessions/{payload['session_id']}/script",
                json={"source": f"value_{index} = {index}"},
                headers={"X-EV3-Session-Token": payload["owner_token"]},
            )
            return created.status_code, response.status

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(create_and_load, range(8)))

    assert results == [(201, "200 OK")] * 8
