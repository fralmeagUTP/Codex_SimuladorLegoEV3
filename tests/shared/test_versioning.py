import tomllib
from pathlib import Path

from simulador_ev3 import __version__
from simulador_ev3._version import APP_VERSION, WEB_ASSET_VERSION


def test_package_version_has_a_single_python_source() -> None:
    root = Path(__file__).resolve().parents[2]
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))

    assert __version__ == APP_VERSION == "1.5.0"
    assert pyproject["project"]["dynamic"] == ["version"]
    assert pyproject["tool"]["setuptools"]["dynamic"]["version"] == {"attr": "simulador_ev3.__version__"}
    # ui3 invalida correctamente la caché de los activos tras el rediseño Web.
    assert WEB_ASSET_VERSION == f"v{APP_VERSION}-ui3"


def test_readme_declares_current_package_version() -> None:
    root = Path(__file__).resolve().parents[2]
    readme = (root / "README.md").read_text(encoding="utf-8")

    assert f"Version actual: {APP_VERSION}" in readme
