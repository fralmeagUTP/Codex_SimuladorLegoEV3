"""Contrato compartido para configuración de depuración de las interfaces."""

from __future__ import annotations

MAX_DEBUG_WATCHES = 20
MAX_DEBUG_WATCH_LENGTH = 200


def normalize_breakpoints(values) -> set[int]:
    """Convierte valores de UI en líneas positivas únicas."""

    result: set[int] = set()
    for value in values or ():
        try:
            line = int(value)
        except (TypeError, ValueError):
            continue
        if line > 0:
            result.add(line)
    return result


def normalize_watches(values) -> list[str]:
    """Aplica los límites compartidos de expresiones watch."""

    result: list[str] = []
    for value in list(values or ())[:MAX_DEBUG_WATCHES]:
        expression = str(value).strip()
        if expression and len(expression) <= MAX_DEBUG_WATCH_LENGTH:
            result.append(expression)
    return result
