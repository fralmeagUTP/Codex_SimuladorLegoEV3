"""Contrato versionado, portable y sin identidad personal para misiones.

Estos DTOs pertenecen al dominio: ni Web ni Tkinter deben serializar formatos
propios para las misiones o sus resultados.  La persistencia y los adaptadores
de interfaz se limitan a intercambiar los diccionarios producidos aquí.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

MISSION_SCHEMA_VERSION = 1
_IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
_FORBIDDEN_METADATA_KEYS = frozenset({"email", "name", "student", "student_id", "user", "username"})


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} debe ser texto no vacío")
    return value.strip()


def _require_mapping(value: object, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} debe ser un objeto JSON")
    if any(not isinstance(key, str) for key in value):
        raise ValueError(f"{field_name} debe usar claves de texto")
    return value


def _validate_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    forbidden = sorted(key for key in metadata if key.casefold() in _FORBIDDEN_METADATA_KEYS)
    if forbidden:
        raise ValueError("metadata no puede contener datos personales: " + ", ".join(forbidden))
    return dict(metadata)


@dataclass(frozen=True)
class MissionRubricCriterion:
    """Criterio puntuable de una misión."""

    identifier: str
    title: str
    description: str
    max_points: float

    def __post_init__(self) -> None:
        _require_text(self.identifier, "rubric.identifier")
        _require_text(self.title, "rubric.title")
        _require_text(self.description, "rubric.description")
        if self.max_points <= 0:
            raise ValueError("rubric.max_points debe ser mayor que cero")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "title": self.title,
            "description": self.description,
            "max_points": self.max_points,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> MissionRubricCriterion:
        return cls(
            identifier=_require_text(raw.get("id"), "rubric.id"),
            title=_require_text(raw.get("title"), "rubric.title"),
            description=_require_text(raw.get("description"), "rubric.description"),
            max_points=float(raw.get("max_points", 0)),
        )


@dataclass(frozen=True)
class MissionAcceptanceCriterion:
    """Regla declarativa que una futura evaluación de traza debe verificar."""

    identifier: str
    description: str
    expected: Mapping[str, Any]

    def __post_init__(self) -> None:
        _require_text(self.identifier, "acceptance.identifier")
        _require_text(self.description, "acceptance.description")
        if not self.expected:
            raise ValueError("acceptance.expected no puede estar vacío")

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.identifier, "description": self.description, "expected": dict(self.expected)}

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> MissionAcceptanceCriterion:
        return cls(
            identifier=_require_text(raw.get("id"), "acceptance.id"),
            description=_require_text(raw.get("description"), "acceptance.description"),
            expected=dict(_require_mapping(raw.get("expected"), "acceptance.expected")),
        )


@dataclass(frozen=True)
class MissionDefinition:
    """Definición portable de una misión, independiente de la interfaz."""

    identifier: str
    version: int
    title: str
    objective: str
    world_file: str
    starter_script: str
    acceptance_criteria: tuple[MissionAcceptanceCriterion, ...]
    rubric: tuple[MissionRubricCriterion, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)
    schema_version: int = MISSION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != MISSION_SCHEMA_VERSION:
            raise ValueError(f"schema_version no compatible: {self.schema_version}")
        if not _IDENTIFIER_RE.fullmatch(self.identifier):
            raise ValueError("id de misión inválido; use minúsculas, números y guiones")
        if self.version < 1:
            raise ValueError("version debe ser un entero positivo")
        for field_name in ("title", "objective", "world_file", "starter_script"):
            _require_text(getattr(self, field_name), field_name)
        if not self.acceptance_criteria:
            raise ValueError("la misión debe incluir al menos un criterio de aceptación")
        if not self.rubric:
            raise ValueError("la misión debe incluir al menos un criterio de rúbrica")
        object.__setattr__(self, "metadata", _validate_metadata(_require_mapping(self.metadata, "metadata")))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "id": self.identifier,
            "version": self.version,
            "title": self.title,
            "objective": self.objective,
            "world_file": self.world_file,
            "starter_script": self.starter_script,
            "acceptance_criteria": [criterion.to_dict() for criterion in self.acceptance_criteria],
            "rubric": [criterion.to_dict() for criterion in self.rubric],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> MissionDefinition:
        data = _require_mapping(raw, "mission")
        schema_version = data.get("schema_version")
        if schema_version != MISSION_SCHEMA_VERSION:
            raise ValueError(f"schema_version no compatible: {schema_version}")
        acceptance = data.get("acceptance_criteria")
        rubric = data.get("rubric")
        if not isinstance(acceptance, list) or not isinstance(rubric, list):
            raise ValueError("acceptance_criteria y rubric deben ser listas")
        return cls(
            identifier=_require_text(data.get("id"), "id"),
            version=int(data.get("version", 0)),
            title=_require_text(data.get("title"), "title"),
            objective=_require_text(data.get("objective"), "objective"),
            world_file=_require_text(data.get("world_file"), "world_file"),
            starter_script=_require_text(data.get("starter_script"), "starter_script"),
            acceptance_criteria=tuple(MissionAcceptanceCriterion.from_dict(item) for item in acceptance),
            rubric=tuple(MissionRubricCriterion.from_dict(item) for item in rubric),
            metadata=dict(_require_mapping(data.get("metadata", {}), "metadata")),
            schema_version=schema_version,
        )


@dataclass(frozen=True)
class MissionCriterionResult:
    """Resultado de un criterio, sin identidad de quien ejecutó la misión."""

    identifier: str
    passed: bool
    evidence: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.identifier, "passed": self.passed, "evidence": dict(self.evidence)}


@dataclass(frozen=True)
class MissionResult:
    """Evidencia local exportable de una evaluación de misión."""

    mission_id: str
    mission_version: int
    passed: bool
    score: float
    criteria: tuple[MissionCriterionResult, ...]
    simulation_profile: str
    created_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    trace_reference: str | None = None
    schema_version: int = MISSION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != MISSION_SCHEMA_VERSION:
            raise ValueError(f"schema_version no compatible: {self.schema_version}")
        if not _IDENTIFIER_RE.fullmatch(self.mission_id):
            raise ValueError("mission_id inválido")
        if self.mission_version < 1 or self.score < 0:
            raise ValueError("mission_version y score deben ser no negativos y válidos")
        _require_text(self.simulation_profile, "simulation_profile")
        _require_text(self.created_at_utc, "created_at_utc")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "mission_id": self.mission_id,
            "mission_version": self.mission_version,
            "passed": self.passed,
            "score": self.score,
            "criteria": [criterion.to_dict() for criterion in self.criteria],
            "simulation_profile": self.simulation_profile,
            "created_at_utc": self.created_at_utc,
            "trace_reference": self.trace_reference,
        }
