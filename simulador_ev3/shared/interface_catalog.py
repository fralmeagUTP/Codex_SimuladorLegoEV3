"""Vocabulario versionado que las dos interfaces usan para la sesion.

No contiene widgets: centraliza estados, disponibilidad de controles, mensajes,
atajos, validaciones y rutas de recuperacion para que Web y Tkinter no diverjan
al traducir la misma sesion de simulacion.
"""

from __future__ import annotations

INTERFACE_CATALOG_VERSION = 1

SESSION_STATE_MESSAGES = {
    "created": "Prepare un programa o un mundo para comenzar.",
    "ready": "Listo para ejecutar.",
    "running": "Programa en ejecucion.",
    "paused": "Programa pausado.",
    "finished": "El programa se ejecuto correctamente.",
    "stopped": "Ejecucion detenida y reiniciada.",
    "error": "El programa termino con un error.",
    "timed_out": "El programa supero el tiempo maximo configurado.",
    "resetting": "Restaurando el estado inicial del mundo.",
    "expired": "La sesion expiro; cree una nueva sesion.",
}

# Etiquetas de usuario: el valor técnico de ``SessionStatus`` se conserva en
# API, trazas y atributos de diagnóstico, mientras las dos interfaces muestran
# el mismo vocabulario pedagógico localizado.
SESSION_STATUS_LABELS = {
    "created": "Listo",
    "ready": "Listo",
    "started": "Ejecutando",
    "running": "Ejecutando",
    "resumed": "Ejecutando",
    "paused": "Pausado",
    "finished": "Finalizado",
    "stopped": "Detenido",
    "timed_out": "Tiempo agotado",
    "error": "Error",
    "reset": "Listo",
    "resetting": "Reiniciando",
    "world_loaded": "Listo",
    "expired": "Sesión expirada",
}

KEYBOARD_SHORTCUTS = {
    "run": "F5",
    "pause_resume": "F6",
    "stop_reset": "Shift+F5",
    "help": "F1",
    "close_dialog": "Escape",
}

# Opciones publicadas por el menú de ambas interfaces. El cero representa el
# modo sin límite, que conserva la posibilidad de detención manual.
RUNTIME_LIMIT_OPTIONS = (0.0, 30.0, 60.0, 120.0, 300.0)


def is_supported_runtime_limit(value: float) -> bool:
    """Indica si un valor pertenece al contrato visible de tiempo máximo."""

    return float(value) in RUNTIME_LIMIT_OPTIONS

NAVIGATION_MENU = {
    "file": "Archivo",
    "learn": "Aprender",
    "worlds": "Mundos",
    "guided_practice": "Prácticas guiadas",
    "settings": "Configuración",
    "diagnostics": "Diagnóstico",
    "help": "Ayuda",
}

NAVIGATION_MENU_DESCRIPTIONS = {
    "file": "Crear, abrir y guardar programas.",
    "learn": "Programas organizados para aprender robótica paso a paso.",
    "worlds": "Crear, importar y seleccionar entornos de simulación.",
    "guided_practice": "Actividades con objetivo, mundo y programa; incluye retos evaluables con progreso.",
    "settings": "Ajustes visuales y de comportamiento de la simulación.",
    "diagnostics": "Herramientas para revisar el estado técnico y exportar evidencia.",
    "help": "Guías, referencias e información sobre BotLab Studio.",
}

NAVIGATION_MENU_ICONS = {
    "file": "file",
    "learn": "book",
    "worlds": "map",
    "guided_practice": "route",
    "settings": "settings",
    "diagnostics": "stethoscope",
    "help": "help",
}

# Las claves antiguas se conservan únicamente para redireccionar enlaces y
# pruebas de compatibilidad durante la migración de la interfaz.
LEGACY_NAVIGATION_CATEGORY_MAP = {
    "Ejemplos": "learn",
    "Escenarios": "guided_practice",
    "Tema": "settings",
    "Fidelidad": "settings",
    "Tiempo máximo": "settings",
    "Trazas": "diagnostics",
}

# Orden visible común para la Web y la aplicación de escritorio.
NAVIGATION_MENU_ORDER = tuple(NAVIGATION_MENU.values())

VALIDATION_MESSAGES = {
    "script_required": "No hay script cargado para ejecutar.",
    "world_name_required": "El nombre del mundo es requerido.",
    "invalid_coordinates": "Las coordenadas deben ser numericas y validas.",
}

RECOVERY_ROUTES = {
    "error": "Revise el editor, corrija el programa y vuelva a ejecutar.",
    "timed_out": "Aumente el tiempo maximo o detenga y reinicie el programa.",
    "expired": "Recargue la aplicacion y restaure o cree una sesion.",
}


def controls_for_status(status: str) -> dict[str, bool]:
    normalized = str(status).strip().lower()
    running = normalized == "running"
    paused = normalized == "paused"
    return {
        "run": not running and not paused,
        "pause": running,
        "resume": paused,
        "stop_reset": running or paused,
    }


def message_for_status(status: str) -> str:
    return SESSION_STATE_MESSAGES.get(str(status).strip().lower(), "Estado de simulacion actualizado.")


def label_for_status(status: str) -> str:
    """Devuelve la etiqueta localizada sin cambiar el estado técnico."""

    normalized = str(status).strip().lower()
    return SESSION_STATUS_LABELS.get(normalized, normalized.replace("_", " ").capitalize())
