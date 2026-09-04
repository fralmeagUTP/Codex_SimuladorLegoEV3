# Requerimientos técnicos y manual de despliegue Web

> Vigencia: 2026-09-02. Aplicable al Simulador EV3 Pybricks/BotLab Studio
> 1.5.0. Complementa `GUIA_INSTALACION_CPANEL.md` y `GUIA_DESPLIEGUE_LINUX.md`.

## 1. Resumen ejecutivo

La aplicación Web es una aplicación Python/Flask de estado dinámico: cada
navegador recibe una sesión de simulación y los programas Pybricks se ejecutan
en procesos hijos aislados. **No puede instalarse como sitio estático ni como
función serverless.**

La opción recomendada es un servidor Linux con Docker y proxy HTTPS. Un hosting
cPanel/Passenger es viable únicamente si su proveedor permite procesos hijos de
Python, procesos persistentes y directorios temporales privados. La aplicación
no incorpora autenticación, usuarios ni roles; las sesiones se aíslan mediante
cookies y tokens de capacidad por navegador.

## 2. Requerimientos del hosting

### 2.1 Requisitos obligatorios

| Recurso o capacidad | Requisito |
| --- | --- |
| Sistema operativo | Linux x86_64 administrado o VPS. Windows Server no es la ruta de producción soportada. |
| Python | 3.11 o 3.12. Python 3.10 no es compatible con el proyecto. |
| Aplicación persistente | WSGI/Passenger, Waitress detrás de proxy o contenedor Docker; debe conservarse entre solicitudes. |
| Procesos hijos | Debe permitir `multiprocessing`/`spawn`, espera y terminación de procesos hijos del mismo usuario. |
| HTTPS | Certificado TLS válido y redirección permanente de HTTP a HTTPS. |
| Almacenamiento | Directorio de aplicación de lectura y directorios privados de escritura para temporales y, si se usa, metadatos de sesión. |
| Red | Acceso entrante HTTPS; las salidas de workers deben poder limitarse con firewall o política de red. |
| Dominio | Dominio o subdominio configurado. Para subruta, el proveedor debe soportar correctamente WSGI bajo prefijo. |

Un plan que prohíba `fork`/`spawn`, mate procesos en segundo plano, limite la
aplicación a una solicitud muy corta o no permita definir variables de entorno
**no es apto** para el simulador.

### 2.2 Dimensionamiento recomendado

Los valores siguientes cubren la configuración predeterminada: hasta 20
sesiones activas y hasta 8 simulaciones simultáneas. Deben reducirse esos
límites si el servidor es menor.

| Perfil | CPU | RAM | Disco libre | Uso esperado |
| --- | ---: | ---: | ---: | --- |
| Piloto/aula pequeña | 2 vCPU | 4 GB | 5 GB | 10–20 usuarios conectados, hasta 4 simulaciones simultáneas. |
| Aula estándar | 4 vCPU | 8 GB | 10 GB | 20–40 usuarios conectados, hasta 8 simulaciones simultáneas. |
| Varias aulas | 8 vCPU | 16 GB | 20 GB | Requiere Redis, métricas y prueba de carga específica antes de publicar. |

No dimensione por usuarios conectados solamente: los procesos de simulación
activos son el recurso dominante. Como mínimo, el proveedor debe permitir 1
proceso WSGI más los workers configurados y un margen operativo; para el perfil
predeterminado se recomienda una cuota de al menos 16 procesos del usuario.

### 2.3 Requisitos de proxy y red

- Soportar Server-Sent Events (SSE) sin buffering y con timeout superior a 60 s.
- Preservar `Origin`, `Host`, `X-Forwarded-Proto` y `Set-Cookie`; activar
  confianza de cabeceras proxy únicamente cuando el proxy sea administrado.
- Permitir cabeceras CSP, HSTS y cookies `Secure`/`HttpOnly`/`SameSite`.
- Limitar el tamaño de solicitud a un valor acorde con los mundos JSON: 2 MiB
  es suficiente para el contrato actual; no habilitar cargas arbitrarias.
