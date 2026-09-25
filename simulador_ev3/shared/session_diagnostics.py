"""Formato portable y seguro para exportar diagnósticos de sesión.

El contenido puede consultarse en Web o escritorio sin incluir código de los
programas ni credenciales de la sesión.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Mapping

DIAGNOSTIC_SCHEMA_VERSION = 1


def build_session_diagnostic_payload(
    session: Mapping[str, Any],
    *,
    runtime: Mapping[str, Any] | None = None,
    render: Mapping[str, Any] | None = None,
    worker: Mapping[str, Any] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Construye el contrato JSON común para diagnósticos exportables."""

    return {
        "schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "session": dict(session),
        "runtime": dict(runtime or {}),
        "render": dict(render or {}),
        "worker": dict(worker or {}),
    }
