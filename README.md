# Simulador EV3 Pybricks

Version actual: 1.5.0 (fuente única: `simulador_ev3/_version.py`)

Simulador educativo LEGO EV3 con API Pybricks virtual, motor 2D, editor de
mundos, telemetría, depuración y dos interfaces activas: Web Flask y escritorio
Tkinter. Ambas utilizan el mismo contrato de sesión y catálogo funcional.

## Estado actual

- Liberación: **apta con observaciones**, sin defectos críticos o altos abiertos.
- Web y Tkinter: paridad funcional cerrada para el alcance 1.5.0.
- OpenSpec: cambio de paridad archivado; especificaciones base vigentes.
- QA del 2026-08-05: 829 pruebas aprobadas y 6 E2E de escritorio omitidas en la
  ejecución global; esas 6 se ejecutaron separadamente en Windows gráfico y
  aprobaron 6/6. GitHub Actions aprobó Windows, Linux, E2E Web, contenedor,
  empaquetado, análisis estático, cobertura y resiliencia.

El detalle vigente se encuentra en
[`Documentos/ESTADO_ACTUAL_PROYECTO.md`](Documentos/ESTADO_ACTUAL_PROYECTO.md)
y el inventario documental en
[`Documentos/INDICE_DOCUMENTACION.md`](Documentos/INDICE_DOCUMENTACION.md).

## Capacidades

- Ejecución aislada de scripts Python estilo Pybricks y cancelación manual.
- Robot EV3, motores A–D, sensores S1–S4, LED, altavoz y LCD 178×128.
- `DriveBase`, perfiles de fidelidad, trazas, misiones y resultados exportables.
- Depuración con breakpoints, paso, continuar y watches.
- Mundos JSON, editor visual, escenarios y catálogos educativos compartidos.
- Sesiones Web independientes, SSE con polling de respaldo y recuperación de
  worker.
- Temas claro/oscuro, teclado, diseño adaptable Web y evidencia visual Tkinter.
- Métricas JSON/Prometheus, health check y trazas OpenTelemetry configurables.

## Requisitos

- Python 3.11 o 3.12.
- Windows para la experiencia Tkinter soportada y su E2E nativo.
- Chrome/Edge/Chromium para la Web y Playwright.
- Docker opcional para despliegue Linux.

## Instalación de desarrollo

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev,desktop-e2e,web-prod]"
.\.venv\Scripts\python.exe -m playwright install chromium
```

No es necesario activar el entorno virtual si se invoca su intérprete como en
los comandos anteriores.

## Ejecutar la aplicación Web

```powershell
.\scripts\start_web.cmd
```

Abrir `http://127.0.0.1:5050/`. Rutas principales:

- `/`: simulación y editor Pybricks.
- `/worlds`: editor de mundos.
- `/help`: centro de ayuda.
- `/healthz`: salud y versión.
- `/metrics?format=prometheus`: métricas Prometheus.

Detener o reiniciar:

```powershell
.\scripts\stop_web.cmd
.\scripts\restart_web.cmd
```

Para otro puerto: `.\scripts\start_web.ps1 -Port 5053`. El puerto oficial
predeterminado continúa siendo 5050.

## Ejecutar la aplicación de escritorio

```powershell
.\.venv\Scripts\python.exe -m simulador_ev3.ui.main_window
```

Tkinter utiliza el worker aislado por defecto. El modo local mediante
`EV3_LOCAL_RUNTIME_ENABLED=true` existe solo para compatibilidad controlada de
desarrollo y pruebas.

## Distribución Windows

La distribución de escritorio se genera con PyInstaller. El proceso oficial
incluye recursos visuales, ejemplos y mundos, y produce:

- `dist\SimuladorEV3\SimuladorEV3.exe`: aplicación dentro de su carpeta de
  distribución. No se debe copiar el `.exe` por separado.
- `dist\SimuladorEV3-<versión>-Windows-x64.zip`: paquete portable para
  descomprimir y ejecutar.
- `dist\installer\Setup-SimuladorEV3-<versión>-Windows-x64.exe`: instalador
  para Windows, cuando Inno Setup 6 está disponible.

Para construir solo el ejecutable y el ZIP portable:

```powershell
.\scripts\build_release_windows.ps1 -PythonExe .\.venv\Scripts\python.exe -SkipInstaller
```

Consulta la [guía de release Windows](Documentos/GUIA_RELEASE_WINDOWS.md) para
los requisitos, verificaciones y distribución.

## Pruebas y calidad

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --cov=simulador_ev3 --cov-report=term-missing -q
.\.venv\Scripts\python.exe -m ruff check simulador_ev3 tests
.\.venv\Scripts\python.exe -m mypy
.\.venv\Scripts\python.exe -m bandit -q -c pyproject.toml -r simulador_ev3 --severity-level medium
.\.venv\Scripts\python.exe -m pip_audit
openspec validate --all --strict
```

E2E de escritorio, únicamente con sesión gráfica Windows visible:

```powershell
$env:EV3_RUN_DESKTOP_E2E = "1"
.\.venv\Scripts\python.exe -m pytest tests/e2e/test_desktop_pywinauto.py -q -rs
```

Los resultados indicados arriba son evidencia fechada, no sustituyen una nueva
ejecución sobre el commit que se desea liberar.

## Arquitectura resumida

```text
Web Flask / Tkinter
        │
SimulationSession versionada
        │
Worker aislado + RuntimeSandbox
        │
API Pybricks virtual
        │
SimulationEngine + dominio EV3 + mundos JSON
```

La física avanza nominalmente cada 20 ms (50 Hz). La Web recibe snapshots y
usa interpolación visual; la UI muestra centímetros, el motor conserva
milímetros y los ángulos se expresan en grados.

## Documentación

- [Manual de uso](Documentos/MANUAL_DE_USO.md)
- [Arquitectura C4](Documentos/ARQUITECTURA_C4.md)
- [Operación Windows](Documentos/GUIA_OPERACION_WINDOWS.md)
- [Despliegue Linux](Documentos/GUIA_DESPLIEGUE_LINUX.md)
- [Configuración](Documentos/REFERENCIA_CONFIGURACION.md)
- [Seguridad y aula](Documentos/SEGURIDAD_Y_USO_EN_AULA.md)
- [Pruebas](docs/testing/estrategia_pruebas.md)
- [Contribución](CONTRIBUTING.md)

## Seguridad y alcance

El sandbox reduce riesgo pero no convierte el servicio en un entorno público de
ejecución de código no confiable. En producción se requieren secreto único,
HTTPS, cookies seguras, límites positivos y controles de acceso adecuados. El
simulador no reemplaza la validación final sobre un robot EV3 físico.
