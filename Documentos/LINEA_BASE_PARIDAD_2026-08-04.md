# Línea base de paridad Web / Tkinter — 2026-08-04

**Cambio:** `cerrar-paridad-y-liberacion-ambas-apps`  
**Commit de inicio:** `ebeb4fb`  
**Sistema:** Windows; Python 3.12.5; Chrome 150.0.7871.188; Edge
151.0.4129.59.

## Ejecuciones realizadas

| ID | Comando | Resultado | Interpretación |
|---|---|---|---|
| QA-WEB-E2E | `.venv\\Scripts\\python.exe -m pytest tests\\e2e\\test_web_playwright.py -q` | 54 PASS, 60,71 s | Navegador real: controles, menús, sesión, mundo, depuración, teclado, tema y móvil cubiertos por la suite actual. |
| QA-DESK-E2E | `EV3_RUN_DESKTOP_E2E=1 .venv\\Scripts\\python.exe -m pytest tests\\e2e\\test_desktop_pywinauto.py -q -rs` | 5 PASS, 22,29 s | Escritorio gráfico real: arranque, navegación, ejecución, depuración, teclado y desbloqueo de menús. |
| QA-ALL-BASE | `.venv\\Scripts\\python.exe -m pytest tests\\runtime\\test_isolated_worker.py tests\\web tests\\e2e\\test_web_playwright.py -q` | Sin resultado concluyente | La consola terminó la espera a 64 s; no se registra como PASS/FAIL. Debe relanzarse desde CI o con recolector de salida persistente. |
| QA-ALL-LOCAL | `EV3_RUN_DESKTOP_E2E=1 .venv\\Scripts\\python.exe -m pytest tests -q` | Sin resultado concluyente | Se agotó el límite operativo de 120 s sin resumen de pytest; el proceso de pruebas ya no quedó activo. Las campañas segmentadas son la evidencia válida. |
| QA-LOCAL-CAPAS-1 | `pytest tests/application tests/persistence tests/pybricks_api tests/shared tests/ui tests/release tests/runtime tests/load -q` | PASS: 392/392 en 37,96 s | Servicios, UI nativa, runtime, carga, contratos, release y documentación. |
| QA-LOCAL-CAPAS-2 | `pytest tests/core tests/domain -q` | PASS: 243/243 en 0,84 s | Motor, eventos, colas y reglas de dominio. |
| QA-LOCAL-CAPAS-3 | `pytest tests/web -q` | PASS: 137/137 en 14,22 s | Rutas, sesiones, frontend, mundos, contenedor y Web. |

## Observaciones

- Antes de activar `EV3_RUN_DESKTOP_E2E=1`, los cinco casos de escritorio se
  omitían por protección de entorno. No se consideraron aprobados hasta la
  ejecución gráfica posterior.
- El resultado Web confirma la automatización existente, pero no completa el
  recorrido manual de los 23 ejemplos, 12 mundos y 4 escenarios de la matriz.
- No se detectó un defecto nuevo en estas suites. La ausencia de defectos en
  automatización no sustituye la revisión visual final ni la prueba de todos
  los recursos catalogados.

## Recorrido manual Web en navegador real

La instancia oficial local `http://127.0.0.1:5052/` se ejercitó mediante clics
reales el 2026-08-04. Los diez menús principales abrieron y cerraron; se
confirmó el contenido de Archivo, Ejemplos, Mundos, Escenarios, Misiones, Tema,
Fidelidad, Tiempo máximo, Trazas y Ayuda.

| Catálogo | Acción real | Resultado |
|---|---|---|
| 23 ejemplos Python | Selección individual desde el menú Ejemplos | PASS: los 23 actualizaron `Programa actual` con el recurso seleccionado. |
| 12 mundos JSON | Apertura del submenú y selección individual | PASS: los 12 actualizaron `Mundo actual` y dejaron la sesión en `ready`. |
| 4 escenarios | Selección individual | PASS: cada uno cargó el mundo y programa previstos, con sesión `ready`. |
| 3 misiones | Selección individual | PASS: cada una cargó el mundo y programa previstos, con sesión `ready`. |

### WEB-PAR-001 — Submenú de mundos no operable sin hover

- **Severidad:** media (accesibilidad y navegación por clic/teclado).
- **Reproducción inicial:** abrir Mundos por clic y pulsar “Mundos
  preestablecidos”. El controlador global cerraba el menú padre antes de que se
  pudiera elegir un mundo.
