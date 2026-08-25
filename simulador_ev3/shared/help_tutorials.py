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


@dataclass(frozen=True)
class HelpReference:
    """Documento o referencia que las dos interfaces presentan con el mismo nombre."""

    identifier: str
    title: str
    summary: str
    filename: str
    audience: tuple[str, ...]


@dataclass(frozen=True)
class GlossaryTerm:
    """Término breve que evita que Web y escritorio expliquen Pybricks distinto."""

    identifier: str
    term: str
    definition: str


@dataclass(frozen=True)
class HelpMenuAction:
    """Comando de ayuda común; evita rótulos distintos entre interfaces."""

    identifier: str
    label: str
    guide_id: str | None = None
    external_url: str | None = None


@dataclass(frozen=True)
class TeacherRoute:
    """Plan breve para que un docente acompañe una práctica verificable."""

    title: str
    objective: str
    minutes: int
    guide_ids: tuple[str, ...]
    suggested_evidence: str
    physical_robot_warning: str


# Conserva el nombre público utilizado por integraciones y pruebas previas.
HelpTutorial = HelpGuide


HELP_MENU_ACTIONS: tuple[HelpMenuAction, ...] = (
    HelpMenuAction("help-center", "Centro de ayuda"),
    HelpMenuAction("quick-first-simulation", "Guía rápida: primera simulación", "first-simulation"),
    HelpMenuAction("session-diagnostics", "Diagnóstico de sesión"),
    HelpMenuAction("export-diagnostics", "Exportar diagnóstico JSON"),
    HelpMenuAction(
        "lego-ev3-book",
        "Libro: Programación en Python para robótica (LEGO EV3)",
        external_url=("https://repositorio.utp.edu.co/entities/publication/2cb3c888-47b1-4653-8b05-46c27a87ae81"),
    ),
    HelpMenuAction("about", "Acerca de"),
)


def help_menu_action(identifier: str) -> HelpMenuAction:
    """Devuelve una acción de ayuda por identificador estable."""

    for action in HELP_MENU_ACTIONS:
        if action.identifier == identifier:
            return action
    raise KeyError(identifier)


HELP_CATEGORIES: tuple[tuple[str, str], ...] = (
    ("empezar", "Empezar"),
    ("simular", "Simular"),
    ("mundos", "Crear mundos"),
    ("programar", "Programar"),
    ("depurar", "Depurar"),
    ("resolver", "Resolver problemas"),
)


HELP_REFERENCES: tuple[HelpReference, ...] = (
    HelpReference(
        identifier="user-manual",
        title="Manual de uso",
        summary="Flujos completos de uso en Web y escritorio, incluidos mundos, ejecución y recuperación.",
        filename="MANUAL_DE_USO.md",
        audience=("estudiante", "docente"),
    ),
    HelpReference(
        identifier="learning-guide",
        title="Guía de aprendizaje por ejemplos",
        summary="Ruta didáctica para avanzar desde la primera simulación hasta sensores y depuración.",
        filename="GUIA_APRENDIZAJE_EJEMPLOS.md",
        audience=("estudiante", "docente"),
    ),
    HelpReference(
        identifier="pybricks-limits",
        title="Diferencias simulador–robot físico",
        summary="Compatibilidad educativa declarada y aspectos que deben comprobarse también en un EV3 real.",
        filename="DIFERENCIAS_SIMULADOR_ROBOT.md",
        audience=("estudiante", "docente", "desarrollador"),
    ),
    HelpReference(
        identifier="technical-manual-web",
        title="Manual técnico Web",
        summary="Arquitectura, sesiones y operación de la aplicación Web.",
        filename="MANUAL_TECNICO_WEB.html",
        audience=("docente", "desarrollador", "soporte"),
    ),
    HelpReference(
        identifier="technical-manual-desktop",
        title="Manual técnico de escritorio",
        summary="Arquitectura, operación y empaquetado de la aplicación Tkinter.",
        filename="MANUAL_TECNICO_ESCRITORIO.html",
        audience=("docente", "desarrollador", "soporte"),
    ),
)


