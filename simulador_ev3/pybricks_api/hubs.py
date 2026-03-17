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
            Color.RED:    "RED",
            Color.GREEN:  "GREEN",
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
        duration: float  = 100.0,
        volume: int      = 50,
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


class _Buttons:
    """ev3.buttons — botones físicos."""

    def pressed(self) -> list[Button]:
        """Lista de botones actualmente presionados (siempre [] en sim)."""
        ctx = PybricksContext.get_current()
        pressed = ctx.engine._brick.buttons.pressed_buttons
        # ButtonsModel usa Button del dominio; aquí mapeamos al enum Pybricks
        return []   # Extensión futura: mapear correctamente


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
        q   = ctx.command_queue
        self.light   = _Light(q)
        self.speaker = _Speaker(q)
        self.screen  = _Screen(q)
        self.buttons = _Buttons()
