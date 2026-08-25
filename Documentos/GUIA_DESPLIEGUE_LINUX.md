# Despliegue Linux para aula o servidor

> Estado: revisado al 2026-08-05. Versión aplicable: `1.5.0`. Audiencia:
> operacion. Fuente ejecutable: `Dockerfile` y `simulador_ev3/web/config.py`.

## Perfil endurecido de contenedor

Para producción use `docker-compose.production.yml`, con secretos entregados por
el entorno del servidor y no por Git:

```bash
export EV3_WEB_SECRET_KEY='secreto-aleatorio-de-al-menos-32-caracteres'
export EV3_WEB_OPERATIONS_TOKEN='otro-secreto-operativo-de-al-menos-32-caracteres'
docker compose -f docker-compose.production.yml up -d --build
```

El perfil ejecuta como usuario no privilegiado, usa raíz de solo lectura, crea
`/tmp/ev3` como `tmpfs` privado, limita memoria, CPU y PIDs, elimina capacidades
Linux y activa `no-new-privileges`. El límite de PIDs es el límite del
contenedor, no una garantía de que cada script use una cantidad determinada de
procesos. El worker bloquea red dentro de Python; la denegación de egress a
nivel de red debe configurarse además en el firewall, proxy o política de red
de Nyquist/Docker.

Los workers usan sólo `/tmp/ev3/workers`; al iniciar, la aplicación limpia
directorios `ev3-worker-*` vencidos sin borrar archivos ajenos ni terminar
procesos activos. Ajuste `EV3_WEB_WORKER_TEMP_MAX_AGE_S` si su operación
necesita otra antigüedad.

## Requisitos

- Docker o motor compatible.
- HTTPS inverso cuando la aplicacion sea accesible fuera de localhost.
- Una clave privada de al menos 32 caracteres para produccion.

## Construccion y ejecucion

```bash
docker build -t simulador-ev3:local .
docker run --rm -p 5050:5050 \
  -e EV3_WEB_APP_ENV=production \
  -e EV3_WEB_SECRET_KEY='reemplazar-por-clave-unica-de-al-menos-32-caracteres' \
  -e EV3_WEB_SCRIPT_MAX_RUNTIME_S=30 \
  -e EV3_WEB_SESSION_COOKIE_SECURE=true \
  simulador-ev3:local
```

El contenedor se ejecuta como el usuario `ev3` sin privilegios. No introducir
secretos en Dockerfile, imagenes, argumentos de build ni repositorio.

## Verificacion

```bash
curl --fail http://127.0.0.1:5050/healthz
curl --fail 'http://127.0.0.1:5050/metrics?format=prometheus'
```

La primera respuesta debe informar `status: ok` y la version distribuible. La
segunda contiene metricas de solicitudes, sesiones y workers. El endpoint de
metricas debe quedar protegido por red o proxy en un despliegue no local.

## Persistencia y recuperacion

Los mundos se almacenan como JSON. Montar un volumen de solo los directorios
necesarios para conservar mundos de aula y aplicar backup externo. Las sesiones
en memoria son temporales; Redis o file mirror son configuraciones avanzadas
documentadas en los playbooks de cPanel y no son requisito para aula local.

Ante un reinicio, las pestanas deben crear una sesion nueva. Ante una caida
recuperable del worker, la sesion intenta restaurar el script y la configuracion
documentados; revisar `/healthz`, logs y la notificacion de la interfaz.

## Operacion segura

- Usar proxy HTTPS y `EV3_WEB_SESSION_COOKIE_SECURE=true` en produccion.
- Definir limites de sesiones y simulaciones segun memoria disponible.
- Conservar `EV3_WEB_ENABLE_SECURITY_HEADERS=true` salvo excepcion justificada.
- Consultar `SEGURIDAD_Y_USO_EN_AULA.md` y `REFERENCIA_CONFIGURACION.md`.

## Compuerta de liberación

Antes de publicar una imagen, ejecutar la construcción, `/healthz`, métricas y
una simulación corta; registrar tag, digest y commit. La campaña del 2026-08-05
aprobó construcción y smoke HTTP 200 como usuario no privilegiado. Ese resultado
es evidencia histórica del commit evaluado y debe repetirse para una imagen nueva.
