"""
surface_model.py
================
Modelo de la superficie del mundo en que se mueve el robot EV3.

La superficie define para cada celda (x, y):
    - Color predominante  → usado por ColorSensor en modo color()
    - Reflectancia 0-100  → usado por ColorSensor en modo reflection()

Implementación: grilla de celdas cuadradas de tamaño configurable.
Valores predeterminados: superficie blanca (reflectancia 100, Color WHITE).

Unidades: mm en el espacio del mundo.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Tuple


class SurfaceColor(Enum):
    """
    Colores de superficie reconocibles por el ColorSensor.
    Mapea directamente a pybricks.parameters.Color.
    """

    NONE = auto()  # sin superficie / fuera de límites
    WHITE = auto()
    BLACK = auto()
    RED = auto()
    GREEN = auto()
    BLUE = auto()
    YELLOW = auto()
    BROWN = auto()


# Reflectancia predeterminada por color de superficie (0-100 %)
_DEFAULT_REFLECTANCE: Dict[SurfaceColor, float] = {
    SurfaceColor.NONE: 0.0,
    SurfaceColor.WHITE: 95.0,
    SurfaceColor.BLACK: 5.0,
    SurfaceColor.RED: 30.0,
    SurfaceColor.GREEN: 40.0,
    SurfaceColor.BLUE: 20.0,
    SurfaceColor.YELLOW: 80.0,
    SurfaceColor.BROWN: 15.0,
}


@dataclass
class SurfaceCell:
    """Una celda individual de la grilla de superficie."""

    color: SurfaceColor = SurfaceColor.WHITE
    reflectance: float = 95.0  # 0-100 %


# Clave de grilla: (columna, fila) en unidades de celda
GridKey = Tuple[int, int]


class SurfaceModel:
    """
    Grilla de celdas que define la superficie del escenario.

    Uso:
        surface = SurfaceModel(cell_size_mm=50.0)         # celdas de 5 cm
        surface.set_cell(0, 0, SurfaceColor.WHITE)
        surface.set_line(x0=0, y0=100, x1=500, y1=100,
                         width_mm=20, color=SurfaceColor.BLACK)
        color, reflectance = surface.query(x_mm=125.0, y_mm=100.0)

    Args:
        cell_size_mm: Tamaño en mm de cada celda cuadrada (default 50 mm).
        default_color: Color de fondo de todas las celdas no definidas.
    """

    def __init__(
        self,
        cell_size_mm: float = 50.0,
        default_color: SurfaceColor = SurfaceColor.WHITE,
    ) -> None:
        if cell_size_mm <= 0:
            raise ValueError("cell_size_mm debe ser > 0")
        self.cell_size_mm = cell_size_mm
        self.default_color = default_color
        self._grid: Dict[GridKey, SurfaceCell] = {}

    # ------------------------------------------------------------------ #
    # Escritura de celdas
    # ------------------------------------------------------------------ #

    def set_cell(
        self,
        col: int,
        row: int,
        color: SurfaceColor,
        reflectance: float | None = None,
    ) -> None:
        """
        Define el color (y opcionalmente la reflectancia) de una celda.
        Si reflectance es None, usa el valor predeterminado para ese color.
        """
        r = reflectance if reflectance is not None else _DEFAULT_REFLECTANCE[color]
        self._grid[(col, row)] = SurfaceCell(color=color, reflectance=r)

    def set_rect(
        self,
        x_mm: float,
        y_mm: float,
        width_mm: float,
        height_mm: float,
        color: SurfaceColor,
        reflectance: float | None = None,
    ) -> None:
        """Rellena un rectángulo del mundo con un color dado."""
        cs = self.cell_size_mm
        col_min = int(x_mm / cs)
        col_max = int((x_mm + width_mm) / cs)
        row_min = int(y_mm / cs)
        row_max = int((y_mm + height_mm) / cs)
        for col in range(col_min, col_max + 1):
            for row in range(row_min, row_max + 1):
                self.set_cell(col, row, color, reflectance)

    # ------------------------------------------------------------------ #
    # Consulta de posición
    # ------------------------------------------------------------------ #

    def _world_to_grid(self, x_mm: float, y_mm: float) -> GridKey:
        """Convierte coordenadas de mundo (mm) a clave de grilla."""
        col = int(x_mm / self.cell_size_mm)
        row = int(y_mm / self.cell_size_mm)
        return col, row

    def query(self, x_mm: float, y_mm: float) -> tuple[SurfaceColor, float]:
        """
        Consulta el color y reflectancia de la superficie en (x_mm, y_mm).

        Returns:
            (SurfaceColor, reflectance_0_100)
        """
        key = self._world_to_grid(x_mm, y_mm)
        if key in self._grid:
            cell = self._grid[key]
            return cell.color, cell.reflectance
        # Celda no definida → color de fondo
        default_r = _DEFAULT_REFLECTANCE[self.default_color]
        return self.default_color, default_r

    def query_color(self, x_mm: float, y_mm: float) -> SurfaceColor:
        """Solo el color de superficie en (x_mm, y_mm)."""
        color, _ = self.query(x_mm, y_mm)
        return color

    def query_reflectance(self, x_mm: float, y_mm: float) -> float:
        """Solo la reflectancia (0-100 %) en (x_mm, y_mm)."""
        _, r = self.query(x_mm, y_mm)
        return r

    def iter_defined_cells(self):
        """Expone las celdas configuradas sin revelar la estructura interna."""
        return tuple((col, row, cell) for (col, row), cell in self._grid.items())

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SurfaceModel(cell_size={self.cell_size_mm}mm, cells={len(self._grid)}, default={self.default_color.name})"
        )
