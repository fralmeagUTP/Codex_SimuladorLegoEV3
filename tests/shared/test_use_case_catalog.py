from pathlib import Path

from simulador_ev3.shared.use_case_catalog import (
    INTERFACE_PARITY_CATALOG_VERSION,
    REQUIRED_INTERFACES,
    USE_CASES,
    use_case_ids,
)


def test_use_case_catalog_has_unique_stable_identifiers() -> None:
    identifiers = use_case_ids()

    assert INTERFACE_PARITY_CATALOG_VERSION == 1
    assert len(identifiers) == len(set(identifiers))
    assert all(identifier.startswith("UC-") for identifier in identifiers)
    assert REQUIRED_INTERFACES == frozenset({"web", "tkinter"})


def test_use_case_catalog_is_documented_in_openspec() -> None:
    root = Path(__file__).resolve().parents[2]
    document = root / "openspec" / "use-cases" / "interface-parity-v1.md"
    content = document.read_text(encoding="utf-8")

    assert "Versión de catálogo: `1`" in content
    for use_case in USE_CASES:
        assert use_case.identifier in content


def test_use_case_catalog_is_audited_in_parity_matrix() -> None:
    root = Path(__file__).resolve().parents[2]
    matrix = root / "openspec" / "use-cases" / "matriz-paridad-actual-v1.md"
    content = matrix.read_text(encoding="utf-8")

    assert "Fecha de auditoría: `2026-07-24`" in content
    for use_case in USE_CASES:
        assert use_case.identifier in content


def test_required_use_cases_cannot_be_declared_as_single_interface_features() -> None:
    root = Path(__file__).resolve().parents[2]
    matrix = root / "openspec" / "use-cases" / "matriz-paridad-actual-v1.md"
    content = matrix.read_text(encoding="utf-8")

    for use_case in USE_CASES:
        if use_case.planned:
            continue
        row = next(line for line in content.splitlines() if f"| {use_case.identifier} |" in line)
        assert "| Completa |" in row, use_case.identifier
