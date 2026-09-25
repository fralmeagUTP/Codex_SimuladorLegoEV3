"""File-backed shared session metadata store for shared hosting."""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any


class FileSessionStore:
    """Cross-worker metadata mirror using JSON files on shared filesystem."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._enabled = bool(config.get("FILE_MIRROR_ENABLED", True))
        configured_dir = config.get("FILE_MIRROR_DIR")
        if configured_dir is None:
            configured_dir = Path(tempfile.gettempdir()) / "ev3web_session_mirror"
        self._base_dir = Path(configured_dir).expanduser().resolve()
        self._prefix = str(config.get("REDIS_PREFIX", "ev3web")).strip() or "ev3web"
        self._lock = threading.RLock()
        self._stats: dict[str, int] = {
            "writes_ok": 0,
            "writes_failed": 0,
            "touch_ok": 0,
            "touch_failed": 0,
            "delete_ok": 0,
            "delete_failed": 0,
            "fetch_ok": 0,
            "fetch_miss": 0,
            "fetch_failed": 0,
            "expired_cleanups": 0,
        }
        self._last_error: str | None = None
        if self._enabled:
            try:
                self._base_dir.mkdir(parents=True, exist_ok=True)
                self._restrict_permissions(self._base_dir, 0o700)
                self._last_error = None
            except Exception as exc:  # noqa: BLE001
                self._enabled = False
                self._last_error = type(exc).__name__

    def diagnostics(self) -> dict[str, Any]:
        return {
            "enabled": self._enabled,
            "driver": "file",
            "dir": str(self._base_dir),
            "last_error": self._last_error,
            **self._stats,
        }

    def upsert_metadata(self, session_id: str, metadata: dict[str, Any], ttl_s: int) -> bool:
        if not self._enabled:
            self._stats["writes_failed"] += 1
            return False
        payload = {
            "session_id": session_id,
            "expires_at": int(time.time()) + max(int(ttl_s), 1),
            "updated_at": int(time.time()),
            "metadata": {str(k): self._stringify(v) for k, v in metadata.items()},
        }
        ok = self._write_payload(session_id, payload)
        self._stats["writes_ok" if ok else "writes_failed"] += 1
        return ok

    def touch(self, session_id: str, last_seen_at: Any, ttl_s: int) -> bool:
        if not self._enabled:
            self._stats["touch_failed"] += 1
            return False
        payload = self._read_payload(session_id)
        if payload is None:
            self._stats["touch_failed"] += 1
            return False
        metadata = payload.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        metadata["last_seen_at"] = self._stringify(last_seen_at)
        payload["metadata"] = metadata
        payload["expires_at"] = int(time.time()) + max(int(ttl_s), 1)
        payload["updated_at"] = int(time.time())
        ok = self._write_payload(session_id, payload)
        self._stats["touch_ok" if ok else "touch_failed"] += 1
        return ok

    def delete(self, session_id: str) -> bool:
        if not self._enabled:
            self._stats["delete_failed"] += 1
            return False
        try:
            path = self._path_for(session_id)
            if path.exists():
                path.unlink()
            self._stats["delete_ok"] += 1
            return True
        except Exception as exc:  # noqa: BLE001
            self._last_error = type(exc).__name__
            self._stats["delete_failed"] += 1
            return False

    def fetch_metadata(self, session_id: str) -> dict[str, str] | None:
        if not self._enabled:
            self._stats["fetch_failed"] += 1
            return None
        payload = self._read_payload(session_id)
        if payload is None:
            self._stats["fetch_miss"] += 1
            return None
        expires_at = int(payload.get("expires_at", 0))
        if expires_at > 0 and expires_at <= int(time.time()):
            self.delete(session_id)
            self._stats["expired_cleanups"] += 1
            self._stats["fetch_miss"] += 1
            return None
        metadata = payload.get("metadata", {})
        if not isinstance(metadata, dict):
            self._stats["fetch_failed"] += 1
            return None
        normalized = {str(k): str(v) for k, v in metadata.items()}
        if "session_id" not in normalized:
            normalized["session_id"] = session_id
        self._stats["fetch_ok"] += 1
        return normalized

    def _path_for(self, session_id: str) -> Path:
        safe = str(session_id)
        if not safe or len(safe) > 128 or any(not (ch.isalnum() or ch in {"-", "_"}) for ch in safe):
            raise ValueError("Identificador de sesión inválido para el espejo de archivos.")
        path = (self._base_dir / f"{self._prefix}_session_{safe}.json").resolve()
        if path.parent != self._base_dir:
            raise ValueError("Ruta de espejo de sesión inválida.")
        return path

    def _read_payload(self, session_id: str) -> dict[str, Any] | None:
        path = self._path_for(session_id)
        try:
            if not path.exists():
                return None
            text = path.read_text(encoding="utf-8")
            data = json.loads(text)
            if isinstance(data, dict):
                return data
            return None
        except Exception as exc:  # noqa: BLE001
            self._last_error = type(exc).__name__
            return None

    def _write_payload(self, session_id: str, payload: dict[str, Any]) -> bool:
        tmp_path: Path | None = None
        try:
            path = self._path_for(session_id)
            tmp_path = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
            with self._lock:
                path.parent.mkdir(parents=True, exist_ok=True)
                tmp_path.write_text(
                    json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                    encoding="utf-8",
                )
                self._restrict_permissions(tmp_path, 0o600)
                tmp_path.replace(path)
                self._restrict_permissions(path, 0o600)
            self._last_error = None
            return True
        except Exception as exc:  # noqa: BLE001
            self._last_error = type(exc).__name__
            try:
                if tmp_path is not None and tmp_path.exists():
                    tmp_path.unlink()
            except Exception:  # noqa: BLE001
                pass
            return False

    @staticmethod
    def _stringify(value: Any) -> str:
        if value is None:
            return ""
        return str(value)

    @staticmethod
    def _restrict_permissions(path: Path, mode: int) -> None:
        """Intenta limitar acceso a propietario; Windows conserva sus ACL propias."""

        try:
            os.chmod(path, mode)
        except OSError:
            # El almacenamiento sigue disponible si la plataforma no expone chmod.
            pass
