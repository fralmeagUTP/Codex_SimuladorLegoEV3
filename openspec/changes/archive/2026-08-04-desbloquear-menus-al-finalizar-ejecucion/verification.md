# Verificación planificada

| ID | Interfaz | Flujo | Resultado esperado |
| --- | --- | --- | --- |
| MENU-001 | Web | Ejecutar un script no terminado | Los menús de contexto están deshabilitados. |
| MENU-002 | Web | Finalización natural del script | Los menús de contexto se habilitan sin reiniciar. |
| MENU-003 | Web | Detener y reiniciar | Los menús se habilitan y la sesión vuelve a creada. |
| MENU-004 | Tkinter | Ejecutar y pausar un script | Los menús de contexto están deshabilitados. |
| MENU-005 | Tkinter | Finalización natural, error y tiempo agotado | Los menús de contexto se habilitan. |
| MENU-006 | Tkinter | Detener y reiniciar | Los menús se habilitan sin afectar el reinicio visual. |

La evidencia inicial ya confirma MENU-001 y MENU-003 en Web, y confirma el fallo de MENU-002. Ningún caso restante se marcará aprobado sin una ejecución real o una prueba automatizada que valide la interacción correspondiente.

## Evidencia de implementación (2026-07-28)

- `MENU-001` Web: aprobado en navegador real. Con un bucle activo, Archivo, Ejemplos, Mundos y Tema se observaron deshabilitados.
- `MENU-002` Web: aprobado en navegador real. Un script con `wait(50)` llegó a `finished` y los mismos menús se observaron habilitados sin recargar.
- `MENU-003` Web: aprobado en navegador real. Tras Detener y reiniciar, la sesión llegó a `created` y los menús se observaron habilitados.
- Pruebas automatizadas: 3 pruebas Tkinter y 2 pruebas Web seleccionadas aprobadas con Python 3.12.5; Ruff aprobado. La validación ampliada de `tests/ui/test_ui.py` y `tests/web/test_web_app.py` aprobó 171 pruebas, y `tests/e2e/test_web_playwright.py` aprobó 26 pruebas E2E.
- `MENU-004` a `MENU-006`: cubiertos parcialmente por la regresión de estado Tkinter. Queda pendiente una verificación manual visual de escritorio.

Se añadió `test_desktop_menus_unlock_after_execution_finishes_or_resets`, que valida bloqueo al iniciar y desbloqueo después de reiniciar y finalizar naturalmente. La campaña Pywinauto se ejecutó con `EV3_RUN_DESKTOP_E2E=1`, pero las pruebas fueron omitidas: el entorno de ejecución no expone una ventana Windows visible. Este resultado es un bloqueo de infraestructura, no una aprobación ni un defecto funcional.

## Cierre de validación de CI (2026-07-28)

- Suite local completa: `749 passed, 4 skipped` con Python 3.12.5.
- Calidad local: Ruff y Mypy aprobados; `openspec validate desbloquear-menus-al-finalizar-ejecucion --strict` aprobado.
- CI de la rama `codex/desbloquear-menus-al-finalizar-ejecucion`: los cuatro flujos ejecutados para el commit `00f97c1` finalizaron correctamente, incluida la matriz Windows Python 3.11/3.12, Linux, E2E web y evidencia visual.
- Reintento explícito de la verificación nativa: `$env:EV3_RUN_DESKTOP_E2E='1'; .\.venv\Scripts\python.exe -m pytest tests/e2e/test_desktop_pywinauto.py::test_desktop_menus_unlock_after_execution_finishes_or_resets -q -rs` fue omitido porque el host no expone un escritorio Windows visible. MENU-004 a MENU-006 siguen pendientes únicamente de esa observación visual manual.

## Verificación manual Tkinter (2026-07-28)

Con la ventana real `Simulador EV3 Pybricks` visible en un escritorio Windows se ejecutó el ejemplo finito de LED cargado en el editor. La automatización interactuó con los botones y con el menú Archivo de esa misma instancia, sin crear una segunda aplicación:

- `MENU-004`: aprobado. Tras pulsar Ejecutar, Archivo no se desplegó, lo que confirma su bloqueo durante la ejecución.
- `MENU-006`: aprobado. Tras pulsar Detener y reiniciar, Archivo volvió a desplegarse.
- `MENU-005`: aprobado. Tras una finalización natural del ejemplo, Archivo volvió a desplegarse.

La tarea 4.3 queda completada. El intento de Pywinauto que crea una segunda instancia continúa condicionado por el entorno, pero no invalida esta verificación real sobre la aplicación visible.
