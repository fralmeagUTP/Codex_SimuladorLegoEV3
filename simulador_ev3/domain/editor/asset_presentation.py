"""Metadatos de presentación compartidos para el editor visual de mundos.

El modelo persistente conserva claves técnicas y coordenadas en píxeles. Este
módulo traduce dichos detalles a textos y unidades adecuados para las dos
interfaces sin alterar el formato JSON de los mundos.
"""

from __future__ import annotations

from dataclasses import dataclass

from simulador_ev3.domain.editor.world_editor_model import CELL_SIZE_MM, GRID_SIZE_PX, normalize_asset_key


@dataclass(frozen=True)
class AssetPresentation:
    """Nombre, categoría y ayuda de un asset para usuarios finales."""

    category: str
    name: str
    tooltip: str


ASSET_PRESENTATIONS: dict[str, AssetPresentation] = {
    "robot_ev3_32x32": AssetPresentation("Robot", "Robot EV3", "Define la posición inicial del robot."),
    "wall_64x64_a": AssetPresentation("Obstáculos", "Muro metálico A", "Obstáculo sólido de 2 × 2 celdas."),
    "wall_64x64_b": AssetPresentation("Obstáculos", "Muro metálico B", "Obstáculo sólido de 2 × 2 celdas."),
    "wall_64x64_c": AssetPresentation("Obstáculos", "Muro metálico C", "Obstáculo sólido de 2 × 2 celdas."),
    "floor_tile_256_a": AssetPresentation("Suelos", "Suelo A", "Baldosa de suelo de 8 × 8 celdas."),
    "floor_tile_256_b": AssetPresentation("Suelos", "Suelo B", "Baldosa de suelo de 8 × 8 celdas."),
    "floor_tile_256_c": AssetPresentation("Suelos", "Suelo C", "Baldosa de suelo de 8 × 8 celdas."),
    "zone_white_128": AssetPresentation("Zonas y metas", "Zona blanca", "Zona de color blanco de 4 × 4 celdas."),
    "zone_red_128": AssetPresentation("Zonas y metas", "Zona roja", "Zona de color rojo de 4 × 4 celdas."),
    "zone_green_128": AssetPresentation("Zonas y metas", "Zona verde", "Zona de color verde de 4 × 4 celdas."),
    "line_64_64_hor": AssetPresentation("Líneas", "Línea horizontal", "Tramo de línea horizontal de 2 × 2 celdas."),
    "line_64_64_ver": AssetPresentation("Líneas", "Línea vertical", "Tramo de línea vertical de 2 × 2 celdas."),
    "line_64x64_cruz": AssetPresentation("Líneas", "Cruce de líneas", "Intersección de cuatro direcciones."),
    "line_64_64_infder": AssetPresentation(
        "Líneas", "Curva inferior derecha", "Curva de línea hacia la parte inferior derecha."
    ),
    "line_64_64_infizq": AssetPresentation(
        "Líneas", "Curva inferior izquierda", "Curva de línea hacia la parte inferior izquierda."
    ),
    "line_64_64_supder": AssetPresentation(
        "Líneas", "Curva superior derecha", "Curva de línea hacia la parte superior derecha."
    ),
    "line_64_64_supizq": AssetPresentation(
        "Líneas", "Curva superior izquierda", "Curva de línea hacia la parte superior izquierda."
    ),
}

CATEGORY_ORDER = ("Robot", "Obstáculos", "Suelos", "Líneas", "Zonas y metas", "Sensores")


def presentation_for_asset(asset_key: str) -> AssetPresentation:
    """Obtiene presentación segura, incluso para assets futuros o heredados."""

    key = normalize_asset_key(asset_key)
    return ASSET_PRESENTATIONS.get(
        key,
        AssetPresentation("Otros", key.replace("_", " ").title(), "Elemento del mundo."),
    )


def pixels_to_cells(value_px: int | float) -> float:
    """Convierte una coordenada interna a celdas de cuadrícula."""

    return float(value_px) / GRID_SIZE_PX


def pixels_to_mm(value_px: int | float) -> float:
    """Convierte una coordenada interna a milímetros del mundo."""

    return pixels_to_cells(value_px) * CELL_SIZE_MM


def cells_to_pixels(value_cells: int | float) -> int:
    """Convierte la unidad de edición visible al valor interno persistido."""

    return int(round(float(value_cells) * GRID_SIZE_PX))


def cells_to_mm(value_cells: int | float) -> float:
    """Indica la equivalencia física visible de un tamaño en celdas."""

    return float(value_cells) * CELL_SIZE_MM
