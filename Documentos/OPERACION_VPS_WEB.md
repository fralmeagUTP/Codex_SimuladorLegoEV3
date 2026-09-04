# Operación del VPS Web de BotLab Studio

Esta guía aplica al perfil Docker/Caddy de un VPS Linux de 2 vCPU y 8 GB. No
requiere autenticación de usuarios: el token operativo protege exclusivamente
los diagnósticos del servicio.

## Valores operativos iniciales

- Máximo de sesiones activas: 20.
- Máximo de simulaciones simultáneas: 4.
- Límite por script: 120 segundos.
- Contenedor de aplicación: 2 CPU, 768 MiB y 64 PIDs.
- Logs Docker: cinco archivos de hasta 10 MiB por servicio.

No aumente la concurrencia sin una campaña de carga que registre CPU, memoria,
latencia, errores y experiencia visual del navegador.

## Staging local equivalente

Antes del VPS, se puede validar el empaquetado en Docker sin usar los puertos
80/443 del equipo: copie `.env.production.example` a `.env.production`, use
secretos locales desechables, `EV3_WEB_PUBLIC_HOST=localhost` y los puertos
`8080`/`8443`. Inicie el perfil y compruebe `https://localhost:8443` aceptando
el certificado local de Caddy. Al terminar, ejecute `docker compose down -v` y
elimine el archivo temporal `.env.production`.

## Compuerta de aceptación previa a liberar

Tras desplegar en staging o VPS, exporte el token desde el almacén seguro y
ejecute la compuerta. No se imprime ni persiste el token, la cookie o el ID de
la sesión temporal.

```bash
export EV3_WEB_OPERATIONS_TOKEN='token-operativo-del-almacen-seguro'
./scripts/validate_vps_release.sh https://SIMULADOR.SU-DOMINIO
unset EV3_WEB_OPERATIONS_TOKEN
```

La compuerta verifica contenedores, red interna de Waitress, HTTPS, redirección
desde HTTP, salud, métricas, cookie segura y cierre de una sesión temporal.
Para staging local con puertos alternos añada, antes de ejecutarla:

```bash
export EV3_WEB_HTTP_URL=http://localhost:8080
```

## Consulta diaria

Desde la carpeta del repositorio en el VPS:

```bash
export EV3_WEB_OPERATIONS_TOKEN='token-operativo-del-almacen-seguro'
./scripts/vps_healthcheck.sh https://SIMULADOR.SU-DOMINIO
docker compose -f docker-compose.production.yml ps
docker stats --no-stream simulador-ev3 caddy
df -h / /srv/simulador-ev3
docker compose -f docker-compose.production.yml logs --tail=100 simulador-ev3 caddy
unset EV3_WEB_OPERATIONS_TOKEN
```

Investigue antes de abrir más cupos si CPU se sostiene por encima de 80 %, la
memoria disponible baja de 1 GB, hay reinicios, `5xx`, workers huérfanos o el
disco supera 80 %.

## Salud, métricas y tablero

- `/healthz`: disponibilidad y diagnóstico protegido.
- `/metrics?format=prometheus`: solicitudes, `5xx`, sesiones, workers, memoria
  de workers, CPU y cola.
- `/operations`: tablero de operación protegido por la misma política.

No publique estos endpoints ni el token en material docente. Para un monitor
externo, configure el token como secreto de ese monitor; no lo coloque en una
URL, script versionado, navegador compartido o captura de pantalla.

## Actualización controlada

1. Avise que las sesiones son efímeras y se cerrarán durante el mantenimiento.
2. Compruebe la salud actual y cree un respaldo no secreto:

   ```bash
   sudo EV3_VPS_SERVICE_OWNER="$USER" ./scripts/prepare_vps_storage.sh
   ./scripts/backup_vps_release.sh /srv/simulador-ev3
   git rev-parse HEAD
   ```

3. Registre el commit actual y obtenga el commit o etiqueta aprobado:

   ```bash
   git fetch --tags origin
   git switch <etiqueta-o-commit-aprobado>
   docker compose -f docker-compose.production.yml --env-file .env.production up -d --build
   ```

4. Ejecute `vps_healthcheck.sh`, una simulación corta y la comprobación de dos
   sesiones independientes. Registre resultado, fecha y versión.

## Reversión

1. Detenga nuevas actividades y anote los errores sin copiar tokens.
2. Vuelva al commit o etiqueta anterior validado.
3. Reconstruya e inicie con el mismo archivo `.env.production`:

   ```bash
   git switch <etiqueta-anterior-validada>
   docker compose -f docker-compose.production.yml --env-file .env.production up -d --build
   ```

4. Verifique salud, métricas, HTTPS y aislamiento en dos navegadores. Rote
   secretos únicamente si hubo sospecha de exposición.

## Respaldo y limpieza

`backup_vps_release.sh` conserva solo configuración versionada y documentación.
No respalda `.env.production`, certificados, cookies, tokens, sesiones, trazas
ni temporales. Esos secretos se conservan exclusivamente en el gestor de
secretos o respaldo cifrado administrado por la institución.

Los temporales de workers se alojan en `tmpfs`; se eliminan al reiniciar el
contenedor y además el runtime limpia residuos propios caducados. Revise el
espacio de Docker y aplique la política institucional de retención antes de
ejecutar limpieza de imágenes o volúmenes.
