# Informe final de QA funcional integral — Aplicación Web

**Fecha:** 2026-07-28
**Conclusión:** **NO APTA PARA LIBERAR**

## Entorno y evidencia

| Elemento | Valor |
|---|---|
| URL probada | `http://127.0.0.1:5050/` |
| Servidor | `python -m simulador_ev3.web.waitress_server` |
| Rama / commit | `agent/release-1-5-0` / `90ee112` |
| Python / SO | 3.12.5 (`.venv`) / Windows |
| Navegador | Navegador integrado Codex, motor Chromium, sesión gráfica visible |
| Chrome/Edge certificado | **BLOCKED**: no hay conector disponible para certificar versión y DevTools nativos. |
| Temas | Claro y oscuro; persistencia tras recargar comprobada. |
| Viewports | 1920×1080, 1280×800, 1024×768 y 390×844 |
| Evidencias | `Documentos/EVIDENCIA_TESTEO_INTEGRAL_WEB_2026-07-28/` |

Se guardaron: `WEB-F-001-terminal-desync.png`,
`WEB-F-001-error-desync.png`, `WEB-F-002-reset-desync.png`,
`WEB-F-003-movil-recorte.png` y `responsive-*.png`.

No se corrigieron defectos durante la campaña. La captura de consola no mostró
mensajes `warning` ni `error` en los flujos ejecutados.

## Revalidación del informe anterior

| ID | Defecto previo | Resultado | Evidencia observada |
|---|---|---|---|
| WEB-F-001 | Finalización desincronizada | **FAIL** | Pie/editor `finished`; resumen `ACTIVO`, `0.04 s`, tick `2`; LCD vacía. |
| WEB-F-002 | Reinicio visual incompleto | **FAIL** | Pie `created`; resumen aún `ACTIVO`, `0.06 s`, tick `3`. |
| WEB-F-003 | Recorte móvil | **FAIL** | A 390×844, Haces termina en x=392.6 fuera de viewport x=390; canvas de 980 px. |

## Matriz de casos ejecutados realmente

| ID | Acción | Resultado esperado | Resultado observado | Estado |
|---|---|---|---|---|
| WEB-001 | Abrir URL con sesión limpia | Página y estado inicial coherentes | Página y controles cargaron correctamente | PASS |
| WEB-002 | Recargar página | Sesión visual coherente | Telemetría puede conservar datos previos frente al pie | FAIL |
| WEB-003 | Script `EV3Brick`, LCD y `wait(100)` | Snapshot terminal único en todas las vistas | Editor/pie finalizan; telemetría permanece activa y LCD queda vacía | FAIL |
| WEB-004 | Error sintáctico `def roto(:` | Error coherente en todas las vistas | Pie `error`; telemetría sigue `ACTIVO` | FAIL |
| WEB-005 | Detener y reiniciar | Reset uniforme de robot/LCD/tick/tiempo | Pie `created`; resumen no vuelve al estado inicial | FAIL |
| WEB-006 | Menú Misiones | Misiones disponibles y carga de una | Se mostraron tres y cargó «Sigue líneas básico» | PASS parcial |
| WEB-007 | Claro → oscuro → recarga | Cambio y persistencia de tema | `light`, `dark`, `dark` tras recarga | PASS |
| WEB-008 | Haces ON/OFF | Cambio de control visible | Etiqueta cambió a `Haces OFF` | PASS |
| WEB-009 | Zoom + y - | Controles accionables sin error | Ambos botones se accionaron | PASS parcial |
| WEB-010 | Viewports de escritorio | Sin overflow/recortes globales | Sin overflow global a 1920/1280/1024; canvas de 980 px | PASS parcial |
| WEB-011 | Viewport móvil 390×844 | Canvas adaptado y controles accesibles | Haces recortado; canvas fijo 980 px | FAIL |
| WEB-012 | Consola | Sin warnings/error | Captura de consola vacía | PASS |
| WEB-013 | Atrás/Adelante | Estado coherente | No ejercitado en SPA | BLOCKED |
| WEB-014 | Todos los comandos de menú | Cada comando funcional | Solo Tema y Misiones fueron ejercitados | BLOCKED |
| WEB-015 | CRUD de mundos y validaciones | Crear/guardar/recargar/editar/eliminar | No ejercitado | BLOCKED |
| WEB-016 | Escenarios y tres misiones completas | Éxito/fallo/pausa/cancelación coherentes | Bloqueado para PASS por WEB-F-001/F-002 | BLOCKED |
| WEB-017 | Motores, DriveBase, sensores, >30 s e infinito | Semántica y UI coherentes | No ejercitado; estado base inconsistente | BLOCKED |
| WEB-018 | Teclado y foco visible | Tab, Shift+Tab, Enter, Escape | BLOCKED: foco no transferible de forma confiable con este navegador. |
| WEB-019 | Red, API y recuperación | Errores útiles y recuperación | BLOCKED: no se pudo interceptar red en esta sesión. |

