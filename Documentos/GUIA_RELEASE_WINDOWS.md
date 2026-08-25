# Guia de Release Windows - Escritorio Tkinter

Version documentada: 1.5.0
Fecha de actualización: 2026-08-23

Esta guía genera la distribución de escritorio para Windows usando
`PyInstaller`. El resultado incluye el ejecutable, un paquete portable ZIP y,
si Inno Setup 6 está instalado, un instalador nativo.

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

Para generar también el instalador, instalar Inno Setup 6. El script lo busca
en las rutas de instalación usuales de Windows. Si no está instalado, usar
`-SkipInstaller` para generar solamente la distribución portable.

## 2. Generar ejecutable

Opcion recomendada:

```powershell
.\scripts\build_release_windows.ps1 -PythonExe .\.venv\Scripts\python.exe
```

Solo ejecutable y ZIP portable:

```powershell
.\scripts\build_release_windows.ps1 -PythonExe .\.venv\Scripts\python.exe -SkipInstaller
```

Opcion manual:

```powershell
python -m PyInstaller --noconfirm --clean --name SimuladorEV3 --windowed --collect-submodules simulador_ev3 simulador_ev3\ui\main_window.py
```

Salida esperada:

- `dist\SimuladorEV3\SimuladorEV3.exe`
- `dist\SimuladorEV3-1.5.0-Windows-x64.zip`
- `dist\installer\Setup-SimuladorEV3-1.5.0-Windows-x64.exe` (cuando se
  instaló Inno Setup 6 y no se usó `-SkipInstaller`).

## 3. Incluir recursos para distribucion

Copiar junto al ejecutable:

- `examples`
- `worlds`

Estructura recomendada:

- `SimuladorEV3\SimuladorEV3.exe`
- `SimuladorEV3\Documentos\Ejemplos\...`
- `SimuladorEV3\Documentos\Mundos\...`

El script `build_release_windows.ps1` copia y verifica estos recursos de forma
automática. También incorpora los assets de la aplicación, incluidos los de la
pantalla de inicio.

Nota: el script soporta ambas estructuras.
Prioriza `examples/` y `worlds/`; usa `Documentos\Ejemplos` y `Documentos\Mundos` solo como fallback legacy.

Para distribuir la aplicación, entregar una de estas dos alternativas:

1. El instalador `Setup-SimuladorEV3-1.5.0-Windows-x64.exe`.
2. El archivo ZIP completo; el usuario debe descomprimirlo antes de ejecutar
   `SimuladorEV3\SimuladorEV3.exe`.

No distribuir el `.exe` aislado: necesita la carpeta `_internal` y
`Documentos` que se generan junto a él.

## 4. Verificación de la distribución

Antes de entregar, confirmar:

```powershell
Test-Path .\dist\SimuladorEV3\SimuladorEV3.exe
tar -tf .\dist\SimuladorEV3-1.5.0-Windows-x64.zip
```

El listado del ZIP debe contener `SimuladorEV3/SimuladorEV3.exe`,
`SimuladorEV3/_internal/` y `SimuladorEV3/Documentos/`.

## 5. Smoke test manual de release

Con el `.exe` abierto:

1. Ir a `Escenarios` -> `Seguidor de linea` y ejecutar.
2. Ir a `Escenarios` -> `Ultrasonido + obstaculos` y ejecutar.
3. Ir a `Escenarios` -> `Test pantalla/altavoz` y ejecutar.

Criterio de aceptacion:

- La app no se cierra sola.
- El robot se mueve en los escenarios de movimiento.
- El escenario de pantalla/altavoz muestra texto y dispara beeps.

## 6. Problemas comunes

- Si Windows SmartScreen bloquea: seleccionar `Mas informacion` y luego `Ejecutar de todas formas`.
- Si falta audio: verificar volumen del sistema y dispositivo de salida.
- Si no aparecen mundos/ejemplos: confirmar que se copiaron los recursos del release (origen `examples/` y `worlds/`, o fallback `Documentos`).
- Si el instalador no se genera: instalar Inno Setup 6 o ejecutar el build con
  `-SkipInstaller`; el ejecutable y ZIP siguen siendo distribuibles.
- Si el ZIP no se puede crear: cerrar cualquier instancia de `SimuladorEV3.exe`
  y sus procesos hijo antes de volver a ejecutar el build.

## 7. Relacion con version web

La version `1.5.0` tambien incluye la aplicacion web Flask. No se requiere ejecutable para usar la web; basta con iniciar:

```powershell
.\scripts\start_web.cmd
```

La entrega actual puede validarse sin construir `.exe` si el objetivo es operar la version web.

## 8. Permisos y verificacion de seguridad

El ejecutable debe iniciar desde una cuenta Windows estandar; no requiere
ejecucion como administrador. Antes de liberar, pruebe tanto el ZIP extraido
como el instalador con un usuario sin privilegios elevados y confirme que:

- puede abrir y guardar un script `.py` y un mundo `.json` dentro de los limites;
- al ejecutar un script se crea un worker aislado (salvo el modo explicito de
  compatibilidad para desarrollo);
- no aparecen rutas locales ni trazas Python en mensajes de error;
- no se dejan temporales `ev3-worker-*` despues de cerrar la aplicacion.
