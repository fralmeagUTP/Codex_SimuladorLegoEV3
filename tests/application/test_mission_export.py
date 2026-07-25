import json

import pytest

from simulador_ev3.application.mission_export import export_mission_result
from simulador_ev3.domain.assessment import MissionCriterionResult, MissionResult


@pytest.fixture
def result() -> MissionResult:
    return MissionResult(
        mission_id="sigue-linea-basico", mission_version=1, passed=True, score=40,
        criteria=(MissionCriterionResult("tiene-traza", True, {"actual_ticks": 2}),),
        simulation_profile="ideal", created_at_utc="2026-07-25T10:00:00+00:00",
    )


def test_result_json_is_portable_and_contains_no_identity(result: MissionResult) -> None:
    payload = json.loads(export_mission_result(result))

    assert payload["mission_id"] == "sigue-linea-basico"
    assert "student" not in payload
    assert "email" not in payload


def test_result_csv_has_a_row_per_criterion(result: MissionResult) -> None:
    payload = export_mission_result(result, "csv")

    assert "mission_id,mission_version,passed,score,criterion_id,criterion_passed" in payload
    assert "sigue-linea-basico,1,True,40,tiene-traza,True" in payload


def test_result_export_rejects_unknown_format(result: MissionResult) -> None:
    with pytest.raises(ValueError, match="formato"):
        export_mission_result(result, "xml")
