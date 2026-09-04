"""Shared route helpers."""

from __future__ import annotations

from pathlib import Path

from flask import current_app, request

from simulador_ev3.web.errors import InvalidPayload


def get_manager():
    return current_app.extensions["session_manager"]


def request_token() -> str | None:
    prefix = str(current_app.config.get("SESSION_COOKIE_PREFIX", "ev3_"))
    return request.headers.get("X-Session-Token") or request.cookies.get(f"{prefix}owner_token")


def require_session(session_id: str):
    return get_manager().get_session(session_id, request_token())


def json_body() -> dict:
    data = request.get_json(silent=True)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise InvalidPayload("El cuerpo JSON debe ser un objeto.")
    return data


def safe_child(base: Path, name: str, suffix: str) -> Path:
    if not name or any(part in name for part in ("..", "/", "\\")):
        raise InvalidPayload("Nombre de archivo invalido.")
    path = base / name
    if path.suffix.lower() != suffix.lower() or not path.exists() or not path.is_file():
        raise InvalidPayload("Archivo no encontrado.")
    return path
