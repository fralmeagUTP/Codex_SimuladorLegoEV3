# Evidencia MMI — fase 4 — 2026-08-23

Evidencia de recorridos reales de interfaz ejecutados durante el cambio
`igualar-madurez-integral-web-tkinter`. Esta hoja no sustituye la campaña
completa pendiente y no declara aprobadas capacidades no ejercitadas.

## Entorno

- Sistema: Windows.
- Python: 3.12.5, entorno `.venv` del repositorio.
- Web: Chromium controlado por Playwright y servidor Flask de prueba local.
- Escritorio: Tkinter, escritorio Windows visible y `pywinauto`.

## Ejecuciones confirmadas

| Plataforma | Comando | Cobertura real | Resultado |
|---|---|---|---|
| Web | `.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -q -k "primary_menu_has_a_predictable_tab_order or all_primary_menu_triggers_are_reachable_in_tab_order or secondary_web_controls_are_operable_with_keyboard or simulation_menus_load_examples_worlds_and_scenarios or world_editor_builds_valid_world_and_exposes_simulation_link"` | Tabulación, apertura de menús, Enter/Escape, herramientas secundarias, carga de ejemplo/mundo/escenario y creación/aplicación de mundo Web. | 5 PASS, 50 deseleccionadas, 8.07 s. |
| Tkinter | `EV3_RUN_DESKTOP_E2E=1 .venv\Scripts\python.exe -m pytest tests\e2e\test_desktop_pywinauto.py -q -k "desktop_controls_cover_execution_debug_and_keyboard or desktop_preset_world_catalog_loads_every_world"` | Ejecutar, pausar, reanudar, detener/reiniciar, depuración, teclado y carga física de los 12 mundos preestablecidos. | 2 PASS, 4 deseleccionadas, 27.17 s. |
| Contrato compartido | `.venv\Scripts\python.exe -m pytest tests\shared\test_interface_execution_parity.py -q` | Límite, ejecución, pausa, reanudación, cancelación, reset, trazas, perfil, depuración y snapshot terminal. | 15 PASS, 0.75 s. |
| Runtime Pybricks | `.venv\Scripts\python.exe -m pytest tests\release\test_smoke_examples.py tests\release\test_full_program_health.py -q` | Ejemplos críticos y programa integral con motores, DriveBase, sensores S1–S4, LCD, LED, altavoz y telemetría. | 9 PASS, 11.81 s. |

## Resultado y límites

- No se observaron fallos en los recorridos arriba indicados.
- La ejecución inicial de las suites E2E completas no entregó un resumen final
  al recolector antes del corte de salida. Por honestidad, no se clasifica como
  PASS ni como FAIL; se reemplazó por los recorridos focalizados que sí
  produjeron resumen reproducible.
- Permanecen pendientes la ejecución GUI individual de cada ejemplo, misión,
  escenario y operación de editor, y la campaña completa de accesibilidad con
  lector de pantalla del protocolo MMI.
