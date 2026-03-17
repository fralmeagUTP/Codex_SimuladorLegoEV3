"""Tests para EventBus."""

import threading
import time

import pytest

from simulador_ev3.core.event_bus import (
    EVENT_RUNTIME_ERROR,
    EVENT_SENSOR_UPDATED,
    EVENT_SIMULATION_STARTED,
    EVENT_SIMULATION_STOPPED,
    EventBus,
)


# ---------------------------------------------------------------------------
# Subscripción y desuscripción
# ---------------------------------------------------------------------------

class TestSubscription:
    def setup_method(self):
        self.bus = EventBus()
        self.received: list[tuple[str, dict]] = []

    def _handler(self, event: str, payload: dict) -> None:
        self.received.append((event, payload))

    def test_subscribe_and_receive(self):
        self.bus.subscribe(EVENT_SIMULATION_STARTED, self._handler)
        self.bus.publish(EVENT_SIMULATION_STARTED, {})
        assert len(self.received) == 1
        assert self.received[0][0] == EVENT_SIMULATION_STARTED

    def test_no_notification_after_unsubscribe(self):
        self.bus.subscribe(EVENT_SIMULATION_STARTED, self._handler)
        self.bus.unsubscribe(EVENT_SIMULATION_STARTED, self._handler)
        self.bus.publish(EVENT_SIMULATION_STARTED, {})
        assert self.received == []

    def test_unsubscribe_returns_false_if_not_registered(self):
        result = self.bus.unsubscribe(EVENT_SIMULATION_STOPPED, self._handler)
        assert result is False

    def test_double_subscribe_does_not_duplicate(self):
        self.bus.subscribe(EVENT_SIMULATION_STARTED, self._handler)
        self.bus.subscribe(EVENT_SIMULATION_STARTED, self._handler)
        self.bus.publish(EVENT_SIMULATION_STARTED, {})
        assert len(self.received) == 1  # sólo una notificación

    def test_unsubscribe_all_single_event(self):
        self.bus.subscribe(EVENT_SIMULATION_STARTED, self._handler)
        self.bus.subscribe(EVENT_SIMULATION_STOPPED, self._handler)
        self.bus.unsubscribe_all(EVENT_SIMULATION_STARTED)
        self.bus.publish(EVENT_SIMULATION_STARTED, {})
        self.bus.publish(EVENT_SIMULATION_STOPPED, {"reason": "test"})
        assert len(self.received) == 1
        assert self.received[0][0] == EVENT_SIMULATION_STOPPED

    def test_unsubscribe_all_no_event_clears_all(self):
        self.bus.subscribe(EVENT_SIMULATION_STARTED, self._handler)
        self.bus.subscribe(EVENT_SIMULATION_STOPPED, self._handler)
        self.bus.unsubscribe_all()
        self.bus.publish(EVENT_SIMULATION_STARTED, {})
        self.bus.publish(EVENT_SIMULATION_STOPPED, {"reason": "test"})
        assert self.received == []


# ---------------------------------------------------------------------------
# Publicación
# ---------------------------------------------------------------------------

