"""Thread-safe in-memory session manager for web simulations."""

from __future__ import annotations

import hashlib
import json
import secrets
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from simulador_ev3.web.errors import CapacityExceeded, SessionForbidden, SessionNotFound
from simulador_ev3.web.services.simulation_session import SimulationSession


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass
class SessionRecord:
    session_id: str
    owner_token_hash: str
    created_at: datetime
    last_seen_at: datetime
    session: SimulationSession


class SessionManager:
    """Owns active simulation sessions for the Flask app."""

    def __init__(self, config: dict[str, Any], metadata_store: Any | None = None) -> None:
        self._lock = threading.RLock()
        self._capacity_changed = threading.Condition(self._lock)
        self._sessions: dict[str, SessionRecord] = {}
        self._metadata_store = metadata_store
        self._session_backend = str(config.get("SESSION_BACKEND", "memory")).strip().lower() or "memory"
        self._is_redis_primary = self._session_backend == "redis"
        self._degraded_to_memory = False
        self._degraded_reason: str | None = None
        self._counters: dict[str, int] = {
            "sessions_created": 0,
            "sessions_closed": 0,
            "session_not_found_errors": 0,
            "session_forbidden_errors": 0,
            "session_expired_errors": 0,
            "sessions_recovered_from_mirror": 0,
            "session_recovery_failures": 0,
        }
        self._idle_timeout = timedelta(minutes=int(config.get("SESSION_IDLE_TIMEOUT_MIN", 30)))
        self._max_active = int(config.get("MAX_ACTIVE_SESSIONS", 20))
        self._max_running = int(config.get("MAX_RUNNING_SIMULATIONS", 8))
        self._script_max_runtime_s = float(config.get("SCRIPT_MAX_RUNTIME_S", 30.0))
        self._config = config

    def create_session(
        self,
        *,
        evict_inactive: bool = False,
        wait_timeout_s: float = 0.0,
    ) -> tuple[str, str]:
        timeout_s = max(0.0, float(wait_timeout_s))
        deadline = time.monotonic() + timeout_s if timeout_s > 0 else 0.0
        with self._lock:
            while True:
                self.cleanup_expired()
                if evict_inactive and len(self._sessions) >= self._max_active:
                    self._evict_oldest_inactive_locked()
                if len(self._sessions) < self._max_active:
                    session_id = str(uuid.uuid4())
                    owner_token = secrets.token_urlsafe(32)
                    session = SimulationSession(
                        session_id=session_id,
                        config=self._config,
                        max_runtime_s=self._script_max_runtime_s,
                    )
                    now = _utcnow()
                    self._sessions[session_id] = SessionRecord(
                        session_id=session_id,
                        owner_token_hash=_hash_token(owner_token),
                        created_at=now,
                        last_seen_at=now,
                        session=session,
                    )
                    mirrored = self._mirror_upsert_locked(self._sessions[session_id])
                    if self._is_redis_primary and not mirrored:
                        self._mark_degraded_locked("redis_mirror_write_failed_create")
                    self._bump_counter_locked("sessions_created")
                    return session_id, owner_token
                if timeout_s <= 0:
                    raise CapacityExceeded("Se alcanzo el limite de sesiones activas.")
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise CapacityExceeded("Se alcanzo el limite de sesiones activas.")
                self._capacity_changed.wait(timeout=min(remaining, 1.0))

    def get_session(
        self,
        session_id: str,
        owner_token: str | None = None,
        *,
        touch: bool = True,
    ) -> SimulationSession:
        with self._lock:
            record = self._sessions.get(session_id)
            if record is None:
                recovered = self._recover_from_metadata_locked(session_id, owner_token)
                if recovered is not None:
                    record = recovered
                    self._bump_counter_locked("sessions_recovered_from_mirror")
                else:
                    if self._is_redis_primary:
                        self._mark_degraded_locked("redis_recovery_miss_or_unavailable")
                    self._bump_counter_locked("session_recovery_failures")
                    self._bump_counter_locked("session_not_found_errors")
                    raise SessionNotFound("La sesion no existe o expiro.")
            if self._is_expired(record):
                session = record.session
                self._sessions.pop(session_id, None)
                session.close()
                self._bump_counter_locked("session_expired_errors")
                raise SessionNotFound("La sesion expiro por inactividad.")
            if owner_token is not None and _hash_token(owner_token) != record.owner_token_hash:
                self._bump_counter_locked("session_forbidden_errors")
                raise SessionForbidden("Token de sesion invalido.")
            if touch:
                record.last_seen_at = _utcnow()
                self._mirror_touch_locked(record)
            return record.session

    def close_session(self, session_id: str, owner_token: str | None = None) -> None:
        with self._lock:
            record = self._sessions.get(session_id)
            if record is None:
                self._bump_counter_locked("session_not_found_errors")
                raise SessionNotFound("La sesion no existe o expiro.")
            if owner_token is not None and _hash_token(owner_token) != record.owner_token_hash:
                self._bump_counter_locked("session_forbidden_errors")
                raise SessionForbidden("Token de sesion invalido.")
            self._sessions.pop(session_id, None)
            deleted = self._mirror_delete_locked(session_id)
            if self._is_redis_primary and not deleted:
                self._mark_degraded_locked("redis_mirror_delete_failed_close")
            self._bump_counter_locked("sessions_closed")
            self._capacity_changed.notify_all()
        record.session.close()

    def cleanup_expired(self) -> int:
        expired: list[SessionRecord] = []
        with self._lock:
            for session_id, record in list(self._sessions.items()):
                if self._is_expired(record):
                    expired.append(record)
                    self._sessions.pop(session_id, None)
            if expired:
                self._capacity_changed.notify_all()
        for record in expired:
            deleted = self._mirror_delete(record.session_id)
            if self._is_redis_primary and not deleted:
                with self._lock:
                    self._mark_degraded_locked("redis_mirror_delete_failed_cleanup")
            record.session.close()
        return len(expired)

    def running_count(self) -> int:
        with self._lock:
            return sum(1 for rec in self._sessions.values() if rec.session.status == "running")

    def can_start(self) -> bool:
        return self.running_count() < self._max_running

    def evict_oldest_running(self) -> bool:
        """Stop and remove the oldest running session to free one execution slot."""
        with self._lock:
            candidates = [record for record in self._sessions.values() if record.session.status == "running"]
            if not candidates:
                return False
            oldest = min(candidates, key=lambda record: record.last_seen_at)
            self._sessions.pop(oldest.session_id, None)
            deleted = self._mirror_delete_locked(oldest.session_id)
            if self._is_redis_primary and not deleted:
                self._mark_degraded_locked("redis_mirror_delete_failed_evict_running")
            self._capacity_changed.notify_all()
        oldest.session.close()
        return True

    def stats(self) -> dict[str, int]:
        with self._lock:
            return {
                "active_sessions": len(self._sessions),
                "running_simulations": self.running_count(),
                "max_active_sessions": self._max_active,
                "max_running_simulations": self._max_running,
                **self._counters,
            }

    def worker_stats(self) -> dict[str, int | float]:
        """Agrega diagnósticos públicos de workers sin exponer sesiones internas."""
        with self._lock:
            diagnostics = [record.session.worker_diagnostics() for record in self._sessions.values()]
        return {
            "active_workers": sum(int(item.get("worker_alive", 0)) for item in diagnostics),
            "worker_cpu_seconds": round(sum(float(item.get("cpu_s", 0.0)) for item in diagnostics), 6),
            "worker_memory_bytes": sum(int(item.get("memory_bytes", 0)) for item in diagnostics),
            "worker_peak_memory_bytes": sum(int(item.get("peak_memory_bytes", 0)) for item in diagnostics),
            "worker_event_queue_depth": sum(int(item.get("event_queue_depth", 0)) for item in diagnostics),
            "worker_last_tick_total": sum(int(item.get("last_tick", 0)) for item in diagnostics),
        }

    def diagnostics(self) -> dict[str, Any]:
        with self._lock:
            mirror_stats = (
                self._metadata_store.diagnostics()
                if self._metadata_store is not None and hasattr(self._metadata_store, "diagnostics")
                else None
            )
            return {
                "session_backend": self._session_backend,
                "is_redis_primary": self._is_redis_primary,
                "degraded_to_memory": self._degraded_to_memory,
                "degraded_reason": self._degraded_reason,
                "redis_enabled": bool(self._config.get("REDIS_ENABLED", False)),
                "session_idle_timeout_min": int(self._idle_timeout.total_seconds() / 60),
                "metadata_mirror": mirror_stats,
                **self._counters,
            }

    def sync_session_metadata(self, session_id: str) -> bool:
        with self._lock:
            record = self._sessions.get(session_id)
            if record is None:
                return False
            mirrored = self._mirror_upsert_locked(record)
            if self._is_redis_primary and not mirrored:
                self._mark_degraded_locked("redis_mirror_write_failed_sync")
            return mirrored or not self._is_redis_primary

    def _is_expired(self, record: SessionRecord) -> bool:
        return _utcnow() - record.last_seen_at > self._idle_timeout

    def _evict_oldest_inactive_locked(self) -> None:
        candidates = [record for record in self._sessions.values() if record.session.status != "running"]
        if not candidates:
            return
        oldest = min(candidates, key=lambda record: record.last_seen_at)
        self._sessions.pop(oldest.session_id, None)
        self._mirror_delete_locked(oldest.session_id)
        self._capacity_changed.notify_all()
        oldest.session.close()

    def _bump_counter_locked(self, key: str, amount: int = 1) -> None:
        self._counters[key] = self._counters.get(key, 0) + int(amount)

    def _mirror_upsert_locked(self, record: SessionRecord) -> bool:
        if self._metadata_store is None:
            return False
        ok = self._metadata_store.upsert_metadata(
            record.session_id,
            {
                "session_id": record.session_id,
                "owner_token_hash": record.owner_token_hash,
                "created_at": record.created_at.isoformat(),
                "last_seen_at": record.last_seen_at.isoformat(),
                "status": record.session.status,
                "runtime_state_json": json.dumps(
                    record.session.runtime_checkpoint(),
                    ensure_ascii=False,
                ),
            },
            ttl_s=max(int(self._idle_timeout.total_seconds()), 1),
        )
        return bool(ok)

    def _mirror_touch_locked(self, record: SessionRecord) -> bool:
        if self._metadata_store is None:
            return False
        ok = self._metadata_store.touch(
            record.session_id,
            record.last_seen_at,
            ttl_s=max(int(self._idle_timeout.total_seconds()), 1),
        )
        if self._is_redis_primary and not ok:
            self._mark_degraded_locked("redis_mirror_touch_failed")
        return bool(ok)

    def _mirror_delete_locked(self, session_id: str) -> bool:
        if self._metadata_store is None:
            return False
        return bool(self._metadata_store.delete(session_id))

    def _mirror_delete(self, session_id: str) -> bool:
        if self._metadata_store is None:
            return False
        return bool(self._metadata_store.delete(session_id))

    def _recover_from_metadata_locked(
        self,
        session_id: str,
        owner_token: str | None,
    ) -> SessionRecord | None:
        if self._metadata_store is None:
            return None
        if owner_token is None:
            return None
        if not hasattr(self._metadata_store, "fetch_metadata"):
            return None
        data = self._metadata_store.fetch_metadata(session_id)
        if not data:
            return None
        stored_hash = str(data.get("owner_token_hash", "")).strip()
        if not stored_hash or stored_hash != _hash_token(owner_token):
            return None
        now = _utcnow()
        created_at = now
        raw_created_at = str(data.get("created_at", "")).strip()
        if raw_created_at:
            try:
                created_at = datetime.fromisoformat(raw_created_at)
            except ValueError:
                created_at = now
        session = SimulationSession(
            session_id=session_id,
            config=self._config,
            max_runtime_s=self._script_max_runtime_s,
        )
        raw_runtime_state = data.get("runtime_state_json")
        if isinstance(raw_runtime_state, str) and raw_runtime_state.strip():
            try:
                parsed = json.loads(raw_runtime_state)
                if isinstance(parsed, dict):
                    session.restore_runtime_checkpoint(parsed)
            except Exception:  # noqa: BLE001
                pass
        recovered = SessionRecord(
            session_id=session_id,
            owner_token_hash=stored_hash,
            created_at=created_at,
            last_seen_at=now,
            session=session,
        )
        self._sessions[session_id] = recovered
        mirrored = self._mirror_upsert_locked(recovered)
        if self._is_redis_primary and not mirrored:
            self._mark_degraded_locked("redis_mirror_write_failed_recovered")
        return recovered

    def _mark_degraded_locked(self, reason: str) -> None:
        self._degraded_to_memory = True
        self._degraded_reason = reason


class SessionCleanupWorker:
    """Daemon worker that periodically closes expired web sessions."""

    def __init__(self, manager: SessionManager, *, interval_s: float = 60.0) -> None:
        self._manager = manager
        self._interval_s = max(float(interval_s), 0.05)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="ev3-session-cleanup",
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout_s: float = 2.0) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout_s)

    def _run(self) -> None:
        while not self._stop_event.wait(self._interval_s):
            self._manager.cleanup_expired()
