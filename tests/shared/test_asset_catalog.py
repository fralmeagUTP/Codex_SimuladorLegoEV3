import json
from pathlib import Path

from PIL import Image

from simulador_ev3.domain.editor.world_editor_model import normalize_asset_key
from simulador_ev3.shared.asset_catalog import (
    ASSET_CATALOG_VERSION,
    ASSET_DESCRIPTORS,
    asset_candidate_paths,
    asset_filename,
    editor_asset_manifest,
    validate_asset_catalog,
)
from simulador_ev3.shared.interface_catalog import label_for_status
from simulador_ev3.shared.world_editor_projection import placement_geometry


def test_asset_catalog_is_complete_and_all_canonical_assets_exist() -> None:
    validate_asset_catalog()

    assert ASSET_CATALOG_VERSION == 2
    assert all(item.path.is_file() for item in ASSET_DESCRIPTORS)
    assert all(len(item.digest()) == 64 for item in ASSET_DESCRIPTORS)
    for item in ASSET_DESCRIPTORS:
        with Image.open(item.path) as image:
            assert image.size == (item.source_width_px, item.source_height_px)


def test_editor_asset_manifest_declares_geometry_hash_and_anchors() -> None:
    manifest = {str(item["asset_id"]): item for item in editor_asset_manifest()}

    robot = manifest["robot_ev3_32x32"]
    line = manifest["line_64_64_hor"]

    assert robot["asset_catalog_version"] == 2
    assert robot["sha256"] == next(item.digest() for item in ASSET_DESCRIPTORS if item.asset_id == "robot_ev3_32x32")
    assert robot["source_width_px"] == 32
    assert robot["source_height_px"] == 32
    assert robot["logical_width_mm"] == 100.0
    assert robot["placement_anchor"] == "top_left"
    assert robot["visual_anchor"] == "center"
    assert robot["category"] == "Robot"
    assert robot["label"] == "Robot EV3"
    assert "posición inicial" in robot["tooltip"]
    assert line["logical_width_mm"] == 200.0
    assert line["connectors"] == ["E", "W"]


def test_all_saved_world_placements_resolve_canonical_assets() -> None:
    worlds_dir = Path(__file__).resolve().parents[2] / "worlds"
    known_assets = {item.asset_id for item in ASSET_DESCRIPTORS}
    unresolved: list[str] = []

    for world_path in sorted(worlds_dir.glob("*.json")):
        raw = json.loads(world_path.read_text(encoding="utf-8"))
        editor_spec = raw.get("editor_spec", {})
        for placement in editor_spec.get("placements", []):
            asset_id = str(placement.get("asset_key", ""))
            if asset_id not in known_assets:
                unresolved.append(f"{world_path.name}:{asset_id}")

    assert not unresolved, f"Placements sin asset canónico: {', '.join(unresolved)}"


def test_status_labels_are_localized_from_the_shared_catalog() -> None:
    assert label_for_status("running") == "Ejecutando"
    assert label_for_status("finished") == "Finalizado"
    assert label_for_status("timed_out") == "Tiempo agotado"


def test_placement_geometry_uses_world_units_and_rotated_dimensions() -> None:
    geometry = placement_geometry(
        {"asset_key": "line_64_64_hor", "x_px": 64, "y_px": 32, "rotation": 90}
    )

    assert geometry is not None
    assert geometry["x_mm"] == 200.0
    assert geometry["y_mm"] == 100.0
    assert geometry["width_mm"] == 200.0
    assert geometry["height_mm"] == 200.0
    assert geometry["layer"] == "line"


def test_historical_asset_aliases_resolve_to_the_canonical_catalog() -> None:
    assert normalize_asset_key("line_64_64_cruz") == "line_64x64_cruz"
    assert normalize_asset_key("line_64_64_infder.png") == "line_64_64_infder"


def test_web_uses_the_catalog_instead_of_a_second_filename_table() -> None:
    root = Path(__file__).resolve().parents[2]
    canvas_source = (root / "simulador_ev3" / "web" / "static" / "js" / "canvas_world.js").read_text(encoding="utf-8")
    page_source = (root / "simulador_ev3" / "web" / "routes" / "pages.py").read_text(encoding="utf-8")
    tkinter_sources = [
        (root / "simulador_ev3" / "ui" / name).read_text(encoding="utf-8")
        for name in ("asset_library_panel.py", "world_canvas.py", "world_canvas_editor.py")
    ]

    assert "window.EV3_ASSET_FILES" in canvas_source
    assert "window.EV3_ASSET_MANIFEST" in canvas_source
    assert "assetMetadata" in canvas_source
    assert "if (world?.editor_spec?.placements?.length) return;" in canvas_source
    assert "placement_geometry" in "\n".join(tkinter_sources)
    assert "editor_asset_manifest" in page_source
    assert all("asset_" in source and "catalog" in source for source in tkinter_sources)
    manifest_ids = {str(item["asset_id"]) for item in editor_asset_manifest()}
    assert len(manifest_ids) == 17
    assert {"robot_ev3_32x32", "wall_64x64_a", "floor_tile_256_c"} <= manifest_ids
    assert asset_filename("floor_tile_256_c") == "floor_tile_256_c.jpg"
    assert [path.name for path in asset_candidate_paths("floor_tile_256_c")] == [
        "floor_tile_256_c.jpg",
        "floor_tile_256_b.png",
    ]
