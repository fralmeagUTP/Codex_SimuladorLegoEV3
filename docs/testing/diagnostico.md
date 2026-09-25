# Diagnóstico QA

Fecha: 2026-07-24. Alcance: simulador EV3, Web Flask, Tkinter, runtime aislado y frontend.

## Arquitectura detectada

- Python 3.11+; Flask para Web, Tkinter para escritorio y JavaScript sin framework para la UI Web.
- Capas: `domain`, `core`, `application`, `runtime`, `web`, `ui`, `persistence` y `pybricks_api`.
- Ejecución de scripts mediante worker aislado; sesiones Web en memoria/archivo y Redis opcional.
- Sin base de datos relacional ni autenticación de usuarios. La autorización Web se basa en token de propietario de sesión.

## Hallazgos con evidencia

| ID | Severidad | Evidencia | Riesgo | Recomendación |
|---|---|---|---|---|
| QA-01 | Media | `README.md` informa validaciones antiguas (565), mientras la suite actual reúne 672 pruebas. | Diagnóstico de CI incorrecto. | Actualizar resultados y comandos. |
| QA-02 | Media | `ui/main_window.py` contiene múltiples `except Exception: pass`. | Fallos visuales/configuración pueden ocultarse. | Registrar o acotar excepciones en siguiente iteración. |
| QA-03 | Media | `simulation_app.js` conserva orquestación residual pese a controladores extraídos. | Riesgo de regresión frontend. | Seguir extrayendo lógica de editor y SSE/polling en cambios pequeños. |

No se confirmó defecto funcional durante esta auditoría: la evidencia ejecutable terminó sin fallos.

## Actualización de campaña visible — 2026-07-29

La campaña posterior ejercitó la aplicación Web en navegador gráfico y anuló la
conclusión histórica anterior: se confirmaron defectos funcionales reales.

| ID | Severidad | Evidencia UI real | Impacto | Recomendación |
|---|---|---|---|---|
| QA-REG-006 | Resuelta | `WEB-V-017` confirmó que al cancelar Radar ultrasónico permanecía un resultado de misión completada. | El usuario recibía un resultado falso tras una cancelación. | Corregida: el reinicio limpia el resultado y los eventos tardíos se descartan por generación; cubierta por `test_reset_hides_the_terminal_mission_result` (Playwright, 2026-07-30). |
| QA-REG-007 | Resuelta | `WEB-V-018` confirmó controles/barra en `paused` y telemetría aún en `running`. | Paneles de una misma sesión mostraban estados contradictorios. | Corregida: pausa y reanudación publican un snapshot decorado con el estado actual; cubierta por `test_simulation_controls_follow_execution_state` (Playwright, 2026-07-30). |
| QA-REG-009 | Resuelta | `WEB-V-033` confirmó que Depurar con breakpoint no pausaba/finalizaba y reset no recuperaba. | La depuración bloqueaba el flujo normal de ejecución. | Corregida la transición de breakpoint y la publicación del snapshot; cubierta por `test_reset_recovers_a_session_paused_at_a_debug_breakpoint` (Playwright, 2026-07-30). |
| QA-REG-010 | Revalidada | `WEB-V-036` dejó Detener y reiniciar en `resetting` más de un minuto en Ultrasonido + obstáculos. | La UI quedaba inutilizable hasta recargar. | El flujo actual aprobó `test_reset_recovers_the_ultrasonic_obstacle_scenario`: recupera `created`, telemetría y controles (Playwright, 2026-07-30). |
| QA-REG-008 | Resuelta | `WEB-V-026`/`WEB-V-034` confirmó que el editor emitía error de asset sin colocación explícita. | Mensaje erróneo y pérdida de confianza al crear mundo. | Corregida la persistencia implícita durante crear/redimensionar/importar; cubierta por `test_world_editor_blank_canvas_does_not_attempt_an_unselected_placement` (Playwright, 2026-07-30). |
| QA-REG-011 | Revalidada | `WEB-V-042` confirmó que Manual de uso no abría contenido ni informaba indisponibilidad. | Ruta de ayuda declarada pero inoperante. | El enlace actual abre `/help` en una nueva pestaña con contenido; cubierta por `test_help_menu_opens_the_user_manual` (Playwright, 2026-07-30). |
| QA-REG-012 | Media | E2E-ACC-001 confirmó inicialmente 1.29:1 en tres valores de telemetría oscuros. | Resuelto: la prueba E2E de 10 pares críticos aprobó tras aplicar la paleta de resumen oscura. | Mantener el gate WCAG AA en E2E. |
| QA-REG-013 | Alta | El script eliminaba `SimuladorEV3.spec` antes de invocar PyInstaller. | Resuelto estáticamente: conserva y usa la especificación; la ejecución real permanece pendiente de un Windows limpio. | Ejecutar smoke de artefacto cuando haya un equipo apropiado. |

### Dictamen de liberación

**Apta con observaciones** para los flujos Web cubiertos. Persisten límites de
validación de entorno (Docker y escritorio Tkinter no disponibles). La suite
automatizada (777 aprobadas, 4 omitidas),
Ruff, Mypy, Bandit con política oficial y Pip-Audit dan una base sólida de
regresión, pero no compensan fallos reales de estado, cancelación y depuración.
Docker y E2E Tkinter permanecen bloqueados por limitaciones del ambiente de
validación, no por fallos de producto confirmados.
