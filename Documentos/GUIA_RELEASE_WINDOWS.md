# Guía de Release Windows (Fase 9)

Esta guía genera un `.exe` del simulador usando `PyInstaller`.

## 1) Preparar entorno

En PowerShell, desde la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pyinstaller
```

## 2) Generar ejecutable

Opción recomendada (script reproducible):

```powershell
.\scripts\build_release_windows.ps1
```

Opción manual:

```powershell
python -m PyInstaller --noconfirm --clean --name SimuladorEV3 --windowed --collect-submodules simulador_ev3 simulador_ev3\ui\main_window.py
```

Salida esperada:

- Ejecutable: `dist\SimuladorEV3\SimuladorEV3.exe`

## 3) Incluir recursos para distribución

Copia junto al ejecutable estas carpetas:

- `Documentos\Ejemplos`
- `Documentos\Mundos`

Estructura recomendada de entrega:

- `SimuladorEV3\SimuladorEV3.exe`
- `SimuladorEV3\Documentos\Ejemplos\...`
- `SimuladorEV3\Documentos\Mundos\...`

## 4) Smoke test manual de release

Con el `.exe` abierto:

1. Ir a `Escenarios` → `Seguidor de línea` y ejecutar.
2. Ir a `Escenarios` → `Ultrasonido + obstáculos` y ejecutar.
3. Ir a `Escenarios` → `Test pantalla/altavoz` y ejecutar.

Criterio de aceptación:

- La app no se cierra sola.
- El robot se mueve en los 2 escenarios de movimiento.
- El escenario de pantalla/altavoz muestra texto y dispara beeps.

## 5) Problemas comunes

- Si Windows SmartScreen bloquea: seleccionar "Más información" y luego "Ejecutar de todas formas".
- Si falta audio: verificar volumen del sistema y dispositivo de salida.
- Si no aparecen mundos/ejemplos: confirmar que `Documentos` esté junto al `.exe`.
