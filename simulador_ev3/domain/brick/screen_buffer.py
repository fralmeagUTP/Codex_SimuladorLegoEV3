"""
screen_buffer.py
================
Buffer de la pantalla LCD del brick EV3.

La pantalla real del EV3 es de 178×128 píxeles en blanco/negro.
Este modelo mantiene una lista de líneas de texto y una lista de
formas gráficas simples para que la UI las renderice.
Extensión futura: modo bitmap completo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


MAX_LINES = 8   # líneas visibles en modo texto (fuente predeterminada EV3)
MAX_COLS  = 22  # caracteres por línea aprox.


@dataclass
class ScreenBuffer:
    """
    Buffer de texto de la pantalla EV3.

    Attributes:
        _lines: Lista de cadenas de texto, una por línea.
    """

    _lines: List[str] = field(default_factory=list, init=False, repr=False)

    # ------------------------------------------------------------------ #
    # Comandos
    # ------------------------------------------------------------------ #

    def cmd_print(self, text: str, end: str = "\n") -> None:
        """
        Agrega texto a la pantalla (equivale a ev3.screen.print()).
        Cada llamada añade una línea nueva; mantiene las últimas MAX_LINES.
        """
        line = str(text)[:MAX_COLS]
        self._lines.append(line)
        if len(self._lines) > MAX_LINES:
            self._lines.pop(0)  # desplazamiento hacia arriba

    def cmd_clear(self) -> None:
        """Limpia la pantalla (ev3.screen.clear())."""
        self._lines.clear()

    # ------------------------------------------------------------------ #
    # Acceso
    # ------------------------------------------------------------------ #

    @property
    def lines(self) -> List[str]:
        """Copia de las líneas visibles actuales."""
        return list(self._lines)

    def to_dict(self) -> dict:
        """Serializa para SnapshotDTO."""
        return {"lines": self.lines}

    def __repr__(self) -> str:  # pragma: no cover
        return f"ScreenBuffer(lines={len(self._lines)})"