TEACHER_ROUTE = TeacherRoute(
    title="Práctica guiada: del mundo a la evidencia",
    objective=(
        "Que el estudiante configure un mundo, ejecute una misión y explique "
        "el resultado usando telemetría y LCD."
    ),
    minutes=25,
    guide_ids=("create-world", "first-simulation", "use-sensors", "debug-script", "missions"),
    suggested_evidence=(
        "Captura del mundo, código final, resultado de misión y una breve "
        "explicación de la lectura de un sensor."
    ),
    physical_robot_warning=(
        "El simulador es educativo: antes de una demostración real, valide puertos, "
        "batería, montaje, fricción y sensores en el EV3 físico."
    ),
)


PYBRICKS_GLOSSARY: tuple[GlossaryTerm, ...] = (
    GlossaryTerm("ev3brick", "EV3Brick", "Objeto virtual que da acceso a LCD, LED, altavoz y botones del EV3."),
    GlossaryTerm("port", "Port", "Identificador de un puerto físico o virtual, por ejemplo Port.A o Port.S1."),
    GlossaryTerm(
        "motor", "Motor", "Dispositivo que informa velocidad y ángulo y ejecuta movimientos en un puerto configurado."
    ),
    GlossaryTerm("drivebase", "DriveBase", "Control de dos motores para avanzar, girar y consultar la pose del robot."),
    GlossaryTerm(
        "wait", "wait", "Pausa cooperativa del programa; permite actualizar la simulación y atender una cancelación."
    ),
    GlossaryTerm(
        "snapshot", "Snapshot", "Estado coherente de robot, motores, sensores, Brick, LCD y ejecución en un instante."
    ),
    GlossaryTerm(
        "timeout",
        "Tiempo máximo",
        "Límite configurable que protege frente a programas que no terminan; no sustituye Detener y reiniciar.",
    ),
)


