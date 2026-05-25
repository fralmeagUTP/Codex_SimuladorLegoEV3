#!/usr/bin/env python
"""Validate EV3 web /healthz for Redis rollout phases."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any


def _nested_get(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _expect(payload: dict[str, Any], path: str, expected: Any) -> tuple[bool, str]:
    value = _nested_get(payload, path)
    ok = value == expected
    return ok, f"{path}: esperado={expected!r} actual={value!r}"


def _run_checks(payload: dict[str, Any], mode: str) -> list[tuple[bool, str]]:
    checks: list[tuple[bool, str]] = [_expect(payload, "status", "ok")]
    if mode in {"canary", "primary"}:
        checks.extend(
            [
                _expect(payload, "redis.enabled", True),
                _expect(payload, "redis.url_configured", True),
            ]
        )
    if mode == "canary":
        checks.extend(
            [
                _expect(payload, "session_manager.session_backend", "memory"),
                _expect(payload, "session_manager.is_redis_primary", False),
            ]
        )
    elif mode == "primary":
        checks.extend(
            [
                _expect(payload, "session_manager.session_backend", "redis"),
                _expect(payload, "session_manager.is_redis_primary", True),
            ]
        )
    elif mode == "file":
        checks.extend(
            [
                _expect(payload, "session_manager.session_backend", "memory"),
                _expect(payload, "session_manager.is_redis_primary", False),
                _expect(payload, "session_manager.metadata_mirror.driver", "file"),
                _expect(payload, "session_manager.metadata_mirror.enabled", True),
            ]
        )
        redis_enabled = _nested_get(payload, "redis.enabled")
        checks.append((redis_enabled in {False, None}, f"redis.enabled: esperado=False/None actual={redis_enabled!r}"))
    checks.append(_expect(payload, "session_manager.degraded_to_memory", False))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida healthz para rollout Redis.")
    parser.add_argument("url", help="URL completa de healthz, p.ej. https://dominio/app/healthz")
    parser.add_argument(
        "--mode",
        choices=("canary", "primary", "file"),
        default="canary",
        help="Modo de validacion: canary/primary (Redis) o file (shared hosting sin Redis).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Timeout HTTP en segundos.",
    )
    parser.add_argument(
        "--show-json",
        action="store_true",
        help="Imprime el JSON completo recibido desde /healthz.",
    )
    args = parser.parse_args()

    try:
        with urllib.request.urlopen(args.url, timeout=args.timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        print(f"ERROR_HTTP: {exc}")
        return 2

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR_JSON: {exc}")
        return 3

    checks = _run_checks(payload, args.mode)
    failed = [line for ok, line in checks if not ok]

    print(f"Modo: {args.mode}")
    print(f"Worker: id={_nested_get(payload, 'worker_id')} pid={_nested_get(payload, 'worker_pid')}")
    for ok, line in checks:
        mark = "OK" if ok else "FAIL"
        print(f"[{mark}] {line}")
    if failed:
        has_only_legacy_status = (
            isinstance(payload, dict)
            and payload.get("status") == "ok"
            and _nested_get(payload, "session_manager") is None
            and _nested_get(payload, "redis") is None
        )
        if has_only_legacy_status:
            print(
                "\nDiagnostico: la app remota responde /healthz, "
                "pero con contrato antiguo (sin session_manager/redis). "
                "Probable despliegue incompleto o app sin reiniciar."
            )
        if args.show_json:
            print("\nJSON recibido:")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        print("\nResultado: FALLA")
        return 1
    if args.show_json:
        print("\nJSON recibido:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("\nResultado: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
