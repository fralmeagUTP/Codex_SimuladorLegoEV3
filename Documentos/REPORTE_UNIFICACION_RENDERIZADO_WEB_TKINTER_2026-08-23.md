# Cierre de paridad de renderizado y composición — 2026-08-23

**Cambio OpenSpec:** `unificar-renderizado-y-composicion-visual-web-tkinter`
**Alcance:** canvas, assets, pose inicial, paneles de simulación, tema y
respuesta en 1024×768, 1280×800 y 1920×1080.

## Resultado

Se consolidó el catálogo compartido de assets de escritorio como fuente
canónica para Web y Tkinter. Ambos clientes usan la misma geometría de
placements, orden de capas, tamaños lógicos y rotaciones. Al cambiar de
mundo, misión o reiniciar, se eliminan las capas transitorias (traza, haces y
marcadores) antes de dibujar el mundo nuevo.

La Web obtuvo dos correcciones de regresión verificadas:

1. A 1024 px el punto de ruptura ahora entra en composición apilada antes de
   que editor, telemetría o Brick excedan el viewport.
2. Si el manifiesto inyectado no está disponible en una carga concreta, el
   canvas recupera el catálogo canónico desde `/api/editor/assets`, redibuja al
   terminar la carga y muestra el sprite real del robot, no el fallback verde.

Tkinter conserva paneles ajustables, pero el Brick dispone de un mínimo de
340 px y la LCD se escala al ancho asignado; no impone su tamaño de referencia
sobre los paneles vecinos.

## Evidencia visual

Las capturas reproducibles se encuentran en:

`Documentos/EVIDENCIA_RENDERIZADO_PARIDAD_2026-08-23/`

| Plataforma | Temas | Resoluciones | Verificación |
|---|---|---|---|
| Web | Claro y oscuro | 1024×768, 1280×800, 1920×1080 | Canvas, editor, telemetría, Brick, mundo y menús visibles dentro de su contenedor. |
| Tkinter | Claro y oscuro | 1024×768, 1280×800, 1920×1080 | Geometría de telemetría, Brick y LCD comprobada por el capturador nativo. |

Las diferencias permitidas siguen siendo exclusivas del toolkit: relieve y
foco de widgets nativos, barras de desplazamiento y distribución ajustable de
`PanedWindow`. No cambian el asset, la pose, la información ni el significado
del estado de sesión.

## Pruebas ejecutadas

| Comando | Resultado |
|---|---|
| `pytest tests/web/test_frontend_modules.py tests/shared/test_asset_catalog.py tests/shared/test_ui_design_tokens.py tests/ui/test_ui.py -q` | **117 PASS** |
| `pytest tests/e2e/test_web_playwright.py -k "web_exposes_and_loads_the_canonical_robot_asset or map_canvas_and_tools_stay_inside_viewport or critical_simulation_panels_stay_inside_viewport or simulation_menus_load_examples_worlds_and_scenarios" -q` | **10 PASS** |
| Campaña Playwright de cierre (assets, distribución, snapshot terminal, aviso de éxito y cadencia) | **13 PASS** |
| `pytest tests/e2e/test_web_playwright.py -k "real_catalog_loads_every_example_world_scenario_and_mission" -q` | **1 PASS** |
| `EV3_RUN_DESKTOP_E2E=1 pytest tests/e2e/test_desktop_pywinauto.py -k "preset_world_catalog" -q` | **1 PASS** |
| API `start` con código integrado e idempotencia | **2 PASS** |
| `pytest tests/e2e/test_web_playwright.py -k "simulation_page_runs_default_script or terminal_snapshot_synchronizes_status_telemetry_and_lcd or successful_execution_shows_one_accessible_toast_after_terminal_snapshot or web_exposes_and_loads_the_canonical_robot_asset or critical_simulation_panels_stay_inside_viewport or map_canvas_and_tools_stay_inside_viewport" -q` | **12 PASS** |
| `pytest tests/pybricks_api/test_pybricks_api.py -k "wait" -q` | **4 PASS** |
| `openspec validate unificar-renderizado-y-composicion-visual-web-tkinter --strict` | **PASS** |

## Criterios verificados

- El robot visual se carga con el asset canónico y comparte la pose inicial
  entregada en el snapshot.
- Los mundos, ejemplos, escenarios y misiones del catálogo Web se cargan en
  navegador real.
- El catálogo de mundos de escritorio se abre mediante interacción Tkinter
  real.
- El canvas no deja trazas, haces ni marcadores de la sesión anterior.
- Los estados `Listo`, `Ejecutando`, `Pausado`, `Finalizado`, `Error` y
  `Detenido` se derivan del mismo catálogo semántico compartido.
- Tema claro/oscuro y la composición mínima no recortan controles críticos.

## Compuerta de regresión

La canalización mantiene pruebas de assets, contratos y E2E Web. La tarea
`desktop-visual` de `.github/workflows/quality.yml` conserva la comparación
visual de Tkinter con umbral RGB normalizado `0.08`; las capturas del cambio
permiten revisar de forma reproducible las tres resoluciones y ambos temas.

## Cierre de cadencia

La prueba E2E `test_wait_duration_remains_close_to_simulated_time_in_the_browser`
se corrigió para medir sus dos contratos de forma independiente, en lugar de
mezclar la preparación IPC con el tiempo de simulación:

- el estado `running` debe aparecer en un máximo de **0,75 s** después de la
  acción de usuario;
- desde `running` hasta `finished`, la simulación y el render deben mantenerse
  dentro de `max(1,20 s, tiempo_simulado × 1,25)`.

En la campaña de cierre, una espera de **1,02 s** simulados completó el tramo
visible `running → finished` en aproximadamente **0,95 s**. La preparación y
el runtime quedan por tanto observables por separado en
`window.EV3RenderDiagnostics()`, sin ocultar retrasos de inicio ni atribuirlos
erróneamente al renderizado.

También se conserva la cancelación cooperativa de `wait()`. La interfaz Web
mantiene el flujo robusto `cargar código → ejecutar`, verificado en navegador
real; la prueba de cadencia y los flujos de finalización aprobaron.
