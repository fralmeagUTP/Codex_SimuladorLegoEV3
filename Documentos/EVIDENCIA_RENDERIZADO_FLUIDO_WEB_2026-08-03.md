# Evidencia de renderizado fluido Web — 2026-08-03

> Actualización posterior: la cadencia predeterminada de snapshots es 50 Hz,
> alineada con el motor. La primera versión de esta evidencia registraba 30 Hz.

## Resultado completo

- 122 pruebas unitarias e integración Web aprobadas.
- 51 pruebas E2E Playwright aprobadas, incluidas resoluciones de escritorio y
  móvil, reinicio, pausa/reanudación, canvas, menús, temas y un barrido breve
  con ultrasónico.
- La sintaxis del controlador JavaScript se verificó con `node --check`.
- Ruff se ejecuta solamente sobre fuentes Python; los archivos JavaScript se
  validan con Node y con las pruebas que los ejecutan en un navegador real.

## Cambio validado

`openspec/changes/mejorar-renderizado-fluido-web` conserva el motor de
simulaciÃ³n a 50 Hz, publica snapshots Web a 30 Hz por defecto y pinta la pose
del robot mediante `requestAnimationFrame` entre dos snapshots compatibles.
La telemetrÃ­a, la LCD, los sensores y el estado siguen usando exclusivamente
el snapshot autoritativo.

## Salvaguardas verificadas

- No se interpola despuÃ©s de `finished`, `stopped`, `timed_out`, `error`,
  `created`, una colisiÃ³n ni un cambio de generaciÃ³n.
- El snapshot terminal se publica antes del evento terminal.
- La capa estÃ¡tica del mundo permanece en cachÃ© y solo se reconstruye al
  cambiar mundo, tamaÃ±o del canvas o propiedades visuales pertinentes.
- SSE sigue siendo el canal preferido y el controlador existente conserva el
  polling como recuperaciÃ³n.
- `EV3RenderDiagnostics()` permite inspeccionar contadores de snapshots y
  frames en desarrollo, sin mostrarse a estudiantes.

## Comandos ejecutados

```powershell
.\.venv\Scripts\python.exe -m pytest tests\web\test_render_interpolation_controller.py tests\web\test_web_units.py tests\web\test_web_app.py -q
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -q -k "ultrasonic_radar_sweep or simulation_page_runs_default_script or terminal_snapshot_synchronizes_status_telemetry_and_lcd or map_canvas_and_tools_stay_inside_viewport"
.\.venv\Scripts\ruff.exe check simulador_ev3\web\config.py simulador_ev3\web\services\simulation_session.py tests\web\test_render_interpolation_controller.py tests\web\test_web_units.py
```

Resultados de esta iteraciÃ³n: 122 pruebas unitarias/integraciÃ³n Web aprobadas
despuÃ©s de sumar el contrato terminal; 7 pruebas E2E relevantes aprobadas;
Ruff sin incidencias. La ejecuciÃ³n completa queda registrada al finalizar la
baterÃ­a global de este cambio.
