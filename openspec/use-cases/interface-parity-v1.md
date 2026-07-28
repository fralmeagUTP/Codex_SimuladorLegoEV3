# Catálogo de casos de uso — Paridad de interfaces v1

Versión de catálogo: `1`  
Interfaces obligatorias: `web`, `tkinter`

Este catálogo es la fuente de verdad para la paridad funcional. Cada caso de uso
debe estar disponible, validado y documentado en ambas interfaces. La apariencia
puede diferir, pero no las precondiciones, acciones, estados, resultados ni errores.

| ID | Caso de uso | Estado esperado | Estado de paridad |
|---|---|---|---|
| UC-SESSION-01 | Crear o reinicializar contexto de simulación | `created` | Base compartida |
| UC-CODE-01 | Crear, abrir, editar y guardar script Python | `ready` | Base compartida |
| UC-RUN-01 | Ejecutar programa y observar estado final | `finished` | Base compartida |
| UC-RUN-02 | Pausar, reanudar y detener/reiniciar programa | `stopped` | Base compartida |
| UC-DEBUG-01 | Configurar breakpoints, watches, step y continue | `paused` | Base compartida |
| UC-ROBOT-01 | Definir pose inicial del robot | `ready` | Base compartida |
| UC-OBSERVE-01 | Consultar mapa, telemetría, sensores y brick virtual | `running` | Base compartida |
| UC-EXAMPLE-01 | Cargar ejemplos y escenarios educativos | `ready` | Base compartida |
| UC-WORLD-01 | Crear, abrir, guardar, importar y exportar mundos | `ready` | Auditoría de paridad pendiente |
| UC-WORLD-02 | Colocar, mover, rotar, duplicar y eliminar assets | `ready` | Auditoría de paridad pendiente |
| UC-WORLD-03 | Validar y aplicar un mundo a la simulación | `ready` | Auditoría de paridad pendiente |
| UC-HELP-01 | Acceder a ayuda, manual y acerca de | `created` | Auditoría de paridad pendiente |
| UC-TRACE-01 | Registrar, avanzar y exportar trazas de simulación | `ready` | Base compartida |
| UC-PROFILE-01 | Seleccionar perfil ideal, realista o calibrado | `ready` | Base compartida |
| UC-ASSESS-01 | Ejecutar misiones y criterios evaluables | `finished` | Planificado |

## Regla de aceptación

Para cada ID no planificado, una entrega DEBERÁ incluir:

1. implementación utilizable desde Web y Tkinter;
2. misma transición de `SessionStatus` y mismo resultado de dominio;
3. una prueba de contrato compartida;
4. una prueba E2E o UI para cada interfaz;
5. documentación de cualquier diferencia exclusivamente visual.

Los ID planificados pasan a ser obligatorios en la fase aprobada que los implemente.
No se permite añadir un nuevo ID sin incluirlo en `use_case_catalog.py`, en este
archivo y en los deltas OpenSpec que correspondan.
