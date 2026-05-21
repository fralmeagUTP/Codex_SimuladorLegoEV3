"""Thread-safe in-memory session manager for web simulations."""

from __future__ import annotations

import hashlib
import secrets
import threading
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

    def __init__(self, config: dict[str, Any]) -> None:
        self._lock = threading.RLock()
        self._sessions: dict[str, SessionRecord] = {}
        self._idle_timeout = timedelta(
            minutes=int(config.get("SESSION_IDLE_TIMEOUT_MIN", 30))
        )
        self._max_active = int(config.get("MAX_ACTIVE_SESSIONS", 20))
        self._max_running = int(config.get("MAX_RUNNING_SIMULATIONS", 8))
        self._script_max_runtime_s = float(config.get("SCRIPT_MAX_RUNTIME_S", 30.0))
        self._config = config

    def create_session(self) -> tuple[str, str]:
        with self._lock:
            self.cleanup_expired()
            if len(self._sessions) >= self._max_active:
                raise CapacityExceeded("Se alcanzo el limite de sesiones activas.")

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
            return session_id, owner_token

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
                raise SessionNotFound("La sesion no existe o expiro.")
            if self._is_expired(record):
                session = record.session
                self._sessions.pop(session_id, None)
                session.close()
                raise SessionNotFound("La sesion expiro por inactividad.")
            if owner_token is not None and _hash_token(owner_token) != record.owner_token_hash:
                raise SessionForbidden("Token de sesion invalido.")
            if touch:
                record.last_seen_at = _utcnow()
            return record.session

    def close_session(self, session_id: str, owner_token: str | None = None) -> None:
        with self._lock:
            record = self._sessions.get(session_id)
            if record is None:
                raise SessionNotFound("La sesion no existe o expiro.")
            if owner_token is not None and _hash_token(owner_token) != record.owner_token_hash:
                raise SessionForbidden("Token de sesion invalido.")
            self._sessions.pop(session_id, None)
        record.session.close()

    def cleanup_expired(self) -> int:
        expired: list[SessionRecord] = []
        with self._lock:
            for session_id, record in list(self._sessions.items()):
                if self._is_expired(record):
                    expired.append(record)
                    self._sessions.pop(session_id, None)
        for record in expired:
            record.session.close()
        return len(expired)

    def running_count(self) -> int:
        with self._lock:
            return sum(1 for rec in self._sessions.values() if rec.session.status == "running")

    def can_start(self) -> bool:
        return self.running_count() < self._max_running

    def stats(self) -> dict[str, int]:
        with self._lock:
            return {
                "active_sessions": len(self._sessions),
                "running_simulations": self.running_count(),
                "max_active_sessions": self._max_active,
                "max_running_simulations": self._max_running,
            }

    def _is_expired(self, record: SessionRecord) -> bool:
        return _utcnow() - record.last_seen_at > self._idle_timeout


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
