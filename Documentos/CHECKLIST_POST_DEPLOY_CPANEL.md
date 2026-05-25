# Checklist post-deploy cPanel (nyquist.app/simuladorlego)

Usa este checklist despues de publicar en cPanel.

## 1. Configuracion en cPanel

- [ ] Python App creada/actualizada.
- [ ] Python version en 3.11+.
- [ ] Application root: `simuladorlego`.
- [ ] Application URL: `nyquist.app/simuladorlego`.
- [ ] Startup file: `wsgi.py`.
- [ ] Entry point: `app`.
- [ ] Boton Restart ejecutado.

## 2. Dependencias y entorno

- [ ] Entorno virtual activado correctamente.
- [ ] `pip install -e .` ejecutado sin errores.
- [ ] Variables EV3_WEB configuradas (`SECRET_KEY`, `WORLDS_DIR`, `EXAMPLES_DIR`, `IMAGE_ASSETS_DIR`).
- [ ] Si usaras Redis: `EV3_WEB_REDIS_ENABLED`, `EV3_WEB_REDIS_URL`, `EV3_WEB_SESSION_BACKEND` definidos correctamente.
- [ ] Permisos de escritura en `worlds/` (o `Documentos/Mundos` si aun no migraste).

## 3. Validacion funcional web

Abrir y validar:

- [ ] `http://nyquist.app/simuladorlego`
- [ ] `http://nyquist.app/simuladorlego/worlds`
- [ ] `http://nyquist.app/simuladorlego/help`
- [ ] `http://nyquist.app/simuladorlego/healthz` responde OK
- [ ] `healthz` muestra `worker_id`, `worker_pid` y bloque `redis` sin error inesperado.
- [ ] Si `SESSION_BACKEND=redis`: `healthz.session_manager.is_redis_primary=true`.
- [ ] Si Redis falla temporalmente: `healthz.session_manager.degraded_to_memory=true` y la UI sigue operativa.
- [ ] (Opcional) Ejecutar `python scripts/verify_healthz_redis.py "<URL_HEALTHZ>" --mode canary|primary`.

## 4. Flujo minimo de usuario final

- [ ] En **Mundos**, crear un mundo simple.
- [ ] Pulsar **Validar** sin errores bloqueantes.
- [ ] Pulsar **Guardar como** y exportar JSON.
- [ ] Ir a **Simulacion** por menu superior.
- [ ] Cargar un ejemplo y ejecutar script.
- [ ] Ver telemetria y estado del robot.

## 4.1 Prueba de recuperacion de sesion entre workers (Redis)

- [ ] Configurar `EV3_WEB_REDIS_ENABLED=true` y `EV3_WEB_REDIS_URL` valida.
- [ ] Abrir la app en una pestana, cargar script y mundo.
- [ ] Ejecutar una accion de edicion (por ejemplo colocar un asset) y luego detener.
- [ ] Recargar la pestana (F5) y verificar que script/mundo siguen presentes.
- [ ] Validar en `healthz` que sube `sessions_recovered_from_mirror` cuando cambia worker.

## 5. Problemas rapidos

Si algo falla:

- [ ] Revisar log Passenger: `/home/ur5cxigur1qs/logs/simuladorlego_passenger.log`.
- [ ] Confirmar que `wsgi.py` existe en app root y exporta `app`.
- [ ] Confirmar Python 3.11+ (si 3.10, corregir version en cPanel).
- [ ] Reinstalar dependencias y reiniciar app.

## 6. Cierre

- [ ] Navegacion por menu funciona sin escribir rutas manuales.
- [ ] Ayuda muestra URL publicada (`nyquist.app/simuladorlego`) y flujo para usuario final.
- [ ] Si usas Redis primario, seguir completo `Documentos/PLAYBOOK_REDIS_CPANEL_FASE3.md`.
- [ ] Si tu plan no soporta Redis, seguir `Documentos/PLAYBOOK_FILE_MIRROR_CPANEL_SHARED.md`.
