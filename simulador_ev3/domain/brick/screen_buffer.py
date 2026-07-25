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
from typing import Any, List

MAX_LINES = 8  # líneas visibles en modo texto (fuente predeterminada EV3)
MAX_COLS = 22  # caracteres por línea aprox.
SCREEN_WIDTH_PX = 178
SCREEN_HEIGHT_PX = 128
SCREEN_WIDTH_MM = 36.0
SCREEN_HEIGHT_MM = 24.0
SCREEN_DIAGONAL_MM = 47.0
SCREEN_BACKLIGHT_LEDS = 4


@dataclass
class ScreenBuffer:
    """
    Buffer de texto de la pantalla EV3.

    Attributes:
        _lines: Lista de cadenas de texto, una por línea.
    """

    _lines: List[str] = field(default_factory=list, init=False, repr=False)
    _draw_ops: List[dict[str, Any]] = field(default_factory=list, init=False, repr=False)

    # ------------------------------------------------------------------ #
    # Comandos
    # ------------------------------------------------------------------ #

    def cmd_print(self, text: str, end: str = "\n") -> None:
        """
        Agrega texto a la pantalla (equivale a ev3.screen.print()).
        Soporta saltos de línea y wrapping por ancho MAX_COLS.
        Mantiene sólo las últimas MAX_LINES visibles.
        """
        payload = str(text)
        logical_lines = payload.splitlines() or [payload]
        for logical_line in logical_lines:
            self._append_wrapped(logical_line)

    def cmd_clear(self) -> None:
        """Limpia la pantalla (ev3.screen.clear())."""
        self._lines.clear()
        self._draw_ops.clear()

    def cmd_draw_pixel(self, x: int, y: int, color: int = 1) -> None:
        self._draw_ops.append(
            {
                "op": "pixel",
                "x": int(x),
                "y": int(y),
                "color": 1 if int(color) else 0,
            }
        )

    def cmd_draw_line(self, x1: int, y1: int, x2: int, y2: int, color: int = 1) -> None:
        self._draw_ops.append(
            {
                "op": "line",
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2),
                "color": 1 if int(color) else 0,
            }
        )

    def cmd_draw_circle(self, x: int, y: int, r: int, color: int = 1, fill: bool = False) -> None:
        self._draw_ops.append(
            {
                "op": "circle",
                "x": int(x),
                "y": int(y),
                "r": max(0, int(r)),
                "color": 1 if int(color) else 0,
                "fill": bool(fill),
            }
        )

    def cmd_draw_box(self, x: int, y: int, w: int, h: int, color: int = 1, fill: bool = False) -> None:
        self._draw_ops.append(
            {
                "op": "box",
                "x": int(x),
                "y": int(y),
                "w": max(0, int(w)),
                "h": max(0, int(h)),
                "color": 1 if int(color) else 0,
                "fill": bool(fill),
            }
        )

    def _append_wrapped(self, line: str) -> None:
        if line == "":
            self._append_line("")
            return
        for i in range(0, len(line), MAX_COLS):
            self._append_line(line[i : i + MAX_COLS])

    def _append_line(self, line: str) -> None:
        self._lines.append(line[:MAX_COLS])
        if len(self._lines) > MAX_LINES:
            self._lines.pop(0)

    # ------------------------------------------------------------------ #
    # Acceso
    # ------------------------------------------------------------------ #

    @property
    def lines(self) -> List[str]:
        """Copia de las líneas visibles actuales."""
        return list(self._lines)

    @property
    def draw_ops(self) -> List[dict[str, Any]]:
        """Primitivas de dibujo acumuladas para renderizado de pantalla."""
        return [dict(op) for op in self._draw_ops]

    def to_dict(self) -> dict:
        """Serializa para SnapshotDTO."""
        return {
            "lines": self.lines,
            "draw_ops": self.draw_ops,
            "width_px": SCREEN_WIDTH_PX,
            "height_px": SCREEN_HEIGHT_PX,
            "width_mm": SCREEN_WIDTH_MM,
            "height_mm": SCREEN_HEIGHT_MM,
            "diagonal_mm": SCREEN_DIAGONAL_MM,
            "backlight_leds": SCREEN_BACKLIGHT_LEDS,
            "monochrome": True,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"ScreenBuffer(lines={len(self._lines)})"
