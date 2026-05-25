"""Configuration defaults for the Flask web application."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

from simulador_ev3.shared.paths import (
    resolve_examples_dir,
    resolve_image_assets_dir,
    resolve_worlds_dir,
)
from simulador_ev3.shared.ui_settings import UI_FIT_PADDING_RATIO


class DefaultWebConfig:
    SECRET_KEY = "dev-simulador-ev3"
    EXAMPLES_DIR = resolve_examples_dir()
    WORLDS_DIR = resolve_worlds_dir()
    IMAGE_ASSETS_DIR = resolve_image_assets_dir()
    SESSION_IDLE_TIMEOUT_MIN = 30
    MAX_ACTIVE_SESSIONS = 20
    MAX_RUNNING_SIMULATIONS = 8
    SCRIPT_MAX_RUNTIME_S = 0.0
    MAX_SCRIPT_SIZE_BYTES = 128 * 1024
    MAX_WORLD_JSON_SIZE_BYTES = 2 * 1024 * 1024
    SSE_HEARTBEAT_S = 15
    WEB_SNAPSHOT_MAX_HZ = 12.0
    STATIC_ASSET_VERSION = "2026-05-24-responsive-audit-v5"
    SESSION_CLEANUP_INTERVAL_S = 60
    ENABLE_SESSION_CLEANUP_THREAD = True
    ENABLE_SECURITY_HEADERS = True
    SESSION_COOKIE_SECURE = False
    UI_FIT_PADDING_RATIO = UI_FIT_PADDING_RATIO
    DEBUGSTATE_V2_ENABLED = True
    WEB_DEBUGSTATE_V2 = True
    TK_DEBUGSTATE_V2 = True


_ENV_OVERRIDES: dict[str, Callable[[str], Any]] = {
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
    "STATIC_ASSET_VERSION": str,
    "SESSION_CLEANUP_INTERVAL_S": float,
    "ENABLE_SESSION_CLEANUP_THREAD": lambda value: _parse_bool(value),
    "ENABLE_SECURITY_HEADERS": lambda value: _parse_bool(value),
    "SESSION_COOKIE_SECURE": lambda value: _parse_bool(value),
    "UI_FIT_PADDING_RATIO": float,
    "DEBUGSTATE_V2_ENABLED": lambda value: _parse_bool(value),
    "WEB_DEBUGSTATE_V2": lambda value: _parse_bool(value),
    "TK_DEBUGSTATE_V2": lambda value: _parse_bool(value),
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
