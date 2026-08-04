"""Catálogo didáctico compartido por las interfaces Web y Tkinter.

La ayuda de usuario se modela como datos para impedir que cada interfaz anuncie
acciones o use terminología distinta. El manual técnico queda fuera de este
catálogo: solo se enlaza cuando la persona lo necesita explícitamente.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HelpGuide:
    """Guía breve, orientada a una tarea real del simulador."""

    identifier: str
    title: str
    category: str
    summary: str
    destination: str
    image_name: str
    image_alt: str
    minutes: int
    audience: tuple[str, ...]
    keywords: tuple[str, ...]
    prerequisites: tuple[str, ...]
    steps: tuple[str, ...]
    expected_result: str
    recovery: str
    related: tuple[str, ...] = ()


# Conserva el nombre público utilizado por integraciones y pruebas previas.
HelpTutorial = HelpGuide


HELP_CATEGORIES: tuple[tuple[str, str], ...] = (
    ("empezar", "Empezar"),
    ("simular", "Simular"),
    ("mundos", "Crear mundos"),
    ("programar", "Programar"),
    ("depurar", "Depurar"),
    ("resolver", "Resolver problemas"),
)


HELP_GUIDES: tuple[HelpGuide, ...] = (
    HelpGuide(
        identifier="first-simulation",
        title="Mi primera simulación",
        category="empezar",
        summary="Carga un ejemplo, elige un mundo y observa al robot ejecutar su programa.",
        destination="simulation",
        image_name="tutorial_simulacion.svg",
        image_alt="Controles de ejecución, canvas y telemetría de una simulación",
        minutes=3,
        audience=("estudiante", "docente"),
        keywords=("inicio", "ejecutar", "ejemplo", "robot"),
        prerequisites=("Tener abierta la pantalla de Simulación.",),
        steps=(
            "Abre un ejemplo desde el menú Ejemplos.",
            "Selecciona un mundo desde el menú Mundos.",
            "Pulsa Ejecutar y observa el canvas, la telemetría y la pantalla LCD.",
            "Cuando finalice, usa Detener y reiniciar antes de realizar una nueva prueba.",
        ),
        expected_result="El robot se mueve según el script y todos los paneles muestran el mismo estado final.",
        recovery="Si no inicia, confirma que hay un mundo cargado y revisa el mensaje del editor.",
        related=("run-simulation", "recover-script-error"),
    ),
    HelpGuide(
        identifier="create-world",
        title="Crear un mundo con obstáculos",
        category="mundos",
        summary="Construye, valida y guarda un mundo antes de usarlo en simulación.",
        destination="worlds",
        image_name="tutorial_mundo.svg",
        image_alt="Pasos para crear, validar y guardar un mundo con el editor",
        minutes=5,
        audience=("estudiante", "docente"),
        keywords=("mundo", "obstáculo", "guardar", "validar", "robot"),
        prerequisites=("Abrir el Editor de mundos.",),
        steps=(
            "Selecciona un asset de obstáculo o línea y colócalo con clic en el canvas.",
            "Ubica el robot en una posición inicial libre y define su orientación.",
            "Pulsa Validar y corrige cualquier error indicado.",
            "Pulsa Guardar como para exportar el mundo JSON.",
        ),
        expected_result="El mundo queda guardado y puede cargarse desde el menú Mundos de Simulación.",
        recovery="Revisa los elementos superpuestos, la pose inicial y las validaciones antes de guardar.",
        related=("first-simulation", "recover-world-validation"),
    ),
    HelpGuide(
        identifier="run-simulation",
        title="Ejecutar, pausar y reiniciar",
        category="simular",
        summary="Controla una ejecución sin perder el estado visual del mundo ni del robot.",
        destination="simulation",
        image_name="tutorial_simulacion.svg",
        image_alt="Barra de controles de simulación con ejecutar, pausar y reiniciar",
        minutes=3,
        audience=("estudiante", "docente"),
        keywords=("ejecutar", "pausar", "reanudar", "reiniciar", "tiempo máximo"),
        prerequisites=("Tener un script y un mundo cargados.",),
        steps=(
            "Pulsa Ejecutar para iniciar el script.",
            "Usa Pausar para detener el avance temporalmente y Reanudar para continuarlo.",
            "Usa Detener y reiniciar para cancelar la ejecución y volver al inicio del mundo activo.",
        ),
        expected_result=(
            "Los botones cambian de estado correctamente y canvas, LCD y telemetría "
            "permanecen sincronizados."
        ),
        recovery="Si el programa tarda demasiado, ajusta Tiempo máximo o detenlo manualmente con Detener y reiniciar.",
        related=("first-simulation", "recover-script-error"),
    ),
    HelpGuide(
        identifier="use-sensors",
        title="Usar motores y sensores",
        category="programar",
        summary="Comprueba puertos, movimientos y lecturas en la telemetría durante una simulación.",
        destination="simulation",
        image_name="tutorial_simulacion.svg",
        image_alt="Telemetría de motores y sensores conectados al robot EV3",
        minutes=5,
        audience=("estudiante", "docente"),
        keywords=("motor", "sensor", "ultrasónico", "táctil", "puerto", "telemetría"),
        prerequisites=("Tener un mundo con los sensores requeridos y un script Pybricks abierto.",),
        steps=(
            "Conecta cada motor o sensor al puerto indicado en el script.",
            "Ejecuta el programa y observa el bloque correspondiente de telemetría.",
            "Compara el valor del sensor con su posición y los obstáculos del canvas.",
        ),
        expected_result="Los motores informan velocidad, ángulo y estado; los sensores muestran tipo y lectura actual.",
        recovery="Si aparece Sin conectar, revisa el puerto configurado en el script y en el mundo.",
        related=("run-simulation", "recover-script-error"),
    ),
    HelpGuide(
        identifier="debug-script",
        title="Depurar un programa paso a paso",
        category="depurar",
        summary="Usa breakpoints, Paso y Continuar para encontrar dónde se detiene el código.",
        destination="debug",
        image_name="tutorial_debug.svg",
        image_alt="Depuración con breakpoints y ejecución paso a paso",
        minutes=5,
        audience=("estudiante", "docente"),
        keywords=("depurar", "breakpoint", "paso", "continuar", "error"),
        prerequisites=("Tener un script y un mundo cargados en Simulación.",),
        steps=(
            "Haz clic en el margen del editor para poner un breakpoint.",
            "Ejecuta el script en modo Depurar.",
            "Usa Continuar o Paso para inspeccionar el flujo.",
            "Usa Ctrl+Espacio para consultar las APIs Pybricks compatibles.",
        ),
        expected_result="Puedes identificar la línea exacta donde se pausa o falla el programa.",
        recovery="Limpia los breakpoints y vuelve a ejecutar desde el inicio si necesitas repetir la prueba.",
        related=("recover-script-error", "run-simulation"),
    ),
    HelpGuide(
        identifier="recover-script-error",
        title="Resolver un error de programa",
        category="resolver",
        summary="Distingue un error de sintaxis, un puerto no conectado, un límite de tiempo y una detención manual.",
        destination="simulation",
        image_name="tutorial_debug.svg",
        image_alt="Editor mostrando un error y controles para recuperar la simulación",
        minutes=3,
        audience=("estudiante", "docente"),
        keywords=("error", "sintaxis", "puerto", "tiempo", "detener", "recuperar"),
        prerequisites=("Haber intentado ejecutar un programa.",),
        steps=(
            "Lee el mensaje mostrado en el editor o en el estado de la simulación.",
            "Corrige la línea indicada o revisa el puerto y el mundo activo.",
            "Pulsa Detener y reiniciar para limpiar el estado anterior.",
            "Ejecuta de nuevo y comprueba que el estado global sea Finalizado o IDLE.",
        ),
        expected_result=(
            "La simulación vuelve a un estado coherente y el error no se confunde "
            "con una finalización correcta."
        ),
        recovery="Si el problema continúa, abre la guía de depuración y ejecuta el programa por pasos.",
        related=("debug-script", "run-simulation"),
    ),
    HelpGuide(
        identifier="recover-world-validation",
        title="Resolver validaciones del mundo",
        category="resolver",
        summary="Corrige un mundo incompleto o inválido antes de cargarlo en simulación.",
        destination="worlds",
        image_name="tutorial_mundo.svg",
        image_alt="Editor de mundos con validación de elementos y pose inicial",
        minutes=3,
        audience=("estudiante", "docente"),
        keywords=("validación", "mundo", "pose", "obstáculo", "guardar"),
        prerequisites=("Tener abierto el Editor de mundos.",),
        steps=(
            "Abre el detalle de la validación y localiza el elemento señalado.",
            "Corrige propiedades, superposiciones o la posición inicial del robot.",
            "Vuelve a pulsar Validar antes de guardar.",
        ),
        expected_result="El editor confirma que el mundo se puede guardar y cargar en Simulación.",
        recovery="Si no sabes qué modificar, selecciona el elemento y revisa sus propiedades antes de eliminarlo.",
        related=("create-world", "first-simulation"),
    ),
)

# Alias compatible con consumidores existentes. A partir de ahora contiene todo
# el catálogo de guías, no solo tres tarjetas aisladas.
HELP_TUTORIALS = HELP_GUIDES


def guide_by_id(identifier: str) -> HelpGuide:
    """Devuelve una guía estable o informa un identificador inválido."""

    for guide in HELP_GUIDES:
        if guide.identifier == identifier:
            return guide
    raise KeyError(f"Guía de ayuda desconocida: {identifier}")


def tutorial_by_id(identifier: str) -> HelpGuide:
    """Alias compatible de :func:`guide_by_id`."""

    return guide_by_id(identifier)


def guides_for_category(category: str) -> tuple[HelpGuide, ...]:
    """Devuelve las guías de una categoría conocida, en orden didáctico."""

    return tuple(guide for guide in HELP_GUIDES if guide.category == category)


def search_guides(query: str) -> tuple[HelpGuide, ...]:
    """Busca sin distinguir mayúsculas en contenido visible de las guías."""

    normalized = " ".join(query.casefold().split())
    if not normalized:
        return HELP_GUIDES
    return tuple(
        guide
        for guide in HELP_GUIDES
        if normalized
        in " ".join(
            (
                guide.title,
                guide.summary,
                *guide.keywords,
                *guide.steps,
            )
        ).casefold()
    )
