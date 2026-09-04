from pathlib import Path

from simulador_ev3.shared.maturity_manifest import (
    MATURITY_MANIFEST_VERSION,
    MMI_DIMENSIONS,
    MMI_REQUIREMENTS,
    validate_maturity_manifest,
)
from simulador_ev3.shared.use_case_catalog import use_case_ids


def test_mmi_manifest_is_complete_and_weighted() -> None:
    validate_maturity_manifest()

    assert MATURITY_MANIFEST_VERSION == 1
    assert sum(item.weight for item in MMI_DIMENSIONS) == 100
    assert {item.use_case_id for item in MMI_REQUIREMENTS} == set(use_case_ids())


def test_mmi_matrix_has_a_parity_and_evidence_row_for_every_use_case() -> None:
    root = Path(__file__).resolve().parents[2]
    document = (root / "Documentos" / "MATRIZ_MADUREZ_WEB_TKINTER.md").read_text(encoding="utf-8")

    assert "Versión de manifiesto: `1`" in document
    for identifier in use_case_ids():
        row = next(line for line in document.splitlines() if f"| {identifier} |" in line)
        assert row.count("requerida") == 4, identifier
        assert "| Abierta |" in row, identifier


def test_platform_adaptations_are_documented_without_excluding_parity() -> None:
    root = Path(__file__).resolve().parents[2]
    document = (root / "Documentos" / "ADAPTACIONES_PLATAFORMA_WEB_TKINTER.md").read_text(encoding="utf-8")

    for heading in ("Ventana y tamaño", "Sesión", "Archivos", "Móvil", "Accesibilidad", "Recursos"):
        assert heading in document
    assert "No se admite una adaptación" in document
