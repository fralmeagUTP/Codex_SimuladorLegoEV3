# Evidencia QA de Release - 2026-05-20

## Alcance

Validacion del estado web/escritorio del simulador EV3 Pybricks para la fase de distribucion y calidad continua.

Version validada: 1.3.0  
Tag publicado: 1.3  
Commit de release: `d29daed`

## Entorno

- Sistema: Windows
- Python: 3.11.9
- Entorno: `.venv`
- Dependencias: `.\.venv\Scripts\python.exe -m pip install -e .[dev]`
- Navegador E2E: Chromium instalado con `.\.venv\Scripts\python.exe -m playwright install chromium`

## Resultados automatizados

| Bloque | Comando | Resultado |
|---|---|---|
| Web unit/integration | `.\.venv\Scripts\python.exe -m pytest tests\web` | 59 passed |
| E2E browser | `.\.venv\Scripts\python.exe -m pytest tests\e2e` | 12 passed |
| Application + runtime + Pybricks API | `.\.venv\Scripts\python.exe -m pytest tests\application tests\runtime tests\pybricks_api` | 150 passed |
| Core + domain + persistence | `.\.venv\Scripts\python.exe -m pytest tests\core tests\domain tests\persistence` | 231 passed |
| UI Tkinter mock | `.\.venv\Scripts\python.exe -m pytest tests\ui` | 59 passed |
| Release smoke/full health | `.\.venv\Scripts\python.exe -m pytest tests\release` | 9 passed |
| Smoke web servidor real | `.\scripts\restart_web.cmd` + `.\scripts\smoke_web.cmd` | OK |
| Healthcheck servidor real | `Invoke-WebRequest http://127.0.0.1:5050/healthz` | HTTP 200 |
| Build Windows | `powershell -ExecutionPolicy Bypass -File .\scripts\build_release_windows.ps1 -PythonExe .\.venv\Scripts\python.exe` | OK |
| Artefactos build | `dist\SimuladorEV3\SimuladorEV3.exe` + `Documentos\Ejemplos` + `Documentos\Mundos` | OK |
| Validacion final web + E2E + application | `.\.venv\Scripts\python.exe -m pytest tests\web tests\e2e tests\application` | 117 passed |

Total verificado por bloques principales: 520 tests passed. La validacion final de 117 pruebas se ejecuta como bloque adicional solapado para confirmar la integracion web/E2E/application despues de las correcciones finales.

Nota: `.\.venv\Scripts\python.exe -m pytest` se interrumpio por timeout local de 180 s antes de entregar salida consolidada. La validacion se completo ejecutando los bloques del checklist QA por separado.

## Cobertura E2E Playwright

`tests/e2e/test_web_playwright.py` cubre:

- Carga de la pantalla de simulacion `/`.
- Ejecucion del script por defecto y render en pantalla EV3.
- Carga de `/worlds`, seleccion de asset, guardado de mundo y enlace a simulacion.
- Menus web de ejemplos, mundos, escenarios y ayuda.
- Breakpoints clicables desde el margen del editor.
- Ubicacion inicial del robot desde el canvas.
- Auto-indentacion, pares automaticos, autocompletado Pybricks y resaltado de sintaxis.
- Estado del altavoz EV3.
- Edicion de propiedades y arrastre directo de assets en el editor de mundos.
- Carga de `/help`.
- Dos contextos de navegador independientes ejecutando scripts distintos sin cruce de estado visible.

## Evidencia visual generada

Comando:

```powershell
.\.venv\Scripts\python.exe scripts\capture_web_evidence.py
```

Archivos:

- `Documentos\EVIDENCIA_WEB_2026-05-20\simulacion_1366x768.png`
- `Documentos\EVIDENCIA_WEB_2026-05-20\mundos_1366x768.png`
- `Documentos\EVIDENCIA_WEB_2026-05-20\simulacion_1570x900.png`
- `Documentos\EVIDENCIA_WEB_2026-05-20\mundos_1570x900.png`
- `Documentos\EVIDENCIA_WEB_2026-05-20\menu_ejemplos_1366x768.png`
- `Documentos\EVIDENCIA_WEB_2026-05-20\editor_sintaxis_autocomplete_1366x768.png`
- `Documentos\EVIDENCIA_WEB_2026-05-20\brick_altavoz_1366x768.png`
- `Documentos\EVIDENCIA_WEB_2026-05-20\mundos_propiedades_1366x768.png`
- `Documentos\EVIDENCIA_WEB_2026-05-20\perfil_a_sesion_independiente.png`
- `Documentos\EVIDENCIA_WEB_2026-05-20\perfil_b_sesion_independiente.png`

El script valida que los controles principales de `/` y `/worlds` esten visibles en los viewports pedidos, captura flujos nuevos del editor/menus/brick/editor de mundos, y captura dos perfiles independientes ejecutando scripts distintos.

En version `1.3.0`, el script tambien valida que el canvas del mundo web mantenga el tamano Tkinter del mapa base: `640 x 640 px` para `2000 x 2000 mm`.

## Correcciones validadas despues de la evidencia inicial

- El mapa web conserva escala `32 px = 100 mm`.
- Los assets web no se estiran y se colocan centrados como en Tkinter.
- El arrastre de assets conserva offset.
- Scripts que terminan naturalmente pasan a estado `stopped`, evitando apariencia de cuelgue.
- Servidor reiniciado y healthcheck validado con `running_simulations: 0`.

## Pendientes manuales de release

- Ninguno para la entrega web actual.

## Estado

Automatizacion QA web/E2E integrada, evidencia visual generada, smoke web validado y version `1.3` publicada en GitHub. El build Windows fue verificado, pero no es requisito de la entrega actual porque no se distribuira ejecutable por el momento.
