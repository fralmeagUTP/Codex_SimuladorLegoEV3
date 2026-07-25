"""Contratos mínimos para que la documentación operativa no derive del código."""

from pathlib import Path

from simulador_ev3._version import APP_VERSION


def test_documentation_index_references_current_operational_guides() -> None:
    root = Path(__file__).resolve().parents[2]
    index = (root / "Documentos" / "INDICE_DOCUMENTACION.md").read_text(encoding="utf-8")

    for relative_path in (
        "README.md",
        "Documentos/MANUAL_DE_USO.md",
        "Documentos/ARQUITECTURA_C4.md",
        "Documentos/GUIA_OPERACION_WINDOWS.md",
        "Documentos/SEGURIDAD_Y_USO_EN_AULA.md",
        "Documentos/REFERENCIA_CONFIGURACION.md",
    ):
        assert (root / relative_path).is_file()
        assert f"`{relative_path}`" in index


def test_current_guides_identify_the_distributable_version() -> None:
    root = Path(__file__).resolve().parents[2]
    for relative_path in (
        "README.md",
        "Documentos/MANUAL_DE_USO.md",
        "Documentos/ARQUITECTURA_C4.md",
        "Documentos/GUIA_OPERACION_WINDOWS.md",
        "Documentos/GUIA_DESPLIEGUE_LINUX.md",
    ):
        contents = (root / relative_path).read_text(encoding="utf-8")
        assert APP_VERSION in contents, relative_path


def test_documentation_change_contains_required_openspec_artifacts() -> None:
    root = Path(__file__).resolve().parents[2]
    change_root = root / "openspec" / "changes" / "actualizar-documentacion-integral"
    for relative_path in ("proposal.md", "design.md", "tasks.md", "specs/project-documentation/spec.md"):
        assert (change_root / relative_path).is_file()
