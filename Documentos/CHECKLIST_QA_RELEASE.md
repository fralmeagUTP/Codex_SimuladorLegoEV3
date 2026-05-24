# Checklist QA de Release

Usar esta lista antes de publicar un build o entregar una version web/escritorio.

Version vigente del checklist: 1.3.0  
Fecha de actualizacion: 2026-05-20

## 1. Preparacion

- Confirmar version en `pyproject.toml`.
- Confirmar entrada nueva en `CHANGELOG.md`.
- Confirmar que `ROADMAP.md` refleja el estado real.
- Confirmar que `README.md` resume la version publicada y rutas principales.
- Confirmar evidencia QA en `Documentos\EVIDENCIA_QA_RELEASE_YYYY-MM-DD.md`.
- Crear entorno limpio con Python 3.11 o superior.
- Instalar dependencias con `.\.venv\Scripts\python.exe -m pip install -e .[dev]`.

## 2. Pruebas automatizadas

- Ejecutar `.\.venv\Scripts\python.exe -m pytest tests\web`.
- Ejecutar `.\.venv\Scripts\python.exe -m pytest tests\web\test_web_units.py`.
- Ejecutar `.\.venv\Scripts\python.exe -m pytest tests\application tests\runtime tests\pybricks_api`.
- Ejecutar `.\.venv\Scripts\python.exe -m pytest tests\core tests\domain tests\persistence`.
- Ejecutar `.\.venv\Scripts\python.exe -m pytest tests\ui`.
- Ejecutar `.\.venv\Scripts\python.exe -m pytest tests\release`.
- Ejecutar `.\.venv\Scripts\python.exe -m pytest tests\e2e` en un entorno con Chromium de Playwright instalado.
- Revisar que GitHub Actions ejecute `pytest` en Windows sin fallos.

## 3. Smoke web

- Reiniciar servidor con `.\scripts\restart_web.cmd`.
- Verificar `http://127.0.0.1:5050/healthz`.
- Ejecutar `.\scripts\smoke_web.cmd`.
- Abrir `/` y confirmar que carga la pantalla de simulacion.
- Abrir `/worlds` y confirmar que carga el editor de mundos.
- Abrir `/help` y confirmar que carga la ayuda.

## 4. Flujo de simulacion

- Usar menu `Archivo` para crear, abrir y guardar script.
- Cargar un ejemplo desde el menu `Ejemplos`.
- Cargar un ejemplo desde el selector.
- Cargar un escenario desde el menu `Escenarios`.
- Cargar un mundo existente.
- Ejecutar, pausar, reanudar y detener.
- Ejecutar un script corto con `wait(100)` y confirmar que el estado final sea `stopped`.
- Confirmar movimiento del robot en canvas.
- Confirmar actualizacion de telemetria.
- Confirmar LED, pantalla y speaker en panel EV3.
- Probar debug con breakpoints desde el margen, step y continue.
- Probar auto-indentacion, pares automaticos, resaltado de sintaxis y autocompletado `Ctrl+Space`.
- Probar `Ubicar robot` desde canvas y ajuste de theta.

## 5. Flujo de mundos

- Crear mundo nuevo.
- Cambiar tamano del mundo.
- Colocar robot, muros, lineas y zonas.
- Mover por boton y arrastrar directamente un asset.
- Confirmar que el arrastre conserva el offset de seleccion, igual que Tkinter.
- Editar propiedades de asset, posicion y rotacion desde el panel lateral.
- Rotar, duplicar y eliminar un asset.
- Validar mundo.
- Guardar mundo en `worlds/` (o `Documentos\Mundos` si aun no migraste).
- Usar enlace de simulacion del mundo guardado.
- Importar el JSON guardado y confirmar que conserva placements.

## 6. Sesiones y limites

- Abrir dos navegadores o perfiles distintos.
- Confirmar que cada pestana crea una sesion independiente.
- Ejecutar scripts distintos sin cruce de estado.
- Confirmar que `tests\e2e` cubre automaticamente dos contextos de navegador independientes.
- Confirmar que `MAX_ACTIVE_SESSIONS` devuelve HTTP 429 al superar limite.
- Confirmar que `MAX_RUNNING_SIMULATIONS` devuelve HTTP 429 al superar limite.
- Confirmar que sesiones expiradas se cierran con cleanup periodico.

## 7. Revision visual

- Generar evidencia visual con `.\.venv\Scripts\python.exe scripts\capture_web_evidence.py`.
- Revisar `/` en 1366x768 y 1570x900.
- Revisar `/worlds` en 1366x768 y 1570x900.
- Confirmar paridad de mapa con Tkinter: mundo base `2000 x 2000 mm` debe renderizarse como `640 x 640 px`.
- Confirmar que celdas, lineas, muros, zonas y pisos no estan estirados.
- Confirmar que el panel usa scroll si el mapa no cabe completo.
- Revisar captura de menu de ejemplos.
- Revisar captura de editor con sintaxis y autocompletado.
- Revisar captura de brick con altavoz.
- Revisar captura de propiedades del editor de mundos.
- Confirmar que no hay textos solapados.
- Confirmar que canvas, editor, telemetria y brick son visibles sin desplazamientos incoherentes.
- Confirmar que controles principales siguen accesibles en viewport angosto.

## 8. Build Windows opcional

Ejecutar solo si se va a distribuir un ejecutable:

- Ejecutar `.\scripts\build_release_windows.ps1`.
- Confirmar que el ejecutable inicia.
- Confirmar que ejemplos y mundos se incluyen.
- Revisar logs si falla audio o carga de assets.

## 9. Publicacion GitHub

- Confirmar `git status --short --branch` sin cambios de release pendientes.
- Crear commit de release.
- Crear tag anotado, por ejemplo `git tag -a 1.3 -m "Release 1.3"`.
- Publicar con `git push origin main --tags`.
- Verificar remoto con `git ls-remote origin refs/heads/main refs/tags/1.3`.
