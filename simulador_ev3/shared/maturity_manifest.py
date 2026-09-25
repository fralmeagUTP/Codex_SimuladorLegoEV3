"""Manifiesto MMI para gobernar la madurez y paridad Web/Tkinter.

El manifiesto no califica una capacidad por intuicion: cada fila aplicable debe
tener evidencia reproducible de las dos interfaces antes de poder cerrarse.
"""

from __future__ import annotations

from dataclasses import dataclass

from simulador_ev3.shared.use_case_catalog import REQUIRED_INTERFACES, use_case_ids

MATURITY_MANIFEST_VERSION = 1
MMI_TARGET_SCORE = 100
REQUIRED_EVIDENCE_KINDS = frozenset({"automated", "manual", "artifact"})


@dataclass(frozen=True)
class MaturityDimension:
    identifier: str
    name: str
    weight: int
    minimum_score: int
    owner: str


@dataclass(frozen=True)
class MaturityRequirement:
    """Evidencia exigida para que un caso de uso pueda declararse cerrado."""

    use_case_id: str
    dimension_id: str
    evidence_kinds: frozenset[str]
    applies_to: frozenset[str] = REQUIRED_INTERFACES


MMI_DIMENSIONS: tuple[MaturityDimension, ...] = (
    MaturityDimension("architecture", "Arquitectura y contratos", 18, 95, "Arquitectura"),
    MaturityDimension("experience", "Diseno, accesibilidad y navegacion", 16, 95, "UX/UI"),
    MaturityDimension("functionality", "Funcionalidad y sesion", 22, 100, "Desarrollo"),
    MaturityDimension("learning", "Experiencia didactica, ayuda y pedagogia", 14, 95, "Producto educativo"),
    MaturityDimension("quality", "Calidad, pruebas y liberacion", 18, 100, "QA"),
    MaturityDimension("observability", "Observabilidad y soporte", 12, 95, "Operacion"),
)


def _dimension_for_use_case(use_case_id: str) -> str:
    if use_case_id.startswith(("UC-TRACE", "UC-OBSERVE")):
        return "observability"
    if use_case_id.startswith(("UC-HELP", "UC-ASSESS", "UC-EXAMPLE")):
        return "learning"
    if use_case_id.startswith(("UC-WORLD", "UC-CODE")):
        return "experience"
    return "functionality"


MMI_REQUIREMENTS: tuple[MaturityRequirement, ...] = tuple(
    MaturityRequirement(
        use_case_id=identifier,
        dimension_id=_dimension_for_use_case(identifier),
        evidence_kinds=frozenset({"automated", "manual"}),
    )
    for identifier in use_case_ids()
)


# Las excepciones no permiten omitir una capacidad. Documentan la evidencia
# equivalente que corresponde a cada plataforma por sus limites tecnicos.
PLATFORM_ADAPTATIONS = {
    "web-mobile": "Viewport 390x844 y navegacion tactil; no aplica a Tkinter.",
    "tkinter-installer": "Instalador y ventana nativa Windows; no aplica a Web.",
    "web-browser-storage": "Persistencia del navegador y red; en Tkinter se valida almacenamiento local.",
}


def dimension_ids() -> tuple[str, ...]:
    return tuple(dimension.identifier for dimension in MMI_DIMENSIONS)


def validate_maturity_manifest() -> None:
    """Falla temprano si una futura edicion deja casos sin gobierno MMI."""
    dimensions = dimension_ids()
    if len(dimensions) != len(set(dimensions)):
        raise ValueError("Las dimensiones MMI deben tener identificadores unicos.")
    if sum(item.weight for item in MMI_DIMENSIONS) != MMI_TARGET_SCORE:
        raise ValueError("Los pesos MMI deben sumar 100.")
    if not all(0 < item.minimum_score <= MMI_TARGET_SCORE for item in MMI_DIMENSIONS):
        raise ValueError("Los umbrales MMI deben estar entre 1 y 100.")
    requirements = {item.use_case_id: item for item in MMI_REQUIREMENTS}
    if set(requirements) != set(use_case_ids()):
        raise ValueError("Cada caso de uso debe tener un requisito MMI.")
    for item in requirements.values():
        if item.dimension_id not in dimensions:
            raise ValueError("Un requisito MMI referencia una dimension inexistente.")
        if not item.evidence_kinds or not item.evidence_kinds <= REQUIRED_EVIDENCE_KINDS:
            raise ValueError("La evidencia MMI no es valida.")
        if item.applies_to != REQUIRED_INTERFACES:
            raise ValueError("La paridad MMI exige evidencia de Web y Tkinter.")
