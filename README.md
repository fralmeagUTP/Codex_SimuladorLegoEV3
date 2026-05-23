# Simulador EV3 Pybricks

Version actual: 1.3.1

Simulador educativo LEGO EV3 compatible con una API Pybricks virtual. El proyecto incluye aplicacion de escritorio Tkinter y aplicacion web Flask para ejecutar scripts, editar mundos 2D y visualizar telemetria del robot.

## Estado del repositorio

- Rama publicada: `main`
- Version objetivo en GitHub: `1.3.1`
- Interfaz web: incluida desde la version `1.3.0`
- Interfaz escritorio Tkinter: mantenida

## Funcionalidades principales

- Ejecucion de scripts Python estilo Pybricks.
- Simulacion 2D de robot EV3, motores, sensores, LED, pantalla LCD y altavoz.
- Editor de mundos con robot, muros, lineas, zonas y pisos.
- Carga/guardado de mundos JSON.
- Simulacion web multi-sesion con Flask.
- Debug web con breakpoints, step y continue.
- Evidencia visual automatizada para la web.
- Pruebas unitarias, integracion, E2E Playwright y smoke de release.

## Uso rapido web

```powershell
.\scripts\start_web.cmd
```

Abrir:

```text
http://127.0.0.1:5050/
```

Rutas:

- `/`: simulacion del robot.
- `/worlds`: editor de mundos.
- `/help`: ayuda web.

Detener:

```powershell
.\scripts\stop_web.cmd
```

## Uso rapido escritorio

```powershell
.\.venv\Scripts\python.exe -m simulador_ev3.ui.main_window
```

## Documentacion

- Manual de uso: `Documentos/MANUAL_DE_USO.md`
- Guia web Windows: `Documentos/GUIA_WEB_FLASK_WINDOWS.md`
- Roadmap: `ROADMAP.md`
- Checklist QA: `Documentos/CHECKLIST_QA_RELEASE.md`
- Evidencia QA: `Documentos/EVIDENCIA_QA_RELEASE_2026-05-20.md`
- SDD migracion web: `Documentos/SDD_MIGRACION_WEB_FLASK.md`
- Guia release escritorio Windows: `Documentos/GUIA_RELEASE_WINDOWS.md`

## Pruebas recomendadas

```powershell
.\.venv\Scripts\python.exe -m pytest tests\web tests\e2e tests\application
```

Ultima validacion documentada: `117 passed`.

Para validacion completa por bloques, usar `Documentos/CHECKLIST_QA_RELEASE.md`.

## Notas de paridad visual

El mapa web usa la misma escala que Tkinter:

- `32 px = 100 mm`
- mundo base `2000 x 2000 mm` = `640 x 640 px`
- si el mapa no cabe en el panel visible, el contenedor web usa scroll.

Esto evita deformaciones visuales y mantiene la misma dimension fisica de mundos y assets en ambas interfaces.
