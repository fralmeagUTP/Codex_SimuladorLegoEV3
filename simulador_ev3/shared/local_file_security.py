"""Controles comunes para archivos elegidos en la interfaz de escritorio."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Iterable

MAX_SCRIPT_FILE_BYTES = 512 * 1024
MAX_WORLD_FILE_BYTES = 2 * 1024 * 1024
MAX_EXPORT_FILE_BYTES = 8 * 1024 * 1024


class LocalFileSecurityError(ValueError):
    """Error de validacion apto para presentar al usuario final."""


def safe_desktop_error(error: Exception, fallback: str) -> str:
    """Evita que la UI presente rutas, trazas, tokens o fuente del usuario."""

    detail = str(error).strip()
    lowered = detail.lower()
    sensitive_markers = ("traceback", "token", "secret", "password", "\\", "/", "\n", "\r")
    if not detail or len(detail) > 240 or any(marker in lowered for marker in sensitive_markers):
        return fallback
    return detail


def _normalised_suffixes(allowed_suffixes: Iterable[str]) -> frozenset[str]:
    return frozenset(suffix.lower() if suffix.startswith(".") else f".{suffix.lower()}" for suffix in allowed_suffixes)


def validate_open_file(path: str | Path, *, allowed_suffixes: Iterable[str], max_bytes: int) -> Path:
    """Devuelve un archivo existente seguro para lectura limitada."""

    try:
        resolved = Path(path).expanduser().resolve(strict=True)
    except OSError as exc:
        raise LocalFileSecurityError("El archivo seleccionado no esta disponible.") from exc
    if not resolved.is_file():
        raise LocalFileSecurityError("Seleccione un archivo valido.")
    if resolved.suffix.lower() not in _normalised_suffixes(allowed_suffixes):
        raise LocalFileSecurityError("El tipo de archivo seleccionado no esta permitido.")
    try:
        size = resolved.stat().st_size
    except OSError as exc:
        raise LocalFileSecurityError("No fue posible comprobar el archivo seleccionado.") from exc
    if size > max_bytes:
        raise LocalFileSecurityError("El archivo seleccionado supera el tamano permitido.")
    return resolved


def read_text_limited(path: str | Path, *, allowed_suffixes: Iterable[str], max_bytes: int) -> tuple[Path, str]:
    resolved = validate_open_file(path, allowed_suffixes=allowed_suffixes, max_bytes=max_bytes)
    try:
        return resolved, resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise LocalFileSecurityError("No fue posible leer el archivo seleccionado como texto UTF-8.") from exc


def validate_save_path(path: str | Path, *, allowed_suffixes: Iterable[str]) -> Path:
    candidate = Path(path).expanduser()
    if candidate.suffix.lower() not in _normalised_suffixes(allowed_suffixes):
        raise LocalFileSecurityError("El tipo de archivo de destino no esta permitido.")
    try:
        parent = candidate.parent.resolve(strict=True)
    except OSError as exc:
        raise LocalFileSecurityError("La carpeta de destino no esta disponible.") from exc
    if not parent.is_dir():
        raise LocalFileSecurityError("Seleccione una carpeta de destino valida.")
    return parent / candidate.name


def write_text_atomically(
    path: str | Path,
    text: str,
    *,
    allowed_suffixes: Iterable[str],
    max_bytes: int = MAX_EXPORT_FILE_BYTES,
) -> Path:
    """Guarda texto limitado mediante reemplazo atomico."""

    encoded = text.encode("utf-8")
    if len(encoded) > max_bytes:
        raise LocalFileSecurityError("El contenido a guardar supera el tamano permitido.")
    destination = validate_save_path(path, allowed_suffixes=allowed_suffixes)
    fd: int | None = None
    tmp_name: str | None = None
    try:
        fd, tmp_name = tempfile.mkstemp(prefix=".ev3-save-", suffix=".tmp", dir=destination.parent)
        with os.fdopen(fd, "wb") as handle:
            fd = None
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, destination)
        tmp_name = None
        return destination
    except OSError as exc:
        raise LocalFileSecurityError("No fue posible guardar el archivo seleccionado.") from exc
    finally:
        if fd is not None:
            os.close(fd)
        if tmp_name is not None:
            try:
                Path(tmp_name).unlink(missing_ok=True)
            except OSError:
                pass
