"""Shared UI behavior settings for desktop and web adapters."""

from __future__ import annotations

import json
import os
from pathlib import Path

UI_FIT_PADDING_RATIO = 0.05
UI_THEMES = frozenset({"light", "dark"})
DEFAULT_UI_THEME = "light"


def ui_settings_path() -> Path:
    """Ubicación local de preferencias de la interfaz de escritorio."""

    configured = os.environ.get("EV3_UI_SETTINGS_PATH")
    if configured:
        return Path(configured)
    base = Path(os.environ.get("APPDATA") or Path.home())
    return base / "SimuladorEV3" / "ui_settings.json"


def load_ui_theme() -> str:
    """Recupera el tema persistido, sin impedir el arranque si el archivo falla."""

    try:
        payload = json.loads(ui_settings_path().read_text(encoding="utf-8"))
        theme = str(payload.get("theme", DEFAULT_UI_THEME)).strip().lower()
        return theme if theme in UI_THEMES else DEFAULT_UI_THEME
    except (OSError, ValueError, TypeError):
        return DEFAULT_UI_THEME


def save_ui_theme(theme: str) -> str:
    """Guarda una preferencia válida y devuelve su valor normalizado."""

    normalized = str(theme).strip().lower()
    if normalized not in UI_THEMES:
        raise ValueError(f"Tema no soportado: {theme}")
    path = ui_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"theme": normalized}), encoding="utf-8")
    return normalized


def load_desktop_session() -> dict:
    """Devuelve el último contexto local recuperable, o un diccionario vacío."""

    try:
        payload = json.loads(ui_settings_path().read_text(encoding="utf-8"))
        session = payload.get("desktop_session", {})
        return dict(session) if isinstance(session, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def save_desktop_session(session: dict) -> None:
    """Persiste sólo datos de UI seguros para reanudar la preparación local."""

    path = ui_settings_path()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        payload = {}
    payload["desktop_session"] = dict(session)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
