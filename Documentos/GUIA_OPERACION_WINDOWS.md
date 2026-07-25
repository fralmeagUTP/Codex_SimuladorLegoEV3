# Operacion local en Windows

> Estado: actual al 2026-07-24. Version aplicable: `1.4.0`. Audiencia:
> estudiante, docente y soporte local.

## Preparar entorno

Desde la raiz del repositorio, con Python 3.11 o superior:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Si PowerShell no permite activar entornos, no es necesario activarlo: usar
directamente `.\.venv\Scripts\python.exe` en los comandos.

## Aplicacion Web

```powershell
.\scripts\start_web.cmd
```

Abrir `http://127.0.0.1:5050/`. El script valida `/healthz`; los logs quedan en
`C:\tmp\ev3_web_out.log` y `C:\tmp\ev3_web_err.log`.

Para detener o reiniciar:

```powershell
.\scripts\stop_web.cmd
.\scripts\restart_web.cmd
```

Usar `GUIA_WEB_FLASK_WINDOWS.md` para Waitress, otro puerto, produccion y
variables de entorno.

## Aplicacion de escritorio Tkinter

```powershell
.\.venv\Scripts\python.exe -m simulador_ev3.ui.main_window
```

La aplicacion usa el worker aislado por defecto. Si falla al cargar mundo o
ejecutar, revisar el mensaje mostrado, verificar el entorno y ejecutar las
pruebas de UI. No activar `EV3_LOCAL_RUNTIME_ENABLED=true` salvo desarrollo o
diagnostico controlado.

## Diagnostico rapido

1. Web sin respuesta: abrir `/healthz`, revisar logs y comprobar que el puerto
   5050 no este ocupado.
2. Script detenido: revisar estado `finished`, `timed_out` o `error` y exportar
   traza para reproducir el caso.
3. Mundo no visible: confirmar que esta en `worlds/` y que el JSON es valido.
4. Diferencia con robot real: seleccionar perfil adecuado y consultar
   `DIFERENCIAS_SIMULADOR_ROBOT.md`.

## Verificacion antes de clase

```powershell
.\.venv\Scripts\python.exe -m pytest tests\ui tests\web -q
.\scripts\smoke_web.cmd
```

Para verificacion completa, consultar `docs/testing/estrategia_pruebas.md` y
`CHECKLIST_QA_RELEASE.md`.