## Hallazgos

### WEB-F-001 — Alta — Estado terminal no sincroniza todas las vistas

**Pasos:** abrir la Web y ejecutar:

```python
from pybricks.hubs import EV3Brick
from pybricks.tools import wait
ev3 = EV3Brick()
ev3.screen.print("QA F001")
wait(100)
```

**Esperado:** editor, barra, LCD, canvas y telemetría muestran el mismo
snapshot terminal. **Observado:** editor/pie muestran `finished`, pero resumen
permanece `ACTIVO`, tiempo `0.04 s`, tick `2` y LCD vacía. También ocurre ante
error sintáctico: el pie llega a `error`, mientras la telemetría conserva
`ACTIVO`. Evidencias: `WEB-F-001-terminal-desync.png` y
`WEB-F-001-error-desync.png`.

### WEB-F-002 — Alta — Reinicio no restaura el estado visual

**Pasos:** ejecutar el script anterior y pulsar **Detener y reiniciar**.
**Esperado:** canvas, robot, LCD, tick, tiempo, motores, sensores y telemetría
vuelven al inicio. **Observado:** el pie indica `created`, pero resumen mantiene
`ACTIVO`, `0.06 s` y tick `3`. Evidencia: `WEB-F-002-reset-desync.png`.

### WEB-F-003 — Media — Canvas móvil fijo y herramienta de haces recortada

**Pasos:** cargar la página a 390×844. **Esperado:** canvas adaptado al
contenedor y controles dentro del viewport. **Observado:** canvas de 980 px y
borde derecho de Haces en x=392.6 para viewport x=390. Evidencia:
`WEB-F-003-movil-recorte.png`.

### WEB-F-004 — Media — Paridad con Tkinter no aprobable

Tkinter tiene evidencia previa de resultados terminales y reinicio coherentes;
la Web presenta WEB-F-001 y WEB-F-002. La paridad de simulación, mundos y
misiones no puede aprobarse hasta resolver la sincronización Web.

## Riesgos y recomendaciones

- **Riesgo alto:** alumnos pueden interpretar como activo o válido un robot que
terminó, falló o fue reiniciado.
- **Riesgo alto:** resultados de misión pueden coexistir con telemetría obsoleta.
- **Riesgo medio:** en móvil hay controles parcialmente inaccesibles.
- **Riesgo medio:** CRUD, sensores, red, teclado y todos los menús no se deben
considerar aprobados; están BLOCKED.

1. Corregir la propagación de snapshots/SSE en `finished`, `error`,
`timed_out`, `stopped` y `reset`, usando una misma generación para canvas, LCD,
telemetría y barra.
2. Añadir E2E que ejecute WEB-F-001 y valide simultáneamente todas las vistas
antes y después de reset.
3. Aplicar breakpoint móvil: canvas limitado al contenedor y toolbar con wrap o
desplazamiento accesible, sin recortar Haces.
4. Repetir la campaña completa en Chrome o Edge con DevTools: cada menú, CRUD
de mundos, sensores, pausa/reanudar, trazas, límite de tiempo y bucle cancelable.

## Conclusión

