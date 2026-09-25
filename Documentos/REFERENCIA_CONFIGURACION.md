# Referencia de configuracion

> Estado: revisado al 2026-08-05. Versión aplicable: `1.5.0`. Fuente de verdad:
> `simulador_ev3/web/config.py` y `simulador_ev3/web/waitress_server.py`.

## Variables principales

| Variable | Predeterminado | Uso |
|---|---:|---|
| `EV3_WEB_HOST` | `127.0.0.1` | Host de Waitress/servidor. |
| `EV3_WEB_PORT` | `5050` | Puerto HTTP. |
| `EV3_WEB_THREADS` | `8` | Hilos de Waitress. |
| `EV3_WEB_APP_ENV` | `development` | Entorno; `production` activa validaciones estrictas. |
| `EV3_WEB_SECRET_KEY` | clave local | Firma de cookies; obligatoria y privada en produccion. |
| `EV3_WEB_SCRIPT_MAX_RUNTIME_S` | `0.0` | Limite de script; debe ser positivo en produccion. |
| `EV3_WEB_MAX_ACTIVE_SESSIONS` | `20` | Maximo de sesiones. |
| `EV3_WEB_MAX_RUNNING_SIMULATIONS` | `8` | Maximo de simulaciones activas. |
| `EV3_WEB_SESSION_IDLE_TIMEOUT_MIN` | `45` | Expiracion por inactividad. |
| `EV3_WEB_SESSION_COOKIE_SECURE` | `false` | Debe ser `true` con HTTPS en produccion. |
| `EV3_WEB_ENABLE_SECURITY_HEADERS` | `true` | Cabeceras HTTP de seguridad. |
| `EV3_WEB_WEB_SSE_ENABLED` | `true` | Eventos en vivo; existe fallback de polling. |
| `EV3_WEB_WEB_POLLING_INTERVAL_MS` | `900` | Intervalo de polling de respaldo. |
| `EV3_LOCAL_RUNTIME_ENABLED` | `false` | Compatibilidad local; no es la ruta normal. |

Las rutas de ejemplos, mundos, imagenes y los parametros Redis/file mirror se
documentan en `GUIA_WEB_FLASK_WINDOWS.md` y las guias especializadas de cPanel.
No copiar credenciales reales en esta tabla ni en ningun archivo versionado.

## Diagnostico y metricas

- `GET /healthz`: version, sesiones, worker y estado de backend.
- `GET /metrics`: resumen JSON de operacion.
- `GET /metrics?format=prometheus` o cabecera `Accept: text/plain`: metricas
  Prometheus de solicitudes, errores, sesiones, workers, memoria, CPU, cola y ticks.
- `GET /operations`: panel local de operaciones cuando se habilita la Web.

Ejemplo local:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5050/healthz
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5050/metrics?format=prometheus
```
