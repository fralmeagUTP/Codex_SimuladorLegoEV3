"""Pruebas del contrato portable de misiones evaluables."""

import pytest

from simulador_ev3.domain.assessment import (
    MISSION_SCHEMA_VERSION,
    MissionAcceptanceCriterion,
    MissionCriterionResult,
    MissionDefinition,
    MissionResult,
    MissionRubricCriterion,
)


@pytest.fixture
def mission() -> MissionDefinition:
    return MissionDefinition(
        identifier="sigue-linea-basico",
        version=1,
        title="Sigue líneas básico",
        objective="Seguir una línea sin terminar por error.",
        world_file="01_linea_negra_basica.json",
        starter_script="11_siguelineas_basico.py",
        acceptance_criteria=(
            MissionAcceptanceCriterion(
                "sin-error", "La ejecución termina correctamente.", {"terminal_status": "completed"}
            ),
        ),
        rubric=(MissionRubricCriterion("ejecucion", "Ejecución", "Finaliza sin error.", 40),),
        metadata={"subject": "sensores", "estimated_minutes": 20},
    )


def test_mission_round_trip_is_versioned_and_portable(mission: MissionDefinition) -> None:
    exported = mission.to_dict()

    restored = MissionDefinition.from_dict(exported)

    assert exported["schema_version"] == MISSION_SCHEMA_VERSION
    assert restored == mission


@pytest.mark.parametrize("schema_version", [0, 2, "1", None])
def test_mission_rejects_unknown_schema_version(mission: MissionDefinition, schema_version: object) -> None:
    payload = mission.to_dict()
    payload["schema_version"] = schema_version

    with pytest.raises(ValueError, match="schema_version no compatible"):
        MissionDefinition.from_dict(payload)


def test_mission_rejects_personal_data_in_metadata(mission: MissionDefinition) -> None:
    payload = mission.to_dict()
    payload["metadata"] = {"student": "Ana"}

    with pytest.raises(ValueError, match="datos personales"):
        MissionDefinition.from_dict(payload)


def test_result_export_contains_only_portable_local_evidence() -> None:
    result = MissionResult(
        mission_id="sigue-linea-basico",
        mission_version=1,
        passed=True,
        score=40,
        criteria=(MissionCriterionResult("sin-error", True, {"terminal_status": "completed"}),),
        simulation_profile="ideal",
        created_at_utc="2026-07-25T10:00:00+00:00",
        trace_reference="traces/sigue-linea.json",
    )

    assert result.to_dict() == {
        "schema_version": 1,
        "mission_id": "sigue-linea-basico",
        "mission_version": 1,
        "passed": True,
        "score": 40,
        "criteria": [{"id": "sin-error", "passed": True, "evidence": {"terminal_status": "completed"}}],
        "simulation_profile": "ideal",
        "created_at_utc": "2026-07-25T10:00:00+00:00",
        "trace_reference": "traces/sigue-linea.json",
    }