- **Causa:** `menu_controller.js` cerraba cualquier botón de un menú
  desplegable, incluido el control que sólo expande el submenú.
- **Corrección:** el subtoggle conserva abierto el grupo; una prueba E2E cubre
  el flujo sin depender de hover.
- **Verificación:** 2/2 pruebas E2E focalizadas aprobadas y carga manual real
  de `01_linea_negra_basica.json` confirmada después de la corrección.

### WEB-PAR-002 — Telemetría retenía `running` tras `finished`

- **Severidad:** alta (representación incoherente del estado terminal).
- **Reproducción inicial:** ejecutar un script corto que escribe en la LCD.
  La barra de sesión mostraba `finished`, pero el resumen de telemetría seguía
  mostrando `running` incluso 1,5 s después.
- **Causa:** `snapshot_response()` devolvía la copia del worker sin redecorarla
  con el estado autoritativo de sesión; esa copia pertenecía al último tick en
  ejecución.
- **Corrección:** todo snapshot expuesto se decora con el estado vigente antes
  de enviarse a sondeo/SSE; se conserva el mismo DTO para canvas, LCD y
  telemetría.
- **Verificación automatizada:** 2 pruebas unitarias terminales y 2 E2E
  focalizadas aprobadas.
- **Verificación manual real:** en una instancia nueva de servidor local
  (`http://127.0.0.1:5053/`), el script de LCD terminó con sesión `finished`,
  telemetría `finished`, tick `2`, tiempo `0.04s` y toast de éxito visible.

## Control de ciclo de ejecución Web

Con un programa `wait(10000)` se ejercitó en navegador real la secuencia:

| Acción | Estado observado |
|---|---|
| Ejecutar | `running.. t=0.52s` |
| Pausar | `paused` |
| Reanudar | `running. t=1.06s` |
| Detener y reiniciar | sesión y telemetría `created`; tick `1`; tiempo `0.02s` |

El tick y tiempo posteriores al reinicio cumplen el contrato de snapshot inicial
del worker (`tick ≤ 1`, `sim_time_s ≤ 0.02`) y no representan arrastre de la
ejecución cancelada.

### Estados terminales Web: éxito, error, cancelación y ritmo de simulación

Se ejecutó el 2026-08-04 el siguiente subconjunto de navegador real Playwright:

```powershell
.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -q -k "successful_execution_shows_one_accessible_toast_after_terminal_snapshot or success_toast_is_not_emitted_for_error_or_manual_stop or reset_replaces_terminal_snapshot_without_late_updates or wait_duration_remains_close_to_simulated_time_in_the_browser"
```

Resultado: **4 PASS** en 9,43 s. Cubre un aviso único y accesible tras el
snapshot terminal, ausencia del aviso ante error y detención manual, reinicio
sin actualizaciones tardías, y duración de una espera simulada de 900 ms dentro
del margen de tiempo real definido por la suite. El límite de tiempo configurable
continúa pendiente de ejecución específica antes de declarar completo PAR-015.

### PAR-010 — Precondición de “Avanzar un tick” verificada

El menú Trazas queda deshabilitado correctamente en `running` y `paused`,
conforme a la política de bloquear menús durante ejecución. En `created` no hay
programa cargado y el tick no avanza. Después de ejecutar un programa corto y
llegar a `finished`, el control quedó disponible y avanzó de tick `2` a `3`,
manteniendo el estado `finished` y mostrando “Se avanzo un tick de simulacion.”

La precondición se considera válida: la herramienta opera sobre una sesión que
ya contiene un programa/snapshot. No hay defecto confirmado.

## Depuración y escritorio: evidencia adicional

| ID | Flujo | Evidencia | Resultado |
|---|---|---|---|
| QA-WEB-DEBUG | Breakpoint, pausa, línea actual, paso, continuar y reinicio | 3 E2E Playwright focalizadas | PASS (7,26 s) |
| QA-DESK-NAV | Navegación Tkinter a ayuda y editor de mundos | 1 E2E pywinauto focalizada | PASS |
| QA-DESK-DEBUG | Ejecución, depuración y teclado Tkinter | 1 E2E pywinauto focalizada | PASS |

La conexión de la herramienta de navegador usada para el recorrido manual se
interrumpió después de los recorridos Web ya registrados. No se comunica como
resultado de aplicación; los recorridos manuales restantes deberán repetirse en
una sesión gráfica disponible antes de liberar.

## Editor de mundos y CRUD Web

