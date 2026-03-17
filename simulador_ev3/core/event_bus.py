"""
event_bus.py — Bus de eventos pub/sub thread-safe para la simulación EV3.

El EventBus desacopla los productores (SimulationEngine, RuntimeController)
de los consumidores (UI, telemetría, tests).

Eventos predefinidos (SAD §6):
    simulation_started   — Motor arrancado; payload: {}
    simulation_stopped   — Motor detenido; payload: {"reason": str}
    runtime_error        — Excepción en script de usuario; payload: {"error": str, "traceback": str}
    sensor_updated       — Lectura de sensor publicada; payload: {"port": str, "data": dict}

Los callbacks se invocan en el hilo que llama a publish(), que normalmente
es el hilo del Engine (tick thread). Las UIs deben encolar en su propio
dispatcher (p. ej. widget.after(0, callback)) si necesitan actualizar
widgets Tkinter desde callbacks.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from typing import Callable, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tipos de evento
# ---------------------------------------------------------------------------

EVENT_SIMULATION_STARTED = "simulation_started"
EVENT_SIMULATION_STOPPED = "simulation_stopped"
EVENT_RUNTIME_ERROR      = "runtime_error"
EVENT_SENSOR_UPDATED     = "sensor_updated"

VALID_EVENTS: frozenset[str] = frozenset({
    EVENT_SIMULATION_STARTED,
    EVENT_SIMULATION_STOPPED,
    EVENT_RUNTIME_ERROR,
    EVENT_SENSOR_UPDATED,
})

# Tipo de handler
EventHandler = Callable[[str, dict], None]
#                         ^event    ^payload


# ---------------------------------------------------------------------------
# EventBus
# ---------------------------------------------------------------------------

class EventBus:
    """
    Bus de eventos pub/sub thread-safe.

    Uso básico:
        bus = EventBus()

        def on_start(event, payload):
            print("Simulación arrancada")

        bus.subscribe(EVENT_SIMULATION_STARTED, on_start)
        bus.publish(EVENT_SIMULATION_STARTED, {})
        bus.unsubscribe(EVENT_SIMULATION_STARTED, on_start)

    Parámetros del constructor:
        strict_events: bool
            Si True (por defecto) lanza ValueError al publicar/suscribir
            eventos no definidos en VALID_EVENTS. Ponlo en False para tests
            con eventos personalizados.
    """

    def __init__(self, strict_events: bool = True) -> None:
        self._strict = strict_events
        self._lock = threading.Lock()
        # event_name → lista de handlers registrados
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Subscripción
    # ------------------------------------------------------------------

    def subscribe(self, event: str, handler: EventHandler) -> None:
        """
        Registra handler para el evento dado.

        Un mismo handler puede suscribirse a múltiples eventos, pero
        registrarlo dos veces en el mismo evento no lo duplica.
        """
        self._validate_event(event)
        with self._lock:
            if handler not in self._subscribers[event]:
                self._subscribers[event].append(handler)

    def unsubscribe(self, event: str, handler: EventHandler) -> bool:
        """
        Elimina el handler del evento.
        Devuelve True si estaba registrado, False si no existía.
        """
        self._validate_event(event)
        with self._lock:
            handlers = self._subscribers[event]
            if handler in handlers:
                handlers.remove(handler)
                return True
            return False

    def unsubscribe_all(self, event: Optional[str] = None) -> None:
        """
        Elimina todos los handlers.
        Si event se omite, limpia TODOS los eventos.
        """
        with self._lock:
            if event is None:
                self._subscribers.clear()
            else:
                self._validate_event(event)
                self._subscribers[event].clear()

    # ------------------------------------------------------------------
    # Publicación
    # ------------------------------------------------------------------

    def publish(self, event: str, payload: dict) -> int:
        """
        Invoca sincrónicamente todos los handlers del evento.

        Devuelve el número de handlers notificados.
        Los errores en handlers individuales se capturan y loguean para
        no interrumpir al resto de suscriptores.
        """
        self._validate_event(event)
        with self._lock:
            handlers = list(self._subscribers[event])  # copia para evitar deadlock

        notified = 0
        for handler in handlers:
            try:
                handler(event, payload)
                notified += 1
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "EventBus: handler %r falló en evento '%s': %s",
                    handler,
                    event,
                    exc,
                )
        return notified

    # ------------------------------------------------------------------
    # Consulta
    # ------------------------------------------------------------------

    def subscriber_count(self, event: str) -> int:
        """Número de handlers registrados para el evento."""
        with self._lock:
            return len(self._subscribers.get(event, []))

    @property
    def all_events(self) -> list[str]:
        """Eventos que tienen al menos un suscriptor."""
        with self._lock:
            return [e for e, h in self._subscribers.items() if h]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _validate_event(self, event: str) -> None:
        if self._strict and event not in VALID_EVENTS:
            raise ValueError(
                f"Evento desconocido: '{event}'. "
                f"Eventos válidos: {sorted(VALID_EVENTS)}"
            )
