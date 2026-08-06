# Guia de Release Windows - Escritorio Tkinter

Version documentada: 1.5.0
Fecha de actualización: 2026-08-05

Esta guia genera un `.exe` del simulador de escritorio usando `PyInstaller`.

Nota: esta guia aplica al ejecutable de escritorio. Para la version web Flask usar `Documentos/GUIA_WEB_FLASK_WINDOWS.md`.

## 1. Preparar entorno

En PowerShell, desde la raiz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,desktop-e2e]"
python -m pip install pyinstaller
```

## 2. Generar ejecutable

Opcion recomendada:

```powershell
.\scripts\build_release_windows.ps1 -PythonExe .\.venv\Scripts\python.exe
```

Opcion manual:

```powershell
python -m PyInstaller --noconfirm --clean --name SimuladorEV3 --windowed --collect-submodules simulador_ev3 simulador_ev3\ui\main_window.py
```

Salida esperada:

- `dist\SimuladorEV3\SimuladorEV3.exe`

## 3. Incluir recursos para distribucion

Copiar junto al ejecutable:

- `examples`
- `worlds`

Estructura recomendada:

- `SimuladorEV3\SimuladorEV3.exe`
- `SimuladorEV3\Documentos\Ejemplos\...`
- `SimuladorEV3\Documentos\Mundos\...`

Nota: el script `build_release_windows.ps1` ya soporta ambas estructuras.
Prioriza `examples/` y `worlds/`; usa `Documentos\Ejemplos` y `Documentos\Mundos` solo como fallback legacy.

## 4. Smoke test manual de release

Con el `.exe` abierto:

1. Ir a `Escenarios` -> `Seguidor de linea` y ejecutar.
2. Ir a `Escenarios` -> `Ultrasonido + obstaculos` y ejecutar.
3. Ir a `Escenarios` -> `Test pantalla/altavoz` y ejecutar.

Criterio de aceptacion:

- La app no se cierra sola.
- El robot se mueve en los escenarios de movimiento.
- El escenario de pantalla/altavoz muestra texto y dispara beeps.

## 5. Problemas comunes

- Si Windows SmartScreen bloquea: seleccionar `Mas informacion` y luego `Ejecutar de todas formas`.
- Si falta audio: verificar volumen del sistema y dispositivo de salida.
- Si no aparecen mundos/ejemplos: confirmar que se copiaron los recursos del release (origen `examples/` y `worlds/`, o fallback `Documentos`).

## 6. Relacion con version web

La version `1.5.0` tambien incluye la aplicacion web Flask. No se requiere ejecutable para usar la web; basta con iniciar:

```powershell
.\scripts\start_web.cmd
```

La entrega actual puede validarse sin construir `.exe` si el objetivo es operar la version web.
