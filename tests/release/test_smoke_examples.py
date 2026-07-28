"""Smoke tests E2E para ejemplos crÃ­ticos de release (Fase 9)."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from simulador_ev3.application.simulation_service import SimulationService
from simulador_ev3.pybricks_api._context import PybricksContext
from simulador_ev3.pybricks_api.factory import PybricksFactory

ROOT_DIR = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = ROOT_DIR / "Documentos" / "Ejemplos"
WORLDS_DIR = ROOT_DIR / "Documentos" / "Mundos"


@pytest.fixture(autouse=True)
def clean_pybricks():
    PybricksContext.clear()
    PybricksFactory.cleanup()
    yield
    PybricksFactory.cleanup()
    PybricksContext.clear()


@pytest.mark.parametrize(
    ("world_file", "example_file", "run_s"),
    [
        ("02_obstaculos_beacon.json", "15_esquiva_obstaculos.py", 0.8),
        ("01_linea_negra.json", "11_siguelineas_basico.py", 0.8),
        ("02_obstaculos_beacon.json", "02_intro_pantalla_altavoz.py", 1.8),
    ],
)
def test_critical_examples_smoke(world_file: str, example_file: str, run_s: float):
    world_path = WORLDS_DIR / world_file
    example_path = EXAMPLES_DIR / example_file

    assert world_path.exists(), f"Mundo no encontrado: {world_path}"
    assert example_path.exists(), f"Ejemplo no encontrado: {example_path}"

    statuses: list[str] = []
    runtime_errors: list[dict] = []

    service = SimulationService()
    service.set_status_callback(lambda status: statuses.append(status))
    service.set_error_callback(lambda payload: runtime_errors.append(payload))

    service.load_world_file(world_path)
    source_code = example_path.read_text(encoding="utf-8")
    service.load_script(source_code)

    service.start()
    time.sleep(run_s)
    service.stop(reason="smoke_test")

    assert "world_loaded" in statuses
    assert "started" in statuses
    assert "stopped" in statuses
    assert runtime_errors == []
