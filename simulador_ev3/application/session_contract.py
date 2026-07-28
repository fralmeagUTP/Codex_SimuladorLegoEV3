"""Contrato versionado que comparten las sesiones Web, Tkinter y el worker."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SESSION_CONTRACT_VERSION = 1


@dataclass(frozen=True)
class SessionCommand:
    session_id: str
    command_id: str
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    version: int = SESSION_CONTRACT_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol_version": self.version,
            "session_id": self.session_id,
            "command_id": self.command_id,
            "type": self.type,
            "payload": self.payload,
        }


@dataclass(frozen=True)
class SessionEvent:
    session_id: str
    sequence: int
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    command_id: str | None = None
    kind: str = "event"
    version: int = SESSION_CONTRACT_VERSION

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "SessionEvent":
        if int(value.get("protocol_version", SESSION_CONTRACT_VERSION)) != SESSION_CONTRACT_VERSION:
            raise ValueError("Version de contrato de sesion no compatible.")
        payload = value.get("payload", {})
        if not isinstance(payload, dict):
            raise ValueError("El payload de evento debe ser un objeto.")
        return cls(
            session_id=str(value.get("session_id", "")),
            sequence=int(value.get("sequence", 0)),
            type=str(value.get("type", "")),
            payload=dict(payload),
            command_id=str(value["command_id"]) if value.get("command_id") is not None else None,
            kind=str(value.get("kind", "event")),
            version=int(value.get("protocol_version", SESSION_CONTRACT_VERSION)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol_version": self.version,
            "session_id": self.session_id,
            "sequence": self.sequence,
            "kind": self.kind,
            "type": self.type,
            "payload": self.payload,
            "command_id": self.command_id,
        }
