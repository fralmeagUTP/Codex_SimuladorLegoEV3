"""Ejecuta una campaña HTTP local de sesiones concurrentes para la Web EV3."""

from __future__ import annotations

import argparse
import json
import socket
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from werkzeug.serving import make_server

from simulador_ev3.web.app import create_app

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE_DIR = ROOT / "Documentos" / "EVIDENCIA_SESIONES_CONCURRENTES"


def free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as socket_handle:
        socket_handle.bind(("127.0.0.1", 0))
        return int(socket_handle.getsockname()[1])


def request_json(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
    token: str | None = None,
) -> tuple[int, dict[str, object]]:
    body = json.dumps(payload or {}).encode("utf-8") if method in {"POST", "PUT", "PATCH"} else None
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["X-Session-Token"] = token
    request = Request(f"{base_url}{path}", data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=10) as response:  # noqa: S310 -- URL estrictamente local.
            return int(response.status), json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raw = exc.read().decode("utf-8")
        return int(exc.code), json.loads(raw) if raw else {}


class LocalWebServer:
    """Instancia HTTP temporal que no interfiere con el servidor del usuario."""

    def __init__(self, max_sessions: int) -> None:
        self.port = free_port()
        temp_root = ROOT / ".load-test-tmp"
        temp_root.mkdir(exist_ok=True)
        self._temp = tempfile.TemporaryDirectory(prefix="sessions_", dir=temp_root)
        root = Path(self._temp.name)
        self.app = create_app(
            {
                "TESTING": True,
                "EXAMPLES_DIR": root / "examples",
                "WORLDS_DIR": root / "worlds",
                "MAX_ACTIVE_SESSIONS": max_sessions,
                "MAX_RUNNING_SIMULATIONS": max_sessions,
                "ENABLE_SESSION_CLEANUP_THREAD": False,
                "FILE_MIRROR_ENABLED": False,
            }
        )
        self.server = make_server("127.0.0.1", self.port, self.app, threaded=True)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def __enter__(self) -> "LocalWebServer":
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.server.shutdown()
        self.thread.join(timeout=3)
        self._temp.cleanup()


def run_campaign(users: int, parallelism: int) -> dict[str, object]:
    """Crea usuarios, demuestra aislamiento y deja el servidor sin sesiones."""

    started = time.perf_counter()
    with LocalWebServer(max_sessions=users) as server:
        def create_user(index: int) -> dict[str, object]:
            user_started = time.perf_counter()
            status, created = request_json(server.base_url, "/api/sessions", method="POST")
            if status != 201:
                return {
                    "index": index,
                    "create_status": status,
                    "latency_ms": round((time.perf_counter() - user_started) * 1000, 2),
                }
            session_id = str(created["session_id"])
            token = str(created["owner_token"])
            script_status, script = request_json(
                server.base_url,
                f"/api/sessions/{session_id}/script",
                method="POST",
                payload={"source": f"session_marker_{index} = {index}"},
                token=token,
            )
            summary_status, summary = request_json(
                server.base_url,
                f"/api/sessions/{session_id}",
                token=token,
            )
            return {
                "index": index,
                "create_status": status,
                "script_status": script_status,
                "summary_status": summary_status,
                "session_id": session_id,
                "token": token,
                "has_script": bool(summary.get("has_script")),
                "script_response": script,
                "latency_ms": round((time.perf_counter() - user_started) * 1000, 2),
            }

        with ThreadPoolExecutor(max_workers=parallelism) as executor:
            users_result = list(executor.map(create_user, range(users)))

        valid_users = [item for item in users_result if item.get("create_status") == 201]
        unique_ids = {item["session_id"] for item in valid_users}
        unique_tokens = {item["token"] for item in valid_users}
        unauthorized_status = 0
        if len(valid_users) >= 2:
            unauthorized_status, _ = request_json(
                server.base_url,
                f"/api/sessions/{valid_users[1]['session_id']}",
                token=str(valid_users[0]["token"]),
            )

        overflow_status, overflow = request_json(server.base_url, "/api/sessions", method="POST")
        _, metrics_before_close = request_json(server.base_url, "/metrics")
        close_statuses = [
            request_json(
                server.base_url,
                f"/api/sessions/{item['session_id']}",
                method="DELETE",
                token=str(item["token"]),
            )[0]
            for item in valid_users
        ]
        _, metrics_after_close = request_json(server.base_url, "/metrics")

    return {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "campaign": {"users": users, "parallelism": parallelism, "transport": "local_http"},
        "results": {
            "created": len(valid_users),
            "unique_session_ids": len(unique_ids),
            "unique_owner_tokens": len(unique_tokens),
            "all_scripts_loaded": all(
                item.get("script_status") == 200 and item.get("has_script") for item in valid_users
            ),
            "cross_session_status": unauthorized_status,
            "overflow_status": overflow_status,
            "overflow_error": overflow,
            "all_closed": all(status == 200 for status in close_statuses),
            "metrics_before_close": metrics_before_close,
            "metrics_after_close": metrics_after_close,
            "max_user_latency_ms": max((float(item["latency_ms"]) for item in valid_users), default=0.0),
        },
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Carga HTTP local de sesiones concurrentes EV3.")
    parser.add_argument("--users", type=int, default=24)
    parser.add_argument("--parallelism", type=int, default=8)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    args = parser.parse_args()
    if args.users < 2 or args.parallelism < 1 or args.parallelism > args.users:
        parser.error("Use al menos dos usuarios y una concurrencia entre 1 y el total.")

    evidence = run_campaign(args.users, args.parallelism)
    results = evidence["results"]
    assert isinstance(results, dict)
    passed = (
        results["created"] == args.users
        and results["unique_session_ids"] == args.users
        and results["unique_owner_tokens"] == args.users
        and results["all_scripts_loaded"]
        and results["cross_session_status"] in {403, 404}
        and results["overflow_status"] == 429
        and results["all_closed"]
        and results["metrics_before_close"].get("active_sessions") == args.users
        and results["metrics_after_close"].get("active_sessions") == 0
    )
    evidence["passed"] = passed
    args.output_dir.mkdir(parents=True, exist_ok=True)
    target = args.output_dir / "campana_sesiones_local.json"
    target.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    print(f"Evidencia: {target.relative_to(ROOT)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
