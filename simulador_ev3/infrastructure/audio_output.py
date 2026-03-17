"""Salida de audio real para el simulador EV3.

En Windows usa `winsound.Beep`; en otros entornos usa un backend nulo
para no romper la simulación.
"""
from __future__ import annotations

import threading
from abc import ABC, abstractmethod


class AudioOutput(ABC):
    @abstractmethod
    def play_beep(self, frequency: int, duration_ms: int, volume: int = 50) -> None:
        """Reproduce un tono de forma no bloqueante."""


class NullAudioOutput(AudioOutput):
    """Backend sin sonido físico (fallback seguro)."""

    def play_beep(self, frequency: int, duration_ms: int, volume: int = 50) -> None:
        return


class WinsoundAudioOutput(AudioOutput):
    """Backend de audio real para Windows usando winsound."""

    def __init__(self) -> None:
        import winsound  # Import local para no fallar fuera de Windows

        self._winsound = winsound

    def play_beep(self, frequency: int, duration_ms: int, volume: int = 50) -> None:
        freq = int(max(37, min(32767, frequency)))
        dur = int(max(10, duration_ms))

        def _run() -> None:
            try:
                self._winsound.Beep(freq, dur)
            except Exception:
                pass

        threading.Thread(target=_run, name="AudioBeepThread", daemon=True).start()


def create_audio_output() -> AudioOutput:
    """Crea el backend de audio apropiado según plataforma."""
    try:
        return WinsoundAudioOutput()
    except Exception:
        return NullAudioOutput()
