# Plan de verificación de liberación Web

| ID | Defecto / flujo | Automatización requerida | Prueba manual visible | Aprobación |
| --- | --- | --- | --- | --- |
| REL-DBG-001 | WEB-DBG-018 | E2E: iniciar debug, detener, reset y comprobar `created` | Repetir con breakpoint y sin breakpoint | UI recupera controles y no recibe eventos viejos |
| REL-RT-001 | WEB-RT-011 | Contrato + E2E con `1 / 0` | Ejecutar y revisar canvas/LCD/telemetría | Estado `error`, un snapshot coherente, Ejecutar habilitado |
| REL-WORLD-001 | WEB-WE-002 | API + E2E de colocar/guardar | Crear mundo con muro, meta y sensor | Sin error de worker; CRUD persistente correcto |
| REL-PERF-001 | WEB-PERF-017 | Reloj determinista + E2E | Cronometrar wait, recta, giro y radar | Dentro de umbrales del diseño y render continuo |
| REL-TRACE-001 | WEB-TRACE-019 | Contrato + E2E | Iniciar traza y avanzar tick | Tick y snapshot incrementan, o control no promete avance |
| REL-UI-001 | WEB-RT-013 | E2E recarga en estados terminales | Recargar tras éxito, error y reset | Botones habilitados según estado recibido |

La regresión se ejecutará en 1920×1080, 1280×800, 1024×768 y 390×844, en tema
claro y oscuro cuando el flujo sea visual. Cualquier caso no ejercitable debe
quedar BLOCKED con el motivo y evidencia; nunca se convierte en PASS por lectura
de código.

## Ejecución registrada — 2026-08-04

| Comando | Resultado | Evidencia |
| --- | --- | --- |
| `pytest tests/runtime/test_isolated_worker.py tests/web tests/e2e/test_web_playwright.py -q` | PASS: 221 pruebas | Runtime aislado, API, contratos y Chromium Playwright. |
| Mismo comando con `--cov=simulador_ev3.web --cov-report=term-missing` | PASS: 221 pruebas, 81.83 % Web | Supera el umbral configurado de 70 %. |
| `ruff check simulador_ev3 tests` | PASS | Sin incidencias. |
| `mypy simulador_ev3` | PASS | 114 archivos productivos sin errores. |
| `bandit -q -r simulador_ev3` | PASS con observaciones | 0 altos; 2 medios asociados al `exec` deliberado del sandbox y 54 bajos históricos. |
| `pip-audit -r requirements.txt` | PASS | Sin vulnerabilidades conocidas. |
| Repetición final: `node --check ...simulation_app.js` y `pytest tests/runtime/test_isolated_worker.py tests/web tests/e2e/test_web_playwright.py -q` | PASS: 221 pruebas | Incluye la regresión de menús cargados por SSE fuera de orden. |

### Revalidación visible dirigida

- En `http://127.0.0.1:5054/`, con `EV3_WORKER_ISOLATION_ENABLED=true`, una
  sesión nueva pasó de **Tick 0** a **Tick 1** mediante **Trazas → Iniciar
  registro → Avanzar un tick** y anunció “Se avanzó un tick de simulación.”
- En la misma sesión aislada se comprobó previamente un breakpoint en pausa,
  congelación del tick, reanudación y reinicio a `created`; también se verificó
  el estado terminal `error` con `1 / 0` y la recuperación de controles.
- El editor de mundos permitió colocar robot y muro, validar y aplicar el mundo
  sin error de worker. El guardado mediante `prompt` nativo queda pendiente de
  una pasada manual en navegador de escritorio: el navegador integrado de la
  campaña no admite ese diálogo, aunque los E2E Chromium del CRUD aprobaron.
- El perfilado de una espera de 2 s identificó una latencia de hasta 1 s en el
  stream SSE: la condición no se despierta al recibir un evento de una cola
  multiproceso. Tras limitar su espera a 50 ms y publicar snapshots del worker
  a 30 Hz, la medición visible fue 2.10 s simulados / 2.32 s de pared (1.11),
  dentro del rango 0.85–1.25 definido por este cambio.
- La suite completa detectó que un evento inicial `ready` retrasado podía
  desbloquear opciones de Trazas durante una ejecución. La UI descarta ahora
  esos eventos obsoletos mientras la ejecución actual está activa; la regresión
  E2E de bloqueo y restauración de todos los menús aprobó.
