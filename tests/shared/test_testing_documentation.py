from pathlib import Path


def test_testing_audit_documents_required_quality_artifacts() -> None:
    root = Path(__file__).resolve().parents[2] / "docs" / "testing"
    for name in (
        "diagnostico.md",
        "inventario_funcional.md",
        "estrategia_pruebas.md",
        "casos_prueba.md",
        "matriz_trazabilidad.md",
        "reporte_ejecucion.md",
    ):
        assert (root / name).is_file()