HELP_GUIDES: tuple[HelpGuide, ...] = (
    HelpGuide(
        identifier="first-simulation",
        title="Mi primera simulación",
        category="empezar",
        summary="Carga un ejemplo, elige un mundo y observa al robot ejecutar su programa.",
        destination="simulation",
        image_name="web/primera_simulacion.png",
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
        image_name="web/crear_mundo.png",
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
        image_name="web/ejecutar_pausar_reiniciar.png",
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
            "Los botones cambian de estado correctamente y canvas, LCD y telemetría permanecen sincronizados."
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
        image_name="web/motores_sensores.png",
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
        image_name="web/depurar_programa.png",
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
        image_name="web/error_programa.png",
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
            "La simulación vuelve a un estado coherente y el error no se confunde con una finalización correcta."
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
        image_name="web/validar_mundo.png",
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
    HelpGuide(
        identifier="missions",
        title="Cargar y comprobar una misión",
        category="simular",
        summary="Abre una misión, identifica su objetivo y comprueba el resultado al finalizar.",
        destination="simulation",
        image_name="web/misiones.png",
        image_alt="Captura real de la simulación con escenario, robot y paneles de resultado",
        minutes=4,
        audience=("estudiante", "docente"),
        keywords=("misión", "objetivo", "resultado", "escenario", "evaluación"),
        prerequisites=("Tener una misión disponible desde el menú Misiones.",),
        steps=(
            "Abre Misiones y selecciona una misión apropiada para tu nivel.",
            "Lee el objetivo y revisa el mundo que se cargó.",
            "Ejecuta el programa y espera el estado Finalizado, Error o Detenido.",
            "Compara el resultado con el objetivo antes de cambiar de misión.",
        ),
        expected_result="La misión informa un resultado y no conserva entidades visuales de una misión anterior.",
        recovery="Usa Detener y reiniciar y vuelve a cargar la misión si el mundo o el resultado no coincide.",
        related=("run-simulation", "recover-script-error"),
    ),
    HelpGuide(
        identifier="traces",
        title="Leer y limpiar trazas",
        category="simular",
        summary="Activa trazas para observar el recorrido y límpialas antes de comparar otra prueba.",
        destination="simulation",
        image_name="web/trazas.png",
        image_alt="Captura real de simulación donde el canvas permite observar el recorrido del robot",
        minutes=3,
        audience=("estudiante", "docente"),
        keywords=("trazas", "trayectoria", "canvas", "recorrido", "comparar"),
        prerequisites=("Tener un mundo y un script que mueva al robot.",),
        steps=(
            "Abre el menú Trazas y activa la visualización.",
            "Ejecuta un recorrido corto y observa la trayectoria en el canvas.",
            "Detén y reinicia antes de una nueva comparación para limpiar la trayectoria anterior.",
        ),
        expected_result="La traza corresponde al recorrido actual y se limpia al reiniciar o cambiar de mundo.",
        recovery="Si quedan líneas antiguas, usa Detener y reiniciar y vuelve a abrir el mundo activo.",
        related=("run-simulation", "missions"),
    ),
    HelpGuide(
        identifier="runtime-limit",
        title="Ajustar el tiempo máximo",
        category="simular",
        summary="Elige un límite razonable para misiones largas sin perder la posibilidad de detener un bucle.",
        destination="simulation",
        image_name="web/tiempo_maximo.png",
        image_alt="Captura real de la interfaz Web con controles y menú de configuración disponibles",
        minutes=3,
        audience=("estudiante", "docente", "soporte"),
        keywords=("tiempo máximo", "límite", "timeout", "bucle", "detener"),
        prerequisites=("Conocer la duración aproximada de la misión.",),
        steps=(
            "Abre Tiempo máximo y selecciona el valor requerido por la misión.",
            "Ejecuta la misión y observa el tiempo en telemetría.",
            "Si el programa no termina, usa Detener y reiniciar; no dependas solo del límite.",
        ),
        expected_result=(
            "El mensaje de límite muestra el valor elegido y una misión válida puede finalizar dentro de él."
        ),
        recovery="Aumenta el límite para una misión válida o revisa bucles sin salida antes de ejecutarla de nuevo.",
        related=("run-simulation", "recover-script-error"),
    ),
    HelpGuide(
        identifier="session-diagnostics",
        title="Revisar el diagnóstico de sesión",
        category="resolver",
        summary="Consulta el estado técnico seguro de la sesión antes de reportar un problema.",
        destination="simulation",
        image_name="web/diagnostico_sesion.png",
        image_alt="Captura real de la aplicación con el editor y el estado disponible para diagnosticar una ejecución",
        minutes=2,
        audience=("docente", "soporte"),
        keywords=("diagnóstico", "sesión", "exportar", "error", "soporte"),
        prerequisites=("Haber reproducido el problema sin compartir código sensible.",),
        steps=(
            "Abre Ayuda y selecciona Diagnóstico de sesión.",
            "Lee el estado, la versión y los contadores mostrados.",
            "Exporta el JSON solo si soporte lo solicita y revisa que no incluya datos personales.",
        ),
        expected_result=(
            "El diagnóstico permite describir el problema sin exponer el contenido del programa ni credenciales."
        ),
        recovery=(
            "Incluye el estado y los pasos de reproducción al solicitar ayuda; "
            "vuelve a iniciar una sesión si está cerrada."
        ),
        related=("recover-script-error", "debug-script"),
    ),
)

# Alias compatible con consumidores existentes. A partir de ahora contiene todo
# el catálogo de guías, no solo tres tarjetas aisladas.
HELP_TUTORIALS = HELP_GUIDES


# Fragmentos pequeños, seguros y autocontenidos. No contienen datos de sesión,
# rutas locales ni credenciales; solo se ofrecen cuando apoyan el objetivo de la guía.
HELP_SAFE_EXAMPLES: dict[str, str] = {
    "first-simulation": (
        "from pybricks.hubs import EV3Brick\n"
        "from pybricks.tools import wait\n\n"
        "ev3 = EV3Brick()\n"
        "ev3.screen.print('Hola, EV3')\n"
        "wait(500)\n"
    ),
    "run-simulation": (
        "from pybricks.hubs import EV3Brick\n"
        "from pybricks.tools import wait\n\n"
        "ev3 = EV3Brick()\n"
        "ev3.screen.print('Ejecución iniciada')\n"
        "wait(1000)\n"
    ),
    "use-sensors": (
        "from pybricks.ev3devices import UltrasonicSensor\n"
        "from pybricks.parameters import Port\n\n"
        "sensor = UltrasonicSensor(Port.S4)\n"
        "print(sensor.distance())\n"
    ),
    "debug-script": "# Coloca un breakpoint en la siguiente línea\nresultado = 1 + 1\nprint(resultado)\n",
}


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
