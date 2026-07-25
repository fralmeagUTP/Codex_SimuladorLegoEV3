"""
hubs.py — EV3Brick Pybricks (pybricks.hubs).

EV3Brick expone los sub-sistemas del ladrillo:
  - light    → LED de estado
  - speaker  → altavoz
  - screen   → pantalla LCD
  - buttons  → botones físicos

Todos los comandos se envían al CommandQueue del engine.
Las lecturas (botones) leen del modelo de dominio directamente.
"""

from __future__ import annotations

from simulador_ev3.core.command_queue import SimulationCommand
from simulador_ev3.pybricks_api._context import PybricksContext
from simulador_ev3.pybricks_api.parameters import Button, Color

# ---------------------------------------------------------------------------
# Sub-objetos del ladrillo
# ---------------------------------------------------------------------------


class _Light:
    """ev3.light — LED de estado."""

    def __init__(self, queue) -> None:
        self._q = queue

    def on(self, color: Color = Color.GREEN) -> None:
        """Enciende el LED con el color dado."""
        # Mapeo Color Pybricks → nombre LedColor del dominio
        _map = {
            Color.RED: "RED",
            Color.GREEN: "GREEN",
            Color.ORANGE: "ORANGE",
            Color.YELLOW: "YELLOW",
        }
        self._q.put(SimulationCommand.led_on(_map.get(color, "GREEN")))

    def off(self) -> None:
        """Apaga el LED."""
        self._q.put(SimulationCommand.led_off())


class _Speaker:
    """ev3.speaker — altavoz."""

    def __init__(self, queue) -> None:
        self._q = queue

    def beep(
        self,
        frequency: float = 440.0,
        duration: float = 100.0,
        volume: int = 50,
    ) -> None:
        """Emite un tono."""
        self._q.put(
            SimulationCommand.play_sound(
                frequency=int(frequency),
                duration_ms=int(duration),
                volume=volume,
            )
        )

    def say(self, text: str) -> None:
        """Simula voz (no implementado — imprime en pantalla)."""
        self._q.put(SimulationCommand.display_text(f"[voz] {text}"))


class _Screen:
    """ev3.screen — pantalla LCD."""

    def __init__(self, queue) -> None:
        self._q = queue

    def print(self, *args, sep: str = " ", end: str = "\n") -> None:
        """
        Muestra texto en la pantalla (equivale a Python print → screen).
        """
        text = sep.join(str(a) for a in args)
        self._q.put(SimulationCommand.display_text(text))

    def clear(self) -> None:
        """Limpia la pantalla."""
        self._q.put(SimulationCommand.screen_clear())

    def draw_pixel(self, x: int, y: int, color: int = 1) -> None:
        """Dibuja un pixel monocromo en coordenadas LCD (178x128)."""
        self._q.put(SimulationCommand.screen_pixel(x, y, color=color))

    # Alias habitual en algunos ejemplos comunitarios.
    def pixel(self, x: int, y: int, color: int = 1) -> None:
        self.draw_pixel(x, y, color=color)

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, color: int = 1) -> None:
        self._q.put(SimulationCommand.screen_line(x1, y1, x2, y2, color=color))

    def draw_circle(self, x: int, y: int, r: int, color: int = 1, fill: bool = False) -> None:
        self._q.put(SimulationCommand.screen_circle(x, y, r, color=color, fill=fill))

    def draw_box(self, x: int, y: int, w: int, h: int, color: int = 1, fill: bool = False) -> None:
        self._q.put(SimulationCommand.screen_box(x, y, w, h, color=color, fill=fill))


class _Buttons:
    """ev3.buttons — botones físicos."""

    def pressed(self) -> list[Button]:
        """Lista de botones actualmente presionados (siempre [] en sim)."""
        PybricksContext.get_current()
        # ButtonsModel usa Button del dominio; aquí mapeamos al enum Pybricks
        return []  # Extensión futura: mapear correctamente


# ---------------------------------------------------------------------------
# EV3Brick
# ---------------------------------------------------------------------------


class EV3Brick:
    """
    Ladrillo EV3 (pybricks.hubs.EV3Brick).

    Atributos:
        light:   LED de estado.
        speaker: Altavoz.
        screen:  Pantalla LCD.
        buttons: Botones físicos.
    """

    def __init__(self) -> None:
        ctx = PybricksContext.get_current()
        q = ctx.command_queue
        self.light = _Light(q)
        self.speaker = _Speaker(q)
        self.screen = _Screen(q)
        self.buttons = _Buttons()
