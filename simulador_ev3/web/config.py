"""Configuration defaults for the Flask web application."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

from simulador_ev3._version import WEB_ASSET_VERSION
from simulador_ev3.shared.paths import (
    resolve_examples_dir,
    resolve_image_assets_dir,
    resolve_worlds_dir,
)
from simulador_ev3.shared.ui_settings import UI_FIT_PADDING_RATIO

DEVELOPMENT_SECRET_KEY = hashlib.sha256(b"ev3-local-development-key").hexdigest()
PRODUCTION_ENVIRONMENTS = frozenset({"production", "prod"})


class DefaultWebConfig:
    APP_ENV = "development"
    SECRET_KEY = DEVELOPMENT_SECRET_KEY
    EXAMPLES_DIR = resolve_examples_dir()
    WORLDS_DIR = resolve_worlds_dir()
    IMAGE_ASSETS_DIR = resolve_image_assets_dir()
    SESSION_IDLE_TIMEOUT_MIN = 45
    MAX_ACTIVE_SESSIONS = 20
    MAX_RUNNING_SIMULATIONS = 8
    SCRIPT_MAX_RUNTIME_S = 120.0
    MAX_SCRIPT_SIZE_BYTES = 128 * 1024
    MAX_WORLD_JSON_SIZE_BYTES = 2 * 1024 * 1024
    SSE_HEARTBEAT_S = 15
    # El motor conserva sus 50 Hz autoritativos. La Web recibe 30 Hz y
    # renderiza los fotogramas intermedios con requestAnimationFrame: así se
    # evita saturar el IPC del worker sin que el movimiento se perciba a saltos.
    WEB_SNAPSHOT_MAX_HZ = 30.0
    START_IDEMPOTENCY_TTL_S = 20.0
    STATIC_ASSET_VERSION = WEB_ASSET_VERSION
    SESSION_CLEANUP_INTERVAL_S = 60
    ENABLE_SESSION_CLEANUP_THREAD = True
    ENABLE_SECURITY_HEADERS = True
    SESSION_COOKIE_SECURE = False
    SESSION_BACKEND = "memory"
    REDIS_ENABLED = False
    REDIS_URL = ""
    REDIS_PREFIX = "ev3web"
    REDIS_CONNECT_TIMEOUT_S = 0.2
    REDIS_SOCKET_TIMEOUT_S = 0.2
    REDIS_HEALTHCHECK_PING = False
    FILE_MIRROR_ENABLED = True
    FILE_MIRROR_DIR = Path(tempfile.gettempdir()) / "ev3web_session_mirror"
    UI_FIT_PADDING_RATIO = UI_FIT_PADDING_RATIO
    SENSOR_BEAMS_ENABLED = True
    DEBUGSTATE_V2_ENABLED = True
    WEB_DEBUGSTATE_V2 = True
    TK_DEBUGSTATE_V2 = True
    WEB_SSE_ENABLED = True
    WEB_POLLING_INTERVAL_MS = 900
    WEB_SESSION_CREATE_WAIT_MS = 0


_ENV_OVERRIDES: dict[str, Callable[[str], Any]] = {
    "APP_ENV": str,
    "SECRET_KEY": str,
    "EXAMPLES_DIR": Path,
    "WORLDS_DIR": Path,
    "IMAGE_ASSETS_DIR": Path,
    "SESSION_IDLE_TIMEOUT_MIN": int,
    "MAX_ACTIVE_SESSIONS": int,
    "MAX_RUNNING_SIMULATIONS": int,
    "SCRIPT_MAX_RUNTIME_S": float,
    "MAX_SCRIPT_SIZE_BYTES": int,
    "MAX_WORLD_JSON_SIZE_BYTES": int,
    "SSE_HEARTBEAT_S": int,
    "WEB_SNAPSHOT_MAX_HZ": float,
    "START_IDEMPOTENCY_TTL_S": float,
    "STATIC_ASSET_VERSION": str,
    "SESSION_CLEANUP_INTERVAL_S": float,
    "ENABLE_SESSION_CLEANUP_THREAD": lambda value: _parse_bool(value),
    "ENABLE_SECURITY_HEADERS": lambda value: _parse_bool(value),
    "SESSION_COOKIE_SECURE": lambda value: _parse_bool(value),
    "SESSION_BACKEND": str,
    "REDIS_ENABLED": lambda value: _parse_bool(value),
    "REDIS_URL": str,
    "REDIS_PREFIX": str,
    "REDIS_CONNECT_TIMEOUT_S": float,
    "REDIS_SOCKET_TIMEOUT_S": float,
    "REDIS_HEALTHCHECK_PING": lambda value: _parse_bool(value),
    "FILE_MIRROR_ENABLED": lambda value: _parse_bool(value),
    "FILE_MIRROR_DIR": Path,
    "UI_FIT_PADDING_RATIO": float,
    "SENSOR_BEAMS_ENABLED": lambda value: _parse_bool(value),
    "DEBUGSTATE_V2_ENABLED": lambda value: _parse_bool(value),
    "WEB_DEBUGSTATE_V2": lambda value: _parse_bool(value),
    "TK_DEBUGSTATE_V2": lambda value: _parse_bool(value),
    "WEB_SSE_ENABLED": lambda value: _parse_bool(value),
    "WEB_POLLING_INTERVAL_MS": int,
    "WEB_SESSION_CREATE_WAIT_MS": int,
}


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Valor booleano invalido: {value}")


def apply_env_overrides(config: dict[str, Any]) -> None:
    """Apply EV3 web configuration from environment variables."""

    for key, caster in _ENV_OVERRIDES.items():
        env_key = f"EV3_WEB_{key}"
        raw = os.environ.get(env_key)
        if raw is None:
            continue
        config[key] = caster(raw)


def is_production(config: dict[str, Any]) -> bool:
    """Return whether the effective configuration targets a production deployment."""

    environment = str(config.get("APP_ENV", "development")).strip().lower()
    return environment in PRODUCTION_ENVIRONMENTS


def validate_runtime_config(config: dict[str, Any]) -> None:
    """Valida límites seguros de transporte y, en producción, de seguridad."""
    problems: list[str] = []
    try:
        snapshot_hz = float(config.get("WEB_SNAPSHOT_MAX_HZ", 0.0))
    except (TypeError, ValueError):
        snapshot_hz = 0.0
    if not 10.0 <= snapshot_hz <= 60.0:
        problems.append("EV3_WEB_WEB_SNAPSHOT_MAX_HZ debe estar entre 10 y 60")

    if not is_production(config):
        if problems:
            raise RuntimeError("Configuracion Web invalida: " + "; ".join(problems))
        return

    secret_key = str(config.get("SECRET_KEY", ""))
    if secret_key == DEVELOPMENT_SECRET_KEY or len(secret_key) < 32:
        problems.append("EV3_WEB_SECRET_KEY debe ser distinta de la clave de desarrollo y tener al menos 32 caracteres")

    try:
        timeout_s = float(config.get("SCRIPT_MAX_RUNTIME_S", 0.0))
    except (TypeError, ValueError):
        timeout_s = 0.0
    if timeout_s <= 0:
        problems.append("EV3_WEB_SCRIPT_MAX_RUNTIME_S debe ser un valor positivo")

    if not bool(config.get("SESSION_COOKIE_SECURE", False)):
        problems.append("EV3_WEB_SESSION_COOKIE_SECURE debe ser true en produccion HTTPS")

    if problems:
        raise RuntimeError("Configuracion de produccion invalida: " + "; ".join(problems))
