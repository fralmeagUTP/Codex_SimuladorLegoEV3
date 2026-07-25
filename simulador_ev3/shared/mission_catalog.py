"""Catálogo local compartido de misiones evaluables para ambas interfaces."""

from __future__ import annotations

from pathlib import Path

from simulador_ev3.domain.assessment import MissionAcceptanceCriterion, MissionDefinition, MissionRubricCriterion


class MissionCatalog:
    """Expone únicamente misiones cuyos recursos locales existen."""

    def __init__(self, examples_dir: Path, worlds_dir: Path) -> None:
        self._examples_dir = examples_dir
        self._worlds_dir = worlds_dir

    def list_missions(self) -> list[MissionDefinition]:
        return [mission for mission in self._builtins() if self.is_available(mission)]

    def get(self, identifier: str) -> MissionDefinition | None:
        return next((mission for mission in self.list_missions() if mission.identifier == identifier), None)

    def is_available(self, mission: MissionDefinition) -> bool:
        example_exists = (self._examples_dir / mission.starter_script).is_file()
        world_exists = (self._worlds_dir / mission.world_file).is_file()
        return example_exists and world_exists

    @staticmethod
    def _builtins() -> tuple[MissionDefinition, ...]:
        return (
            MissionDefinition(
                identifier="sigue-linea-basico", version=1, title="Sigue líneas básico",
                objective="Mantener el robot sobre una línea sin finalizar con error.",
                world_file="01_linea_negra_basica.json", starter_script="11_siguelineas_basico.py",
                acceptance_criteria=(
                    MissionAcceptanceCriterion(
                        "tiene-traza",
                        "La ejecución registra al menos un tick.",
                        {"min_ticks": 1},
                    ),
                ),
                rubric=(MissionRubricCriterion("ejecucion", "Ejecución", "Finaliza sin error.", 40),),
                metadata={"subject": "sensores", "estimated_minutes": 20},
            ),
            MissionDefinition(
                identifier="evita-obstaculos", version=1, title="Evita obstáculos",
                objective="Usar el sensor ultrasónico para evitar una colisión.",
                world_file="05_obstaculos_baliza_ir.json",
                starter_script="15_esquiva_obstaculos.py",
                acceptance_criteria=(
                    MissionAcceptanceCriterion("sin-colision", "No finaliza en colisión.", {"collision": False}),
                ),
                rubric=(MissionRubricCriterion("seguridad", "Seguridad", "Evita obstáculos.", 40),),
                metadata={"subject": "ultrasonido", "estimated_minutes": 20},
            ),
            MissionDefinition(
                identifier="radar-ultrasonido", version=1, title="Radar ultrasónico",
                objective="Registrar varias lecturas al barrer el entorno.",
                world_file="12_radar_ultrasonido_360.json", starter_script="23_radar_ultrasonido_5grados.py",
                acceptance_criteria=(
                    MissionAcceptanceCriterion(
                        "lecturas", "La traza contiene lecturas repetidas.", {"min_sensor_reads": 2}
                    ),
                ),
                rubric=(MissionRubricCriterion("telemetria", "Telemetría", "Registra lecturas.", 40),),
                metadata={"subject": "telemetría", "estimated_minutes": 25},
            ),
        )
