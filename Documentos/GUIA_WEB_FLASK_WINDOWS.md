# Guia Web Flask - Windows

Esta guia describe como operar la version web del Simulador EV3.

## 1. Requisitos

- Python 3.11 o superior.
- Entorno virtual `.venv` creado en la raiz del proyecto.
- Dependencias instaladas con:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
```

## 2. Iniciar servidor

Desde la raiz del proyecto:

```powershell
.\scripts\start_web.ps1
```

Si PowerShell bloquea scripts por politica de ejecucion, usar el wrapper CMD:

```powershell
.\scripts\start_web.cmd
```

URL principal:

```text
http://127.0.0.1:5050/
```

Rutas de usuario:

- `http://127.0.0.1:5050/`: simulacion del robot.
- `http://127.0.0.1:5050/worlds`: creacion de mundos.
- `http://127.0.0.1:5050/help`: ayuda.

## 3. Detener servidor

```powershell
.\scripts\stop_web.ps1
```

Alternativa sin cambiar politica de PowerShell:

```powershell
.\scripts\stop_web.cmd
```

## 4. Reiniciar servidor

```powershell
.\scripts\restart_web.ps1
```

Alternativa sin cambiar politica de PowerShell:

```powershell
.\scripts\restart_web.cmd
```

## 5. Iniciar con Waitress

Waitress es recomendado para ejecucion local mas estable que el servidor de desarrollo de Flask.

Instalar dependencia opcional:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .[web-prod]
```

Iniciar:

```powershell
.\scripts\start_web_waitress.cmd
```

Cambiar cantidad de hilos:

```powershell
.\scripts\start_web_waitress.cmd -Threads 12
```

Para detenerlo se usa el mismo script de parada:

```powershell
.\scripts\stop_web.cmd
```

## 6. Ejecutar en primer plano

Util para ver logs directamente en la consola:

```powershell
.\scripts\start_web.ps1 -Foreground
```

Con wrapper CMD:

```powershell
.\scripts\start_web.cmd -Foreground
```

## 7. Cambiar puerto

```powershell
.\scripts\restart_web.ps1 -Port 5060
```

Con wrapper CMD:

```powershell
.\scripts\restart_web.cmd -Port 5060
```

Luego abrir:

```text
http://127.0.0.1:5060/
```

## 8. Logs

Cuando se ejecuta en segundo plano:

- Salida estandar: `C:\tmp\ev3_web_out.log`
- Errores: `C:\tmp\ev3_web_err.log`
- Salida Waitress: `C:\tmp\ev3_web_waitress_out.log`
- Errores Waitress: `C:\tmp\ev3_web_waitress_err.log`

## 9. Variables de entorno

La aplicacion permite configurar valores sin editar codigo:

| Variable | Uso | Valor por defecto |
|---|---|---|
| `EV3_WEB_HOST` | Host de escucha del servidor. | `127.0.0.1` |
| `EV3_WEB_PORT` | Puerto HTTP. | `5050` |
| `EV3_WEB_THREADS` | Hilos de Waitress. | `8` |
| `EV3_WEB_SECRET_KEY` | Llave Flask para cookies/sesiones. | `dev-simulador-ev3` |
| `EV3_WEB_EXAMPLES_DIR` | Carpeta de ejemplos Pybricks. | `Documentos\Ejemplos` |
| `EV3_WEB_WORLDS_DIR` | Carpeta de mundos JSON. | `Documentos\Mundos` |
| `EV3_WEB_IMAGE_ASSETS_DIR` | Carpeta de imagenes de assets. | `simulador_ev3\images` |
| `EV3_WEB_SESSION_IDLE_TIMEOUT_MIN` | Minutos de inactividad antes de expirar sesion. | `30` |
| `EV3_WEB_MAX_ACTIVE_SESSIONS` | Numero maximo de sesiones activas. | `20` |
| `EV3_WEB_MAX_RUNNING_SIMULATIONS` | Numero maximo de simulaciones corriendo. | `8` |
| `EV3_WEB_SCRIPT_MAX_RUNTIME_S` | Tiempo maximo por script. | `30.0` |
| `EV3_WEB_MAX_SCRIPT_SIZE_BYTES` | Tamano maximo del script. | `131072` |
| `EV3_WEB_MAX_WORLD_JSON_SIZE_BYTES` | Tamano maximo de mundo JSON. | `2097152` |
| `EV3_WEB_SSE_HEARTBEAT_S` | Intervalo de heartbeat SSE. | `15` |
| `EV3_WEB_SESSION_CLEANUP_INTERVAL_S` | Intervalo de limpieza de sesiones expiradas. | `60` |
| `EV3_WEB_ENABLE_SESSION_CLEANUP_THREAD` | Activa limpieza periodica en segundo plano. | `true` |
| `EV3_WEB_ENABLE_SECURITY_HEADERS` | Activa cabeceras basicas de seguridad HTTP. | `true` |
| `EV3_WEB_SESSION_COOKIE_SECURE` | Marca cookies como seguras cuando se use HTTPS. | `false` |

Ejemplo:

```powershell
$env:EV3_WEB_MAX_ACTIVE_SESSIONS = "10"
$env:EV3_WEB_MAX_RUNNING_SIMULATIONS = "4"
.\scripts\restart_web.cmd
```

## 10. Cabeceras de seguridad

Por defecto la web responde con:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: same-origin`
- `Content-Security-Policy` restringida a recursos del propio servidor

Para desactivarlas en una integracion controlada:

```powershell
$env:EV3_WEB_ENABLE_SECURITY_HEADERS = "false"
.\scripts\restart_web.cmd
```

## 11. Flujo operativo recomendado

1. Iniciar servidor con `.\scripts\start_web.ps1`.
2. Abrir `/worlds` para crear y guardar un mundo.
3. Usar **Simular mundo guardado** para abrir `/?world=<archivo>.json`.
4. Ejecutar el script Pybricks desde `/`.
5. Detener servidor con `.\scripts\stop_web.ps1`.

## 12. Depuracion web

La pagina `/` incluye controles basicos de depuracion:

- `Breakpoints`: lineas separadas por coma o espacios, por ejemplo `2, 5, 8`.
- `Debug`: carga el script, aplica breakpoints e inicia en modo debug.
- `Step`: si no hay ejecucion activa, inicia en modo paso a paso; si ya esta activa, avanza una linea.
- `Continuar`: reanuda la ejecucion hasta el siguiente breakpoint o hasta terminar.

Los eventos de depuracion se reciben por SSE y muestran la linea actual o el punto donde el script quedo pausado.

## 13. Smoke test

Verificar estado:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5050/healthz
```

Smoke test completo:

```powershell
.\scripts\smoke_web.cmd
```

En otro puerto:

```powershell
.\scripts\smoke_web.cmd -Port 5060
```

Criterios:

- Respuesta HTTP `200`.
- `status` igual a `ok`.
- La pagina `/` carga la simulacion.
- La pagina `/worlds` carga el editor de mundos.
- Se puede crear, consultar y cerrar una sesion por API.
- Los endpoints de debug aceptan breakpoints, step y continue.