- Restringir `/healthz`, `/metrics` y `/operations` a la red administrativa o
  protegerlos con el token operativo de la aplicación.

### 2.4 Persistencia y escalado

- Para **una sola instancia**, `SESSION_BACKEND=memory` funciona y las sesiones
  se pierden de forma segura al reiniciar.
- Para varios procesos WSGI, varias instancias o balanceador, use Redis
  administrado y configure afinidad de sesión si la plataforma la requiere.
- Los mundos incluidos son de sólo lectura. Los mundos creados por usuarios no
  deben guardarse dentro del código desplegado sin un volumen y política de
  respaldo definidos.
- Los temporales de workers requieren un directorio exclusivo, por ejemplo
  `/var/tmp/simulador-ev3/workers`, propiedad del usuario de la aplicación y
  con permisos `0700`.

## 3. Variables de producción mínimas

Defina las variables en el panel del hosting o en un almacén de secretos. No
las guarde en Git, imágenes ni documentos compartidos.

```text
EV3_WEB_APP_ENV=production
EV3_WEB_SECRET_KEY=<secreto único de al menos 32 caracteres>
EV3_WEB_SESSION_COOKIE_SECURE=true
EV3_WEB_SESSION_COOKIE_PREFIX=__Host-ev3_
EV3_WEB_ENABLE_HSTS=true
EV3_WEB_OPERATIONS_ACCESS_POLICY=token
EV3_WEB_OPERATIONS_TOKEN=<segundo secreto único de al menos 32 caracteres>
EV3_WEB_MAX_ACTIVE_SESSIONS=20
EV3_WEB_MAX_RUNNING_SIMULATIONS=4
EV3_WEB_SCRIPT_MAX_RUNTIME_S=120
EV3_WEB_WORKER_TEMP_ROOT=/var/tmp/simulador-ev3/workers
EV3_WEB_WORKER_TEMP_MAX_AGE_S=3600
EV3_WEB_FILE_MIRROR_ENABLED=true
EV3_WEB_FILE_MIRROR_DIR=/var/tmp/simulador-ev3/session-mirror
EV3_WEB_RATE_LIMIT_ENABLED=true
EV3_WEB_RATE_LIMIT_SESSION_CREATE=12
EV3_WEB_RATE_LIMIT_SESSION_COMMAND=120
```

La instalación inicial debe operar con **una sola instancia Web**. Antes de
levantar una segunda réplica, Redis es obligatorio para conservar el aislamiento
de sesiones entre procesos. En ese caso agregue:

```text
EV3_WEB_SESSION_BACKEND=redis
EV3_WEB_REDIS_ENABLED=true
EV3_WEB_REDIS_URL=redis://<usuario>:<clave>@<host>:6379/0
EV3_WEB_REDIS_PREFIX=ev3web
EV3_WEB_REDIS_HEALTHCHECK_PING=true
```

El prefijo `__Host-ev3_` sólo es válido si la aplicación se entrega siempre por
HTTPS y la cookie se emite para el host sin `Domain`. Si el proveedor monta la
aplicación en una subruta, pruebe la creación de sesión antes de abrirla al
aula; no cambie la política de cookie a insegura para resolver un fallo de
proxy.

## 4. Instalación recomendada: Linux + Docker

### Paso 1. Preparar servidor

1. Cree un usuario de despliegue sin privilegios de root permanentes.
2. Instale Docker Engine y el complemento Docker Compose según la política del
   proveedor.
3. Configure el DNS del dominio hacia la IP pública del VPS y permita los
   puertos TCP 80 y 443 en el firewall. **No abra el puerto 5050**.
4. Verifique que el repositorio contiene `deploy/Caddyfile.production`; el
   perfil Docker crea un `tmpfs` privado, propiedad de UID/GID 10001, para
   workers y espejo de sesiones de forma idempotente.
5. Prepare las rutas privadas de registros y respaldos con el usuario de
   despliegue, sin ubicarlas en `public_html` ni en el repositorio:

```bash
sudo EV3_VPS_SERVICE_OWNER="$USER" ./scripts/prepare_vps_storage.sh
```

