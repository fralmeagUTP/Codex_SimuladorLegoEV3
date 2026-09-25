"""Puertos versionados para presentar, ensenar y observar una sesion.

Los adaptadores Web y Tkinter pueden tener widgets distintos, pero consumen
estos DTOs sin acceder a atributos privados del runtime o del motor.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol, runtime_checkable

INTERFACE_PORTS_VERSION = 1

# Contrato de privacidad compartido: la observabilidad no transporta código del
# estudiante, tokens de sesión, nombres personales ni valores de formularios.
OBSERVABILITY_RETENTION_DAYS = 30
OBSERVABILITY_REDACTED_FIELDS = frozenset({"source_code", "owner_token", "password", "email", "student_name"})


@dataclass(frozen=True)
class PresentationState:
    session_id: str
    status: str
    controls: dict[str, bool] = field(default_factory=dict)
    message: str = ""
    version: int = INTERFACE_PORTS_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LearningState:
    session_id: str
    activity_id: str | None
    objective: str
    next_step: str
    result: str | None = None
    progress_current: int = 0
    progress_total: int = 1
    version: int = INTERFACE_PORTS_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ObservabilitySnapshot:
    session_id: str
    command_id: str | None
    worker_id: str | None
    status: str
    tick: int | None = None
    simulation_time_s: float | None = None
    error_code: str | None = None
    version: int = INTERFACE_PORTS_VERSION

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return {key: value for key, value in payload.items() if key not in OBSERVABILITY_REDACTED_FIELDS}


@runtime_checkable
class PresentationPort(Protocol):
    def presentation_state(self) -> PresentationState: ...


@runtime_checkable
class LearningPort(Protocol):
    def learning_state(self) -> LearningState: ...


@runtime_checkable
class ObservabilityPort(Protocol):
    def observability_snapshot(self) -> ObservabilitySnapshot: ...
