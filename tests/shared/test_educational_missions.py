from pathlib import Path


def test_missions_documentation_uses_existing_examples_and_trace_evidence() -> None:
    root = Path(__file__).parents[2]
    document = (root / "Documentos" / "MISIONES_EVALUABLES.md").read_text(encoding="utf-8")

    for example in ("11_siguelineas_basico.py", "15_esquiva_obstaculos.py", "23_radar_ultrasonido_5grados.py"):
        assert example in document
    assert "Traza JSON" in document
