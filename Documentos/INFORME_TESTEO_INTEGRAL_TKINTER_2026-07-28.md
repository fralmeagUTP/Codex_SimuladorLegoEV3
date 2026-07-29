# Informe de testeo integral — aplicación de escritorio Tkinter

Fecha: 2026-07-28
Rama evaluada: `codex/desbloquear-menus-al-finalizar-ejecucion`
Commit: `8de29386cda57ee338ba97256b392ba3f0a4938e`
Sistema: Windows 10 Pro 10.0.19045
Python / entorno: Python 3.12.5, `.venv`
Comando de inicio: `./.venv/Scripts/python.exe -m simulador_ev3.ui.main_window`

## Resumen ejecutivo

Resultado: **apta con observaciones para desarrollo; no apta para una liberación
formal basada en esta campaña**.

Se ejercitó la aplicación Tkinter real mediante sus capturadores de ventana y
se generó evidencia de la secuencia de introducción y de la ventana principal
en claro y oscuro, a 1024×768, 1280×800 y 1920×1080 solicitado (el gestor de
ventanas proporcionó 1920×1061 de área cliente). Las capturas no mostraron
tracebacks ni fallos de construcción.

También se intentó automatización nativa de mouse y teclado con `pywinauto`.
Aunque la sesión permite capturar la UI, no expone sus ventanas a ese backend;
por ello los cuatro recorridos de interacción real fueron omitidos. Los casos
que necesitan clics, escritura, menús, diálogos o scripts se registran como
**BLOCKED**, no como aprobados.

## Evidencia y comandos ejecutados

Directorio de evidencias: `Documentos/EVIDENCIA_TESTEO_INTEGRAL_TKINTER_2026-07-28/`.

| Comando | Resultado |
|---|---|
| `python scripts/capture_desktop_intro.py --output-dir ...` | PASS; generó `intro.png` y `ventana_principal.png`. |
| `python scripts/capture_desktop_evidence.py --theme all --size 1024x768 --size 1280x800 --size 1920x1080 --verify-layout` | PASS; seis capturas y comprobación de geometría terminadas con código 0. |
| `EV3_RUN_DESKTOP_E2E=1 python -m pytest tests/e2e/test_desktop_pywinauto.py -q -rs` | BLOCKED; 4 omitidas porque el escritorio no es visible para `pywinauto`. |
| `python -m pytest -q` (ejecución previa del mismo commit) | PASS; 770 aprobadas, 4 omitidas. No sustituye validación de UI real. |

Capturas relevantes:

- [Introducción](EVIDENCIA_TESTEO_INTEGRAL_TKINTER_2026-07-28/intro.png)
- [Ventana principal](EVIDENCIA_TESTEO_INTEGRAL_TKINTER_2026-07-28/ventana_principal.png)
- [Claro 1024×768](EVIDENCIA_TESTEO_INTEGRAL_TKINTER_2026-07-28/simulacion_light_1024x768.png)
- [Oscuro 1024×768](EVIDENCIA_TESTEO_INTEGRAL_TKINTER_2026-07-28/simulacion_dark_1024x768.png)
- [Claro 1280×800](EVIDENCIA_TESTEO_INTEGRAL_TKINTER_2026-07-28/simulacion_light_1280x800.png)
- [Oscuro 1280×800](EVIDENCIA_TESTEO_INTEGRAL_TKINTER_2026-07-28/simulacion_dark_1280x800.png)
- [Claro 1920×1061](EVIDENCIA_TESTEO_INTEGRAL_TKINTER_2026-07-28/simulacion_light_1920x1061.png)
- [Oscuro 1920×1061](EVIDENCIA_TESTEO_INTEGRAL_TKINTER_2026-07-28/simulacion_dark_1920x1061.png)

## Matriz de casos ejecutados

