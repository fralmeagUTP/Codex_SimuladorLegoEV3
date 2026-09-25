"""Configuración común y clasificación ejecutable de las suites de calidad."""

import os
from pathlib import Path

import pytest

from tests.qa_factories import TestWorkspace, make_workspace

os.environ.setdefault("EV3_LOCAL_RUNTIME_ENABLED", "true")


@pytest.fixture
def qa_workspace(tmp_path: Path) -> TestWorkspace:
    """Espacio aislado para pruebas que escriben mundos o metadatos de sesión."""

    return make_workspace(tmp_path / "qa-workspace")


_MARKERS_BY_DIRECTORY = {
    "application": ("integration",),
    "core": ("unit",),
    "domain": ("unit",),
    "e2e": ("e2e", "ui"),
    "load": ("performance",),
    "persistence": ("integration",),
    "pybricks_api": ("unit", "contract"),
    "release": ("release",),
    "runtime": ("unit", "contract"),
    "shared": ("contract",),
    "ui": ("ui",),
    "web": ("integration",),
}


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Etiqueta pruebas por capa sin obligar a decorar cientos de archivos."""

    for item in items:
        path_parts = Path(str(item.fspath)).parts
        try:
            directory = path_parts[path_parts.index("tests") + 1]
        except (ValueError, IndexError):
            continue
        for marker in _MARKERS_BY_DIRECTORY.get(directory, ()):
            item.add_marker(getattr(pytest.mark, marker))
        if directory == "web" and any(token in item.name.lower() for token in ("token", "auth", "security")):
            item.add_marker(pytest.mark.security)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[object]):
    """Expone el resultado a fixtures que conservan evidencia de fallos."""

    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