### Paso 2. Obtener el código

```bash
git clone https://github.com/fralmeagUTP/Codex_SimuladorLegoEV3.git simulador-ev3
cd simulador-ev3
git switch <rama-o-etiqueta-aprobada>
```

No despliegue automáticamente una rama de desarrollo sin pruebas aprobadas.

### Paso 3. Crear el archivo de secretos

```bash
umask 077
cp .env.production.example .env.production
nano .env.production
```

Reemplace los dos secretos y defina `EV3_WEB_PUBLIC_HOST` con el dominio real
y `EV3_WEB_TLS_EMAIL` con el correo que recibirá avisos de certificado. Mantenga
el archivo fuera de Git.

### Paso 4. Construir e iniciar

```bash
docker compose -f docker-compose.production.yml --env-file .env.production up -d --build
docker compose -f docker-compose.production.yml ps
docker compose -f docker-compose.production.yml logs --tail=100
```

El perfil incluido ejecuta como usuario no privilegiado, raíz de sólo lectura,
`tmpfs` privado, límite de 64 PIDs, 768 MiB y 2 CPU. Aumente esos límites en
`docker-compose.production.yml` únicamente tras una prueba de carga.

### Paso 5. Configurar el proxy HTTPS

El perfil incluido arranca Caddy y administra automáticamente TLS, redirección
HTTP a HTTPS, cabeceras `X-Forwarded-*` y SSE sin buffering. La aplicación
`simulador-ev3` pertenece a una red Docker interna y no expone `5050` al host.
Si la institución usa Nginx/Cloudflare externo, mantenga el mismo contrato:
HTTPS hasta el navegador, `X-Forwarded-Proto: https`, SSE sin buffering y
conexión interna exclusiva al contenedor Web.

### Paso 6. Verificar antes de abrir al público

```bash
curl --fail https://SU-DOMINIO/healthz \
  -H "X-EV3-Operations-Token: $EV3_WEB_OPERATIONS_TOKEN"
curl --fail "https://SU-DOMINIO/metrics?format=prometheus" \
  -H "X-EV3-Operations-Token: $EV3_WEB_OPERATIONS_TOKEN"
```

Abra dos navegadores independientes, cree una sesión en cada uno y ejecute una
simulación corta. Verifique que no comparten editor, telemetría ni mundo.

## 5. Instalación alternativa: cPanel / Passenger

Use esta ruta sólo después de confirmar con soporte del hosting que el proceso
Passenger puede iniciar y conservar workers hijos de Python. Si no puede,
migre a VPS/contenedor; no desactive el aislamiento como sustituto.

### Paso 1. Crear la aplicación

En **Setup Python App** configure:

| Campo | Valor |
| --- | --- |
| Python | 3.11 o 3.12 |
| Application root | Carpeta privada, por ejemplo `simuladorlego` |
| Application URL | Dominio, subdominio o ruta autorizada |
| Startup file | `wsgi.py` |
| Entry point | `app` |

### Paso 2. Subir código e instalar dependencias

```bash
cd /home/USUARIO/simuladorlego
source /home/USUARIO/virtualenv/simuladorlego/3.11/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install .
```

Suba como mínimo `simulador_ev3/`, `examples/`, `worlds/`, `pyproject.toml`,
`requirements.txt` y el wrapper `wsgi.py` basado en
`Documentos/wsgi_cpanel.py`. No suba `.venv/`, `build/`, `dist/`, caches ni
evidencia local.

### Paso 3. Crear directorios privados

```bash
mkdir -p /home/USUARIO/tmp/simulador-ev3/workers
mkdir -p /home/USUARIO/tmp/simulador-ev3/session-mirror
chmod 700 /home/USUARIO/tmp/simulador-ev3 /home/USUARIO/tmp/simulador-ev3/workers /home/USUARIO/tmp/simulador-ev3/session-mirror
```

Use esas rutas para `EV3_WEB_WORKER_TEMP_ROOT` y
`EV3_WEB_FILE_MIRROR_DIR`. No use `public_html` ni el directorio del código
para temporales o secretos.

