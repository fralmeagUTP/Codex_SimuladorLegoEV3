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
