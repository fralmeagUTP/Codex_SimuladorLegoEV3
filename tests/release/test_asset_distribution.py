"""Integridad de los recursos canÃ³nicos en los artefactos Windows."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile

import pytest

from simulador_ev3.shared.asset_catalog import ASSET_DESCRIPTORS

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
APP_ROOT = DIST / "SimuladorEV3"
ZIP_PATH = DIST / "SimuladorEV3-1.5.0-Windows-x64.zip"
INSTALLER_SCRIPT = ROOT / "scripts" / "installer" / "SimuladorEV3.iss"


def _packaged_asset_paths() -> tuple[Path, ...]:
    return tuple(APP_ROOT / "_internal" / "simulador_ev3" / "assets" / item.filename for item in ASSET_DESCRIPTORS)


def test_pyinstaller_distribution_contains_all_canonical_assets() -> None:
    if not APP_ROOT.is_dir():
        pytest.skip("El artefacto PyInstaller no se ha construido en este entorno.")

    missing = [str(path.relative_to(ROOT)) for path in _packaged_asset_paths() if not path.is_file()]
    assert not missing, f"Assets ausentes en PyInstaller: {', '.join(missing)}"
    mismatched = [
        item.filename
        for item in ASSET_DESCRIPTORS
        if sha256((APP_ROOT / "_internal" / "simulador_ev3" / "assets" / item.filename).read_bytes()).hexdigest()
        != item.digest()
    ]
    assert not mismatched, f"Assets desactualizados en PyInstaller: {', '.join(mismatched)}"


def test_portable_zip_contains_the_same_canonical_assets() -> None:
    if not ZIP_PATH.is_file():
        pytest.skip("El ZIP portable no se ha construido en este entorno.")

    with ZipFile(ZIP_PATH) as archive:
        entries = set(archive.namelist())

    prefix = "SimuladorEV3/_internal/simulador_ev3/assets/"
    missing = [f"{prefix}{item.filename}" for item in ASSET_DESCRIPTORS if f"{prefix}{item.filename}" not in entries]
    assert not missing, f"Assets ausentes en ZIP: {', '.join(missing)}"
    with ZipFile(ZIP_PATH) as archive:
        mismatched = [
            item.filename
            for item in ASSET_DESCRIPTORS
            if sha256(archive.read(f"{prefix}{item.filename}")).hexdigest() != item.digest()
        ]
    assert not mismatched, f"Assets desactualizados en ZIP: {', '.join(mismatched)}"


def test_installer_recipe_packages_the_verified_pyinstaller_tree_recursively() -> None:
    """El instalador no define otra lista divergente de recursos."""

    recipe = INSTALLER_SCRIPT.read_text(encoding="utf-8")

    assert 'Source: "..\\..\\dist\\SimuladorEV3\\*"' in recipe
    assert "recursesubdirs createallsubdirs" in recipe
