"""Carga acotada para detectar regresiones de concurrencia en sesiones web."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

import pytest

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

    # La prueba no pretende establecer un SLA: verifica que el escenario de
    # concurrencia deja observabilidad utilizable para una campaña sostenida.
    # Es importante consultarlo después de la carga, no sólo comprobar que las
    # solicitudes HTTP respondieron correctamente.
    with app.test_client() as client:
        metrics = client.get("/metrics").get_json()

    assert metrics is not None
    assert metrics["active_sessions"] == 8
    # `/metrics` se excluye deliberadamente del contador para no contaminar su
    # propia medición: 8 altas de sesión y 8 cargas de script.
    assert metrics["requests_total"] >= 16
    assert metrics["average_duration_ms"] >= 0
    # El perfil TESTING usa el runtime local por diseño; los contadores de
    # worker siguen debiendo estar disponibles aunque su valor sea cero.
    assert metrics["active_workers"] >= 0
    assert metrics["worker_memory_bytes"] >= 0
    assert metrics["worker_peak_memory_bytes"] >= metrics["worker_memory_bytes"]
    assert metrics["worker_event_queue_depth"] >= 0
    assert metrics["worker_last_tick_total"] >= 0


def test_web_isolated_workers_publish_operational_metrics(tmp_path, monkeypatch) -> None:
    """La carga aislada publica diagnósticos reales, sin fijar un SLA."""

    monkeypatch.setenv("EV3_WORKER_ISOLATION_ENABLED", "true")
    app = create_app(
        {
            "TESTING": True,
            "EXAMPLES_DIR": tmp_path / "examples",
            "WORLDS_DIR": tmp_path / "worlds",
            "MAX_ACTIVE_SESSIONS": 2,
            "MAX_RUNNING_SIMULATIONS": 2,
            "ENABLE_SESSION_CLEANUP_THREAD": False,
        }
    )
    sessions: list[dict[str, str]] = []
    try:
        with app.test_client() as client:
            for _ in range(2):
                payload = client.post("/api/sessions").get_json()
                assert payload is not None
                sessions.append(payload)
            # La primera consulta solicita heartbeat; la segunda consume sus
            # eventos, evitando asumir que IPC entrega en el mismo instante.
            client.get("/metrics")
            time.sleep(0.1)
            metrics = client.get("/metrics").get_json()

        assert metrics is not None
        assert metrics["active_sessions"] == 2
        assert metrics["active_workers"] == 2
        assert metrics["worker_memory_bytes"] > 0
        assert metrics["worker_peak_memory_bytes"] >= metrics["worker_memory_bytes"]
        assert metrics["worker_event_queue_depth"] >= 0
        assert metrics["worker_last_tick_total"] >= 0
    finally:
        manager = app.extensions["session_manager"]
        for session in sessions:
            manager.close_session(session["session_id"], session["owner_token"])


@pytest.mark.performance
def test_web_sustained_parallel_load_respects_local_latency_budget(tmp_path) -> None:
    """La carga sintética sostenida debe conservar latencia acotada y métricas sanas.

    El umbral es deliberadamente amplio para CI: detecta bloqueos/regresiones de
    serialización, no pretende sustituir una prueba de capacidad de producción.
    """
    rounds = 3
    parallelism = 4
    app = create_app(
        {
            "TESTING": True,
            "EXAMPLES_DIR": tmp_path / "examples",
            "WORLDS_DIR": tmp_path / "worlds",
            "MAX_ACTIVE_SESSIONS": rounds * parallelism + 2,
            "MAX_RUNNING_SIMULATIONS": rounds * parallelism + 2,
            "ENABLE_SESSION_CLEANUP_THREAD": False,
        }
    )

    def create_and_load(index: int) -> tuple[int, int, float]:
        started_at = time.perf_counter()
        with app.test_client() as client:
            created = client.post("/api/sessions")
            payload = created.get_json()
            assert payload is not None
            loaded = client.post(
                f"/api/sessions/{payload['session_id']}/script",
                json={"source": f"round_value_{index} = {index}"},
                headers={"X-EV3-Session-Token": payload["owner_token"]},
            )
        return created.status_code, loaded.status_code, time.perf_counter() - started_at

    campaign_started_at = time.perf_counter()
    results: list[tuple[int, int, float]] = []
    with ThreadPoolExecutor(max_workers=parallelism) as executor:
        for round_index in range(rounds):
            first = round_index * parallelism
            results.extend(executor.map(create_and_load, range(first, first + parallelism)))
    campaign_duration_s = time.perf_counter() - campaign_started_at

    assert [(created, loaded) for created, loaded, _ in results] == [(201, 200)] * (rounds * parallelism)
    assert max(duration for _, _, duration in results) < 2.0
    assert campaign_duration_s < 5.0

    with app.test_client() as client:
        metrics = client.get("/metrics").get_json()
    assert metrics is not None
    assert metrics["active_sessions"] == rounds * parallelism
    assert metrics["average_duration_ms"] >= 0
    assert metrics["worker_event_queue_depth"] >= 0
