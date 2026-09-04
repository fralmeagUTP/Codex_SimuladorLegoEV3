"""Rutas didácticas versionadas y compartidas entre Web y Tkinter."""

from dataclasses import dataclass

LEARNING_CATALOG_VERSION = 1


@dataclass(frozen=True)
class LearningRoute:
    """Actividad guiada con evidencia observable en el simulador."""

    identifier: str
    title: str
    objective: str
    prerequisites: tuple[str, ...]
    guide_ids: tuple[str, ...]
    example_files: tuple[str, ...]
    practice: str
    success_criteria: tuple[str, ...]
    recovery: str


LEARNING_ROUTES: tuple[LearningRoute, ...] = (
    LearningRoute(
        identifier="first-simulation",
        title="Primera simulación",
        objective="Ejecutar un ejemplo y relacionar el estado del robot con canvas, telemetría y LCD.",
        prerequisites=("Tener abierta la pantalla de Simulación.",),
        guide_ids=("first-simulation", "run-simulation"),
        example_files=("01_intro_led.py", "02_intro_pantalla_altavoz.py"),
        practice="Cargue un ejemplo, ejecútelo y reinicie el mundo al finalizar.",
        success_criteria=(
            "El estado final es Finalizado sin error.",
            "Canvas, telemetría y pantalla LCD muestran el mismo resultado terminal.",
        ),
        recovery="Revise el mensaje del editor, cargue un mundo y vuelva a ejecutar desde el inicio.",
    ),
    LearningRoute(
        identifier="motors-and-sensors",
        title="Motores y sensores",
        objective="Comparar movimientos y lecturas de sensores con los elementos del mundo activo.",
        prerequisites=("Completar Primera simulación.", "Tener un mundo con obstáculos o líneas."),
        guide_ids=("use-sensors", "run-simulation"),
        example_files=("03_movimiento_basico.py", "08_sensor_ultrasonido_frenado.py"),
        practice="Ejecute un ejemplo de movimiento y describa el cambio observado en motor y sensor.",
        success_criteria=(
            "La telemetría presenta puertos y lecturas esperadas.",
            "La posición visual del robot concuerda con la telemetría.",
        ),
        recovery="Confirme los puertos del script y el tipo de sensor configurado en el mundo.",
    ),
    LearningRoute(
        identifier="debug-and-recovery",
        title="Depuración y recuperación",
        objective="Usar breakpoints y mensajes de error para corregir un programa sin perder el estado de la sesión.",
        prerequisites=("Completar Primera simulación.",),
        guide_ids=("debug-script", "recover-script-error"),
        example_files=("11_siguelineas_basico.py",),
        practice="Añada un breakpoint, avance por pasos y reinicie tras una detención manual.",
        success_criteria=(
            "La pausa de depuración identifica una línea y permite continuar.",
            "Detener y reiniciar restaura la pose inicial del mundo activo.",
        ),
        recovery="Limpie los breakpoints, revise el error del editor y repita la ejecución desde el inicio.",
    ),
)


def route_by_id(identifier: str) -> LearningRoute:
    """Obtiene una ruta estable o informa un identificador inválido."""

    for route in LEARNING_ROUTES:
        if route.identifier == identifier:
            return route
    raise KeyError(f"Ruta de aprendizaje desconocida: {identifier}")


def initial_learning_route() -> LearningRoute:
    """Ruta que ambas interfaces presentan cuando aún no hay misión activa."""

    return route_by_id("first-simulation")
