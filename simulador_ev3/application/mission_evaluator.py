"""Evaluación determinista de criterios declarativos sobre una traza EV3."""

from __future__ import annotations

from simulador_ev3.application.simulation_trace import SimulationTrace
from simulador_ev3.domain.assessment import MissionCriterionResult, MissionDefinition, MissionResult


class MissionEvaluator:
    """Evalúa el subconjunto versionado de reglas que puede probarse localmente."""

    def evaluate(self, mission: MissionDefinition, trace: SimulationTrace, simulation_profile: str) -> MissionResult:
        results = tuple(
            self._evaluate_criterion(item.identifier, dict(item.expected), trace)
            for item in mission.acceptance_criteria
        )
        passed = all(result.passed for result in results)
        score = sum(item.max_points for item in mission.rubric) if passed else 0.0
        return MissionResult(
            mission_id=mission.identifier,
            mission_version=mission.version,
            passed=passed,
            score=score,
            criteria=results,
            simulation_profile=simulation_profile,
        )

    @staticmethod
    def _evaluate_criterion(identifier: str, expected: dict, trace: SimulationTrace) -> MissionCriterionResult:
        if "min_ticks" in expected:
            minimum = int(expected["min_ticks"])
            actual = len(trace.snapshots)
            return MissionCriterionResult(identifier, actual >= minimum, {"actual_ticks": actual, "min_ticks": minimum})
        if "collision" in expected:
            target = bool(expected["collision"])
            collisions = sum(bool(snapshot.get("colliding")) for snapshot in trace.snapshots)
            passed = collisions == 0 if not target else collisions > 0
            return MissionCriterionResult(identifier, passed, {"collisions": collisions, "expected": target})
        if "min_sensor_reads" in expected:
            minimum = int(expected["min_sensor_reads"])
            actual = sum(
                len(snapshot.get("sensors", []))
                for snapshot in trace.snapshots
                if isinstance(snapshot.get("sensors"), list)
            )
            return MissionCriterionResult(
                identifier,
                actual >= minimum,
                {"actual_reads": actual, "min_sensor_reads": minimum},
            )
        return MissionCriterionResult(identifier, False, {"error": "Regla de misión no compatible"})
