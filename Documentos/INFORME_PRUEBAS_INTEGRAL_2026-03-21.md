# Informe de Pruebas Integral
Fecha: 2026-03-21  
Proyecto: Simulador EV3 Pybricks

Actualizacion documental: 2026-05-20  
Version vigente del proyecto: 1.3.0

## 1. Objetivo
Verificar de forma integral que el programa funciona correctamente (núcleo, API Pybricks, runtime, persistencia, UI y smoke de release), y documentar problemas encontrados.

## 2. Nuevas pruebas agregadas
Se añadió la batería:

- `tests/release/test_full_program_health.py`

Cobertura nueva:

- Flujo E2E con `SimulationService` + carga de mundo.
- Script integrado que usa:
  - Motores (`Motor`, `DriveBase`)
  - Sensores (`TouchSensor`, `InfraredSensor`, `ColorSensor`, `UltrasonicSensor`)
  - Brick (`light`, `screen`, `speaker`)
- Validación de telemetría efectiva (motores activos, sensores S1..S4, LED/LCD/sonido).
- Smoke extendido de ejemplos reales:
  - `01_basico_avanzar.py`
  - `04_sensor_ultrasonido.py`
  - `06_siguelineas_basico.py`
  - `11_ledRojo.py`
  - `12_pantalla_altavoz_test.py`

## 3. Ejecución realizada
Comandos ejecutados:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\release\test_full_program_health.py
.\.venv\Scripts\python.exe -m pytest -q tests\ui\test_ui.py::TestMainWindow::test_cmd_run_calls_service
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado final:

- `437 passed in 33.02s`

## 4. Problemas encontrados

### PD-01 (resuelto): Test UI inestable por condición temporal
- Evidencia inicial: falló `tests/ui/test_ui.py::TestMainWindow::test_cmd_run_calls_service`.
- Causa: el test asumía estado `RUNNING` inmediato después de `_cmd_run("x = 1")`.  
  El script puede terminar muy rápido y pasar a `STOPPED` antes de la aserción.
- Acción: se ajustó la aserción para aceptar `RUNNING` o `STOPPED`.
- Estado: **resuelto**.

### PD-02 (no bloqueante): Alto volumen de salida en ejemplos con bucles de impresión
- Observación: ejemplos con `print` dentro de `while True` (p. ej. `Documentos/Ejemplos/04_sensores.py`) pueden generar salida masiva en consola durante ejecuciones largas.
- Impacto: ruido de logs y degradación de rendimiento al depurar.
- Recomendación: limitar frecuencia de impresión o usar muestreo cada N iteraciones.
- Estado: **abierto (mejora de calidad, no funcional crítico)**.

## 5. Conclusión
El programa pasa la verificación integral automatizada actual: **sin fallos funcionales bloqueantes en la suite**.  
Se detectó y corrigió un problema de estabilidad en pruebas UI, y queda una mejora recomendada de higiene de logs en scripts de ejemplo.

## 6. Actualizacion 2026-05-20

La version `1.3.0` agrega validacion web y E2E sobre lo documentado originalmente:

- `tests\web`: pruebas unitarias/integracion Flask y contratos web.
- `tests\e2e`: pruebas Playwright sobre simulacion, editor de mundos, ayuda y sesiones independientes.
- `tests\application`: validacion de estado `stopped` cuando un script termina naturalmente.
- Evidencia visual generada en `Documentos\EVIDENCIA_WEB_2026-05-20`.

Ultima validacion integrada ejecutada:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\web tests\e2e tests\application
```

Resultado: `117 passed`.
