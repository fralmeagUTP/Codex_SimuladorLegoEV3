"""Regresiones de disponibilidad del catÃ¡logo comÃºn en las dos interfaces."""

from __future__ import annotations

import json
from pathlib import Path

from simulador_ev3.examples.example_catalog import ExampleCatalog
from simulador_ev3.shared.mission_catalog import MissionCatalog
from simulador_ev3.shared.paths import resolve_examples_dir, resolve_worlds_dir
from simulador_ev3.web.app import create_app


def test_all_examples_and_worlds_are_readable_from_the_shared_catalog() -> None:
    """Impide menÃºs con recursos rotos en Tkinter o en la API Web."""

    examples_dir = resolve_examples_dir()
    worlds_dir = resolve_worlds_dir()
    examples = ExampleCatalog(examples_dir).list_examples()
    worlds = sorted(worlds_dir.glob("*.json"))

    assert len(examples) >= 20
    assert len(worlds) >= 10
    for example in examples:
        source = example.path.read_text(encoding="utf-8")
        assert source.strip(), example.name
        # El catÃ¡logo se carga desde menÃºs de las dos interfaces: un archivo
        # no analizable serÃ­a una opciÃ³n visible pero inutilizable.
        compile(source, str(example.path), "exec")
    for world in worlds:
        payload = json.loads(world.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), world.name
        is_editor_world = "editor_spec" in payload
        is_legacy_grid_world = {"world_width_cells", "world_height_cells"}.issubset(payload)
        assert is_editor_world or is_legacy_grid_world, world.name


def test_web_catalog_endpoints_publish_the_same_examples_worlds_and_missions_as_tkinter() -> None:
    """La Web y Tkinter deben resolver los mismos recursos locales."""

    examples_dir = resolve_examples_dir()
    worlds_dir = resolve_worlds_dir()
    expected_examples = [item.name for item in ExampleCatalog(examples_dir).list_examples()]
    expected_worlds = [path.name for path in sorted(worlds_dir.glob("*.json"))]
    expected_missions = [mission.identifier for mission in MissionCatalog(examples_dir, worlds_dir).list_missions()]
    app = create_app(
        {
            "TESTING": True,
            "FILE_MIRROR_ENABLED": False,
            "ENABLE_SESSION_CLEANUP_THREAD": False,
            "EXAMPLES_DIR": examples_dir,
            "WORLDS_DIR": worlds_dir,
        }
    )

    with app.test_client() as client:
        web_examples = [item["name"] for item in client.get("/api/examples").get_json()["examples"]]
        web_worlds = [item["name"] for item in client.get("/api/worlds").get_json()["worlds"]]
        web_missions = [item["id"] for item in client.get("/api/missions").get_json()["missions"]]

    assert web_examples == expected_examples
    assert web_worlds == expected_worlds
    assert web_missions == expected_missions


def test_tkinter_menu_builders_are_backed_by_the_shared_catalogs() -> None:
    root = Path(__file__).resolve().parents[2]
    tkinter_source = (root / "simulador_ev3" / "ui" / "main_window.py").read_text(encoding="utf-8")

    assert "ExampleCatalog(_EXAMPLES_DIR)" in tkinter_source
    assert "MissionCatalog(_EXAMPLES_DIR, _WORLDS_DIR)" in tkinter_source
    assert "_populate_examples_menu" in tkinter_source
    assert "_populate_worlds_menu" in tkinter_source
    assert "_populate_missions_menu" in tkinter_source
