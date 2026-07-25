"""Exportación portable de resultados de misiones, sin información personal."""

from __future__ import annotations

import csv
import io
import json

from simulador_ev3.domain.assessment import MissionResult


def export_mission_result(result: MissionResult, format: str = "json") -> str:
    """Serializa un resultado local para entregar o archivar en el aula."""
    if format == "json":
        return json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if format == "csv":
        output = io.StringIO(newline="")
        writer = csv.DictWriter(
            output,
            fieldnames=("mission_id", "mission_version", "passed", "score", "criterion_id", "criterion_passed"),
        )
        writer.writeheader()
        for criterion in result.criteria:
            writer.writerow(
                {
                    "mission_id": result.mission_id,
                    "mission_version": result.mission_version,
                    "passed": result.passed,
                    "score": result.score,
                    "criterion_id": criterion.identifier,
                    "criterion_passed": criterion.passed,
                }
            )
        return output.getvalue()
    raise ValueError("El formato debe ser 'json' o 'csv'.")
