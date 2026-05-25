# Informe de Testeo Integral - 2026-05-25

## Objetivo
Validar estabilidad funcional y regresiones del Simulador EV3 (desktop + web), con foco adicional en recuperacion de sesion para hosting compartido.

## Alcance ejecutado
1. Pruebas unitarias/integracion/e2e de todo el repositorio.
2. Smoke test de endpoints y flujo API web.
3. Verificacion de compilacion Python.
4. Verificacion de wiring de recuperacion de sesion (file mirror), idempotencia de `start`, retry/backoff y fallback stream->polling.

## Comandos ejecutados
1. `.\.venv\Scripts\python.exe -m pytest -q`
2. `.\.venv\Scripts\python.exe -m compileall -q simulador_ev3 scripts tests`
3. `powershell -ExecutionPolicy Bypass -File .\scripts\smoke_web.ps1`
4. `.\.venv\Scripts\python.exe scripts/check_runtime_code.py`

## Resultados
1. Suite completa: **577 passed**.
2. Compilacion: **OK** (sin errores).
3. Smoke web local: **OK** en rutas criticas (`/healthz`, `/`, `/worlds`, `/help`, assets, sesion, snapshot, debug endpoints).
4. Runtime code check: **OK**
   - `has_file_store_import: True`
   - `has_create_metadata_store: True`
   - `metadata_mirror.enabled: True`
   - `metadata_mirror.driver: file`

## Cambios validados en esta iteracion
1. Single-flight frontend para evitar doble ejecucion en `start`.
2. Idempotencia backend de `start` por `request_id` con TTL configurable.
3. Retry/backoff para `loadScript`, `start` y `snapshot`.
4. Recuperacion silenciosa de sesion con `reuse: true`.
5. Reintento de reconexion a stream cuando esta en polling fallback.
6. Timeout de sesion por defecto ajustado a **45 minutos**.
7. Versionado de assets actualizado para invalidar cache (`session-retry-v4`).

## Hallazgos y riesgo residual
1. El codigo local y los tests quedan en verde.
2. Persisten riesgos operativos de infraestructura compartida (proxy/CDN/HTTP2/Passenger) fuera del control del aplicativo.
3. Si en produccion reaparece "sesion no existe o expiro", revisar primero:
   - cache estatico no invalidado,
   - app no reiniciada,
   - worker antiguo sirviendo codigo previo.

## Criterios de salida (cumplidos)
1. 0 tests fallidos.
2. Smoke API exitoso.
3. Sin errores de compilacion.
4. Documentacion tecnica y operativa actualizada.
