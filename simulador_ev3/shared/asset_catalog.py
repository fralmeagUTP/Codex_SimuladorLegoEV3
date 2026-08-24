"""Catalogo unico y versionado de figuras usadas por Web y Tkinter.

Los dos adaptadores resuelven el mismo ``asset_id`` contra el directorio de
activos canonico. Esto evita que una interfaz use una copia antigua o un nombre
de archivo distinto para el mismo elemento del mundo.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from simulador_ev3.domain.editor.world_editor_model import CELL_SIZE_MM, ASSET_CATALOG, normalize_asset_key
from simulador_ev3.shared.paths import resolve_image_assets_dir

ASSET_CATALOG_VERSION = 2

_EDITOR_FILENAMES = {
    "robot_ev3_32x32": "robot_ev3_32x32.png",
    "wall_64x64_a": "wall_64x64_a.png",
    "wall_64x64_b": "wall_64x64_b.png",
    "wall_64x64_c": "wall_64x64_c.png",
    "zone_green_128": "zone_green_128.png",
    "zone_red_128": "zone_red_128.png",
    "zone_white_128": "zone_white_128.png",
    "line_64_64_hor": "line_64_64_Hor.png",
    "line_64_64_ver": "line_64_64_Ver.png",
    "line_64x64_cruz": "line_64X64_Cruz.png",
    "line_64_64_infder": "line_64_64_InfDer.png",
    "line_64_64_infizq": "line_64_64_InfIzq.png",
    "line_64_64_supder": "line_64_64_SupDer.png",
    "line_64_64_supizq": "line_64_64_SupIzq.png",
    "floor_tile_256_a": "floor_tile_256_a.png",
    "floor_tile_256_b": "floor_tile_256_b.png",
    "floor_tile_256_c": "floor_tile_256_c.jpg",
}

_BRANDING_FILENAMES = {
    "intro-screen": "Intro.png",
    "logo-nyquist": "Logo_Nyquist.png",
    "logo-robotica-aplicada": "Logo_Robotica_Aplicada.png",
    "logo-utp": "utp_logo.png",
}

# Tamaño de origen aprobado para los archivos canónicos. La geometría dentro
# del mundo no depende de estos píxeles: se define con ``width_cells`` y
# ``CELL_SIZE_MM``. Registrarlos evita que Web reciba una copia reducida o que
# el bundle de escritorio incluya una variante antigua con el mismo nombre.
_SOURCE_DIMENSIONS_PX = {
    "robot_ev3_32x32": (32, 32),
    "wall_64x64_a": (64, 64),
    "wall_64x64_b": (64, 64),
    "wall_64x64_c": (64, 64),
    "zone_green_128": (128, 128),
    "zone_red_128": (128, 128),
    "zone_white_128": (128, 128),
    "line_64_64_hor": (64, 64),
    "line_64_64_ver": (64, 64),
    "line_64x64_cruz": (64, 64),
    "line_64_64_infder": (64, 64),
    "line_64_64_infizq": (64, 64),
    "line_64_64_supder": (64, 64),
    "line_64_64_supizq": (64, 64),
    "floor_tile_256_a": (256, 256),
    "floor_tile_256_b": (256, 256),
    "floor_tile_256_c": (256, 256),
    "intro-screen": (1672, 941),
    "logo-nyquist": (246, 300),
    "logo-robotica-aplicada": (200, 200),
    "logo-utp": (300, 200),
}

# Compatibilidad controlada para equipos antiguos que no pueden abrir una
# textura JPEG. La excepción vive en el catálogo, no repartida por las UI.
_ASSET_FALLBACK_FILENAMES = {"floor_tile_256_c": ("floor_tile_256_b.png",)}


@dataclass(frozen=True)
class AssetDescriptor:
    asset_id: str
    filename: str
    category: str
    source: str = "simulador_ev3/assets"
    source_width_px: int = 0
    source_height_px: int = 0
    placement_anchor: str = "top_left"
    visual_anchor: str = "top_left"

    @property
    def path(self) -> Path:
        return resolve_image_assets_dir() / self.filename

    def digest(self) -> str:
        return sha256(self.path.read_bytes()).hexdigest()


def _descriptor(asset_id: str, filename: str, category: str) -> AssetDescriptor:
    width_px, height_px = _SOURCE_DIMENSIONS_PX[asset_id]
    return AssetDescriptor(
        asset_id=asset_id,
        filename=filename,
        category=category,
        source_width_px=width_px,
        source_height_px=height_px,
        # Los placements se guardan desde la esquina superior izquierda. La
        # pose del robot, en cambio, se dibuja alrededor de su centro físico.
        placement_anchor="top_left",
        visual_anchor="center" if asset_id == "robot_ev3_32x32" else "top_left",
    )


ASSET_DESCRIPTORS: tuple[AssetDescriptor, ...] = tuple(
    _descriptor(asset_id, filename, "world-editor") for asset_id, filename in _EDITOR_FILENAMES.items()
) + tuple(_descriptor(asset_id, filename, "branding") for asset_id, filename in _BRANDING_FILENAMES.items())


def asset_descriptor(asset_id: str) -> AssetDescriptor:
    normalized = normalize_asset_key(asset_id)
    for descriptor in ASSET_DESCRIPTORS:
        if descriptor.asset_id == normalized:
            return descriptor
    raise KeyError(f"Asset no registrado: {asset_id}")


def asset_filename(asset_id: str) -> str:
    return asset_descriptor(asset_id).filename


def asset_path(asset_id: str) -> Path:
    """Ruta canónica del recurso compartido para los adaptadores de UI."""
    return asset_descriptor(asset_id).path


def asset_candidate_paths(asset_id: str) -> tuple[Path, ...]:
    """Ruta canónica seguida de fallbacks explícitos y auditables."""
    descriptor = asset_descriptor(asset_id)
    root = descriptor.path.parent
    return (descriptor.path, *(root / filename for filename in _ASSET_FALLBACK_FILENAMES.get(descriptor.asset_id, ())))


def editor_asset_manifest() -> tuple[dict[str, object], ...]:
    """Metadatos que Web entrega y Tkinter usa desde el mismo identificador."""
    return tuple(
        {
            "asset_id": key,
            "filename": asset_filename(key),
            "asset_catalog_version": ASSET_CATALOG_VERSION,
            "sha256": asset_descriptor(key).digest(),
            "source_width_px": asset_descriptor(key).source_width_px,
            "source_height_px": asset_descriptor(key).source_height_px,
            "type": spec.asset_type,
            "layer": spec.layer,
            "width_cells": spec.width_cells,
            "height_cells": spec.height_cells,
            "logical_width_mm": spec.width_cells * CELL_SIZE_MM,
            "logical_height_mm": spec.height_cells * CELL_SIZE_MM,
            "placement_anchor": asset_descriptor(key).placement_anchor,
            "visual_anchor": asset_descriptor(key).visual_anchor,
            "connectors": sorted(spec.connectors),
        }
        for key, spec in ASSET_CATALOG.items()
    )


def validate_asset_catalog() -> None:
    asset_ids = tuple(item.asset_id for item in ASSET_DESCRIPTORS)
    if len(asset_ids) != len(set(asset_ids)):
        raise ValueError("Los asset_id deben ser unicos.")
    if set(_EDITOR_FILENAMES) != set(ASSET_CATALOG):
        raise ValueError("Todo asset del editor debe resolver un archivo canonico.")
    if set(_SOURCE_DIMENSIONS_PX) != set(asset_ids):
        raise ValueError("Todo asset canonico debe declarar dimensiones de origen.")
    invalid_dimensions = [item.asset_id for item in ASSET_DESCRIPTORS if item.source_width_px <= 0 or item.source_height_px <= 0]
    if invalid_dimensions:
        raise ValueError(f"Assets con dimensiones invalidas: {', '.join(invalid_dimensions)}")
    missing = [str(item.path) for item in ASSET_DESCRIPTORS if not item.path.is_file()]
    if missing:
        raise ValueError(f"Assets canonicos ausentes: {', '.join(missing)}")
