"""
ev3brick_model.py
=================
Modelo de dominio del brick EV3 completo.

Agrega todos los sub-modelos del hardware del brick EV3:
    - LED de estado     (LedModel)
    - Altavoz           (SpeakerModel)
    - Pantalla LCD      (ScreenBuffer)
    - Botones           (ButtonsModel)

Es el equivalente de dominio a la clase EV3Brick de Pybricks.
La capa pybricks_api/hubs.py delegará todas sus operaciones
a este modelo mediante CommandQueue.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from simulador_ev3.domain.brick.buttons_model import ButtonsModel
from simulador_ev3.domain.brick.led_model import LedModel
from simulador_ev3.domain.brick.screen_buffer import ScreenBuffer
from simulador_ev3.domain.brick.speaker_model import SpeakerModel


@dataclass
class EV3BrickModel:
    """
    Modelo del brick EV3 (hardware central).

    Attributes:
        light:   Modelo del LED de estado.
        speaker: Modelo del altavoz.
        screen:  Buffer de la pantalla LCD.
        buttons: Modelo de los botones físicos.
    """

    light: LedModel = field(default_factory=LedModel)
    speaker: SpeakerModel = field(default_factory=SpeakerModel)
    screen: ScreenBuffer = field(default_factory=ScreenBuffer)
    buttons: ButtonsModel = field(default_factory=ButtonsModel)

    # ------------------------------------------------------------------ #
    # Evolución temporal — llamado por SimulationEngine.update()
    # ------------------------------------------------------------------ #

    def update(self, dt: float) -> None:
        """
        Avanza el estado del brick un step de `dt` segundos.
        Actualmente solo el altavoz tiene evolución temporal.
        """
        self.speaker.update(dt)

    # ------------------------------------------------------------------ #
    # Serialización para SnapshotDTO
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        """
        Construye el diccionario de estado del brick para el SnapshotDTO.

        Returns:
            dict con las claves: led, speaker, screen, buttons
        """
        return {
            "led": self.light.to_dict(),
            "speaker": self.speaker.to_dict(),
            "screen": self.screen.to_dict(),
            "buttons": self.buttons.to_dict(),
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"EV3BrickModel(led={self.light!r}, speaker={self.speaker!r})"
