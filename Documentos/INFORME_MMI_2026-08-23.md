# Informe MMI — 2026-08-23

## Alcance y trazabilidad

Este informe cierra la tarea 7.5 del cambio OpenSpec
`igualar-madurez-integral-web-tkinter`. La evidencia se obtuvo sobre la rama
`codex/desbloquear-menus-al-finalizar-ejecucion`, commit `cbfd977`, en Windows
con el entorno virtual del repositorio. No sustituye una ejecución remota de
CI ni una revisión manual con lector de pantalla.

La campaña cubre los contratos comunes, Web/Chromium, Tkinter/Pywinauto,
calidad estática, seguridad, cobertura de las capas núcleo y pruebas de carga,
runtime aislado y artefactos de liberación. Los registros de E2E se conservan
en `artifacts/mmi-e2e-2026-08-23/`.

## Evidencia ejecutada

| Área | Comando o evidencia | Resultado |
|---|---|---|
| E2E Web | `.venv\\Scripts\\python.exe -m pytest tests\\e2e\\test_web_playwright.py -q` | **56 PASS** en 66.30 s. |
| Catálogo real Web | `pytest tests\\e2e\\test_web_playwright.py -k real_catalog_loads_every -q` | **1 PASS** en 9.52 s; ejercita visualmente 23 ejemplos, 12 mundos, 4 escenarios y las misiones publicadas. |
| E2E Tkinter | `EV3_RUN_DESKTOP_E2E=1 ... pytest tests\\e2e\\test_desktop_pywinauto.py -q -rs` | **7 PASS** en 112.25 s. |
| Catálogo real Tkinter | `EV3_RUN_DESKTOP_E2E=1 ... pytest tests\\e2e\\test_desktop_pywinauto.py -k real_catalog_loads_examples -q -rs` | **1 PASS** en 31.74 s; ejercita los ejemplos, escenarios y misiones distribuidos desde los menús nativos. |
| Editor de mundos | `pytest tests\\ui\\test_world_editor_navigation.py tests\\shared\\test_world_editor_projection.py tests\\application\\test_world_editor_service.py tests\\web\\test_qa_world_crud.py -q` | **14 PASS** en 0.66 s. |
| Ciclo de vida cruzado | `pytest tests\\shared\\test_interface_execution_parity.py tests\\application\\test_desktop_session_adapter.py -q` | **22 PASS** en 2.90 s; incluye regresión de error terminal equivalente. |
| Snapshots críticos | `pytest tests\\shared\\test_interface_execution_parity.py tests\\ui\\test_ui.py -k "terminal_snapshot or reset_restore or stop_and_reset_applies_initial_snapshot or reset_discards_late_snapshot" -q` y E2E Web equivalente | **4 PASS** y **2 PASS**, respectivamente. |
| Accesibilidad automatizable | Pruebas Tkinter de tema/Escape y E2E Web de contraste, Tab, Enter y Escape. | **5 PASS** Tkinter y **14 PASS** Web. |
| Contrato compartido | `pytest tests/application/test_session_contract.py tests/web/test_web_app.py tests/runtime/test_isolated_worker.py -q` | **134 PASS** en 22.92 s. |
| Núcleo y dominio | `pytest tests/core tests/domain --cov=simulador_ev3.core --cov=simulador_ev3.domain --cov-fail-under=90 -q` | **243 PASS**; cobertura real **92.61 %**. |
| Calidad estática | Ruff y Mypy | Ruff sin hallazgos; Mypy: **115** archivos fuente, sin errores. |
| Seguridad | Bandit con política del repositorio y Pip-Audit | Salida 0; Pip-Audit: sin vulnerabilidades conocidas. |
| Carga y resiliencia | `pytest tests/load tests/runtime/test_isolated_worker.py -q` | **36 PASS** en 14.15 s. |
| Liberación | `pytest tests/release -q` | **12 PASS** en 11.81 s; artefactos `dist/` presentes. |

La matriz detallada de los casos de interfaz se mantiene en
`Documentos/MATRIZ_E2E_MMI_2026-08-23.md`.

## Resultado por dimensión

| Dimensión MMI | Resultado | Decisión |
|---|---|---|
| Arquitectura y contrato de sesión | Puertos, DTOs y recuperación cubiertos por pruebas de contrato. | PASS |
| Diseño, navegación y assets | Tokens, catálogos, pruebas de integridad y validación manual con Narrador en ambas UI. | PASS |
| Funcionalidad de sesión | Catálogos, editor, ciclo de vida, reinicio, eventos tardíos y recuperación de worker cubiertos. | PASS |
| Experiencia didáctica | Rutas, ayuda, glosario y retroalimentación formativa compartidos. | PASS |
| Observabilidad y soporte | Diagnóstico, exportación, redacción y guía de soporte disponibles. | PASS |
| Calidad y liberación | Compuertas locales principales aprobadas; matriz E2E publicada. | PASS con límites indicados. |

## Observaciones y tareas pendientes

El cambio OpenSpec queda completado. Permanecen límites de evidencia ajenos a
sus tareas funcionales:

- La compuerta Mutmut está configurada para CI Linux/WSL, pero no se ejecutó en
  esta sesión Windows; no se presenta como evidencia local aprobada.
- No se ejecutó CI remoto para el commit `cbfd977` durante esta campaña.

## Decisión de liberación

**Apta con observaciones para pruebas integradas y demostración controlada.**
La evidencia local no muestra fallos en las compuertas ejecutadas. Una
liberación general debe repetir la CI remota, incluida la compuerta de
mutación Linux/WSL, con evidencia trazable a su commit de liberación.