La aplicación Web **no es apta para liberar**. Los tres defectos del informe
de 2026-07-27 se reprodujeron en navegador real y permanecen abiertos. Los
casos no ejercitados están declarados BLOCKED, no aprobados por inferencia.

---

## Revalidación automatizada posterior a la corrección — 2026-07-28

Se implementó la corrección en el contrato de sesión Web. El estado se añade al
DTO de snapshot, los estados terminales fuerzan la publicación del snapshot
actual, y `reset` invalida los eventos intermedios/tardíos antes de publicar un
único estado inicial. Además, el canvas se limita al ancho disponible y la barra
de herramientas se adapta en móvil.

| Defecto | Prueba de regresión ejecutada | Resultado |
|---|---|---|
| WEB-F-001 | `test_terminal_snapshot_synchronizes_status_telemetry_and_lcd` | PASS automatizado |
| WEB-F-002 | `test_reset_replaces_terminal_snapshot_without_late_updates` | PASS automatizado |
| WEB-F-003 | `test_map_canvas_and_tools_stay_inside_viewport` en 1920×1080, 1280×800, 1024×768 y 390×844 | PASS automatizado |

Comandos ejecutados:

```powershell
.\.venv\Scripts\python.exe -m ruff check simulador_ev3/web/services/simulation_session.py simulador_ev3/runtime/isolated_worker.py tests/web/test_web_app.py tests/e2e/test_web_playwright.py
.\.venv\Scripts\python.exe -m pytest tests/web/test_web_app.py tests/e2e/test_web_playwright.py tests/runtime/test_isolated_worker.py -q
```

Resultado comprobado: **135 pruebas aprobadas en 44.07 s**; Ruff sin errores y
`git diff --check` sin errores de espacios.

### Limitación de esta revalidación

La instancia oficial fue reiniciada en `http://127.0.0.1:5050/`, pero la sesión
gráfica del navegador integrada devolvió una pestaña no asociada a la sesión de
automatización y no permitió tomar una nueva evidencia manual. Por honestidad,
los tres defectos se consideran corregidos por E2E automatizado, pero queda
pendiente una pasada gráfica visible con DevTools antes de cambiar la conclusión
histórica de liberación del informe completo.

## Revalidación gráfica visible completada — 2026-07-28

La conexión gráfica fue recuperada contra `http://127.0.0.1:5050/` y se
ejecutaron los tres flujos de regresión en el navegador visible.

| Defecto | Resultado visible observado | Estado |
|---|---|---|
| WEB-F-001 | Al terminar el script LCD, el estado global y la telemetría mostraron `finished`, con tiempo `0.14 s` y tick `7`. | PASS |
| WEB-F-002 | Tras cancelar un bucle infinito, estado y telemetría mostraron `created`, tick `1` y tiempo `0.02 s`. | PASS |
| WEB-F-003 | A 390×844 el canvas terminó en x=356 y Haces en x=261; no hubo overflow horizontal en claro ni oscuro. | PASS |

La consola no registró errores ni advertencias en los flujos. Evidencias:
`WEB-F-001-corregido-terminal.png`, `WEB-F-002-corregido-reset.png`,
`WEB-F-003-corregido-movil-claro.png` y
`WEB-F-003-corregido-movil-oscuro.png`.

Entorno gráfico registrado: Microsoft Edge WebView `149.0.4022.98`. Las pruebas
E2E registraron respuestas HTTP exitosas para creación de sesión, script,
inicio, snapshot y reset. La sesión gráfica no expone panel de red ni HAR, por
lo que no se declara una inspección DevTools de solicitudes.

### Conclusión actualizada

Los defectos WEB-F-001, WEB-F-002 y WEB-F-003 están corregidos y revalidados
de forma automatizada y visual. La aplicación sigue **apta con observaciones**:
el CRUD exhaustivo de mundos, todos los menús, red y el catálogo completo de
misiones/sensores permanecen BLOCKED en la campaña integral y requieren una
iteración QA independiente antes de declarar una liberación sin observaciones.
