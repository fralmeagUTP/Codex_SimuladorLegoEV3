"""Contrato compartido de estados para sesiones de simulación.

Las interfaces Web y Tkinter reciben los mismos estados emitidos por la capa de
aplicación. Este módulo centraliza nombres, estados terminales y transiciones
válidas para evitar que cada adaptador defina su propia máquina de estados.
"""

from __future__ import annotations

from enum import StrEnum


class SessionStatus(StrEnum):
    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"
    STOPPED = "stopped"
    ERROR = "error"
    TIMED_OUT = "timed_out"
    RESETTING = "resetting"
    EXPIRED = "expired"


TERMINAL_STATUSES = frozenset(
    {
        SessionStatus.FINISHED,
        SessionStatus.STOPPED,
        SessionStatus.ERROR,
        SessionStatus.TIMED_OUT,
        SessionStatus.EXPIRED,
    }
)


_ALLOWED_TRANSITIONS: dict[SessionStatus, frozenset[SessionStatus]] = {
    SessionStatus.CREATED: frozenset(
        {SessionStatus.CREATED, SessionStatus.READY, SessionStatus.RESETTING, SessionStatus.EXPIRED}
    ),
    SessionStatus.READY: frozenset(
        {SessionStatus.READY, SessionStatus.RUNNING, SessionStatus.RESETTING, SessionStatus.EXPIRED}
    ),
    SessionStatus.RUNNING: frozenset(
        {
            SessionStatus.RUNNING,
            SessionStatus.PAUSED,
            SessionStatus.FINISHED,
            SessionStatus.STOPPED,
            SessionStatus.ERROR,
            SessionStatus.TIMED_OUT,
            SessionStatus.RESETTING,
            SessionStatus.EXPIRED,
        }
    ),
    SessionStatus.PAUSED: frozenset(
        {
            SessionStatus.PAUSED,
            SessionStatus.RUNNING,
            SessionStatus.STOPPED,
            SessionStatus.ERROR,
            SessionStatus.TIMED_OUT,
            SessionStatus.RESETTING,
            SessionStatus.EXPIRED,
        }
    ),
    SessionStatus.FINISHED: frozenset(
        {
            SessionStatus.FINISHED,
            SessionStatus.READY,
            SessionStatus.RUNNING,
            SessionStatus.RESETTING,
            SessionStatus.EXPIRED,
        }
    ),
    SessionStatus.STOPPED: frozenset(
        {
            SessionStatus.STOPPED,
            SessionStatus.READY,
            SessionStatus.RUNNING,
            SessionStatus.RESETTING,
            SessionStatus.EXPIRED,
        }
    ),
    SessionStatus.ERROR: frozenset(
        {
            SessionStatus.ERROR,
            SessionStatus.READY,
            SessionStatus.RUNNING,
            SessionStatus.RESETTING,
            SessionStatus.EXPIRED,
        }
    ),
    SessionStatus.TIMED_OUT: frozenset(
        {
            SessionStatus.TIMED_OUT,
            SessionStatus.READY,
            SessionStatus.RUNNING,
            SessionStatus.RESETTING,
            SessionStatus.EXPIRED,
        }
    ),
    SessionStatus.RESETTING: frozenset({SessionStatus.RESETTING, SessionStatus.CREATED, SessionStatus.EXPIRED}),
    SessionStatus.EXPIRED: frozenset({SessionStatus.EXPIRED}),
}


def normalize_status(value: str | SessionStatus) -> SessionStatus:
    """Convierte un valor externo a su representación canónica."""
    return value if isinstance(value, SessionStatus) else SessionStatus(str(value).strip().lower())


def can_transition(current: str | SessionStatus, target: str | SessionStatus) -> bool:
    """Indica si una transición de sesión está permitida por el contrato."""
    return normalize_status(target) in _ALLOWED_TRANSITIONS[normalize_status(current)]


def is_terminal(status: str | SessionStatus) -> bool:
    """Indica si el estado ya no ejecuta un programa."""
    return normalize_status(status) in TERMINAL_STATUSES
