# Playbook Redis cPanel - Fase 3

Fecha: 2026-05-25
Objetivo: activar `SESSION_BACKEND=redis` con degradacion segura a memoria.

## 1. Prerrequisitos

- App Python ya publicada en cPanel (`wsgi.py` + entrypoint `app`).
- `requirements.txt` instalado en el virtualenv de cPanel (incluye `redis>=5.1,<8`).
- Redis accesible desde el hosting (`host:puerto`) con credenciales validas.

## 2. Variables exactas (cPanel -> Environment Variables)

Configurar estas variables:

```text
EV3_WEB_SESSION_BACKEND=memory
EV3_WEB_REDIS_ENABLED=true
EV3_WEB_REDIS_URL=redis://usuario:clave@host:6379/0
EV3_WEB_REDIS_PREFIX=ev3web
EV3_WEB_REDIS_CONNECT_TIMEOUT_S=0.3
EV3_WEB_REDIS_SOCKET_TIMEOUT_S=0.3
EV3_WEB_REDIS_HEALTHCHECK_PING=true
```

Notas:

- Si tu proveedor exige TLS, usa `rediss://...`.
- Deja `EV3_WEB_SESSION_BACKEND=memory` en el primer reinicio (canary).

## 3. Activacion en dos pasos (recomendado)

### Paso A (canary sin riesgo)

1. Guardar variables.
2. Restart app en cPanel.
3. Abrir `https://tu-dominio/tu-app/healthz`.

Esperado:

- `status = "ok"`
- `redis.enabled = true`
- `redis.url_configured = true`
- `session_manager.session_backend = "memory"`
- `session_manager.degraded_to_memory = false`

Si esto falla, no pases al Paso B.

Validacion automatica opcional:

```bash
python scripts/verify_healthz_redis.py "https://tu-dominio/tu-app/healthz" --mode canary
```

### Paso B (Redis primario)

1. Cambiar solo:

```text
EV3_WEB_SESSION_BACKEND=redis
```

2. Guardar.
3. Restart app.
4. Validar de nuevo `healthz`.

Esperado:

- `session_manager.is_redis_primary = true`
- `session_manager.degraded_to_memory = false`
- `redis.client_available = true`

Validacion automatica opcional:

```bash
python scripts/verify_healthz_redis.py "https://tu-dominio/tu-app/healthz" --mode primary
```

## 4. Prueba funcional obligatoria

1. Abrir la app en navegador A.
2. Cargar ejemplo + mundo.
3. Ejecutar y detener.
4. Recargar (F5).
5. Verificar que script/mundo siguen.
6. Revisar `healthz` y confirmar aumento de:
   - `sessions_recovered_from_mirror` (si hubo cambio de worker)

## 5. Lectura rapida de fallos en healthz

Si ves:

- `degraded_to_memory = true`
- `degraded_reason` con prefijo `redis_...`

Significa que Redis fallo y la app se auto-protegió usando memoria local.

Acciones:

1. Verificar `EV3_WEB_REDIS_URL`.
2. Confirmar conectividad saliente al puerto Redis desde hosting.
3. Revisar si Redis requiere TLS (`rediss://`).
4. Reiniciar app tras corregir.

## 6. Rollback inmediato (30 segundos)

Si necesitas volver al modo estable:

```text
EV3_WEB_SESSION_BACKEND=memory
```

Luego:

1. Guardar variables.
2. Restart app.
3. Confirmar en `healthz`:
   - `session_manager.session_backend = "memory"`
   - `session_manager.is_redis_primary = false`

## 7. Criterio de exito

- No reaparece el error de sesion perdida por cambio de worker.
- `healthz` estable con `degraded_to_memory=false`.
- Flujo de ejecutar/pausar/detener funciona tras recargas del navegador.
