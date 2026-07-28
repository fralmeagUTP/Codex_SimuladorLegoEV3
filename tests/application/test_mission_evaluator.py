from simulador_ev3.application.mission_evaluator import MissionEvaluator
from simulador_ev3.application.simulation_trace import SimulationTrace
from simulador_ev3.domain.assessment import MissionAcceptanceCriterion, MissionDefinition, MissionRubricCriterion


def _mission(expected: dict) -> MissionDefinition:
    return MissionDefinition(
        identifier="prueba-radar",
        version=1,
        title="Prueba", objective="Prueba determinista", world_file="world.json", starter_script="starter.py",
        acceptance_criteria=(MissionAcceptanceCriterion("criterio", "Criterio", expected),),
        rubric=(MissionRubricCriterion("puntos", "Puntos", "Resultado", 40),),
    )


def test_evaluator_accepts_deterministic_trace_with_sensor_evidence() -> None:
    trace = SimulationTrace(
        [
            {"tick": 1, "colliding": False, "sensors": [{"port": "S1"}]},
            {"tick": 2, "colliding": False, "sensors": [{"port": "S1"}]},
        ]
    )

    result = MissionEvaluator().evaluate(_mission({"min_sensor_reads": 2}), trace, "ideal")

    assert result.passed is True
    assert result.score == 40
    assert result.criteria[0].evidence["actual_reads"] == 2


def test_evaluator_rejects_collision_when_mission_requires_safe_route() -> None:
    trace = SimulationTrace([{"tick": 1, "colliding": False}, {"tick": 2, "colliding": True}])

    result = MissionEvaluator().evaluate(_mission({"collision": False}), trace, "ideal")

    assert result.passed is False
    assert result.score == 0
