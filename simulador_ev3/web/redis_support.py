"""Optional Redis diagnostics helpers for phased session migration."""

from __future__ import annotations

from typing import Any


def redis_runtime_state(config: dict[str, Any]) -> dict[str, Any]:
    """Return Redis state without mutating runtime behavior."""

    enabled = bool(config.get("REDIS_ENABLED", False))
    backend = str(config.get("SESSION_BACKEND", "memory")).strip().lower() or "memory"
    url = str(config.get("REDIS_URL", "")).strip()
    ping_enabled = bool(config.get("REDIS_HEALTHCHECK_PING", False))
    result: dict[str, Any] = {
        "backend": backend,
        "enabled": enabled,
        "url_configured": bool(url),
        "ping_enabled": ping_enabled,
        "client_available": False,
        "ping_ok": None,
        "error": None,
    }
    try:
        import redis  # type: ignore[import-not-found]
    except Exception:  # noqa: BLE001
        result["error"] = "redis_package_not_installed"
        return result

    result["client_available"] = True
    if not enabled:
        return result
    if not url:
        result["ping_ok"] = False
        result["error"] = "redis_url_missing"
        return result
    if not ping_enabled:
        return result

    try:
        client = redis.Redis.from_url(
            url,
            socket_connect_timeout=float(config.get("REDIS_CONNECT_TIMEOUT_S", 0.2)),
            socket_timeout=float(config.get("REDIS_SOCKET_TIMEOUT_S", 0.2)),
        )
        result["ping_ok"] = bool(client.ping())
    except Exception as exc:  # noqa: BLE001
        result["ping_ok"] = False
        result["error"] = type(exc).__name__
    return result

