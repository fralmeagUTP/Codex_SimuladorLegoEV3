"""Controles HTTP reutilizables para el despliegue anónimo del simulador."""

from __future__ import annotations

import secrets
import threading
import time
from collections import defaultdict, deque
from collections.abc import Iterable
from typing import Any

from flask import Request

from simulador_ev3.web.errors import CrossOriginRequest, OperationalAccessDenied, RateLimitExceeded


class ClientRateLimiter:
    """Limitador local de ventana deslizante, acotado y sin identidad de usuario."""

    def __init__(self, *, max_keys: int = 4096) -> None:
        self._lock = threading.RLock()
        self._hits: dict[tuple[str, str], deque[float]] = defaultdict(deque)
        self._max_keys = max(1, int(max_keys))

    def allow(self, client: str, bucket: str, *, limit: int, window_s: float) -> tuple[bool, int]:
        now = time.monotonic()
        normalized_limit = max(1, int(limit))
        normalized_window = max(0.1, float(window_s))
        key = (client, bucket)
        with self._lock:
            self._prune(now, normalized_window)
            hits = self._hits[key]
            while hits and now - hits[0] >= normalized_window:
                hits.popleft()
            if len(hits) >= normalized_limit:
                retry_after_s = max(1, int(normalized_window - (now - hits[0])) + 1)
                return False, retry_after_s
            hits.append(now)
            self._trim_keys()
            return True, 0

    def _prune(self, now: float, window_s: float) -> None:
        for key, hits in list(self._hits.items()):
            while hits and now - hits[0] >= window_s:
                hits.popleft()
            if not hits:
                self._hits.pop(key, None)

    def _trim_keys(self) -> None:
        overflow = len(self._hits) - self._max_keys
        if overflow <= 0:
            return
        oldest = sorted(self._hits, key=lambda item: self._hits[item][0])[:overflow]
        for key in oldest:
            self._hits.pop(key, None)


def client_identity(request: Request, config: dict[str, Any]) -> str:
    """Obtiene IP de cliente sin confiar en cabeceras salvo configuración explícita."""

    if bool(config.get("TRUST_PROXY_HEADERS", False)):
        forwarded = request.headers.get("X-Forwarded-For", "").split(",", 1)[0].strip()
        if forwarded:
            return forwarded
        real_ip = request.headers.get("X-Real-IP", "").strip()
        if real_ip:
            return real_ip
    return str(request.remote_addr or "unknown")


def enforce_origin(request: Request) -> None:
    """Rechaza peticiones mutables de navegador que declaran origen cruzado."""

    if request.method not in {"POST", "PUT", "PATCH", "DELETE"} or not request.path.startswith("/api/"):
        return
    fetch_site = request.headers.get("Sec-Fetch-Site", "").strip().lower()
    if fetch_site == "cross-site":
        raise CrossOriginRequest("La solicitud de origen cruzado no está permitida.")
    origin = request.headers.get("Origin", "").strip()
    if not origin:
        return
    expected = request.host_url.rstrip("/")
    if not secrets.compare_digest(origin.rstrip("/"), expected):
        raise CrossOriginRequest("La solicitud no pertenece al origen de la aplicación.")


def enforce_operational_access(request: Request, config: dict[str, Any]) -> None:
    """Protege diagnóstico operativo sin introducir autenticación de usuarios."""

    if request.path not in {"/healthz", "/metrics", "/operations"}:
        return
    policy = str(config.get("OPERATIONS_ACCESS_POLICY", "public")).strip().lower()
    if policy == "public":
        return
    client = client_identity(request, config)
    allowed = {item.strip() for item in _as_items(config.get("OPERATIONS_ALLOWED_CLIENTS", "127.0.0.1,::1"))}
    if policy == "local" and client in allowed:
        return
    if policy == "token":
        expected = str(config.get("OPERATIONS_TOKEN", ""))
        received = request.headers.get("X-EV3-Operations-Token", "")
        if expected and secrets.compare_digest(received, expected):
            return
    raise OperationalAccessDenied("El diagnóstico operativo no está disponible para este cliente.")


def _as_items(value: object) -> Iterable[str]:
    if isinstance(value, str):
        return value.split(",")
    if isinstance(value, (tuple, list, set, frozenset)):
        return (str(item) for item in value)
    return ()


def enforce_rate_limit(request: Request, config: dict[str, Any], limiter: ClientRateLimiter) -> None:
    """Limita rutas que crean workers o reciben cargas de tamaño relevante."""

    if not bool(config.get("RATE_LIMIT_ENABLED", True)):
        return
    bucket: str | None = None
    limit = 0
    if request.method == "POST" and request.path == "/api/sessions":
        bucket = "session-create"
        limit = int(config.get("RATE_LIMIT_SESSION_CREATE", 12))
    elif request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.path.startswith("/api/sessions/"):
        bucket = "session-command"
        limit = int(config.get("RATE_LIMIT_SESSION_COMMAND", 120))
    if bucket is None:
        return
    allowed, retry_after_s = limiter.allow(
        client_identity(request, config),
        bucket,
        limit=limit,
        window_s=float(config.get("RATE_LIMIT_WINDOW_S", 60.0)),
    )
    if not allowed:
        raise RateLimitExceeded(
            "Demasiadas solicitudes; espere antes de intentarlo de nuevo.",
            retry_after_s=retry_after_s,
        )