| ID | Área | Estado | Resultado observado |
|---|---|---|---|
| TK-START-01 | Inicio desde fuente | PASS | El flujo real produjo introducción y ventana principal. |
| TK-START-02 | Introducción `assets/Intro.png` | PASS | Captura tomada durante la introducción; el activo se muestra a 800×450 px, que es la configuración vigente. |
| TK-START-03 | Transición tras introducción | PASS | Se generó una sola ventana principal después de la introducción. |
| TK-START-04 | Duración, centrado, foco y cierre prematuro de intro | BLOCKED | Requiere temporización/entrada nativa observable; `pywinauto` no accede al escritorio. |
| TK-LAYOUT-01 | Ventana a 1024×768, 1280×800 y 1920×1080 | PASS | Canvas, editor, telemetría y Brick recibieron geometría positiva en ambos temas. |
| TK-LAYOUT-02 | Telemetría, LCD y Robot/Estado alcanzables | PASS | `--verify-layout` validó dimensiones; el panel Brick conserva desplazamiento cuando el contenido supera su vista. |
| TK-LAYOUT-03 | Minimizar, restaurar, redimensionar manualmente | BLOCKED | No hay canal de entrada gráfica. |
| TK-THEME-01 | Claro y oscuro | PASS | Se obtuvieron seis capturas; no se observó texto claro sobre fondo claro ni oscuro sobre fondo oscuro en las áreas visibles. |
| TK-THEME-02 | Alternancias repetidas y persistencia | BLOCKED | Requiere interacción del menú Tema y reinicio visible. |
| TK-MENU-01 | Archivo, Ejemplos, Mundos, Escenarios, Misiones | BLOCKED | Menús no automatizables en esta sesión. |
| TK-MENU-02 | Fidelidad, Trazas, Tiempo máximo y Ayuda | BLOCKED | Menús y diálogos no automatizables en esta sesión. |
| TK-WORLD-01 | CRUD, validaciones y capas del editor de mundos | BLOCKED | Requiere selección, arrastre y diálogos nativos. |
| TK-MISSION-01 | Escenarios, misiones, éxito, error y cancelación | BLOCKED | Requiere cargar y ejecutar flujos interactivos. |
| TK-SCRIPT-01 | Intérprete Pybricks, LCD, motores y sensores | BLOCKED | Requiere escribir scripts y usar controles de ejecución. |
| TK-SCRIPT-02 | Aviso único de finalización exitosa | BLOCKED | El diálogo nativo no es alcanzable en esta sesión. |
| TK-CONTROL-01 | Ejecutar, pausar, reanudar, detener/reiniciar | BLOCKED | El recorrido E2E nativo se omitió por ausencia de escritorio visible. |
| TK-CANVAS-01 | Colisiones, sensores, trazas, zoom y paneo | BLOCKED | Requiere control de mouse/teclado. |
| TK-TELEMETRY-01 | Actualización en tiempo real y valores extensos | BLOCKED | La construcción se observó, pero no se ejecutó una misión real mediante UI. |
| TK-CLOSE-01 | Cierre durante ejecución, diálogos y callbacks | BLOCKED | El capturador cerró limpiamente ventanas temporales, pero no se ejercitó cierre durante una ejecución controlada por UI. |
| TK-A11Y-01 | Tab, Shift+Tab, Enter, Escape y foco | BLOCKED | Requiere entrada nativa. |

## Hallazgos e inconsistencias

No se confirmó un defecto funcional nuevo durante la parte ejecutable de esta
campaña. La principal limitación de calidad es de verificación, no del
producto:

### TK-2026-07-28-001 — Automatización nativa bloqueada

- Severidad: **media** (riesgo de liberación).
- Evidencia: los cuatro casos de `test_desktop_pywinauto.py` fueron omitidos.
- Resultado: `el entorno no expone la ventana de introducción en un escritorio
  Windows visible` y tres `timed out` al esperar la ventana principal.
- Impacto: no es posible certificar los recorridos de menús, diálogos, editor,
  scripts, simulación, accesibilidad ni cierre mediante interacción real.
- Recomendación: repetir la campaña en una sesión Windows interactiva (consola
  local o agente CI con escritorio activo), conservando `EV3_RUN_DESKTOP_E2E=1`.

## Paridad con Web

La paridad funcional de contratos y regresiones no gráficas está cubierta por
la suite compartida aprobada. Esta campaña no puede certificar la paridad de
interacciones visibles Web–Tkinter porque los clics de escritorio quedaron
bloqueados. La ventana Tkinter conserva las áreas equivalentes: simulación,
editor, telemetría y Brick/LCD.

## Riesgos y recomendaciones

1. Antes de una liberación a usuarios, ejecutar de nuevo los casos BLOCKED en
   una sesión con entrada Windows real y adjuntar las capturas por caso.
2. Priorizar: ejecución/pausa/reanudación/reinicio; mundos; scripts con error y
   éxito; tema; menús y diálogos; cierre durante ejecución.
3. Mantener `scripts/capture_desktop_intro.py` y
   `scripts/capture_desktop_evidence.py` como regresión visual de tamaños y
   temas, pero no tratarlos como sustitutos de navegación manual.

## Conclusión

**Apta con observaciones para desarrollo, no apta para liberar formalmente con
esta evidencia únicamente.** La aplicación real inicia, muestra su introducción
y renderiza de forma consistente en los tamaños y temas probados. Sin embargo,
la campaña solicitada exige interacción de mouse/teclado real para aprobar sus
flujos críticos y el entorno actual la bloquea; dichos flujos permanecen
honestamente en estado `BLOCKED`.