class TestPublish:
    def setup_method(self):
        self.bus = EventBus()
        self.received: list[dict] = []

    def test_publish_returns_handler_count(self):
        def h1(e, p): pass
        def h2(e, p): pass
        self.bus.subscribe(EVENT_SENSOR_UPDATED, h1)
        self.bus.subscribe(EVENT_SENSOR_UPDATED, h2)
        count = self.bus.publish(EVENT_SENSOR_UPDATED, {"port": "S1", "data": {}})
        assert count == 2

    def test_publish_no_subscribers_returns_zero(self):
        count = self.bus.publish(EVENT_RUNTIME_ERROR, {"error": "x", "traceback": ""})
        assert count == 0

    def test_payload_passed_to_handler(self):
        payloads = []
        self.bus.subscribe(EVENT_SIMULATION_STOPPED,
                           lambda e, p: payloads.append(p))
        self.bus.publish(EVENT_SIMULATION_STOPPED, {"reason": "user"})
        assert payloads[0]["reason"] == "user"

    def test_faulty_handler_does_not_break_others(self):
        results = []

        def bad_handler(e, p):
            raise RuntimeError("fallo intencional")

        def good_handler(e, p):
            results.append(p)

        self.bus.subscribe(EVENT_SIMULATION_STARTED, bad_handler)
        self.bus.subscribe(EVENT_SIMULATION_STARTED, good_handler)
        # No debe lanzar excepción
        count = self.bus.publish(EVENT_SIMULATION_STARTED, {})
        assert count == 1  # sólo good_handler notificado con éxito
        assert len(results) == 1

    def test_multiple_events_independent(self):
        log: list[str] = []
        self.bus.subscribe(EVENT_SIMULATION_STARTED,
                           lambda e, p: log.append("start"))
        self.bus.subscribe(EVENT_SIMULATION_STOPPED,
                           lambda e, p: log.append("stop"))
        self.bus.publish(EVENT_SIMULATION_STARTED, {})
        self.bus.publish(EVENT_SIMULATION_STOPPED, {"reason": "ok"})
        assert log == ["start", "stop"]


# ---------------------------------------------------------------------------
# Validación de eventos
# ---------------------------------------------------------------------------

class TestStrictEvents:
    def test_unknown_event_raises_in_strict_mode(self):
        bus = EventBus(strict_events=True)
        with pytest.raises(ValueError, match="Evento desconocido"):
            bus.subscribe("evento_inventado", lambda e, p: None)

    def test_unknown_event_ok_in_non_strict_mode(self):
        bus = EventBus(strict_events=False)
        received = []
        bus.subscribe("evento_inventado", lambda e, p: received.append(p))
        bus.publish("evento_inventado", {"x": 1})
        assert received[0]["x"] == 1


# ---------------------------------------------------------------------------
# Thread-safety
# ---------------------------------------------------------------------------

class TestThreadSafety:
    def test_concurrent_subscribe_and_publish(self):
        """Suscribirse y publicar desde múltiples hilos no debe corromper estado."""
        bus = EventBus()
        results: list[int] = []
        lock = threading.Lock()
        N = 50

        def subscriber_thread(i: int):
            def h(e, p):
                with lock:
                    results.append(i)
            bus.subscribe(EVENT_SENSOR_UPDATED, h)

        def publisher_thread():
            for _ in range(N):
                bus.publish(EVENT_SENSOR_UPDATED, {"port": "S1", "data": {}})
                time.sleep(0.001)

        sub_threads = [threading.Thread(target=subscriber_thread, args=(i,))
                       for i in range(5)]
        pub_thread = threading.Thread(target=publisher_thread)

        for t in sub_threads:
            t.start()
        pub_thread.start()

        pub_thread.join()
        for t in sub_threads:
            t.join()

        assert len(results) > 0  # al menos algunos handlers llamados


# ---------------------------------------------------------------------------
# subscriber_count y all_events
# ---------------------------------------------------------------------------

class TestQueryMethods:
    def test_subscriber_count(self):
        bus = EventBus()
        assert bus.subscriber_count(EVENT_SIMULATION_STARTED) == 0
        bus.subscribe(EVENT_SIMULATION_STARTED, lambda e, p: None)
        assert bus.subscriber_count(EVENT_SIMULATION_STARTED) == 1

    def test_all_events(self):
        bus = EventBus()
        bus.subscribe(EVENT_SIMULATION_STARTED, lambda e, p: None)
        bus.subscribe(EVENT_SENSOR_UPDATED, lambda e, p: None)
        events = bus.all_events
        assert EVENT_SIMULATION_STARTED in events
        assert EVENT_SENSOR_UPDATED in events
        assert len(events) == 2
