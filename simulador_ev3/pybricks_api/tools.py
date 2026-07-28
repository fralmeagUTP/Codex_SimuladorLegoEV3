"""
tools.py — Herramientas Pybricks (pybricks.tools).

Contiene wait(ms) y StopWatch, que los scripts de usuario llaman
para temporización. En el simulador:
  - wait(ms) hace un sleep real de ms milisegundos, pero primero comprueba
    si el sandbox ha sido detenido (stop_event). Esto permite que el
    RuntimeController detenga el script cooperativamente.
  - StopWatch emula el cronómetro Pybricks (tiempo de pared).
"""

from __future__ import annotations

import time as _time

from simulador_ev3.pybricks_api._context import PybricksContext


def wait(time_ms: float) -> None:
    """
    Espera `time_ms` milisegundos.

    Si el sandbox está señalado para detenerse (stop_event), la espera
    se interrumpe y no se lanza excepción (el script terminará
    naturalmente al salir del bucle o al no haber más instrucciones).
    """
    ctx = PybricksContext.get_current()
    # Esperamos en intervalos de 10 ms para reaccionar al stop_event rápido
    remaining_s = max(0.0, float(time_ms)) / 1000.0
    interval = 0.01  # 10 ms

    if ctx.stop_event.is_set():
        raise SystemExit

    while remaining_s > 0:
        # El engine puede quedar pausado durante una misión. En ese estado no
        # se descuenta el tiempo solicitado: el script conserva la espera que
        # quedaba al reanudar y Stop sigue siendo inmediato.
        while ctx.pause_event.is_set():
            if ctx.stop_event.is_set():
                raise SystemExit
            _time.sleep(interval)
        sleep_s = min(remaining_s, interval)
        _time.sleep(sleep_s)
        if ctx.stop_event.is_set():
            raise SystemExit
        if not ctx.pause_event.is_set():
            remaining_s -= sleep_s


class StopWatch:
    """
    Cronómetro Pybricks de tiempo de pared.

    Métodos:
        time()  → ms transcurridos desde el último reset
        pause() → pausa el cronómetro
        resume()→ reanuda el cronómetro
        reset() → reinicia a 0 (sigue corriendo)
    """

    def __init__(self) -> None:
        self._start: float = _time.perf_counter()
        self._paused_at: float = 0.0
        self._paused: bool = False
        self._elapsed_paused: float = 0.0

    def time(self) -> int:
        """Milisegundos transcurridos."""
        if self._paused:
            elapsed_s = self._paused_at - self._start - self._elapsed_paused
        else:
            elapsed_s = _time.perf_counter() - self._start - self._elapsed_paused
        return int(elapsed_s * 1000)

    def pause(self) -> None:
        if not self._paused:
            self._paused_at = _time.perf_counter()
            self._paused = True

    def resume(self) -> None:
        if self._paused:
            self._elapsed_paused += _time.perf_counter() - self._paused_at
            self._paused = False

    def reset(self) -> None:
        self._start = _time.perf_counter()
        self._paused = False
        self._paused_at = 0.0
        self._elapsed_paused = 0.0
