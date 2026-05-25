# Plan tecnico de migracion a Redis por fases (sin romper lo actual)

Fecha: 2026-05-25
Estado: aprobado para ejecucion incremental

## Objetivo

Eliminar errores por cambio de worker (`SESSION_NOT_FOUND`) en hosting multi-proceso, migrando sesion runtime desde memoria local a Redis de forma gradual y reversible.

## Copia de seguridad previa (ya creada)

- `backups/backup_20260525_005442.bundle`
- `backups/backup_20260525_005454_source.zip`

## Alcance

- Web Flask (`simulador_ev3/web`)
- Sesiones runtime de simulacion
- Diagnostico operacional en `GET /healthz`

No incluye cambios de UX funcional en simulacion ni cambios de API publica.

## Fase 0 (hecha): observabilidad y banderas

Objetivo: preparar la migracion sin activar Redis en runtime.

Implementado:

- Configuracion nueva:
  - `EV3_WEB_SESSION_BACKEND`
  - `EV3_WEB_REDIS_ENABLED`
  - `EV3_WEB_REDIS_URL`
  - `EV3_WEB_REDIS_PREFIX`
  - `EV3_WEB_REDIS_CONNECT_TIMEOUT_S`
  - `EV3_WEB_REDIS_SOCKET_TIMEOUT_S`
  - `EV3_WEB_REDIS_HEALTHCHECK_PING`
- Diagnostico en `healthz`:
  - `worker_id`, `worker_pid`
  - `session_manager` (backend y contadores)
  - `redis` (configurado/disponible/ping opcional)
- Contadores de errores de sesion:
  - `session_not_found_errors`
  - `session_forbidden_errors`
  - `session_expired_errors`
- Dependencia preparada:
  - `requirements.txt` incluye `redis>=5.1,<8`
  - extra opcional `web-redis` en `pyproject.toml`

Rollback Fase 0:

- Desactivar banderas Redis (o no definirlas).
- No hay impacto funcional, backend sigue `memory`.

## Fase 1 (hecha): store Redis pasivo (mirror de metadata)

Objetivo: escribir metadata de sesion en Redis sin leerla como fuente primaria.

Implementado:

- Adaptador `RedisSessionStore` (keys por `session_id` con prefijo configurable).
- `SessionManager` ahora espeja metadata en create/get(touch)/close/cleanup/eviction.
- Endpoints de control de ejecucion sincronizan metadata (`start/pause/resume/stop/reset`).
- Fuente de verdad sigue siendo memoria (`SESSION_BACKEND=memory`).

Validacion:

- Suite web local: `91 passed`.
- Sin cambios visibles para usuario final.

Rollback:

- `EV3_WEB_REDIS_ENABLED=false`.

## Fase 2 (hecha): dual-read con fallback a memoria

Objetivo: permitir recuperar sesion aunque cambie el worker.

Implementado:

- En `get_session`: si no existe en memoria, intentar recuperar metadata desde Redis.
- Validacion de propiedad por `owner_token_hash`.
- Si coincide token: recrear sesion en el worker actual y restaurar checkpoint:
  - `source_code`
  - mundo actual (`world_wrapper`)
  - `breakpoints` y `watches`
  - metadata de estado para UI
- Contadores de recuperacion/falla:
  - `sessions_recovered_from_mirror`
  - `session_recovery_failures`
- Sincronizacion de checkpoint despues de cambios de script/mundo/editor/control.

Limitacion conocida (aceptada en Fase 2):

- No se reanuda una ejecucion en curso al migrar de worker.
- Si la sesion se recupera durante `running/paused`, queda en `ready` por seguridad.
- La continuidad de ejecucion multi-worker completa se aborda en Fase 3.

Rollback:

- Forzar `SESSION_BACKEND=memory`.

## Fase 3 (hecha): Redis como fuente primaria de metadata de sesion

Objetivo: eliminar dependencia de afinidad por proceso.

Implementado:

- `SESSION_BACKEND=redis` habilita modo primario Redis en `SessionManager`.
- En modo Redis primario:
  - escritura/lectura de metadata por mirror Redis como fuente compartida,
  - cache in-memory por worker para objetos vivos,
  - recuperacion de checkpoint al cambiar de worker.
- Degradacion controlada:
  - si Redis falla, la app sigue en memoria sin detener servicio,
  - se marca `degraded_to_memory=true` y `degraded_reason` en diagnostico.
- `healthz` expone estado operacional:
  - `is_redis_primary`
  - `degraded_to_memory`
  - `degraded_reason`

Validacion:

- Pruebas unitarias/web locales: `96 passed`.
- Recuperacion entre workers de script+mundo+debug basico validada en tests.

Rollback:

- `SESSION_BACKEND=memory`.

## Fase 4: endurecimiento y operacion

Objetivo: estabilidad operativa.

Cambios:

- Circuit breaker si Redis no responde.
- Métricas de latencia Redis y tasa de recuperacion.
- Limpieza de claves huerfanas.
- Documentacion final y runbook de incidentes.

Validacion:

- Prueba de degradacion (Redis caido).
- App debe seguir operando en modo memoria temporal.

Rollback:

- Desactivar Redis y reiniciar app.

## Requisitos exactos en hosting para Redis

1. Servicio Redis accesible por red desde la app Python (host:puerto).
2. URL de conexion establecida en:
   - `EV3_WEB_REDIS_URL=redis://usuario:clave@host:puerto/0`
3. Libreria Python redis instalada en el virtualenv:
   - `pip install -r requirements.txt`
4. Permiso de salida TCP desde el hosting al puerto Redis (normalmente 6379 o TLS).
5. Si Redis exige TLS, usar URL `rediss://...`.

## Alternativa para hosting compartido sin Redis (implementada)

Si el proveedor no permite Redis, usar mirror por archivos:

- `EV3_WEB_REDIS_ENABLED=false`
- `EV3_WEB_FILE_MIRROR_ENABLED=true`
- `EV3_WEB_FILE_MIRROR_DIR=/tmp/ev3web_session_mirror`

Esto mantiene recuperacion entre workers sin servicios externos.

## Variables recomendadas para activar por fases

Fase 0:

```env
EV3_WEB_SESSION_BACKEND=memory
EV3_WEB_REDIS_ENABLED=false
EV3_WEB_REDIS_HEALTHCHECK_PING=false
```

Fase 1-2 (canary):

```env
EV3_WEB_SESSION_BACKEND=memory
EV3_WEB_REDIS_ENABLED=true
EV3_WEB_REDIS_URL=redis://usuario:clave@host:6379/0
EV3_WEB_REDIS_PREFIX=ev3web
EV3_WEB_REDIS_HEALTHCHECK_PING=true
```

Fase 3:

```env
EV3_WEB_SESSION_BACKEND=redis
EV3_WEB_REDIS_ENABLED=true
EV3_WEB_REDIS_URL=redis://usuario:clave@host:6379/0
```

## Criterio de exito

- Cero errores recurrentes "La sesion no existe o expiro" por cambio de worker.
- `healthz` consistente con backend/worker.
- Sin regresiones en suite web.
