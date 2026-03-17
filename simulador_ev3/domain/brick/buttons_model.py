"""
buttons_model.py
================
Modelo de los botones físicos del brick EV3.

El brick EV3 tiene 6 botones:
    UP, DOWN, LEFT, RIGHT, CENTER (Enter), BACK (Escape)

Este modelo mantiene el estado de presión de cada botón.
En la UI, los eventos de teclado o clicks del usuario
modifican este estado mediante el controlador de aplicación.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Set


class Button(Enum):
    """Botones disponibles en el brick EV3."""
    UP     = auto()
    DOWN   = auto()
    LEFT   = auto()
    RIGHT  = auto()
    CENTER = auto()
    BACK   = auto()


@dataclass
class ButtonsModel:
    """
    Modelo del panel de botones del brick EV3.

    Mantiene un conjunto de botones actualmente presionados.
    """

    _pressed: Set[Button] = field(default_factory=set, init=False, repr=False)

    # ------------------------------------------------------------------ #
    # Manipulación de estado (desde UI/controller)
    # ------------------------------------------------------------------ #

    def press(self, button: Button) -> None:
        """Marca un botón como presionado."""
        self._pressed.add(button)

    def release(self, button: Button) -> None:
        """Marca un botón como liberado."""
        self._pressed.discard(button)

    def release_all(self) -> None:
        """Libera todos los botones."""
        self._pressed.clear()

    # ------------------------------------------------------------------ #
    # Lectura (desde pybricks_api)
    # ------------------------------------------------------------------ #

    def is_pressed(self, button: Button) -> bool:
        """True si el botón está actualmente presionado."""
        return button in self._pressed

    def pressed_buttons(self) -> Set[Button]:
        """Conjunto de botones actualmente presionados."""
        return set(self._pressed)

    # ------------------------------------------------------------------ #
    # Serialización
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {"pressed": [b.name for b in self._pressed]}

    def __repr__(self) -> str:  # pragma: no cover
        names = [b.name for b in self._pressed]
        return f"ButtonsModel(pressed={names})"