| ID | Alcance | Resultado |
|---|---|---|
| QA-WEB-WORLD-E2E | Crear mundo, lienzo vacío, propiedades y arrastre | 4/4 E2E Playwright PASS (6,81 s). |
| QA-WEB-WORLD-CRUD | Guardado aislado y eliminación de mundo personalizado/preestablecido | 3/3 pytest PASS (0,47 s). |

Esta evidencia valida el flujo Web automatizado, pero no reemplaza la
comparación visual/manual con el editor de mundos nativo Tkinter.

## Compuerta técnica local

| Componente | Resultado |
|---|---|
| Ruff | PASS: sin incidencias. |
| Mypy | PASS: 109 módulos sin incidencias. |
| Bandit (severidad media+) | PASS: sin incidencias reportadas. |
| Pip-Audit | PASS: sin vulnerabilidades conocidas. |
| Núcleo y dominio | PASS: 243 pruebas; 92,6 % de cobertura, mínimo 90 %. |
| Worker aislado y carga | PASS: 34 pruebas. |

La ejecución de cobertura emitió una advertencia no bloqueante del entorno:
`coverage.tracer` C no está disponible y se empleó el trazador Python. El
resultado de cobertura se considera válido, aunque puede ser más lento.

## Verificación visual nativa de Tkinter

El capturador nativo ejecutó su validación de geometría en tema claro y oscuro:

| Resolución solicitada | Resultado |
|---|---|
| 1920×1080 | PASS: telemetría 795×528, Brick 385×528, LCD 346×171. |
| 1280×800 | PASS: telemetría 523×352, Brick 260×352, LCD 228×171. |
| 1024×768 | PASS: telemetría 369×320, Brick 321×320, LCD 289×171. |
| Editor de mundos (1280×800) | PASS en ambos temas; ventana 1320×860 por tamaño mínimo propio del editor. |

Se inspeccionó visualmente la captura oscura 1024×768: los controles, editor,
telemetría, Brick y LCD son visibles y legibles, sin solapamiento de paneles.
Las capturas se conservan como artefactos locales de QA ignorados por Git.

## Backend Web y operación Linux

| ID | Acción | Resultado |
|---|---|---|
| QA-WEB-BACKEND | `pytest tests/web -q` | PASS: 137/137 en 19,66 s. |
| QA-DOCKER-BUILD | `docker build --tag simulador-ev3:qa-baseline .` | PASS: imagen `simulador-ev3:qa-baseline` construida en 35,6 s. |

Docker Desktop se inició posteriormente y la construcción concluyó correctamente.
El smoke posterior con `EV3_WEB_SECRET_KEY` efímera y
`EV3_WEB_SESSION_COOKIE_SECURE=true` devolvió `200` en `/healthz`. El artefacto
Linux queda validado localmente; faltaría ejecución remota en CI para cerrar la
compuerta multi-plataforma.

El empaquetado Windows se ejecutó en salida aislada tras añadir los parámetros
opcionales `BuildRoot` y `DistRoot` al script. El EXE temporal generado en
`C:\tmp\ev3_release_qa\dist\SimuladorEV3\SimuladorEV3.exe` inició
correctamente y no se modificaron `build/` ni `dist/` del proyecto.

## Sesiones, aislamiento y recuperación

| Alcance | Resultado |
|---|---|
| Creación y propiedad de sesión | PASS: 3 pruebas de token y aislamiento entre sesiones. |
| Recuperación desde metadatos y token inválido | PASS: 3 pruebas. |
| Recuperación de worker tras reinicio forzado | PASS: 2 pruebas. |

Total focalizado: 8/8. Los resultados verifican que una sesión no modifica otra
con su propio token y que el worker puede reconstruirse conservando el contrato
de sesión documentado.

## Accesibilidad y móvil Web

Las regresiones Playwright de contraste en claro/oscuro, toast móvil 390×844,
apertura de menú por teclado, Escape y orden de tabulación aprobaron una
ejecución anterior de 15/15 en 16,18 s. La ampliación actual aprobó 20/20 en
26,23 s e incorporó la verificación de canvas y herramientas en 1920×1080,
1280×800, 1024×768 y 390×844. Esta evidencia es automatizada en navegador;
la inspección manual final de móvil permanece pendiente hasta recuperar la
sesión de navegador.

## Regresión Web completa posterior a correcciones

