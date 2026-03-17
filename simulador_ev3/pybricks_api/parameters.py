"""
parameters.py — Enums Pybricks (pybricks.parameters).

Replica exacta de los enumerados que los scripts Pybricks reales usan.
Los valores str de Port permiten pasarlos directamente al CommandQueue.
"""
from __future__ import annotations

from enum import Enum, auto


class Port(str, Enum):
    """Puertos del brick EV3."""
    # Puertos de motor
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    # Puertos de sensor
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"

    def __str__(self) -> str:  # pragma: no cover
        return self.value


class Color(Enum):
    """Colores Pybricks."""
    BLACK  = auto()
    BLUE   = auto()
    GREEN  = auto()
    YELLOW = auto()
    RED    = auto()
    WHITE  = auto()
    BROWN  = auto()
    ORANGE = auto()
    NONE   = auto()   # sin color detectado


class Stop(Enum):
    """Modo de parada del motor al finalizar un comando acotado."""
    COAST = auto()   # desliza libremente
    BRAKE = auto()   # frena activamente, luego desliza
    HOLD  = auto()   # mantiene la posición con torque
    NONE  = auto()   # continúa (sin parada)


class Direction(Enum):
    """Dirección positiva del motor."""
    CLOCKWISE        = auto()
    COUNTERCLOCKWISE = auto()


class Button(Enum):
    """Botones físicos del brick EV3."""
    LEFT_DOWN  = auto()
    DOWN       = auto()
    RIGHT_DOWN = auto()
    LEFT       = auto()
    CENTER     = auto()
    RIGHT      = auto()
    LEFT_UP    = auto()
    UP         = auto()
    RIGHT_UP   = auto()


# Mapa Color Pybricks → nombre del SurfaceColor del dominio
PYBRICKS_TO_SURFACE: dict[Color, str] = {
    Color.BLACK:  "BLACK",
    Color.BLUE:   "BLUE",
    Color.GREEN:  "GREEN",
    Color.YELLOW: "YELLOW",
    Color.RED:    "RED",
    Color.WHITE:  "WHITE",
    Color.BROWN:  "BROWN",
    Color.NONE:   "NONE",
}

# Mapa SurfaceColor nombre → Color Pybricks
SURFACE_TO_PYBRICKS: dict[str, Color] = {
    v: k for k, v in PYBRICKS_TO_SURFACE.items()
}

# Mapa Stop → nombre StopMode del dominio
STOP_TO_STOPMODE: dict[Stop, str] = {
    Stop.COAST: "COAST",
    Stop.BRAKE: "BRAKE",
    Stop.HOLD:  "HOLD",
    Stop.NONE:  "COAST",
}
