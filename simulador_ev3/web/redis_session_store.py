"""Redis-backed passive metadata mirror for phased session migration."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class RedisSessionStore:
    """Best-effort metadata mirror; never raises to callers."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._enabled = bool(config.get("REDIS_ENABLED", False))
        self._url = str(config.get("REDIS_URL", "")).strip()
        self._prefix = str(config.get("REDIS_PREFIX", "ev3web")).strip() or "ev3web"
        self._connect_timeout = float(config.get("REDIS_CONNECT_TIMEOUT_S", 0.2))
        self._socket_timeout = float(config.get("REDIS_SOCKET_TIMEOUT_S", 0.2))
        self._client: Any | None = None
        self._client_ready = False
        self._stats: dict[str, int] = {
            "writes_ok": 0,
            "writes_failed": 0,
            "touch_ok": 0,
            "touch_failed": 0,
            "delete_ok": 0,
            "delete_failed": 0,
        }
        self._last_error: str | None = None

    def diagnostics(self) -> dict[str, Any]:
        return {
            "enabled": self._enabled,
            "url_configured": bool(self._url),
            "prefix": self._prefix,
            "client_ready": self._client_ready,
            "last_error": self._last_error,
            **self._stats,
        }

    def upsert_metadata(self, session_id: str, metadata: dict[str, Any], ttl_s: int) -> bool:
        client = self._get_client()
        if client is None:
            self._stats["writes_failed"] += 1
            return False
        try:
            payload = {key: self._stringify(value) for key, value in metadata.items()}
            key = self._key(session_id)
            client.hset(key, mapping=payload)
            client.expire(key, max(int(ttl_s), 1))
            self._stats["writes_ok"] += 1
            return True
        except Exception as exc:  # noqa: BLE001
            self._last_error = type(exc).__name__
            self._stats["writes_failed"] += 1
            return False

    def touch(self, session_id: str, last_seen_at: datetime, ttl_s: int) -> bool:
        client = self._get_client()
        if client is None:
            self._stats["touch_failed"] += 1
            return False
        try:
            key = self._key(session_id)
            client.hset(
                key,
                mapping={
                    "last_seen_at": last_seen_at.isoformat(),
                    "updated_at": datetime.utcnow().isoformat() + "Z",
                },
            )
            client.expire(key, max(int(ttl_s), 1))
            self._stats["touch_ok"] += 1
            return True
        except Exception as exc:  # noqa: BLE001
            self._last_error = type(exc).__name__
            self._stats["touch_failed"] += 1
            return False

    def delete(self, session_id: str) -> bool:
        client = self._get_client()
        if client is None:
            self._stats["delete_failed"] += 1
            return False

    def fetch_metadata(self, session_id: str) -> dict[str, str] | None:
        client = self._get_client()
        if client is None:
            return None
        try:
            data = client.hgetall(self._key(session_id))
            if not data:
                return None
            normalized = {str(k): str(v) for k, v in data.items()}
            if "session_id" not in normalized:
                normalized["session_id"] = session_id
            return normalized
        except Exception as exc:  # noqa: BLE001
            self._last_error = type(exc).__name__
            return None
        try:
            client.delete(self._key(session_id))
            self._stats["delete_ok"] += 1
            return True
        except Exception as exc:  # noqa: BLE001
            self._last_error = type(exc).__name__
            self._stats["delete_failed"] += 1
            return False

    def _get_client(self) -> Any | None:
        if not self._enabled or not self._url:
            return None
        if self._client is not None:
            return self._client
        try:
            import redis  # type: ignore[import-not-found]

            self._client = redis.Redis.from_url(
                self._url,
                socket_connect_timeout=self._connect_timeout,
                socket_timeout=self._socket_timeout,
                decode_responses=True,
            )
            self._client.ping()
            self._client_ready = True
            self._last_error = None
        except Exception as exc:  # noqa: BLE001
            self._client = None
            self._client_ready = False
            self._last_error = type(exc).__name__
        return self._client

    def _key(self, session_id: str) -> str:
        return f"{self._prefix}:session:{session_id}:meta"

    @staticmethod
    def _stringify(value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if value is None:
            return ""
        return str(value)
