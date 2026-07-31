# Matriz de trazabilidad de calidad

> Los requisitos son inferidos salvo referencia explícita a OpenSpec. `UI real`
> exige navegador o escritorio visible; una prueba interna no reemplaza esa
> evidencia.

| Requisito | Función | Riesgo | Componente | Caso / prueba | Prioridad | Estado |
|---|---|---|---|---|---|---|
| R-01 Ejecutar scripts con límite y cancelación | F-01, F-02 | Crítico | runtime, sesión | `tests/runtime/test_runtime.py`, `test_isolated_worker.py` | P0 | Automatizado |
| R-02 Estado terminal coherente | F-01, F-08, F-09 | Crítico | adaptadores Web/Tkinter | regresión `QA-REG-001`, `test_reset_hides_the_terminal_mission_result`, `test_simulation_controls_follow_execution_state`, `test_reset_recovers_a_session_paused_at_a_debug_breakpoint`, `test_reset_recovers_the_ultrasonic_obstacle_scenario`; campaña UI | P0 | Automatizado; QA-REG-006/007/009 corregidas y QA-REG-010 revalidada en Web |
| R-03 Worker recuperable | F-03 | Crítico | isolated worker | `tests/runtime/test_isolated_worker.py` | P0 | Automatizado |
| R-04 Motor y física deterministas | F-05, F-06 | Crítico | domain/core | `tests/domain/robot`, `tests/core/test_simulation_engine.py` | P0 | Automatizado |
| R-05 Sesión Web autorizada | F-07 | Crítico | API/sesiones | `tests/web/test_web_app.py` | P0 | Automatizado |
| R-06 CRUD de mundos seguro | F-04 | Alto | editor/persistencia | `tests/application/test_world_editor_service.py`, API mundos | P1 | Parcial |
| R-07 Pybricks soportado y errores explícitos | F-02, F-06 | Alto | `pybricks_api` | `tests/pybricks_api/test_pybricks_api.py` y scripts UI | P1 | Parcial |
| R-08 Paridad Web/Tkinter | F-08, F-09 | Alto | contratos compartidos | `tests/shared/test_interface_execution_parity.py` | P1 | Parcial |
| R-09 Menús/diálogos/controles operables | F-08, F-09 | Alto | UI | Playwright + pyautogui | P1 | Parcial |
| R-10 Misiones y resultados | F-10 | Alto | evaluación/misiones | `tests/application/test_mission_evaluator.py`, E2E | P1 | Parcial |
| R-11 Accesibilidad y responsive | F-08, F-09, F-12 | Medio | UI/CSS/Tk | Playwright y capturas de escritorio | P2 | Parcial; contraste Web crítico cubierto, falta Tkinter visible |
| R-12 Seguridad estática y dependencia | F-02, F-07, F-14 | Alto | repositorio | Ruff, Mypy, Bandit, Pip-Audit | P1 | Automatizado |
| R-13 Rendimiento y carga | F-03, F-07, F-13 | Medio | worker/web | `tests/load/test_web_session_load.py` | P2 | Parcial |
| R-14 Instalación y artefactos | F-14 | Alto | Docker/PyInstaller | `tests/release`, smoke limpio | P1 | Parcial; script Windows corregido, falta artefacto y Docker real |

## Regla de estado

`Automatizado` significa que existe una prueba ejecutable, no que una versión
concreta esté aprobada. El estado de liberación se decide solo con el reporte
de ejecución vigente y su evidencia asociada.
