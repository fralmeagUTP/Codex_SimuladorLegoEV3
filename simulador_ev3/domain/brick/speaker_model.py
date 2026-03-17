"""
speaker_model.py
================
Modelo del altavoz del brick EV3.

Mantiene el estado de reproducción de sonido para que:
    - El engine sepa que hay audio activo durante dt segundos.
    - El SnapshotDTO refleje el estado del altavoz para UI/telemetría.
En una implementación futura se puede conectar a winsound / playsound.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class SpeakerState(Enum):
    IDLE    = auto()  # sin sonido
    BEEPING = auto()  # emitiendo un tono
    PLAYING = auto()  # reproduciendo archivo


@dataclass
class SpeakerModel:
    """
    Modelo del altavoz del brick EV3.

    Attributes:
        state:          Estado actual del altavoz.
        _frequency_hz:  Frecuencia del tono activo (Hz).
        _remaining_ms:  Tiempo restante del sonido (ms simulados).
        _volume:        Volumen 0-100.
    """

    state: SpeakerState        = field(default=SpeakerState.IDLE, init=False)
    _frequency_hz: float       = field(default=440.0, init=False, repr=False)
    _remaining_ms: float       = field(default=0.0,   init=False, repr=False)
    _volume:       int         = field(default=50,    init=False, repr=False)

    # ------------------------------------------------------------------ #
    # Comandos
    # ------------------------------------------------------------------ #

    def cmd_beep(
        self,
        frequency: float = 440.0,
        duration_ms: float = 100.0,
        volume: int = 50,
    ) -> None:
        """
        Emite un tono (ev3.speaker.beep() de Pybricks).
        """
        self._frequency_hz = float(frequency)
        self._remaining_ms  = float(duration_ms)
        self._volume        = max(0, min(100, volume))
        self.state          = SpeakerState.BEEPING

    def cmd_play_file(self, filename: str) -> None:
        """
        Registra la reproducción de un archivo de sonido.
        """
        self._remaining_ms = 500.0  # duración estimada por defecto
        self.state         = SpeakerState.PLAYING

    # ------------------------------------------------------------------ #
    # Evolución temporal
    # ------------------------------------------------------------------ #

    def update(self, dt: float) -> None:
        """Avanza el estado del altavoz un tick de `dt` segundos."""
        if self.state in (SpeakerState.BEEPING, SpeakerState.PLAYING):
            self._remaining_ms -= dt * 1000.0
            if self._remaining_ms <= 0.0:
                self._remaining_ms = 0.0
                self.state = SpeakerState.IDLE

    # ------------------------------------------------------------------ #
    # Serialización
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "state":        self.state.name,
            "frequency_hz": self._frequency_hz,
            "remaining_ms": self._remaining_ms,
            "volume":       self._volume,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"SpeakerModel(state={self.state.name})"
