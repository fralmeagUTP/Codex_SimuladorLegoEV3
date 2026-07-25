# Guia Web Flask - Windows

Esta guia describe como operar la version web del Simulador EV3 en Windows.

Estado oficial de interfaces:

- La Web y Tkinter son interfaces soportadas con el mismo contrato de sesion.
- La Web es la referencia visual y ofrece simulacion, mundos, ayuda y operaciones.

Version documentada: 1.4.0
Fecha de actualizacion: 2026-07-24

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

Verificar salud del servidor:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5050/healthz
```

La respuesta debe incluir `status`, `active_sessions` y `running_simulations`.

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
| --- | --- | --- |
| `EV3_WEB_HOST` | Host de escucha del servidor. | `127.0.0.1` |
| `EV3_WEB_PORT` | Puerto HTTP. | `5050` |
| `EV3_WEB_THREADS` | Hilos de Waitress. | `8` |
| `EV3_WEB_APP_ENV` | Entorno de ejecucion (`development` o `production`). | `development` |
| `EV3_WEB_SECRET_KEY` | Llave Flask para cookies/sesiones. | `dev-simulador-ev3` |
| `EV3_WEB_EXAMPLES_DIR` | Carpeta de ejemplos Pybricks. | `examples` |
| `EV3_WEB_WORLDS_DIR` | Carpeta de mundos JSON. | `worlds` |
| `EV3_WEB_IMAGE_ASSETS_DIR` | Carpeta de imagenes de assets. | `simulador_ev3\assets` |
| `EV3_WEB_SESSION_IDLE_TIMEOUT_MIN` | Minutos de inactividad antes de expirar sesion. | `45` |
| `EV3_WEB_MAX_ACTIVE_SESSIONS` | Numero maximo de sesiones activas. | `20` |
| `EV3_WEB_MAX_RUNNING_SIMULATIONS` | Numero maximo de simulaciones corriendo. | `8` |
| `EV3_WEB_SCRIPT_MAX_RUNTIME_S` | Tiempo maximo por script; obligatorio positivo en produccion. | `0.0` |
| `EV3_WEB_MAX_SCRIPT_SIZE_BYTES` | Tamano maximo del script. | `131072` |
| `EV3_WEB_MAX_WORLD_JSON_SIZE_BYTES` | Tamano maximo de mundo JSON. | `2097152` |
| `EV3_WEB_SSE_HEARTBEAT_S` | Intervalo de heartbeat SSE. | `15` |
| `EV3_WEB_SESSION_CLEANUP_INTERVAL_S` | Intervalo de limpieza de sesiones expiradas. | `60` |
| `EV3_WEB_ENABLE_SESSION_CLEANUP_THREAD` | Activa limpieza periodica en segundo plano. | `true` |
| `EV3_WEB_ENABLE_SECURITY_HEADERS` | Activa cabeceras basicas de seguridad HTTP. | `true` |
| `EV3_WEB_SESSION_COOKIE_SECURE` | Marca cookies como seguras cuando se use HTTPS. | `false` |
| `EV3_WEB_WEB_SSE_ENABLED` | Activa actualizaciones SSE; existe fallback por polling. | `true` |
| `EV3_WEB_WEB_POLLING_INTERVAL_MS` | Intervalo del fallback por polling. | `900` |

La referencia completa, incluidos Redis, file mirror y parametros de UI, esta
en `Documentos/REFERENCIA_CONFIGURACION.md`; el codigo fuente de verdad es
`simulador_ev3/web/config.py`.

### Despliegue en produccion

Al definir `EV3_WEB_APP_ENV=production`, la aplicacion rechaza el arranque si se conserva una configuracion insegura. Debes definir una llave propia de al menos 32 caracteres, un limite positivo para cada script y HTTPS para las cookies:

```powershell
$env:EV3_WEB_APP_ENV = "production"
$env:EV3_WEB_SECRET_KEY = "reemplaza-esta-clave-por-un-secreto-largo-y-unico"
$env:EV3_WEB_SCRIPT_MAX_RUNTIME_S = "30"
$env:EV3_WEB_SESSION_COOKIE_SECURE = "true"
```

La clave de ejemplo no debe reutilizarse: almacenala en el gestor de secretos o la configuracion segura del servidor.

Compatibilidad temporal:

- Si todavia no migraste carpetas, tambien puedes apuntar a `Documentos\Ejemplos` y `Documentos\Mundos`.

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

## 11. Operacion y observabilidad

- `http://127.0.0.1:5050/healthz` informa version, sesiones, worker y backend.
- `http://127.0.0.1:5050/metrics` devuelve metricas JSON.
- `http://127.0.0.1:5050/metrics?format=prometheus` expone formato Prometheus.
- `http://127.0.0.1:5050/operations` muestra el panel de operaciones local.

No publicar `/metrics` o `/operations` fuera de una red controlada sin aplicar
la proteccion de acceso que corresponda al entorno.

## 12. Flujo operativo recomendado

1. Iniciar servidor con `.\scripts\start_web.ps1`.
2. Abrir `/worlds` para crear y guardar un mundo.
3. Usar **Simular mundo guardado** para abrir `/?world=<archivo>.json`.
4. Ejecutar el script Pybricks desde `/`.
5. Detener servidor con `.\scripts\stop_web.ps1`.

## 12. Tamano del mapa y paridad con Tkinter

La web conserva la escala del editor Tkinter:

- `32 px = 100 mm`.
- Mundo base `2000 x 2000 mm` = `640 x 640 px`.
- El canvas web mide el tamano real del mundo; el panel hace scroll si no cabe completo.
- La colocacion de muros, lineas, zonas y pisos se centra sobre la celda seleccionada igual que en Tkinter.
- El arrastre mantiene el offset desde donde se tomo el asset.

Esto evita mapas deformados o assets descuadrados.

## 13. Depuracion web

La pagina `/` incluye controles basicos de depuracion:

- `Breakpoints`: lineas separadas por coma o espacios, por ejemplo `2, 5, 8`.
- `Debug`: carga el script, aplica breakpoints e inicia en modo debug.
- `Step`: si no hay ejecucion activa, inicia en modo paso a paso; si ya esta activa, avanza una linea.
- `Continuar`: reanuda la ejecucion hasta el siguiente breakpoint o hasta terminar.

Los eventos de depuracion se reciben por SSE y muestran la linea actual o el punto donde el script quedo pausado.

## 14. Estado de ejecucion

Cuando un script termina naturalmente, la sesion debe cambiar a `finished` y conservar el ultimo snapshot hasta un reinicio manual.

Si la aplicacion parece colgada:

1. Revisar `http://127.0.0.1:5050/healthz`.
2. Confirmar que `running_simulations` no crece indefinidamente.
3. Ejecutar `.\scripts\restart_web.cmd` si quedo una sesion antigua.
4. Validar con `.\scripts\smoke_web.cmd`.

## 15. Smoke test

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
