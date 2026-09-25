"""Contratos mínimos para que la documentación operativa no derive del código."""

import re
from pathlib import Path

from simulador_ev3._version import APP_VERSION


def test_documentation_index_references_current_operational_guides() -> None:
    root = Path(__file__).resolve().parents[2]
    index = (root / "Documentos" / "INDICE_DOCUMENTACION.md").read_text(encoding="utf-8")

    for relative_path in (
        "README.md",
        "Documentos/ESTADO_ACTUAL_PROYECTO.md",
        "Documentos/MANUAL_DE_USO.md",
        "Documentos/ARQUITECTURA_C4.md",
        "Documentos/GUIA_OPERACION_WINDOWS.md",
        "Documentos/SEGURIDAD_Y_USO_EN_AULA.md",
        "Documentos/REFERENCIA_CONFIGURACION.md",
    ):
        assert (root / relative_path).is_file()
        assert f"`{relative_path}`" in index


def test_canonical_documentation_is_current_and_indexed() -> None:
    root = Path(__file__).resolve().parents[2]
    index = (root / "Documentos" / "INDICE_DOCUMENTACION.md").read_text(encoding="utf-8")
    canonical_paths = (
        "README.md",
        "CHANGELOG.md",
        "ROADMAP.md",
        "CONTRIBUTING.md",
        "Documentos/ESTADO_ACTUAL_PROYECTO.md",
        "Documentos/MANUAL_DE_USO.md",
        "Documentos/ARQUITECTURA_C4.md",
        "Documentos/GUIA_OPERACION_WINDOWS.md",
        "Documentos/GUIA_DESPLIEGUE_LINUX.md",
        "Documentos/REFERENCIA_CONFIGURACION.md",
        "Documentos/CONTROLES_CALIDAD.md",
        "Documentos/CHECKLIST_QA_RELEASE.md",
        "docs/testing/estrategia_pruebas.md",
        "docs/testing/reporte_ejecucion.md",
    )

    for relative_path in canonical_paths:
        path = root / relative_path
        assert path.is_file(), relative_path
        assert relative_path in index, relative_path

    for relative_path in canonical_paths:
        if relative_path in {"CONTRIBUTING.md"}:
            continue
        contents = (root / relative_path).read_text(encoding="utf-8")
        assert APP_VERSION in contents, relative_path


def test_readme_local_markdown_links_and_documented_scripts_exist() -> None:
    root = Path(__file__).resolve().parents[2]
    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")

    local_links = re.findall(r"\[[^\]]+\]\((?!https?://|#|mailto:)([^)]+)\)", readme)
    assert local_links
    for reference in local_links:
        target = (readme_path.parent / reference.split("#", 1)[0]).resolve()
        assert target.exists(), f"README.md -> {reference}"

    documented_scripts = set(re.findall(r"(?:\.\\)?(scripts\\[A-Za-z0-9_.-]+)", readme))
    assert documented_scripts
    for reference in documented_scripts:
        target = root / Path(reference.replace("\\", "/"))
        assert target.is_file(), f"README.md -> {reference}"


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
    changes_root = root / "openspec" / "changes"
    active_root = changes_root / "actualizar-documentacion-integral"
    archived_roots = sorted(changes_root.glob("archive/*-actualizar-documentacion-integral"))
    change_root = active_root if active_root.is_dir() else archived_roots[-1]
    for relative_path in ("proposal.md", "design.md", "tasks.md", "specs/project-documentation/spec.md"):
        assert (change_root / relative_path).is_file()
