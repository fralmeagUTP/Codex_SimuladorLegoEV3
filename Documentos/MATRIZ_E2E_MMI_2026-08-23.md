# Matriz E2E MMI — 2026-08-23

Esta matriz aplica el mismo catálogo funcional de
`MATRIZ_PARIDAD_CIERRE_WEB_TKINTER.md`. Cada resultado conserva un resumen de
ejecución actual y completo en `artifacts/mmi-e2e-2026-08-23/`.

| Plataforma | Comando | Evidencia obtenida | Estado |
|---|---|---|---|
| Web / Chromium | `.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -q` | **56 PASS** en 66.30 s; resumen persistente en `web.stdout.log`. | PASS |
| Web / Chromium, catálogo distribuido | `.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -k "real_catalog_loads_every" -q` | **1 PASS** en 9.52 s; carga visible de 23 ejemplos, 12 mundos, 4 escenarios y las misiones disponibles. | PASS |
| Tkinter / Pywinauto | `EV3_RUN_DESKTOP_E2E=1 .venv\Scripts\python.exe -m pytest tests\e2e\test_desktop_pywinauto.py -q -rs` | Primera ejecución: 6 PASS, 1 FAIL por coordenada rígida del menú Ayuda. Tras usar el atajo oficial F1: **7 PASS** en 112.25 s; `desktop-rerun.stdout.log`. | PASS |
| Tkinter / Pywinauto, catálogo distribuido | `EV3_RUN_DESKTOP_E2E=1 ... pytest tests\e2e\test_desktop_pywinauto.py -k real_catalog_loads_examples -q -rs` | **1 PASS** en 31.74 s; carga real de ejemplos, escenarios y misiones desde los menús nativos. JUnit: `desktop-real-catalog.xml`. | PASS |
| Contrato común | `pytest tests/application/test_session_contract.py tests/web/test_web_app.py tests/runtime/test_isolated_worker.py -q` | 134 PASS en 22.92 s en la campaña actual. | PASS |

## Corrección del arnés Tkinter

El caso de navegación usaba la coordenada rígida `(800, 53)` para abrir Ayuda.
Al variar el ancho de los menús, esa coordenada dejó de seleccionar el control
correcto. Se sustituyó por `{F1}`, atajo oficial de la aplicación. No se
modificó comportamiento de producto; se estabilizó el oráculo E2E nativo.