### Paso 4. Configurar variables y reiniciar

En el panel **Environment Variables**, copie las variables de la sección 3,
sustituya `/var/tmp/...` por `/home/USUARIO/tmp/...`, y pulse **Restart**.
Conserve `SESSION_BACKEND=memory` sólo para una instancia Passenger. Para más
de un proceso, configure Redis administrado y realice la validación de sesiones
concurrentes.

### Paso 5. Validar

1. Abra la URL pública por HTTPS y confirme carga de la pantalla principal.
2. Cargue un mundo, ejecute un ejemplo y use **Detener y reiniciar**.
3. Abra una segunda ventana privada y confirme aislamiento de sesiones.
4. Consulte salud y métricas sólo con el token de operaciones.
5. Revise el log de Passenger sin publicar rutas, tokens ni scripts privados.

## 6. Operación diaria

### Actualizar versión

1. Ponga la instancia en mantenimiento o avise al aula: las sesiones activas
   se perderán durante el reinicio.
2. Obtenga el commit/etiqueta aprobado.
3. Instale dependencias si cambió `pyproject.toml` o `requirements.txt`.
4. Reinicie el servicio/contenedor.
5. Ejecute salud, métricas protegidas y una simulación corta.
6. Registre fecha, commit, configuración no secreta y resultado.

### Copias y retención

- Respaldar sólo mundos creados que se decida conservar y configuración no
  secreta necesaria para restaurar el servicio.
- No respaldar tokens, cookies, trazas o temporales de workers como parte del
  contenido docente.
- Las sesiones son efímeras; un reinicio es una recuperación válida y no debe
  intentar reanudar scripts en ejecución.

### Monitoreo mínimo

- Disponibilidad: `/healthz` protegido.
- Capacidad: sesiones activas, workers activos, cola y memoria mediante
  `/metrics?format=prometheus` protegido.
- Sistema: memoria, CPU, PIDs y espacio de temporales del host/contenedor.
- Seguridad: errores 429, fallos de worker y reinicios inesperados.

## 7. Diagnóstico y reversión

| Síntoma | Acción segura |
| --- | --- |
| La app no inicia | Verificar Python 3.11+, variables obligatorias y log privado del proceso. No muestre el traceback al usuario. |
| Error al ejecutar script | Confirmar que el hosting permite procesos hijos y que hay cuota de PIDs, memoria y directorio temporal. |
| Sesiones cruzadas o perdidas entre solicitudes | Usar una instancia o configurar Redis para multiproceso; revisar afinidad de sesión del proxy. |
| SSE no actualiza | Desactivar buffering del proxy y aumentar timeout de lectura. |
| `403` en salud/métricas | Enviar `X-EV3-Operations-Token` o acceder desde cliente local autorizado. |
| Alta memoria | Reducir `MAX_RUNNING_SIMULATIONS`, revisar workers y aumentar recursos tras prueba de carga. |

Para revertir, despliegue el último commit/imagen validado, rote los secretos si
se sospecha exposición, reinicie el servicio y ejecute las verificaciones del
paso 6. Consulte `MODELO_AMENAZAS_Y_REVERSION_SEGURIDAD.md` para el protocolo
completo.

## 8. Checklist de aceptación del hosting

- [ ] Python 3.11 o 3.12 disponible.
- [ ] HTTPS, redirección HTTP y certificado vigente.
- [ ] Procesos hijos permitidos y cuota suficiente de PIDs.
- [ ] 2 vCPU/4 GB/5 GB como mínimo para piloto; capacidad ampliada según aula.
- [ ] Directorios privados con permisos 0700 para temporales y metadatos.
- [ ] Variables de producción y secretos configurados fuera del repositorio.
- [ ] Endpoints operativos protegidos por token o red administrativa.
- [ ] Proxy compatible con SSE sin buffering.
- [ ] Prueba de dos sesiones independientes, ejecución, reinicio y recuperación aprobada.
- [ ] Plan de respaldo, actualización y reversión documentado.
