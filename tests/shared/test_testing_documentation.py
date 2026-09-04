from pathlib import Path


def test_testing_audit_documents_required_quality_artifacts() -> None:
    root = Path(__file__).resolve().parents[2] / "docs" / "testing"
    for name in (
        "diagnostico.md",
        "inventario_funcional.md",
        "estrategia_pruebas.md",
        "casos_prueba.md",
        "catalogo_regresiones.md",
        "conformidad_pybricks_qa.md",
        "linea_base_cobertura.md",
        "matriz_trazabilidad.md",
        "paridad_interfaces_qa.md",
        "reporte_ejecucion.md",
    ):
        assert (root / name).is_file()
