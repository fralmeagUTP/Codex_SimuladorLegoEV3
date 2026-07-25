"""Catálogo versionado de casos de uso que deben mantener paridad de interfaz."""

from __future__ import annotations

from dataclasses import dataclass

INTERFACE_PARITY_CATALOG_VERSION = 1
REQUIRED_INTERFACES = frozenset({"web", "tkinter"})


@dataclass(frozen=True)
class UseCase:
    identifier: str
    name: str
    category: str
    expected_state: str
    planned: bool = False


USE_CASES: tuple[UseCase, ...] = (
    UseCase("UC-SESSION-01", "Crear o reinicializar contexto de simulación", "sesion", "created"),
    UseCase("UC-CODE-01", "Crear, abrir, editar y guardar script Python", "codigo", "ready"),
    UseCase("UC-RUN-01", "Ejecutar programa y observar estado final", "ejecucion", "finished"),
    UseCase("UC-RUN-02", "Pausar, reanudar y detener/reiniciar programa", "ejecucion", "stopped"),
    UseCase("UC-DEBUG-01", "Configurar breakpoints, watches, step y continue", "depuracion", "paused"),
    UseCase("UC-ROBOT-01", "Definir pose inicial del robot", "simulacion", "ready"),
    UseCase("UC-OBSERVE-01", "Consultar mapa, telemetría, sensores y brick virtual", "observabilidad", "running"),
    UseCase("UC-EXAMPLE-01", "Cargar ejemplos y escenarios educativos", "contenido", "ready"),
    UseCase("UC-WORLD-01", "Crear, abrir, guardar, importar y exportar mundos", "mundos", "ready"),
    UseCase("UC-WORLD-02", "Colocar, mover, rotar, duplicar y eliminar assets", "mundos", "ready"),
    UseCase("UC-WORLD-03", "Validar y aplicar un mundo a la simulación", "mundos", "ready"),
    UseCase("UC-HELP-01", "Acceder a ayuda, manual y acerca de", "ayuda", "created"),
    UseCase("UC-TRACE-01", "Registrar, avanzar y exportar trazas de simulación", "trazabilidad", "ready"),
    UseCase("UC-PROFILE-01", "Seleccionar perfil ideal, realista o calibrado", "fidelidad", "ready"),
    UseCase("UC-ASSESS-01", "Ejecutar misiones y criterios evaluables", "evaluacion", "finished", planned=True),
)


def use_case_ids() -> tuple[str, ...]:
    """Devuelve identificadores estables en el orden del catálogo."""
    return tuple(item.identifier for item in USE_CASES)