La suite `tests/e2e/test_web_playwright.py -q` se ejecutó después de las
correcciones WEB-PAR-001 y WEB-PAR-002 y del ajuste de tolerancia de
cuantización: **55/55 PASS en 70,84 s**. Incluye sesión, menús, ejemplos,
mundos, escenarios, misiones, canvas, telemetría, LCD, depuración, temas,
teclado, móvil y editor Web.

La suite gráfica de escritorio se relanzó sobre el mismo árbol de trabajo con
`EV3_RUN_DESKTOP_E2E=1`: **5/5 PASS en 25,46 s**. Verifica arranque,
navegación, ejecución, depuración, teclado y desbloqueo de menús de Tkinter.

## Contrato de sesión y cadencia de renderizado

| ID | Comando | Resultado |
|---|---|---|
| QA-CONTRACT-PARITY | `pytest tests/shared/test_interface_execution_parity.py tests/application/test_session_contract.py tests/application/test_desktop_session_adapter.py -q` | PASS: 17/17 en 3,79 s. |
| QA-WEB-RENDER | `pytest tests/web/test_render_interpolation_controller.py tests/web/test_web_app.py -q -k "render or interpolation or runtime_timeout or pause_does_not_consume_runtime_timeout_budget"` | PASS: 5/5 en 2,60 s. |

El caso de espera en navegador mantiene el límite de tiempo de pared y acepta
únicamente una discrepancia de hasta dos ticks de 20 ms en el snapshot final.
Es una cuantización propia del bucle de simulación, no una ampliación del tiempo
permitido de la ejecución.

## Revisión de seguridad del sandbox

Bandit identifica `exec` para ejecutar el programa Pybricks y `eval` para las
watches del depurador. Ambos son comportamientos necesarios y quedaron con
supresiones **por línea**, justificadas: el programa Web se ejecuta en worker
aislado y la watch se valida previamente contra un AST restrictivo. No se
deshabilitó ninguna regla de Bandit de forma global.

Verificación posterior: `bandit -q -ll -r simulador_ev3` y Mypy aprobaron sin
hallazgos; `pytest tests/runtime/test_runtime.py -q` aprobó **47/47** en 2,80 s.

## Próximo paso obligatorio

Ejecutar el catálogo completo de recursos y los flujos manuales en ambos temas
y resoluciones. Cualquier elemento no ejercitable se registrará como `BLOCKED`.

## Compuerta global posterior a correcciones

| Fecha | Comando | Resultado |
|---|---|---|
| 2026-08-04 | `.venv\\Scripts\\pytest.exe -q` | **PASS: 829 aprobadas, 5 omitidas, 122,13 s**. |
| 2026-08-04 | `EV3_RUN_DESKTOP_E2E=1 .venv\\Scripts\\pytest.exe tests\\e2e\\test_desktop_pywinauto.py -q -rs` | **PASS: 5/5, 31,50 s**. |

Las cinco omisiones de la compuerta global son los mismos E2E de escritorio
protegidos por la variable `EV3_RUN_DESKTOP_E2E`; se ejecutaron de forma
explícita en la segunda fila y aprobaron. Por tanto, no representan casos sin
probar en el entorno gráfico local.

Se corrigieron también dos regresiones confirmadas durante el cierre:

- **WEB-PAR-001:** activar un mundo preestablecido ya no cierra primero su
  submenú; queda cubierto por `test_world_presets_remain_open_when_activated_by_click`.
- **WEB-PAR-002:** el snapshot final ya no conserva el estado `running` de un
  worker obsoleto; queda cubierto por
  `test_snapshot_response_redecorates_stale_worker_snapshot_with_terminal_status`.

La comprobación restante para una liberación sin observaciones es operativa,
no una falla conocida de estas suites: repetir la matriz manual completa cuando
se restablezca una sesión de navegador gráfico y validar Docker/paquete Windows
en un entorno donde no sea necesario sobrescribir artefactos existentes.

### Bloqueo de revisión manual posterior

El 2026-08-04 se reinició el servidor oficial en `127.0.0.1:5053`; el proceso
quedó en escucha, pero el navegador integrado disponible para la campaña no
pudo acceder al bucle local y devolvió `ERR_CONNECTION_REFUSED`. No se usó este
resultado como fallo de producto porque la misma instancia estaba accesible en
el host y las campañas Playwright locales aprobaban. Los casos de inspección
manual que no quedaron realizados antes de perder la conexión permanecen
**BLOCKED por infraestructura de navegador**, y deberán repetirse desde Chrome
o Edge en el host antes de emitir una liberación sin observaciones.
