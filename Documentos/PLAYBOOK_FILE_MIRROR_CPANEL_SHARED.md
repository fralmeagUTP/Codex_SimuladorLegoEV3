# Playbook File Mirror (cPanel Shared sin Redis)

Fecha: 2026-05-25
Objetivo: compartir estado de sesiones entre workers sin Redis ni root.

## 1. Cuándo usar este playbook

Usar cuando tu proveedor confirma que el plan compartido no soporta Redis.

## 2. Variables exactas en cPanel

Configura estas variables:

```text
EV3_WEB_SESSION_BACKEND=memory
EV3_WEB_REDIS_ENABLED=false
EV3_WEB_REDIS_URL=
EV3_WEB_FILE_MIRROR_ENABLED=true
EV3_WEB_FILE_MIRROR_DIR=/tmp/ev3web_session_mirror
```

Opcional:

```text
EV3_WEB_REDIS_PREFIX=ev3web
```

## 3. Reinicio y validación

1. Guardar variables.
2. Restart app en cPanel.
3. Validar healthz con script:

```bash
python scripts/verify_healthz_redis.py "https://nyquist.app/simuladorlego/healthz" --mode file --show-json
```

Esperado:

- `status = "ok"`
- `session_manager.session_backend = "memory"`
- `session_manager.metadata_mirror.driver = "file"`
- `session_manager.metadata_mirror.enabled = true`
- `session_manager.degraded_to_memory = false`

## 4. Prueba funcional recomendada

1. Abrir simulador.
2. Cargar script y mundo.
3. Ejecutar y detener.
4. Recargar navegador.
5. Verificar que script/mundo no se pierden.

## 5. Troubleshooting

Si `metadata_mirror.enabled=false`:

1. Revisar permisos de escritura de `EV3_WEB_FILE_MIRROR_DIR`.
2. Usar ruta segura de sistema (`/tmp/ev3web_session_mirror`).
3. Reiniciar la app.

Si aparece `degraded_to_memory=true`:

- Revisar `degraded_reason` en `healthz`.
- Confirmar que la carpeta del mirror existe y es escribible.

## 6. Rollback rápido

Para volver al modo simple sin mirror:

```text
EV3_WEB_FILE_MIRROR_ENABLED=false
```

Reiniciar app.
