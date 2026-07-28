# Simulador EV3 Pybricks

Version actual: 1.5.0 (fuente unica: `simulador_ev3/_version.py`)

Simulador educativo LEGO EV3 compatible con una API Pybricks virtual. El proyecto incluye aplicacion de escritorio Tkinter y aplicacion web Flask para ejecutar scripts, editar mundos 2D y visualizar telemetria del robot.

## Estado de interfaces

- Web Flask: simulacion (`/`), editor de mundos (`/worlds`) y ayuda (`/help`).
- Escritorio Tkinter: simulacion local, editor, mundos, telemetria y brick virtual.
- Ambas interfaces consumen el contrato de sesion compartido y mantienen paridad
  funcional de simulacion, perfiles, trazas y depuracion. La Web es la referencia
  visual; Tkinter conserva pequenas diferencias propias de controles nativos.

## Estado del repositorio

- Rama publicada: `main`
- Version objetivo en GitHub: `1.5.0`
- Interfaz web: incluida desde la version `1.3.0`
- Interfaz escritorio Tkinter: soportada para uso local Windows

## Estructura estandar de recursos

- Ejemplos compartidos: `examples/`
- Mundos compartidos: `worlds/`
- Documentacion e indice: `Documentos/INDICE_DOCUMENTACION.md`

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
- Estado final visible y reinicio explicito de simulacion.
- Evidencia visual reproducible de Web y Tkinter.
- Pruebas unitarias, integracion, contrato, UI, E2E Playwright, carga y release.

## Uso rapido web

Requisito: Python 3.11 o superior. Instalar dependencias antes de iniciar:

```powershell
py -3.12 -m pip install -r requirements.txt
```

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

### Configuracion segura de produccion

El modo local conserva sus valores educativos por defecto. Para desplegar la web en produccion, configura el entorno y usa HTTPS:

```powershell
$env:EV3_WEB_APP_ENV = "production"
$env:EV3_WEB_SECRET_KEY = "reemplaza-por-un-secreto-unico-de-al-menos-32-caracteres"
$env:EV3_WEB_SCRIPT_MAX_RUNTIME_S = "30"
$env:EV3_WEB_SESSION_COOKIE_SECURE = "true"
```

El servidor rechaza el arranque si falta una clave segura, si el tiempo maximo por script no es positivo o si las cookies no estan marcadas para HTTPS. No publiques la clave en el repositorio.

## Uso rapido escritorio

```powershell
.\.venv\Scripts\python.exe -m simulador_ev3.ui.main_window
```

Si no existe `.venv`, usar el interprete instalado compatible:

```powershell
py -3.12 -m simulador_ev3.ui.main_window
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

- Indice y estado documental: `Documentos/INDICE_DOCUMENTACION.md`
- Manual de uso: `Documentos/MANUAL_DE_USO.md`
- Guia web Windows: `Documentos/GUIA_WEB_FLASK_WINDOWS.md`
- Guia despliegue Linux: `Documentos/GUIA_DESPLIEGUE_LINUX.md`
- Arquitectura C4: `Documentos/ARQUITECTURA_C4.md`
- Diferencias simulador-robot: `Documentos/DIFERENCIAS_SIMULADOR_ROBOT.md`
- Controles de calidad: `Documentos/CONTROLES_CALIDAD.md`
- Roadmap: `ROADMAP.md`
- Checklist QA: `Documentos/CHECKLIST_QA_RELEASE.md`
- Evidencia QA: `Documentos/EVIDENCIA_QA_RELEASE_2026-05-20.md`
- SDD migracion web: `Documentos/SDD_MIGRACION_WEB_FLASK.md`
- Guia release escritorio Windows: `Documentos/GUIA_RELEASE_WINDOWS.md`

## Pruebas recomendadas

```powershell
py -3.12 -m pytest -q
py -3.12 -m ruff check simulador_ev3 tests
py -3.12 -m mypy
```

Ultima validacion actual: **689 pruebas aprobadas** y 71.50% de cobertura el
2026-07-24, junto con Ruff, Mypy, Bandit y Pip-Audit sin fallos. Este resultado
es evidencia fechada; volver a ejecutar los comandos anteriores para obtener el estado vigente. Para el detalle
de pruebas, cobertura, E2E y analisis de seguridad ver `docs/testing/` y
`Documentos/CONTROLES_CALIDAD.md`.

Cambios destacados 1.5.0:
- Misiones evaluables locales, resultados portables y exportación JSON/CSV.
- Paridad de navegación, ayuda y mundos reforzada entre Web y Tkinter.
- Regresión visual Tkinter en CI y requisitos OpenSpec archivados en las especificaciones base.

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
