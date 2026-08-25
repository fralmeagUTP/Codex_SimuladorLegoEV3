"""Contrato estable para contenido didáctico y progreso local de la ayuda.

No contiene información de sesiones, código de estudiantes ni rutas locales.
Las interfaces pueden persistir únicamente :class:`GuideProgress` usando el
identificador de la guía y los pasos que el propio usuario haya marcado.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

HELP_CONTENT_CONTRACT_VERSION = 1
HELP_PROGRESS_STORAGE_KEY = "ev3-help-guide-progress-v1"


class LearningLevel(StrEnum):
    """Nivel didáctico que permite filtrar recorridos sin duplicar guías."""

    INITIAL = "inicial"
    INTERMEDIATE = "intermedio"
    ADVANCED = "avanzado"


@dataclass(frozen=True)
class VerifiableStep:
    """Paso observable con una señal que la persona puede comprobar."""

    identifier: str
    instruction: str
    verification: str


@dataclass(frozen=True)
class GuideVisualReference:
    """Referencia portable a una captura registrada en el manifiesto."""

    guide_id: str
    platform: str
    filename: str
    alt: str
    transcript: str
    theme: str
    ui_version: str


@dataclass(frozen=True)
class GuideProgress:
    """Estado mínimo y privado que una interfaz puede guardar localmente."""

    guide_id: str
    completed_step_ids: tuple[str, ...] = ()
    completed: bool = False

    def sanitized(self, allowed_step_ids: tuple[str, ...]) -> "GuideProgress":
        """Descarta pasos inválidos y nunca conserva información ajena a la guía."""

        allowed = set(allowed_step_ids)
        completed = tuple(step_id for step_id in self.completed_step_ids if step_id in allowed)
        return GuideProgress(
            guide_id=self.guide_id,
            completed_step_ids=completed,
            completed=self.completed and set(allowed_step_ids).issubset(completed),
        )


PRIVACY_POLICY = (
    "El progreso se guarda solo en el navegador o equipo local. No incluye código, "
    "identificadores de sesión, rutas locales, nombres de estudiante ni datos del robot."
)
