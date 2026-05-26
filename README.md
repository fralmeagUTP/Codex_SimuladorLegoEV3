# Simulador EV3 Pybricks

Version actual: 1.3.3

Simulador educativo LEGO EV3 compatible con una API Pybricks virtual. El proyecto incluye aplicacion de escritorio Tkinter y aplicacion web Flask para ejecutar scripts, editar mundos 2D y visualizar telemetria del robot.

## Estado de interfaces

- Frontend principal: Web Flask (`/` y `/worlds`).
- Frontend legado: Tkinter (`simulador_ev3/ui`) en modo mantenimiento correctivo.
- Politica de evolucion: nuevas funcionalidades primero en web; en escritorio solo correcciones necesarias de compatibilidad.

## Estado del repositorio

- Rama publicada: `main`
- Version objetivo en GitHub: `1.3.3`
- Interfaz web: incluida desde la version `1.3.0`
- Interfaz escritorio Tkinter: legado en mantenimiento

## Estructura estandar de recursos

- Ejemplos compartidos: `examples/`
- Mundos compartidos: `worlds/`
- Documentacion: `Documentos/` (legacy, en proceso de migracion a `docs/`)

Compatibilidad: el codigo mantiene fallback a `Documentos/Ejemplos` y `Documentos/Mundos` para no romper despliegues existentes.

## Funcionalidades principales

- Ejecucion de scripts Python estilo Pybricks.
- Simulacion 2D de robot EV3, motores, sensores, LED, pantalla LCD y altavoz.
- Pantalla EV3 monocroma 178x128 con texto y primitivas de dibujo (`draw_pixel`, `draw_line`, `draw_circle`, `draw_box`).
- Editor de mundos con robot, muros, lineas, zonas y pisos.
- Carga/guardado de mundos JSON.
- Simulacion web multi-sesion con Flask.
- Debug web con breakpoints, step y continue.
- Resaltado de linea actual en modo depuracion web.
- Boton unico `Detener y reiniciar` para salida consistente de ejecucion.
- Auto-reinicio de estado al finalizar scripts para evitar sesiones colgadas.
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

## Pantalla EV3 simulada

La pantalla del brick ya no es solo textual. El simulador soporta dos niveles de salida:

- Texto con `ev3.screen.print(...)` y `ev3.screen.clear()`.
- Dibujo monocromo en coordenadas LCD reales (`178 x 128`) con:
  - `ev3.screen.draw_pixel(x, y)`
  - `ev3.screen.draw_line(x1, y1, x2, y2)`
  - `ev3.screen.draw_circle(x, y, r, fill=False)`
  - `ev3.screen.draw_box(x, y, w, h, fill=False)`

El ejemplo `23_radar_ultrasonido_5grados.py` usa esta API para dibujar el radar como geometria real en la LCD, en lugar de una rejilla ASCII.

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

Ultima validacion documentada: `565 passed`.

Validacion tecnica reciente (2026-05-25):
- `tests/core/test_command_queue.py` + `tests/core/test_simulation_engine.py` + `tests/application/test_application.py` + `tests/pybricks_api/test_pybricks_api.py`: `169 passed`.
- `tests/web/test_web_app.py`: `73 passed`.
- E2E Playwright focalizadas:
  - `test_simulation_gutter_breakpoints_and_robot_start`: `passed`.
  - `test_world_editor_builds_valid_world_and_exposes_simulation_link`: `passed`.

Cambios destacados 1.3.3:
- Carga de mundos en web: al abrir un mundo se respeta y visualiza de inmediato la pose preestablecida del robot.
- Mejora del ejemplo `16_resolver_laberinto.py` con logica de exploracion mas robusta para laberintos de pasillo.

Para validacion completa por bloques, usar `Documentos/CHECKLIST_QA_RELEASE.md`.

## Notas de paridad visual

El mapa web usa la misma escala que Tkinter:

- `32 px = 100 mm`
- mundo base `2000 x 2000 mm` = `640 x 640 px`
- si el mapa no cabe en el panel visible, el contenedor web usa scroll.

Esto evita deformaciones visuales y mantiene la misma dimension fisica de mundos y assets en ambas interfaces.

## Unidades de medida en interfaz

- Distancias mostradas al usuario en web y Tkinter: `cm`.
- Unidad interna del motor de simulacion y geometria del mundo: `mm`.
- Angulos: `deg`.
