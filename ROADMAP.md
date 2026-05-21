# ROADMAP - Simulador EV3 Pybricks

Estado actualizado: 2026-05-20  
Version publicada: 1.3.0  
Repositorio: `fralmeagUTP/Codex_SimuladorLegoEV3`

## Estado General

El proyecto cuenta con dos interfaces activas:

- **Escritorio Tkinter**: aplicacion original para simulacion, editor de codigo, telemetria y editor de mundos.
- **Web Flask**: aplicacion multi-sesion con simulacion en `/`, editor de mundos en `/worlds` y ayuda en `/help`.

La version `1.3.0` esta publicada en GitHub mediante el tag `1.3`.

## Fases Completadas

- **Fase 1 - Domain: robot base**
  - Modelos principales del robot y base de movimiento.

- **Fase 2 - Domain: sensores y mundo**
  - Sensores de dominio, mundo 2D, colisiones base y superficies.

- **Fase 3 - Core: simulacion**
  - `CommandQueue`, `EventBus`, `SimulationEngine`.
  - Snapshots de estado para UI, web y telemetria.

- **Fase 4 - Runtime**
  - `ExecutionPolicy`, `RuntimeSandbox`, `RuntimeController`.
  - Watchdog de ejecucion y soporte de debug.

- **Fase 5 - API Pybricks virtual**
  - `pybricks.hubs`, `ev3devices`, `robotics`, `tools`, `parameters`.
  - `PybricksFactory` y `PybricksContext` aislado por contexto.

- **Fase 6 - Application Layer**
  - `SimulationService` como fachada de alto nivel.
  - `SnapshotDTO` para serializacion.
  - Propagacion correcta de estado `stopped` cuando un script termina naturalmente.

- **Fase 7 - UI Tkinter**
  - Ventana principal, canvas de mundo, editor, panel brick y telemetria.
  - Editor visual de mundos.

- **Fase 8 - Infraestructura**
  - Persistencia JSON de mundos.
  - Catalogo de ejemplos y mundos preset.

- **Fase 9 - Pulido y release escritorio**
  - Menus de ejemplos, mundos y escenarios.
  - Empaquetado Windows opcional.
  - Smoke tests de release.

- **Fase 10 - Web Flask y calidad continua**
  - Backend Flask con sesiones independientes.
  - Frontend web de simulacion y editor de mundos.
  - SSE con fallback por polling.
  - Debug web con breakpoints, step y continue.
  - CI en GitHub Actions.
  - Pruebas web, E2E Playwright, release y evidencia visual.

## Version Web 1.3.0

Implementado:

- Pagina `/` para simulacion del robot.
- Pagina `/worlds` para creacion y edicion de mundos.
- Pagina `/help` para ayuda operativa.
- Menus web `Archivo`, `Ejemplos`, `Mundos`, `Escenarios` y `Ayuda`.
- Editor web con numeros de linea, breakpoints clicables, resaltado de sintaxis, auto-indentacion, pares automaticos y autocompletado Pybricks contextual.
- Ubicacion inicial del robot desde canvas con `theta_deg`.
- Panel EV3 Brick con LED, LCD y altavoz.
- Editor de mundos con propiedades editables, rotacion, duplicado, eliminacion y arrastre directo.
- Guardado de mundos y enlace directo `/?world=<archivo>.json`.
- Sesiones independientes por pestana/navegador.
- Cleanup de sesiones expiradas.

## Paridad Visual Tkinter/Web

La web mantiene el tamano del mapa igual al de Tkinter:

- Escala de editor: `32 px = 100 mm`.
- Mundo base: `2000 x 2000 mm`.
- Tamano de canvas base: `640 x 640 px`.
- Si el panel visible es menor que el mapa, el contenedor web usa scroll.

Tambien se alineo la colocacion de assets:

- Assets multicelda se centran sobre la celda seleccionada, como en Tkinter.
- El arrastre conserva el offset desde el punto donde se tomo el objeto.
- El robot web usa dimensiones derivadas del sprite Tkinter.

## Estado de Pruebas

Ultima validacion relevante:

- `.\.venv\Scripts\python.exe -m pytest tests\web tests\e2e tests\application`
- Resultado: `117 passed`

Tambien se validaron previamente bloques de runtime, Pybricks API, UI, core, domain, persistence y release. La lista operativa completa esta en:

- `Documentos/CHECKLIST_QA_RELEASE.md`
- `Documentos/EVIDENCIA_QA_RELEASE_2026-05-20.md`

## Documentacion Disponible

- `README.md`: entrada principal del repositorio.
- `Documentos/MANUAL_DE_USO.md`: uso web y escritorio.
- `Documentos/GUIA_WEB_FLASK_WINDOWS.md`: operacion web en Windows.
- `Documentos/GUIA_RELEASE_WINDOWS.md`: build opcional de escritorio.
- `Documentos/SDD_MIGRACION_WEB_FLASK.md`: especificacion tecnica web.
- `Documentos/CHECKLIST_QA_RELEASE.md`: checklist de publicacion.
- `Documentos/EVIDENCIA_QA_RELEASE_2026-05-20.md`: evidencia de pruebas.
- `CHANGELOG.md`: historial de versiones.

## Siguientes Iteraciones Sugeridas

- Preview mas detallado al arrastrar assets del editor de mundos.
- Panel visual persistente de errores y advertencias de validacion.
- Exportacion de trazas de simulacion a CSV/JSON.
- Mejoras de cobertura Pybricks avanzada: `run_target`, `run_until_stalled`, `curve`, `hsv`, `detectable_colors`.
- Empaquetado web opcional para despliegue local con instalador.
- Autenticacion real si se expone fuera de entorno local/aula.
