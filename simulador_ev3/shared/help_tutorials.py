"""Contenido didáctico compartido por las interfaces Web y Tkinter."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HelpTutorial:
    """Tutorial de una tarea clave del simulador."""

    identifier: str
    title: str
    destination: str
    image_name: str
    image_alt: str
    steps: tuple[str, ...]
    expected_result: str
    recovery: str


HELP_TUTORIALS: tuple[HelpTutorial, ...] = (
    HelpTutorial(
        identifier="create-world",
        title="Tutorial A: Crear tu primer mundo",
        destination="worlds",
        image_name="tutorial_mundo.svg",
        image_alt="Pasos para crear, validar y guardar un mundo",
        steps=(
            "Abre la sección Mundos.",
            "Selecciona muros o líneas y colócalos con clic en el canvas.",
            "Pulsa Validar.",
            "Pulsa Guardar como y guarda el archivo JSON.",
        ),
        expected_result="El mundo queda exportado como .json.",
        recovery="Revisa las validaciones pendientes y corrige el mundo antes de guardarlo.",
    ),
    HelpTutorial(
        identifier="run-simulation",
        title="Tutorial B: Ejecutar un script en simulación",
        destination="simulation",
        image_name="tutorial_simulacion.svg",
        image_alt="Vista guiada de simulación con controles y telemetría",
        steps=(
            "Abre la sección Simulación.",
            "Abre un ejemplo desde el menú Ejemplos.",
            "Selecciona un mundo desde el menú Mundos.",
            "Pulsa Ejecutar y observa la telemetría.",
        ),
        expected_result="El robot cambia estado y se ven datos de sensores, motores y altavoz EV3.",
        recovery="Confirma que hay un mundo cargado y que el script no contiene errores de sintaxis.",
    ),
    HelpTutorial(
        identifier="debug-script",
        title="Tutorial C: Depurar por pasos",
        destination="debug",
        image_name="tutorial_debug.svg",
        image_alt="Depuración con breakpoints y ejecución paso a paso",
        steps=(
            "En Simulación, haz clic en el margen del editor para poner breakpoints.",
            "Ejecuta el script en modo Depurar.",
            "Usa Continuar o Paso para inspeccionar el flujo.",
            "Usa Ctrl+Espacio para consultar APIs Pybricks.",
        ),
        expected_result="Puedes identificar la línea exacta donde se detiene o falla el código.",
        recovery="Limpia los breakpoints y vuelve a ejecutar desde el inicio.",
    ),
)


def tutorial_by_id(identifier: str) -> HelpTutorial:
    """Devuelve un tutorial estable o informa un identificador inválido."""

    for tutorial in HELP_TUTORIALS:
        if tutorial.identifier == identifier:
            return tutorial
    raise KeyError(f"Tutorial de ayuda desconocido: {identifier}")
