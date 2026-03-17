"""
led_model.py
============
Modelo del LED de estado del brick EV3.

El brick EV3 tiene un LED bicolor (rojo/verde/naranja) alrededor
de los botones centrales. Puede estar:
    - Apagado
    - Encendido en un color: RED, GREEN, ORANGE, YELLOW, etc.
    - Parpadeando (extensión futura)

Este modelo solo mantiene el estado; la UI consume el SnapshotDTO
para renderizarlo visualmente.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class LedColor(Enum):
    """
    Colores soportados por el LED del brick EV3.
    Refleja los valores de pybricks.parameters.Color relevantes al LED.
    """
    OFF    = auto()
    RED    = auto()
    GREEN  = auto()
    ORANGE = auto()
    YELLOW = auto()


@dataclass
class LedModel:
    """
    Modelo del LED de estado del brick EV3.

    Attributes:
        _is_on:   Indica si el LED está encendido.
        _color:   Color actual del LED (LedColor.OFF si apagado).
    """

    _is_on: bool     = field(default=False, init=False, repr=False)
    _color: LedColor = field(default=LedColor.OFF, init=False, repr=False)

    # ------------------------------------------------------------------ #
    # Propiedades de lectura
    # ------------------------------------------------------------------ #

    @property
    def is_on(self) -> bool:
        """True si el LED está encendido."""
        return self._is_on

    @property
    def color(self) -> LedColor:
        """Color actual del LED. LedColor.OFF si está apagado."""
        return self._color

    # ------------------------------------------------------------------ #
    # Comandos
    # ------------------------------------------------------------------ #

    def cmd_on(self, color: LedColor = LedColor.GREEN) -> None:
        """
        Enciende el LED con el color especificado.
        Equivale a ev3.light.on(Color.X) de Pybricks.
        """
        if color == LedColor.OFF:
            self.cmd_off()
            return
        self._is_on = True
        self._color = color

    def cmd_off(self) -> None:
        """
        Apaga el LED.
        Equivale a ev3.light.off() de Pybricks.
        """
        self._is_on = False
        self._color = LedColor.OFF

    # ------------------------------------------------------------------ #
    # Serialización para SnapshotDTO
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        """Serializa el estado del LED para el SnapshotDTO."""
        return {
            "is_on": self._is_on,
            "color": self._color.name,
        }

    def __repr__(self) -> str:  # pragma: no cover
        state = f"ON({self._color.name})" if self._is_on else "OFF"
        return f"LedModel(state={state})"
