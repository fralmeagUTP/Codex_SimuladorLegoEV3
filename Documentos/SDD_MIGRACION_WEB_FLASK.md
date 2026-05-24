# SDD - Migracion Web del Simulador LEGO EV3 con Flask

Documento completado segun la plantilla SDD (Specification Driven Development).

## 1. Informacion General del Proyecto

| Campo | Valor |
|---|---|
| Nombre del Proyecto | Migracion Web del Simulador LEGO EV3 Pybricks |
| Version | 1.4 |
| Fecha | 2026-05-20 |
| Autor(es) | Equipo del proyecto Simulador LEGO EV3 / Codex |
| Stakeholders | Estudiantes, docentes, desarrolladores del simulador, usuarios de robotica educativa |
| Descripcion General | Conversion del simulador EV3 de escritorio basado en `tkinter` a una aplicacion web con Flask, Python, HTML, CSS y JavaScript. |
| Objetivo del Sistema | Permitir editar codigo Pybricks, construir mundos 2D, ejecutar simulaciones EV3 y visualizar telemetria desde navegador con multiples sesiones independientes. |
| Alcance | Backend Flask multi-sesion, frontend web, editor de codigo, editor de mundos, interpretacion de scripts Pybricks, motor de simulacion, telemetria, EV3 Brick virtual, ejemplos y mundos existentes. |

### Alcance incluido

- Multiples sesiones de usuario independientes.
- Una instancia de simulacion por sesion.
- Editor de codigo Python en navegador.
- Carga y ejecucion de scripts compatibles con Pybricks.
- Construccion, validacion, importacion y exportacion de mundos EV3.
- Render 2D de mundo, robot, obstaculos, lineas, zonas, trayectoria y colisiones.
- Panel EV3: LED, pantalla, altavoz y botones.
- Telemetria de robot, motores, sensores, brick, tiempo y colision.
- Catalogo de ejemplos y mundos existentes.
- API REST y streaming de snapshots.
- Paridad visual de mapa con Tkinter usando escala `32 px = 100 mm`.
- Estado de ejecucion consistente: scripts finalizados se reportan como `stopped`.

### Fuera del MVP inicial

- Aislamiento fuerte para usuarios publicos no confiables.
- Persistencia en base de datos.
- Autenticacion completa por usuario.
- Escalamiento distribuido con workers externos.
- Empaquetado final de produccion.
- Autenticacion de usuarios remotos y despliegue publico multiusuario.

## 2. Vision del Sistema

| Campo | Descripcion |
|---|---|
| Problema que resuelve | El simulador actual depende de una interfaz de escritorio `tkinter`, lo que limita acceso remoto, uso concurrente, despliegue en aula y evolucion de UI. |
| Usuarios objetivo | Estudiantes de robotica, docentes, instructores, desarrolladores y usuarios que aprenden Pybricks sin hardware fisico EV3. |
| Beneficios esperados | Acceso desde navegador, sesiones simultaneas, experiencia mas portable, reutilizacion del motor actual, integracion con ayuda y ejemplos. |
| Contexto de uso | Laboratorios educativos, computadores locales, red de aula, demostraciones, practica individual y evaluacion de scripts EV3. |

La migracion no debe reescribir la logica de simulacion. Debe preservar el dominio, motor, runtime, API Pybricks virtual, persistencia JSON y ejemplos existentes, reemplazando principalmente la capa `simulador_ev3/ui`.

## 3. Requisitos Funcionales (RF)

| ID | Requisito | Descripcion | Prioridad | Actor |
|---|---|---|---|---|
| RF-01 | Crear sesion | El sistema debe crear una sesion independiente con `session_id` y `owner_token`. | Alta | Usuario |
| RF-02 | Gestionar sesion | El sistema debe consultar, cerrar, expirar y limpiar sesiones sin afectar a otras. | Alta | Sistema |
| RF-03 | Editar codigo | El usuario debe escribir, modificar y cargar codigo Python Pybricks en el navegador. | Alta | Usuario |
| RF-04 | Ejecutar codigo | El sistema debe ejecutar el codigo en un sandbox asociado a la sesion. | Alta | Usuario |
| RF-05 | Controlar simulacion | El usuario debe ejecutar, pausar, reanudar, detener y reiniciar la simulacion. | Alta | Usuario |
| RF-06 | Interpretar Pybricks | El sistema debe soportar `pybricks.hubs`, `ev3devices`, `robotics`, `tools` y `parameters`. | Alta | Sistema |
| RF-07 | Procesar comandos | El sistema debe traducir llamadas Pybricks a `SimulationCommand`. | Alta | Sistema |
| RF-08 | Simular robot | El motor debe actualizar robot, motores, sensores, brick y mundo a 50 Hz. | Alta | Sistema |
| RF-09 | Emitir snapshots | El sistema debe exponer snapshots JSON por polling o SSE. | Alta | Sistema |
| RF-10 | Renderizar mundo | El frontend debe dibujar mundo, robot, trayectoria, colisiones y capas visuales. | Alta | Usuario |
| RF-11 | Mostrar telemetria | El frontend debe mostrar pose, motores, sensores, brick, ticks y tiempo. | Alta | Usuario |
| RF-12 | Gestionar mundos | El usuario debe crear, cargar, guardar, importar, exportar y aplicar mundos a la simulacion. | Alta | Usuario |
| RF-13 | Validar mundos | El sistema debe validar estructura, limites, solapes, robot unico y conectividad de lineas. | Alta | Sistema |
| RF-14 | Construir mundos | El editor debe permitir colocar, mover, rotar, duplicar y eliminar assets. | Alta | Usuario |
| RF-15 | Convertir mundo | El sistema debe convertir `EditorWorldModel` a `WorldModel` fisico antes de simular. | Alta | Sistema |
| RF-16 | Cargar ejemplos | El usuario debe seleccionar scripts desde `Documentos/Ejemplos`. | Media | Usuario |
| RF-17 | Cargar mundos preset | El usuario debe seleccionar mundos desde `Documentos/Mundos`. | Media | Usuario |
| RF-18 | Mostrar errores | El sistema debe mostrar error resumido y traceback sin tumbar servidor ni otras sesiones. | Alta | Usuario |
| RF-19 | Reproducir audio web | El navegador debe reproducir beeps del brick con Web Audio API. | Media | Usuario |
| RF-20 | Depurar codigo | El sistema debe soportar breakpoints, step y continue si se activa modo debug. | Media | Usuario |
| RF-21 | Separar funcionalidades web | La simulacion del robot y la creacion de mundos deben estar en paginas independientes. | Alta | Usuario |
| RF-22 | Simular mundo guardado | Despues de guardar un mundo, el usuario debe poder abrir la simulacion con ese mundo cargado por URL. | Alta | Usuario |

## 4. Requisitos No Funcionales (RNF)

| ID | Tipo | Descripcion | Prioridad |
|---|---|---|---|
| RNF-01 | Rendimiento | El engine debe correr a 50 Hz por sesion activa. | Alta |
| RNF-02 | Rendimiento UI | El navegador debe renderizar con `requestAnimationFrame` usando el ultimo snapshot recibido. | Alta |
| RNF-03 | Concurrencia | Dos o mas sesiones deben ejecutar scripts distintos sin cruzar estado. | Alta |
| RNF-04 | Seguridad | Cada endpoint de sesion debe validar `session_id` y `owner_token`. | Alta |
| RNF-05 | Seguridad | El sandbox debe bloquear modulos peligrosos como `os`, `sys`, `subprocess`, `socket`, `threading` y similares. | Alta |
| RNF-06 | Seguridad | `max_runtime_s` debe ser obligatorio en web para evitar ejecuciones infinitas. | Alta |
| RNF-07 | Escalabilidad | Deben existir limites `MAX_ACTIVE_SESSIONS`, `MAX_RUNNING_SIMULATIONS` y timeout de inactividad. | Alta |
| RNF-08 | Mantenibilidad | La capa web debe vivir en `simulador_ev3/web` sin modificar innecesariamente `simulador_ev3/ui`. | Alta |
| RNF-09 | Compatibilidad | Los mundos JSON existentes deben seguir cargando. | Alta |
| RNF-10 | Compatibilidad | Los ejemplos Pybricks existentes deben ejecutarse sin cambios cuando usen API soportada. | Alta |
| RNF-11 | Portabilidad | El backend debe poder ejecutarse localmente en Windows con Python 3.11+. | Media |
| RNF-12 | Observabilidad | Deben registrarse errores por sesion y eventos de estado. | Media |
| RNF-13 | Usabilidad | La UI debe separar simulacion y creacion de mundos para evitar controles mezclados. | Alta |
| RNF-14 | Integridad | La fuente de verdad del mundo debe estar en backend, no en estados divergentes de JavaScript. | Alta |
| RNF-15 | Aislamiento tecnico | La API Pybricks virtual no debe mezclar contexto entre sesiones. | Alta |

## 5. Casos de Uso

### 5.1 Diagrama de Casos de Uso

Diagrama textual:

```text
Usuario
  -> Crear sesion
  -> Editar codigo
  -> Cargar ejemplo
  -> Construir mundo
  -> Validar mundo
  -> Aplicar mundo a simulacion
  -> Ejecutar simulacion
  -> Pausar/Reanudar/Detener
  -> Ver telemetria
  -> Ver errores/debug
  -> Exportar mundo/script

Sistema
  -> Expirar sesiones
  -> Limpiar hilos
  -> Emitir snapshots
  -> Ejecutar sandbox
```

### 5.2 Especificacion de Casos de Uso

#### CU-01 - Crear sesion

- Actor: Usuario.
- Descripcion: Abre la app web y solicita una sesion aislada.
- Precondiciones: Servidor Flask activo.
- Flujo principal: navegador solicita `POST /api/sessions`; backend crea `SimulationSession`; devuelve `session_id` y `owner_token`.
- Flujos alternativos: si se supera capacidad, responde `429`.
- Postcondiciones: sesion creada en estado `created`.

#### CU-02 - Ejecutar script Pybricks

- Actor: Usuario.
- Descripcion: Ejecuta codigo Python compatible con Pybricks.
- Precondiciones: sesion valida y codigo cargado.
- Flujo principal: usuario pulsa ejecutar; backend carga codigo en `RuntimeSandbox`; crea modulos Pybricks; inicia `EngineThread` y `ScriptThread`; emite snapshots.
- Flujos alternativos: error de sintaxis o runtime se publica en panel de errores.
- Postcondiciones: simulacion corriendo, detenida o en error.

#### CU-03 - Construir mundo

- Actor: Usuario.
- Descripcion: Crea o modifica un mundo desde el editor web.
- Precondiciones: sesion valida.
- Flujo principal: selecciona asset; lo coloca en grid; backend actualiza `EditorWorldModel`; valida; frontend redibuja.
- Flujos alternativos: placement invalido devuelve errores de validacion.
- Postcondiciones: mundo actualizado en la sesion.

#### CU-04 - Aplicar mundo a simulacion

- Actor: Usuario.
- Descripcion: Usa el mundo construido como entorno fisico de simulacion.
- Precondiciones: mundo valido.
- Flujo principal: frontend llama `apply-to-simulation`; backend convierte con `WorldEditorService.to_world_model()`; actualiza `SimulationService`.
- Flujos alternativos: mundo invalido no se aplica.
- Postcondiciones: engine usa el mundo convertido.

#### CU-05 - Ver telemetria y EV3 Brick

- Actor: Usuario.
- Descripcion: Observa el estado del robot y brick virtual.
- Precondiciones: sesion creada, preferiblemente simulacion activa.
- Flujo principal: frontend recibe snapshots; actualiza canvas, motores, sensores, pantalla, LED y audio.
- Flujos alternativos: si no hay snapshot, muestra estado vacio o detenido.
- Postcondiciones: UI sincronizada con ultimo snapshot.

## 6. Modelo de Datos

### 6.1 Diccionario de Datos

| Entidad | Atributo | Tipo | Descripcion |
|---|---|---|---|
| UserSession | session_id | string | Identificador unico de sesion. |
| UserSession | owner_token | string | Token opaco para controlar la sesion. |
| UserSession | state | enum | `created`, `ready`, `running`, `paused`, `stopped`, `error`, `expired`. |
| UserSession | created_at | datetime | Fecha de creacion. |
| UserSession | last_seen_at | datetime | Ultima actividad. |
| SimulationSession | service | SimulationService | Fachada de simulacion por sesion. |
| SimulationSession | latest_snapshot | dict | Ultimo `SnapshotDTO.to_dict()`. |
| SimulationSession | latest_error | dict/null | Error y traceback de runtime. |
| SimulationSession | event_buffer | queue | Buffer de eventos SSE. |
| EditorWorldModel | schema_version | int | Version del esquema. |
| EditorWorldModel | grid_size_px | int | Tamano de celda visual, por defecto 32. |
| EditorWorldModel | world_width_cells | int | Ancho del mundo en celdas. |
| EditorWorldModel | world_height_cells | int | Alto del mundo en celdas. |
| Placement | id | string | Id unico del asset colocado. |
| Placement | asset_key | string | Clave del asset en `ASSET_CATALOG`. |
| Placement | x | int | Coordenada X en pixeles de editor. |
| Placement | y | int | Coordenada Y en pixeles de editor. |
| Placement | rotation | int | Rotacion 0, 90, 180 o 270. |
| WorldModel | width_mm | float | Ancho fisico del mundo. |
| WorldModel | height_mm | float | Alto fisico del mundo. |
| WorldModel | surface | SurfaceModel | Superficie de colores. |
| WorldModel | obstacles | list | Obstaculos fisicos. |
| WorldModel | beacons | list | Balizas IR. |
| SnapshotDTO | tick | int | Tick del engine. |
| SnapshotDTO | sim_time_s | float | Tiempo simulado. |
| SnapshotDTO | robot | dict | Pose del robot. |
| SnapshotDTO | motors | list | Estado de motores A-D. |
| SnapshotDTO | sensors | list | Estado de sensores conectados. |
| SnapshotDTO | brick | dict | LED, pantalla, altavoz y botones. |
| SnapshotDTO | colliding | bool | Estado de colision. |

### 6.2 Diagrama Entidad-Relacion (DER)

```text
UserSession 1 -- 1 SimulationSession
SimulationSession 1 -- 1 SimulationService
SimulationSession 1 -- 1 EditorWorldModel
EditorWorldModel 1 -- N Placement
SimulationService 1 -- 1 SimulationEngine
SimulationEngine 1 -- 1 WorldModel
WorldModel 1 -- N ObstacleModel
WorldModel 1 -- 1 SurfaceModel
WorldModel 1 -- N BeaconModel
SimulationEngine 1 -- N StateSnapshot
StateSnapshot 1 -- 1 SnapshotDTO
```

## 7. Arquitectura del Sistema

### 7.1 Estilo Arquitectonico

Arquitectura por capas con backend Flask y frontend web:

- Presentacion: HTML, CSS, JavaScript, Canvas 2D.
- API web: Flask Blueprints.
- Aplicacion: `SimulationSession`, `SessionManager`, `SimulationService`, `WorldEditorService`.
- Dominio: robot, sensores, brick, mundo, editor.
- Core: `SimulationEngine`, `CommandQueue`, `EventBus`.
- Runtime: `RuntimeController`, `RuntimeSandbox`, `ExecutionPolicy`.
- Infraestructura: persistencia JSON, assets, audio web en navegador.

### 7.2 Diagrama de Componentes

```text
Browser
  |-- HTML/CSS/JS
  |-- CanvasWorld
  |-- CodeEditor
  |-- TelemetryPanel
  |-- BrickPanel
  |-- API Client
        |
        v
Flask App
  |-- pages routes
  |-- api_simulation
  |-- api_worlds
  |-- api_examples
  |-- api_editor
        |
        v
SessionManager
  |-- SimulationSession[session_id]
        |
        v
SimulationService
  |-- RuntimeController
  |-- SimulationEngine
  |-- WorldEditorService
  |-- Pybricks virtual API
```

### 7.3 Diagrama de Paquetes

```text
simulador_ev3
  application
  core
  domain
  examples
  infrastructure
  persistence
  pybricks_api
  runtime
  ui              # escritorio existente, no se elimina
  web             # nueva capa Flask
```

### 7.4 Diagrama de Clases

```text
SessionManager
  +create_session()
  +get_session()
  +close_session()
  +cleanup_expired()

SimulationSession
  -service: SimulationService
  -editor_world: EditorWorldModel
  -latest_snapshot: dict
  -latest_error: dict
  +load_script()
  +start()
  +pause()
  +resume()
  +stop()
  +reset()
  +apply_editor_world()

SimulationService
  +load_script()
  +load_world_file()
  +set_robot_start()
  +start()
  +pause()
  +resume()
  +stop()
  +get_snapshot()

WorldEditorService
  +create_world()
  +place_asset()
  +move_asset()
  +rotate_asset_current()
  +validate()
  +to_world_model()
```

### 7.5 Arquitectura propuesta Flask

La nueva capa web debe agregarse en paralelo a la UI de escritorio. La carpeta `simulador_ev3/ui` no debe eliminarse ni ser dependencia directa de la web.

Estructura recomendada:

```text
simulador_ev3/
  web/
    __init__.py
    app.py
    config.py
    session_manager.py
    routes/
      __init__.py
      pages.py
      api_simulation.py
      api_examples.py
      api_worlds.py
      api_editor.py
    services/
      simulation_session.py
      snapshot_stream.py
      world_dto.py
    templates/
      base.html
      index.html
      worlds.html
      help.html
    static/
      css/
        app.css
      js/
        api.js
        canvas_world.js
        simulation_app.js
        world_editor_app.js
      images/
        ...
```

Responsabilidades:

- `app.py`: crea la app Flask, registra blueprints, configura rutas de estaticos y desactiva reloader en modo simulacion.
- `config.py`: define rutas a `Documentos/Ejemplos`, `Documentos/Mundos`, assets, limites de sesiones y politica de ejecucion.
- `session_manager.py`: administra sesiones activas, tokens, expiracion y limites.
- `api_simulation.py`: endpoints de ciclo de vida de simulacion.
- `api_editor.py`: endpoints de construccion y validacion de mundos.
- `snapshot_stream.py`: polling y/o SSE.
- `world_dto.py`: serializacion del mundo para render web.
- `index.html` + `simulation_app.js`: pagina exclusiva para cargar mundos, ejecutar scripts y ver telemetria.
- `worlds.html` + `world_editor_app.js`: pagina exclusiva para construir, validar, importar/exportar y guardar mundos.

### 7.5.1 Separacion de paginas web

La interfaz web se divide en dos superficies de trabajo:

| Ruta | Proposito | Controles incluidos | Controles excluidos |
|---|---|---|---|
| `/` | Simulacion del robot | Editor de codigo, ejemplos, selector de mundos, ejecutar/pausar/reanudar/detener/reiniciar, canvas, telemetria y EV3 Brick. | Paleta de assets, guardar mundo, importar/exportar mundo. |
| `/worlds` | Creacion de mundos | Paleta de assets, colocar/mover/rotar/duplicar/eliminar, pose inicial, validar, importar/exportar, guardar y enlace para simular. | Editor de codigo, ejecutar/pausar/reanudar/detener/reiniciar y telemetria. |

Flujo entre paginas:

1. El usuario crea el mundo en `/worlds`.
2. El usuario guarda el mundo en `Documentos/Mundos`.
3. El frontend muestra el enlace `/?world=<nombre>.json`.
4. La pagina `/` lee el parametro `world` con `URLSearchParams`.
5. Si el mundo existe en el selector, lo carga automaticamente con `/api/sessions/<id>/world`.

### 7.6 Componentes reutilizables y reemplazables

| Componente actual | Estado para web | Accion |
|---|---|---|
| `simulador_ev3/domain` | Reutilizable | Mantener sin cambios salvo bugs. |
| `simulador_ev3/core` | Reutilizable | Mantener `SimulationEngine`, `CommandQueue`, `EventBus`. |
| `simulador_ev3/runtime` | Reutilizable con adaptacion | Mantener sandbox, agregar aislamiento multi-sesion real. |
| `simulador_ev3/pybricks_api` | Reutilizable con refactor critico | Evitar `PybricksContext` global compartido entre sesiones. |
| `simulador_ev3/application` | Reutilizable | Usar `SimulationService`, `SnapshotDTO`, `WorldEditorService`. |
| `simulador_ev3/persistence` | Reutilizable | Usar `WorldRepository` para JSON existente. |
| `simulador_ev3/examples` | Reutilizable | Exponer con endpoints de ejemplos. |
| `simulador_ev3/assets` | Reutilizable | Copiar o servir como assets estaticos web. |
| `simulador_ev3/ui` | Reemplazar | No migrar linea por linea; crear HTML/CSS/JS nuevo. |
| `audio_output.py` | Adaptar | No reproducir audio en servidor; usar Web Audio API. |

Componentes de `simulador_ev3/ui` a reemplazar:

- `main_window.py` -> layout web y rutas Flask.
- `world_canvas.py` -> `canvas_world.js`.
- `world_canvas_editor.py` -> `world_editor.js`.
- `editor_panel.py` -> editor web (`textarea`, CodeMirror o Monaco).
- `telemetry_panel.py` -> `telemetry.js`.
- `brick_panel.py` -> `brick.js`.
- Dialogos `filedialog` y `messagebox` -> inputs web, modales y mensajes inline.

### 7.7 Modelo de despliegue MVP

Para el MVP local multi-sesion:

- Servidor recomendado: Waitress para operacion local estable; Flask dev server sin reloader solo para pruebas locales.
- Workers: un solo proceso Python hasta resolver aislamiento de Pybricks.
- Threads: multiples threads para atender HTTP/SSE y simulaciones.
- Sesiones: en memoria.
- Persistencia: archivos JSON existentes.
- Operacion Windows: scripts `scripts/start_web.ps1`, `scripts/stop_web.ps1` y `scripts/restart_web.ps1`, con wrappers `.cmd` para equipos que bloquean ejecucion directa de PowerShell.
- Operacion Waitress: `scripts/start_web_waitress.ps1` y `scripts/start_web_waitress.cmd`, usando la entrada `simulador_ev3.web.waitress_server`.
- Verificacion operativa: `scripts/smoke_web.ps1` y `scripts/smoke_web.cmd` validan rutas, assets estaticos y ciclo basico de sesion.
- Configuracion de host/puerto: variables `EV3_WEB_HOST` y `EV3_WEB_PORT`, con valores por defecto `127.0.0.1` y `5050`.
- Configuracion de aplicacion por entorno: `EV3_WEB_SECRET_KEY`, `EV3_WEB_EXAMPLES_DIR`, `EV3_WEB_WORLDS_DIR`, `EV3_WEB_IMAGE_ASSETS_DIR`, `EV3_WEB_SESSION_IDLE_TIMEOUT_MIN`, `EV3_WEB_MAX_ACTIVE_SESSIONS`, `EV3_WEB_MAX_RUNNING_SIMULATIONS`, `EV3_WEB_SCRIPT_MAX_RUNTIME_S`, `EV3_WEB_MAX_SCRIPT_SIZE_BYTES`, `EV3_WEB_MAX_WORLD_JSON_SIZE_BYTES`, `EV3_WEB_SSE_HEARTBEAT_S`, `EV3_WEB_ENABLE_SECURITY_HEADERS` y `EV3_WEB_SESSION_COOKIE_SECURE`.
- Cabeceras HTTP basicas: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `Content-Security-Policy` deben estar activas por defecto.

Para produccion o aula con usuarios no confiables:

- Ejecutar simulaciones en subprocess o workers separados.
- Aislar filesystem, red, CPU, memoria y tiempo.
- Mantener proyectos persistentes en base de datos o almacenamiento por usuario.

## 8. Contratos de Interfaz (UI/UX)

| Pantalla | Evento | Accion | Destino | Regla |
|---|---|---|---|---|
| Simulacion `/` | Cargar pagina | Crear sesion | `POST /api/sessions` | Cada pestana obtiene sesion propia. |
| Simulacion `/` | Parametro `?world=` | Cargar mundo guardado | `/api/sessions/<id>/world` | Solo si el mundo existe en `Documentos/Mundos`. |
| Editor codigo `/` | Click Ejecutar | Enviar script y arrancar | `/script`, `/start` | Requiere sesion valida. |
| Editor codigo `/` | Click Detener | Detener runtime | `/stop` | No afecta otras sesiones. |
| Editor codigo `/` | Click Pausar/Reanudar | Cambiar estado | `/pause`, `/resume` | Solo si esta corriendo/pausado. |
| Crear mundos `/worlds` | Cargar pagina | Crear sesion y mundo formal | `POST /api/sessions`, `/editor/world` | No expone ejecucion de scripts. |
| Canvas mundo `/worlds` | Click en modo pose | Definir posicion inicial | `/robot/start` | Coordenadas se convierten px -> mm. |
| Editor mundo `/worlds` | Click canvas con asset | Colocar placement | `/editor/world/place` | Backend valida asset y grid. |
| Editor mundo `/worlds` | Mover asset | Mover placement | `/editor/world/move` | Debe alinear a grid. |
| Editor mundo `/worlds` | Rotar | Rotar placement | `/editor/world/rotate` | Solo 0, 90, 180, 270. |
| Editor mundo `/worlds` | Duplicar | Clonar placement desplazado | `/editor/world/duplicate` | Evita solapamiento por tamano del asset. |
| Editor mundo `/worlds` | Validar | Obtener errores | `/editor/world/validate` | Backend es fuente de verdad. |
| Editor mundo `/worlds` | Guardar | Persistir JSON | `/editor/world/save` | Devuelve nombre `.json`. |
| Editor mundo `/worlds` | Simular guardado | Abrir simulacion | `/?world=<name>.json` | Integra paginas sin mezclar controles. |
| Telemetria `/` | Snapshot recibido | Actualizar datos | SSE/polling | Usar ultimo snapshot. |
| Brick EV3 `/` | Speaker recibido | Reproducir beep | Web Audio API | No usar audio servidor. |
| Ayuda | Click ayuda | Mostrar documentacion | `/help` o modal | Basada en manual adaptado web. |

## 9. Reglas de Negocio

| ID | Regla | Descripcion |
|---|---|---|
| RN-01 | Sesion aislada | Cada usuario/pestana debe tener su propio estado de simulacion. |
| RN-02 | Sesion protegida | Un usuario no puede controlar una sesion ajena sin `owner_token`. |
| RN-03 | Robot unico | Un mundo formal no puede contener mas de un robot. |
| RN-04 | Grid obligatorio | Todo placement debe estar alineado a `grid_size_px`. |
| RN-05 | Rotaciones discretas | Solo se permiten rotaciones 0, 90, 180 y 270. |
| RN-06 | Limite de mundo | El mundo no puede exceder `MAX_WORLD_PIXELS = 5120` por eje. |
| RN-07 | Muros bloqueantes | Los muros se convierten en obstaculos fisicos. |
| RN-08 | Zonas como superficie | Las zonas se convierten en colores de `SurfaceModel`. |
| RN-09 | Lineas negras | Las lineas se pintan como segmentos negros para `ColorSensor`. |
| RN-10 | Codigo sandbox | El codigo de usuario solo puede usar builtins y modulos permitidos. |
| RN-11 | Comandos bloqueantes | `straight`, `turn`, `run_time` y `run_angle` bloquean solo el `ScriptThread`. |
| RN-12 | Stop cooperativo | `stop` debe interrumpir `pybricks.tools.wait()` mediante `stop_event`. |
| RN-13 | Sin mezcla Pybricks | El contexto Pybricks no puede compartirse globalmente entre sesiones concurrentes. |
| RN-14 | Snapshot oficial | El frontend no calcula fisica; solo renderiza snapshots y mundos recibidos. |
| RN-15 | Errores aislados | Un error de script afecta solo a su sesion. |

## 10. Especificacion de Algoritmos

### 10.1 Algoritmo: Crear sesion

- Entrada: solicitud HTTP.
- Salida: `session_id`, `owner_token`, estado `created`.
- Descripcion:

```text
Inicio
  verificar limites de capacidad
  generar session_id UUID
  generar owner_token
  crear SimulationSession
  registrar en SessionManager
  devolver credenciales de sesion
Fin
```

### 10.2 Algoritmo: Validar mundo

- Entrada: `EditorWorldModel`.
- Salida: reporte con errores y advertencias.
- Descripcion:

```text
Inicio
  validar grid y dimensiones
  validar limite de 5120 px por eje
  validar ids vacios o duplicados
  validar asset_key en catalogo
  validar rotacion soportada
  validar alineacion a grid
  validar limites del mundo
  contar robots
  validar solapes por celda
  validar conectividad de lineas
  devolver ValidationReport
Fin
```

### 10.3 Algoritmo: Convertir mundo formal a mundo fisico

- Entrada: `EditorWorldModel`.
- Salida: `WorldModel`.
- Descripcion:

```text
Inicio
  world_width_mm = world_width_cells * CELL_SIZE_MM
  world_height_mm = world_height_cells * CELL_SIZE_MM
  crear SurfaceModel blanco
  para cada placement:
    si asset es wall: crear ObstacleModel
    si asset es zone: pintar SurfaceModel con color
    si asset es line: pintar segmento negro
    si asset es robot: extraer pose inicial
  devolver WorldModel
Fin
```

### 10.4 Algoritmo: Interpretar y ejecutar codigo Pybricks

- Entrada: codigo Python, sesion.
- Salida: ejecucion, snapshots, errores.
- Descripcion:

```text
Inicio
  cargar codigo en SimulationService
  preparar ExecutionPolicy
  crear API Pybricks virtual para la sesion
  compilar codigo con compile(source, "<script>", "exec")
  ejecutar en RuntimeSandbox con namespace restringido
  traducir llamadas Pybricks a SimulationCommand
  publicar errores si ocurren
Fin
```

### 10.5 Algoritmo: Tick de simulacion

- Entrada: `dt = 0.02`.
- Salida: `StateSnapshot`.
- Descripcion:

```text
Inicio
  drenar CommandQueue
  aplicar comandos a motores, drivebase y brick
  actualizar motores
  sincronizar drivebase
  integrar pose del robot
  detectar colisiones y revertir si aplica
  actualizar sensores
  actualizar brick
  resolver comandos bloqueantes completados
  construir StateSnapshot
  convertir a SnapshotDTO
Fin
```

### 10.6 Algoritmo: Stream de snapshots

- Entrada: callbacks de `SimulationService`.
- Salida: eventos SSE o respuesta polling.
- Descripcion:

```text
Inicio
  recibir SnapshotDTO
  guardar latest_snapshot en SimulationSession
  agregar evento snapshot al buffer SSE
  frontend consume ultimo snapshot
  renderizar canvas y paneles
Fin
```

## 11. API / Servicios

| Endpoint | Metodo | Descripcion |
|---|---|---|
| `/` | GET | Pagina de simulacion del robot. Acepta `?world=<archivo>.json` para carga automatica desde frontend. |
| `/worlds` | GET | Pagina de creacion y guardado de mundos. |
| `/help` | GET | Ayuda web adaptada. |
| `/api/sessions` | POST | Crear sesion. |
| `/api/sessions/<id>` | DELETE | Cerrar sesion. |
| `/api/sessions/<id>/script` | POST | Cargar codigo Python. |
| `/api/sessions/<id>/start` | POST | Iniciar simulacion. |
| `/api/sessions/<id>/pause` | POST | Pausar simulacion. |
| `/api/sessions/<id>/resume` | POST | Reanudar simulacion. |
| `/api/sessions/<id>/stop` | POST | Detener simulacion. |
| `/api/sessions/<id>/reset` | POST | Reiniciar sesion/simulacion. |
| `/api/sessions/<id>/snapshot` | GET | Obtener ultimo snapshot. |
| `/api/sessions/<id>/stream` | GET | Stream SSE de snapshots y eventos. |
| `/api/sessions/<id>/robot/start` | POST | Definir pose inicial del robot. |
| `/api/worlds` | GET | Listar mundos disponibles. |
| `/api/worlds/<name>` | GET | Obtener JSON de mundo. |
| `/api/sessions/<id>/world` | POST | Cargar mundo preset en sesion. |
| `/api/sessions/<id>/world/upload` | POST | Subir mundo JSON. |
| `/api/examples` | GET | Listar ejemplos. |
| `/api/examples/<name>` | GET | Obtener codigo de ejemplo. |
| `/api/editor/assets` | GET | Obtener catalogo de assets. |
| `/api/sessions/<id>/editor/world` | GET/POST | Obtener o crear mundo formal. |
| `/api/sessions/<id>/editor/world/resize` | POST | Redimensionar mundo. |
| `/api/sessions/<id>/editor/world/place` | POST | Colocar asset. |
| `/api/sessions/<id>/editor/world/move` | POST | Mover asset. |
| `/api/sessions/<id>/editor/world/rotate` | POST | Rotar asset. |
| `/api/sessions/<id>/editor/world/duplicate` | POST | Duplicar asset. |
| `/api/sessions/<id>/editor/world/placements/<placement_id>` | DELETE | Eliminar asset. |
| `/api/sessions/<id>/editor/world/validate` | POST | Validar mundo. |
| `/api/sessions/<id>/editor/world/apply-to-simulation` | POST | Convertir y aplicar mundo al engine. |
| `/api/sessions/<id>/debug/breakpoints` | POST | Definir breakpoints. |
| `/api/sessions/<id>/debug/continue` | POST | Continuar debug. |
| `/api/sessions/<id>/debug/step` | POST | Ejecutar siguiente paso. |

### 11.1 Contrato de sesion

Crear sesion:

```http
POST /api/sessions
```

Respuesta:

```json
{
  "session_id": "9c661df0-8ef4-4f34-b6c9-0b8cfcf0bb3d",
  "owner_token": "opaque-token",
  "status": "created",
  "limits": {
    "max_runtime_s": 30,
    "idle_timeout_min": 30
  }
}
```

Reglas:

- `session_id` identifica el estado funcional.
- `owner_token` autoriza operaciones sobre la sesion.
- El token puede devolverse como cookie `HttpOnly`, `SameSite=Lax`; si hay HTTPS, tambien `Secure`.
- Las rutas `/api/sessions/<id>/...` deben responder `404` si la sesion no existe o expiro.
- Deben responder `403` si el token no corresponde.

Contrato minimo de `SessionManager`:

```python
class SessionManager:
    def create_session(self) -> tuple[str, str]: ...
    def get_session(self, session_id: str, owner_token: str | None = None) -> SimulationSession: ...
    def close_session(self, session_id: str) -> None: ...
    def touch(self, session_id: str) -> None: ...
    def cleanup_expired(self) -> int: ...
```

### 11.2 Contrato de carga y ejecucion de script

```http
POST /api/sessions/<id>/script
Content-Type: application/json

{
  "source": "from pybricks.hubs import EV3Brick\n..."
}
```

Respuesta:

```json
{
  "status": "ready",
  "loaded": true,
  "syntax_error": null
}
```

Iniciar:

```http
POST /api/sessions/<id>/start
Content-Type: application/json

{
  "debug": false,
  "step_mode": false
}
```

Respuesta:

```json
{
  "status": "running"
}
```

### 11.3 Contrato de snapshot

```http
GET /api/sessions/<id>/snapshot
```

Respuesta:

```json
{
  "status": "running",
  "snapshot": {
    "tick": 120,
    "sim_time_s": 2.4,
    "colliding": false,
    "robot": {
      "x_mm": 310.0,
      "y_mm": 200.0,
      "theta_deg": 0.0
    },
    "motors": [
      {"port": "A", "speed": 0.0, "angle": 0.0, "state": "IDLE"}
    ],
    "sensors": [
      {"port": "S1", "type": "ColorSensorModel", "value": "BLACK", "data": {}}
    ],
    "brick": {
      "led": "GREEN",
      "screen": {"lines": ["Hola EV3"], "width_px": 178, "height_px": 128},
      "speaker": {"freq": 440, "duration_ms": 100, "volume": 50},
      "buttons": []
    }
  },
  "error": null
}
```

SSE:

```http
GET /api/sessions/<id>/stream
Accept: text/event-stream
```

Eventos:

```text
event: snapshot
data: {"tick": 120, "sim_time_s": 2.4}

event: status
data: {"status": "stopped"}

event: error
data: {"error": "division by zero", "traceback": "..."}
```

### 11.4 Contrato de mundo para render web

El frontend requiere un DTO de mundo que pueda dibujarse sin conocer clases Python:

```json
{
  "width_mm": 2000,
  "height_mm": 2000,
  "surface": {
    "cell_size_mm": 12.5,
    "default_color": "WHITE",
    "cells": [
      {"col": 10, "row": 5, "color": "BLACK", "reflectance": 5.0}
    ]
  },
  "obstacles": [
    {"name": "wall:wall_64x64_a:wall_0001", "vertices": [[100,100], [300,100], [300,300], [100,300]]}
  ],
  "beacons": [
    {"name": "beacon1", "x_mm": 500, "y_mm": 800, "channel": 1}
  ],
  "editor_spec": {
    "schema_version": 1,
    "grid_size_px": 32,
    "world_width_cells": 20,
    "world_height_cells": 20,
    "placements": []
  }
}
```

Regla: cuando exista `editor_spec`, el canvas puede dibujar assets por imagen; si solo existe `world`, debe dibujar geometria basica.

### 11.5 Contrato de validacion de mundo

```http
POST /api/sessions/<id>/editor/world/validate
```

Respuesta:

```json
{
  "valid": false,
  "errors": [
    {
      "code": "OUT_OF_BOUNDS",
      "message": "Placement wall_0001 excede limites del mundo.",
      "placement_id": "wall_0001",
      "cell": [10, 4]
    }
  ],
  "warnings": [
    {
      "code": "LINE_OPEN_END",
      "message": "Linea line_0001 tiene extremo abierto hacia E.",
      "placement_id": "line_0001",
      "cell": [4, 6]
    }
  ]
}
```

## 12. Trazabilidad

| RF | Caso de Uso | Modulo | Prueba |
|---|---|---|---|
| RF-01 | CU-01 | `web/session_manager.py` | Crear sesion devuelve id/token. |
| RF-02 | CU-01 | `SessionManager` | Expira y cierra sesion. |
| RF-03 | CU-02 | `static/js/editor.js` | Editor envia codigo. |
| RF-04 | CU-02 | `RuntimeSandbox` | Ejecuta script simple. |
| RF-05 | CU-02 | `api_simulation.py` | Start/pause/resume/stop/reset. |
| RF-06 | CU-02 | `pybricks_api` | Imports Pybricks funcionan. |
| RF-07 | CU-02 | `CommandQueue` | Llamadas generan comandos. |
| RF-08 | CU-02 | `SimulationEngine` | Robot avanza y sensores actualizan. |
| RF-09 | CU-05 | `SnapshotDTO`, `snapshot_stream.py` | Snapshot JSON valido. |
| RF-10 | CU-05 | `canvas_world.js` | Canvas no vacio y robot visible. |
| RF-11 | CU-05 | `telemetry.js` | Telemetria cambia. |
| RF-12 | CU-03 | `api_editor.py` | CRUD de mundo. |
| RF-13 | CU-03 | `ValidationEngine` | Detecta mundo invalido. |
| RF-14 | CU-03 | `WorldEditorService` | Colocar/mover/rotar/duplicar. |
| RF-15 | CU-04 | `to_world_model()` | Mundo se aplica al engine. |
| RF-16 | CU-02 | `ExampleCatalog` | Lista y carga ejemplos. |
| RF-17 | CU-04 | `WorldRepository` | Carga mundos preset. |
| RF-18 | CU-02 | `RuntimeSandbox` | Error no tumba servidor. |
| RF-19 | CU-05 | `brick.js` | Beep con Web Audio API. |
| RF-20 | CU-02 | `RuntimeSandbox` debug | Step/breakpoints. |

## 13. Plan de Pruebas

| ID | Descripcion | Entrada | Resultado Esperado |
|---|---|---|---|
| PT-01 | Crear dos sesiones | Dos llamadas `POST /api/sessions` | IDs distintos, estados aislados. |
| PT-02 | Ejecutar scripts distintos | Script A y script B en sesiones distintas | Snapshots distintos sin mezcla. |
| PT-03 | Detener una sesion | `POST /stop` en sesion A | Sesion B sigue corriendo. |
| PT-04 | Validar mundo invalido | Placement fuera de limites | Error `OUT_OF_BOUNDS`. |
| PT-05 | Validar robot duplicado | Dos robots | Error `MULTIPLE_ROBOTS`. |
| PT-06 | Convertir mundo | Mundo con muro/zona/linea | `WorldModel` con obstaculos y superficie. |
| PT-07 | Cargar ejemplo | `01_basico_avanzar.py` | Codigo aparece en editor. |
| PT-08 | Ejecutar DriveBase | Script con `straight(300)` | Robot cambia `x_mm/y_mm`. |
| PT-09 | Sensor color | Mundo con linea negra | `ColorSensor` detecta negro/reflection baja. |
| PT-10 | Sensor ultrasonido | Obstaculo frente al robot | Distancia cambia. |
| PT-11 | EV3 Brick | Script con pantalla/LED/beep | UI muestra texto, LED y audio. |
| PT-12 | Runtime error | Script con excepcion | Error visible, servidor sigue activo. |
| PT-13 | Timeout script | Bucle sin fin | Sesion entra en error/stop por timeout. |
| PT-14 | Seguridad import | Script `import os` | ImportError por modulo bloqueado. |
| PT-15 | SSE/polling | Simulacion corriendo | Frontend recibe snapshots. |
| PT-16 | Expiracion | Sesion inactiva | Cleanup detiene hilos y libera memoria. |
| PT-17 | Canvas responsive | Redimensionar ventana | Mundo se redibuja sin perder escala. |
| PT-18 | Exportar mundo | Mundo creado en web | JSON compatible con escritorio. |

## 14. Criterios de Aceptacion

El sistema debe permitir:

- Crear multiples sesiones independientes.
- Ejecutar scripts Pybricks desde navegador.
- Controlar una simulacion por sesion.
- Construir mundos con assets del catalogo formal.
- Validar mundos antes de simular.
- Convertir mundos web a `WorldModel`.
- Cargar mundos y ejemplos existentes.
- Visualizar robot, trayectoria, colisiones, telemetria y EV3 Brick.
- Mostrar errores de runtime y validacion.
- Reproducir audio del brick en navegador.

El sistema debe validar:

- `session_id` existente.
- `owner_token` correcto.
- Limites de sesiones activas.
- Limites de simulaciones corriendo.
- Tiempo maximo de ejecucion de script.
- Modulos bloqueados en sandbox.
- Mundo dentro de limites.
- Un solo robot por mundo.
- Placements alineados a grid.
- Rotaciones permitidas.
- Solapes invalidos.
- Assets reconocidos.

Criterio funcional minimo del MVP:

- Dos navegadores o pestanas ejecutan simulaciones distintas en paralelo sin compartir estado.
- Un script de `Documentos/Ejemplos` se ejecuta sin cambios.
- Un mundo de `Documentos/Mundos` se carga y afecta sensores.
- Un mundo creado en web se exporta y puede abrirse en la app de escritorio.
- Un error de script no afecta otras sesiones.

## 15. Gestion del Proyecto

| Campo | Valor |
|---|---|
| Metodologia | Desarrollo basado en especificaciones, iterativo por fases. |
| Herramientas | Python 3.11+, Flask, HTML, CSS, JavaScript, Canvas 2D, pytest, Playwright, Git. |
| Repositorio | `Codex_SimuladorLegoEV3`. |
| Documentacion base | `Documentos/SDD_MIGRACION_WEB_FLASK.md`, `Documentos/MANUAL_DE_USO.md`, `Documentos/Mundos`, `Documentos/Ejemplos`. |

### Cronograma propuesto

| Fase | Entregable | Resultado |
|---|---|---|
| Fase 1 | Backend Flask multi-sesion | Sesiones, control de simulacion, snapshot por polling. |
| Fase 2 | Frontend de simulacion | Canvas, editor, telemetria, brick. |
| Fase 3 | Construccion de mundos | Editor web, validacion, import/export. |
| Fase 4 | Streaming y debug | SSE, errores, breakpoints opcionales. |
| Fase 5 | Endurecimiento | Aislamiento fuerte, limites, pruebas E2E, preparacion produccion. |

### Plan de migracion detallado

#### Fase 1 - Backend Flask minimo multi-sesion

Entregables:

- Dependencia `Flask`.
- `simulador_ev3/web/app.py`.
- `SessionManager` thread-safe.
- `SimulationSession` como wrapper aislado por usuario.
- Endpoints de sesion, script, start, pause, resume, stop, reset y snapshot.
- Polling inicial para snapshots.

Criterios:

- Dos navegadores crean sesiones distintas.
- Cada sesion carga un script diferente.
- Detener una sesion no detiene la otra.
- Los snapshots no se cruzan entre sesiones.

#### Fase 2 - Frontend de simulacion

Entregables:

- `index.html`, `app.css`, `api.js`, `simulation_app.js`.
- Editor de codigo.
- Canvas de mundo.
- Panel de telemetria.
- Panel EV3 Brick.
- Carga de ejemplos y mundos.
- Carga automatica de mundo con `/?world=<archivo>.json`.

Criterios:

- Un ejemplo se ejecuta desde navegador.
- El robot se mueve en canvas.
- La telemetria cambia en tiempo real.
- LED, pantalla y speaker se reflejan en UI.

#### Fase 3 - Editor de mundos web

Entregables:

- `worlds.html` y `world_editor_app.js`.
- Catalogo de assets desde backend.
- CRUD de `EditorWorldModel`.
- Drag/drop o click-to-place en grid.
- Validacion backend.
- Import/export JSON compatible.
- Conversion y aplicacion a `WorldModel`.
- Guardado en `Documentos/Mundos` y enlace para simular el mundo guardado.

Criterios:

- Un mundo creado en web puede abrirse en escritorio.
- Un mundo existente puede abrirse y editarse en web.
- Sensores responden al mundo convertido.

#### Fase 4 - Streaming, ayuda y debug

Entregables:

- SSE para snapshots y eventos.
- Pagina o modal `/help`.
- Consola de errores.
- Debug opcional: breakpoints, step, continue.

Criterios:

- El frontend recibe eventos sin polling agresivo.
- Los errores de runtime se muestran con traceback.
- La ayuda web cubre flujo de uso, mundos, sesiones y Pybricks.

#### Fase 5 - Endurecimiento y preparacion produccion

Entregables:

- Aislamiento real de Pybricks multi-sesion.
- Limites de CPU/tiempo/memoria.
- Cleanup robusto.
- Pruebas E2E con Playwright.
- CI.

Criterios:

- Scripts no confiables no acceden a filesystem/red.
- Sesiones expiradas liberan hilos.
- El sistema responde `429` al superar capacidad.

### Riesgo tecnico principal

El riesgo original era que `PybricksFactory` registrara modulos en `sys.modules` y que `PybricksContext` fuera global, lo que podia mezclar el engine de una sesion con el script de otra.

Estado actual:

1. `PybricksContext` usa `contextvars.ContextVar` para separar el contexto activo por ejecucion.
2. `PybricksFactory.create()` devuelve un arbol de modulos virtuales para el import hook del sandbox.
3. Los modulos `pybricks.*` no se registran en `sys.modules`; `cleanup()` solo elimina registros legacy si existen.
4. Para uso publico de alta concurrencia, `subprocess` por sesion sigue siendo una opcion futura de endurecimiento.

## 16. Integracion con Agentes de IA

### 16.1 Roles

| Agente | Responsabilidad |
|---|---|
| Arquitecto | Mantener coherencia entre SDD, arquitectura Flask y capas existentes. |
| Backend Flask | Implementar rutas, sesiones, streaming, seguridad y servicios. |
| Frontend Web | Implementar editor, canvas, telemetria, brick y ayuda. |
| Simulacion | Adaptar runtime, Pybricks virtual y aislamiento multi-sesion. |
| QA | Crear pruebas unitarias, integracion, E2E y criterios de aceptacion. |
| Documentacion | Convertir manual actual a ayuda web y mantener SDD actualizado. |

### 16.2 Prompt Base

```text
Actua como un desarrollador experto en Python, Flask, JavaScript y simuladores educativos.
Usa esta especificacion SDD como fuente de verdad.

Restricciones:
- No inventar requisitos.
- Preservar dominio, core, runtime, pybricks_api, persistence y ejemplos existentes.
- No acoplar la nueva web a tkinter.
- Soportar multiples sesiones independientes.
- No compartir SimulationService, SimulationEngine, RuntimeController ni contexto Pybricks entre sesiones.
- Usar WorldEditorService y ValidationEngine para mundos.
- Usar SnapshotDTO como contrato inicial de frontend.
- Generar codigo limpio, probado y mantenible.
```

## 17. Control de Versiones

| Version | Fecha | Cambios |
|---|---|---|
| 0.1 | 2026-05-18 | Creacion inicial del SDD de migracion web Flask. |
| 0.2 | 2026-05-18 | Incorporacion de multiples sesiones de usuario. |
| 0.3 | 2026-05-18 | Detalle de construccion de mundos, interpretacion Pybricks y simulacion web. |
| 1.0 | 2026-05-18 | Reestructuracion completa segun plantilla SDD con 17 apartados. |
| 1.1 | 2026-05-18 | Version hibrida: plantilla formal + detalle tecnico de migracion. |
| 1.2 | 2026-05-18 | Ampliacion de anexos tecnicos con especificaciones detalladas de backend, frontend, seguridad y pruebas. |
| 1.3 | 2026-05-19 | Separacion de paginas web: simulacion en `/`, creacion de mundos en `/worlds`, e integracion `/?world=<archivo>.json`. |
| 1.4 | 2026-05-20 | Actualizacion release 1.3.0: paridad de tamano de mapa con Tkinter, correccion de estado `stopped`, evidencia visual, pruebas web/E2E y publicacion en GitHub. |

## Anexo A - Especificacion de construccion de mundos

### A.1 Modelo formal

El editor web debe usar `EditorWorldModel` como fuente de verdad:

```json
{
  "schema_version": 1,
  "grid_size_px": 32,
  "world_width_cells": 20,
  "world_height_cells": 20,
  "placements": [
    {"id": "wall_0001", "asset_key": "wall_64x64_a", "x": 64, "y": 96, "rotation": 0}
  ]
}
```

Constantes:

- `GRID_SIZE_PX = 32`
- `CELL_SIZE_MM = 100.0`
- `SUPPORTED_ROTATIONS = (0, 90, 180, 270)`
- `MAX_WORLD_PIXELS = 5120`
- `MAX_WORLD_CELLS = 160`
- `MAX_WORLD_MM = MAX_WORLD_CELLS * CELL_SIZE_MM` (el mundo por defecto es `4000 mm x 4000 mm`).

### A.2 Catalogo de assets

| Asset | Tipo | Capa | Tamano | Conectores |
|---|---|---|---|---|
| `robot_ev3_32x32` | robot | robot | 1x1 | - |
| `wall_64x64_a` | wall | wall | 2x2 | - |
| `wall_64x64_b` | wall | wall | 2x2 | - |
| `wall_64x64_c` | wall | wall | 2x2 | - |
| `zone_green_128` | zone | zone | 4x4 | - |
| `zone_red_128` | zone | zone | 4x4 | - |
| `zone_white_128` | zone | zone | 4x4 | - |
| `line_64_64_hor` | line | line | 2x2 | E/W |
| `line_64_64_ver` | line | line | 2x2 | N/S |
| `line_64x64_cruz` | line | line | 2x2 | N/S/E/W |
| `line_64_64_infder` | line | line | 2x2 | N/W |
| `line_64_64_infizq` | line | line | 2x2 | N/E |
| `line_64_64_supder` | line | line | 2x2 | S/W |
| `line_64_64_supizq` | line | line | 2x2 | S/E |
| `floor_tile_256_a` | floor | floor | 8x8 | - |
| `floor_tile_256_b` | floor | floor | 8x8 | - |
| `floor_tile_256_c` | floor | floor | 8x8 | - |

### A.3 Reglas de validacion

Errores bloqueantes:

- `INVALID_GRID`
- `INVALID_WORLD_SIZE`
- `WORLD_SIZE_EXCEEDS_MAX`
- `EMPTY_ID`
- `DUPLICATE_ID`
- `UNKNOWN_ASSET`
- `INVALID_ROTATION`
- `MISALIGNED_PLACEMENT`
- `OUT_OF_BOUNDS`
- `MULTIPLE_ROBOTS`
- `ZONE_OVERLAP`
- `LINE_OVERLAP`
- `WALL_OVERLAP`
- `ROBOT_OVERLAP`
- `WALL_INCOMPATIBLE_OVERLAP`

Advertencias:

- `LINE_OPEN_END`
- `LINE_BROKEN_LINK`
- `LINE_DISCONNECTED_COMPONENTS`

### A.4 Conversion a simulacion

`WorldEditorService.to_world_model()` debe producir:

- `WorldModel.width_mm = world_width_cells * CELL_SIZE_MM`
- `WorldModel.height_mm = world_height_cells * CELL_SIZE_MM`
- `ObstacleModel` para muros.
- `SurfaceModel` para zonas.
- Segmentos negros en superficie para lineas.
- Pose inicial desde placement de robot.

## Anexo B - Interpretacion Pybricks y simulacion

### B.1 Flujo de runtime

```text
Frontend editor
  -> POST /script
  -> SimulationSession.load_script()
  -> SimulationService.load_script()
  -> POST /start
  -> Pybricks virtual API por sesion
  -> RuntimeSandbox.compile/exec
  -> CommandQueue
  -> SimulationEngine.update(dt)
  -> SnapshotDTO
  -> SSE/polling
  -> Canvas/telemetria/brick
```

### B.2 API Pybricks minima

- `pybricks.hubs.EV3Brick`
- `pybricks.ev3devices.Motor`
- `TouchSensor`, `UltrasonicSensor`, `ColorSensor`, `GyroSensor`, `InfraredSensor`
- `pybricks.robotics.DriveBase`
- `pybricks.tools.wait`, `StopWatch`
- `pybricks.parameters.Port`, `Color`, `Stop`, `Direction`, `Button`

### B.3 Mapeo de comandos

| Pybricks | Comando interno |
|---|---|
| `Motor.run` | `MOTOR_RUN` |
| `Motor.run_time` | `MOTOR_RUN_TIME` |
| `Motor.run_angle` | `MOTOR_RUN_ANGLE` |
| `Motor.stop` | `MOTOR_STOP` |
| `Motor.brake` | `MOTOR_BRAKE` |
| `Motor.hold` | `MOTOR_HOLD` |
| `DriveBase.drive` | `DB_DRIVE` |
| `DriveBase.stop` | `DB_STOP` |
| `DriveBase.straight` | `DB_STRAIGHT` |
| `DriveBase.turn` | `DB_TURN` |
| `DriveBase.settings` | `DB_SETTINGS` |
| `EV3Brick.light.on` | `LED_ON` |
| `EV3Brick.light.off` | `LED_OFF` |
| `EV3Brick.speaker.beep` | `PLAY_SOUND` |
| `EV3Brick.screen.print` | `DISPLAY_TEXT` |
| `EV3Brick.screen.clear` | `SCREEN_CLEAR` |

### B.4 Consideracion multi-sesion critica

La implementacion actual ya evita registrar `pybricks.*` en `sys.modules` y usa `ContextVar` para el contexto activo de Pybricks. Esto permite separar las sesiones web dentro del mismo proceso.

Opciones de endurecimiento futuro:

- Subprocess por sesion para aislamiento fuerte de procesos.
- Workers separados para despliegues publicos o multiusuario intensivos.

## Anexo C - Ayuda web

La ayuda existente sirve como base, pero debe adaptarse:

- `MANUAL_DE_USO.md` -> `/help`.
- Menus de escritorio -> botones y paneles web.
- `Archivo`, `Mundos`, `Escenarios` -> acciones en barra lateral/superior.
- Atajos de escritorio -> opcionales en navegador.
- Agregar seccion nueva: sesiones de usuario.
- Agregar seccion nueva: carga/guardado web.
- Agregar seccion nueva: errores de sandbox.

Contenido minimo de ayuda web:

1. Inicio rapido.
2. Editor de codigo.
3. Ejecutar, pausar, detener y reiniciar.
4. Seleccion y construccion de mundo.
5. Posicion inicial del robot.
6. Telemetria.
7. EV3 Brick.
8. Ejemplos.
9. Sesiones.
10. Errores comunes.

## Anexo D - Especificacion detallada de componentes backend

### D.1 `simulador_ev3/web/app.py`

Responsabilidades:

- Crear la aplicacion Flask.
- Registrar blueprints de paginas y API.
- Configurar rutas estaticas.
- Configurar `SessionManager` como extension de aplicacion.
- Exponer `create_app(config=None)` para pruebas.
- Evitar que el reloader cree procesos duplicados cuando haya hilos de simulacion.

Contrato:

```python
def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(DefaultWebConfig)
    if config:
        app.config.update(config)
    app.extensions["session_manager"] = SessionManager(app.config)
    register_blueprints(app)
    return app
```

Configuracion minima:

```python
class DefaultWebConfig:
    EXAMPLES_DIR = "Documentos/Ejemplos"
    WORLDS_DIR = "Documentos/Mundos"
    IMAGE_ASSETS_DIR = "simulador_ev3/assets"
    MAX_ACTIVE_SESSIONS = 20
    MAX_RUNNING_SIMULATIONS = 8
    SESSION_IDLE_TIMEOUT_MIN = 30
    SCRIPT_MAX_RUNTIME_S = 30
    SNAPSHOT_POLL_MIN_MS = 50
    SSE_HEARTBEAT_S = 15
```

### D.2 `SessionManager`

Responsabilidades ampliadas:

- Crear sesiones.
- Validar autorizacion.
- Contabilizar sesiones activas y simulaciones corriendo.
- Evitar carreras entre requests concurrentes.
- Ejecutar limpieza periodica.
- Cerrar sesiones explicitamente cuando el navegador lo solicite.

Estado interno recomendado:

```python
class SessionRecord:
    session_id: str
    owner_token_hash: str
    created_at: datetime
    last_seen_at: datetime
    session: SimulationSession
```

Reglas de concurrencia:

- Usar `threading.RLock` para proteger el diccionario de sesiones.
- No sostener el lock global mientras se ejecuten operaciones largas del engine.
- Cada `SimulationSession` debe tener su propio lock interno.
- `cleanup_expired()` debe llamar `session.close()` fuera del lock global si la operacion puede bloquear.

Errores esperados:

- `SessionNotFound` -> HTTP 404.
- `SessionForbidden` -> HTTP 403.
- `CapacityExceeded` -> HTTP 429.
- `InvalidSessionState` -> HTTP 409.

### D.3 `SimulationSession`

Responsabilidades ampliadas:

- Encapsular exactamente una instancia de `SimulationService`.
- Guardar script actual.
- Guardar mundo actual.
- Guardar editor world actual.
- Guardar ultimo snapshot.
- Guardar ultimo error.
- Mantener estado visible para la UI.
- Mantener buffer de eventos para SSE.
- Exponer operaciones atomicas hacia rutas Flask.

Estado recomendado:

```python
class SimulationSession:
    session_id: str
    service: SimulationService
    editor_service: WorldEditorService
    source_code: str | None
    loaded_world_name: str | None
    status: str
    latest_snapshot: dict | None
    latest_error: dict | None
    event_buffer: deque[dict]
    lock: threading.RLock
```

Callbacks que debe registrar:

- `SimulationService.set_snapshot_callback(self._on_snapshot)`
- `SimulationService.set_error_callback(self._on_error)`
- `SimulationService.set_status_callback(self._on_status)`
- `SimulationService.set_debug_callback(self._on_debug)`

Formato interno de evento:

```json
{
  "type": "snapshot",
  "session_id": "uuid",
  "sequence": 120,
  "payload": {}
}
```

Metodos recomendados:

```python
def load_script(self, source: str) -> dict: ...
def start(self, debug: bool = False, step_mode: bool = False) -> dict: ...
def pause(self) -> dict: ...
def resume(self) -> dict: ...
def stop(self) -> dict: ...
def reset(self) -> dict: ...
def set_robot_start(self, x_mm: float, y_mm: float, theta_deg: float | None) -> dict: ...
def load_world_name(self, name: str) -> dict: ...
def upload_world_json(self, data: dict) -> dict: ...
def get_snapshot(self) -> dict: ...
def close(self) -> None: ...
```

### D.4 Rutas de paginas

`pages.py`:

- `GET /`: renderiza `index.html`.
- `GET /help`: renderiza ayuda web.
- `GET /healthz`: devuelve estado simple.

`/healthz`:

```json
{
  "status": "ok",
  "active_sessions": 3,
  "running_simulations": 1
}
```

### D.5 Rutas de simulacion

`api_simulation.py` debe:

- Resolver sesion con helper comun `require_session()`.
- Validar JSON.
- Traducir errores Python a respuestas HTTP estables.
- No exponer tracebacks internos del servidor; solo tracebacks de script de usuario.

Respuestas de error:

```json
{
  "error": {
    "code": "SESSION_NOT_FOUND",
    "message": "La sesion no existe o expiro."
  }
}
```

Codigos:

- `400`: payload invalido.
- `403`: token invalido.
- `404`: sesion no encontrada.
- `409`: estado incompatible.
- `429`: capacidad excedida.
- `500`: error interno no esperado.

### D.6 Rutas de ejemplos

`api_examples.py`:

- Lista solo archivos `.py` bajo `Documentos/Ejemplos`.
- No permite path traversal.
- Debe normalizar nombres y rechazar `..`, rutas absolutas o separadores.

Respuesta de lista:

```json
{
  "examples": [
    {"name": "01_basico_avanzar.py", "size": 881}
  ]
}
```

Respuesta de detalle:

```json
{
  "name": "01_basico_avanzar.py",
  "source": "from pybricks..."
}
```

### D.7 Rutas de mundos

`api_worlds.py`:

- Lista JSON bajo `Documentos/Mundos`.
- Carga mundo en modo solo lectura.
- Al aplicar a una sesion, crea copia funcional en el estado de esa sesion.
- No permite leer archivos fuera de `WORLDS_DIR`.

Validaciones:

- Extension `.json`.
- Tamano maximo de archivo configurable.
- JSON parseable.
- Version soportada o `editor_spec` soportado.

### D.8 Rutas de editor

`api_editor.py`:

- Nunca debe confiar en coordenadas finales del frontend sin validar.
- Toda mutacion debe pasar por `WorldEditorService`.
- Las respuestas deben devolver el mundo actualizado y el reporte de validacion.

Ejemplo respuesta de `place`:

```json
{
  "world": {
    "schema_version": 1,
    "grid_size_px": 32,
    "world_width_cells": 20,
    "world_height_cells": 20,
    "placements": []
  },
  "placement": {
    "id": "wall_0001",
    "asset_key": "wall_64x64_a",
    "x": 64,
    "y": 64,
    "rotation": 0
  },
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  }
}
```

## Anexo E - Especificacion detallada de frontend

### E.1 Layout principal

La aplicacion web debe abrir directamente en la experiencia de trabajo, no en una landing page.

Distribucion recomendada:

```text
┌────────────────────────────────────────────────────────────┐
│ Barra superior: ejecutar, pausar, detener, mundo, ayuda     │
├───────────────┬───────────────────────────────┬────────────┤
│ Editor codigo │ Canvas mundo/simulacion        │ Telemetria │
│ Ejemplos      │ Editor mundo opcional          │ Brick EV3  │
│ Consola       │                               │ Sensores   │
└───────────────┴───────────────────────────────┴────────────┘
```

Estados visuales:

- `created`: controles de ejecucion deshabilitados hasta cargar script o ejemplo.
- `ready`: ejecutar habilitado.
- `running`: ejecutar deshabilitado; pausar y detener habilitados.
- `paused`: reanudar y detener habilitados.
- `stopped`: ejecutar o reset habilitados.
- `error`: consola visible con error.

### E.2 `api.js`

Responsabilidades:

- Centralizar `fetch`.
- Enviar `owner_token` por header o dejar que cookie HttpOnly lo maneje.
- Convertir respuestas no exitosas en errores de UI.
- Crear cliente SSE.

Funciones:

```javascript
createSession()
deleteSession(sessionId)
loadScript(sessionId, source)
startSimulation(sessionId, options)
pauseSimulation(sessionId)
resumeSimulation(sessionId)
stopSimulation(sessionId)
resetSimulation(sessionId)
getSnapshot(sessionId)
openSnapshotStream(sessionId, handlers)
listExamples()
getExample(name)
listWorlds()
loadWorld(sessionId, name)
getEditorAssets()
placeAsset(sessionId, payload)
validateWorld(sessionId)
applyWorldToSimulation(sessionId)
```

### E.3 `canvas_world.js`

Responsabilidades:

- Dibujar el mundo en Canvas 2D.
- Mantener transformaciones mm -> px.
- Dibujar trayectoria sin modificar el snapshot.
- Dibujar robot con rotacion.
- Indicar colision.
- Soportar resize.
- Capturar clic para pose inicial.

Transformacion:

```javascript
const sx = canvas.width / world.width_mm;
const sy = canvas.height / world.height_mm;

function worldToCanvas(xMm, yMm) {
  return { x: xMm * sx, y: yMm * sy };
}
```

Capas de dibujo:

1. Fondo/floor.
2. Zonas de color.
3. Lineas negras.
4. Muros/obstaculos.
5. Beacons.
6. Trayectoria.
7. Robot.
8. Overlays de seleccion/colocacion.

Reglas:

- La trayectoria debe guardarse en mm y recalcularse en cada render.
- No usar escala de fuente dependiente del viewport.
- No permitir que textos/overlays tapen controles criticos.

### E.4 `world_editor.js`

Responsabilidades:

- Mostrar paleta de assets.
- Permitir seleccionar herramienta.
- Colocar assets alineados al grid.
- Mover, rotar, duplicar y eliminar.
- Mostrar propiedades.
- Sincronizar con backend despues de cada mutacion.

Flujo recomendado:

```text
usuario selecciona asset
  -> click en canvas
  -> snap a grid
  -> POST /editor/world/place
  -> backend valida
  -> frontend redibuja mundo devuelto
```

### E.5 `editor.js`

Opciones:

- MVP: `textarea` con fuente monoespaciada.
- Recomendado: CodeMirror.
- Avanzado: Monaco.

Responsabilidades:

- Mantener codigo actual.
- Cargar ejemplos.
- Marcar lineas de error.
- Marcar breakpoints si debug esta activo.
- Enviar codigo antes de ejecutar.

### E.6 `telemetry.js`

Debe mostrar:

- Estado de sesion.
- Tick.
- Tiempo simulado.
- Pose: X, Y, theta.
- Colision.
- Motores A-D.
- Sensores conectados.
- Ultimo error resumido.

Actualizacion:

- Evitar recrear todo el DOM en cada snapshot.
- Actualizar nodos existentes.
- Formatear numeros con precision fija razonable.

### E.7 `brick.js`

Debe representar:

- LED con color actual.
- Pantalla LCD EV3 con lineas del snapshot.
- Speaker mediante Web Audio API.
- Botones como estado visual.

Audio:

```javascript
function playBeep(freq, durationMs, volume) {
  const ctx = new AudioContext();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.frequency.value = freq;
  gain.gain.value = Math.max(0, Math.min(1, volume / 100));
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start();
  osc.stop(ctx.currentTime + durationMs / 1000);
}
```

Regla: evitar repetir el mismo beep en cada render. Debe deduplicarse por tick o por evento.

### E.8 Consola de errores

Debe mostrar:

- Estado.
- Mensaje de error.
- Traceback desplegable.
- Ultimas lineas debug si existen.
- Boton limpiar.

## Anexo F - Seguridad, concurrencia y aislamiento

### F.1 Riesgos

| Riesgo | Impacto | Mitigacion |
|---|---|---|
| `exec()` de codigo de usuario | Ejecucion peligrosa | Sandbox, limites y aislamiento futuro. |
| Regresion en aislamiento Pybricks | Cruce de sesiones | `ContextVar`, import hook por sesion y pruebas concurrentes. |
| Uso accidental de `sys.modules` para `pybricks.*` | Modulos Pybricks compartidos | Mantener modulos virtuales fuera de `sys.modules`; cleanup legacy. |
| Demasiadas sesiones | CPU/memoria alta | Limites y cleanup. |
| SSE abiertas | Recursos retenidos | Heartbeat y cierre por timeout. |
| Path traversal | Lectura arbitraria | Normalizar nombres y limitar directorios. |
| Scripts infinitos | Hilos ocupados | `max_runtime_s` y stop cooperativo. |

### F.2 Politica de ejecucion web

Valores recomendados:

```python
ExecutionPolicy(
    max_runtime_s=30,
    allow_math=True,
    allow_time=False,
)
```

Builtins permitidos:

- Tipos basicos.
- Funciones de coleccion y calculo.
- `print`.
- Excepciones comunes.

Bloqueados:

- Sistema operativo.
- Red.
- Subprocesos.
- Hilos.
- Introspeccion peligrosa.
- Importacion arbitraria.

### F.3 Aislamiento multi-sesion

Debe cumplirse:

- No compartir `SimulationService`.
- No compartir `SimulationEngine`.
- No compartir `RuntimeController`.
- No compartir `RuntimeSandbox`.
- No compartir mundo mutable.
- No compartir `PybricksContext`.
- No compartir cola de comandos.

Estrategia actual por etapas:

1. `PybricksContext` usa `ContextVar`.
2. `PybricksFactory` no registra `pybricks.*` en `sys.modules`.
3. Existen pruebas de independencia de sesiones y de no registro en `sys.modules`.
4. Para uso publico, mover runtime a subprocess sigue como endurecimiento futuro.

### F.4 Limites de capacidad

Parametros:

- `MAX_ACTIVE_SESSIONS`
- `MAX_RUNNING_SIMULATIONS`
- `SESSION_IDLE_TIMEOUT_MIN`
- `SCRIPT_MAX_RUNTIME_S`
- `MAX_SCRIPT_SIZE_BYTES`
- `MAX_WORLD_JSON_SIZE_BYTES`
- `MAX_SSE_CLIENTS`

Comportamiento:

- Si se supera `MAX_ACTIVE_SESSIONS`: `429`.
- Si se supera `MAX_RUNNING_SIMULATIONS`: permitir crear sesion pero rechazar `start`.
- Si expira una sesion: detener runtime, limpiar callbacks, eliminar del manager.

## Anexo G - Estrategia de pruebas ampliada

### G.1 Unitarias

- `SessionManager.create_session`.
- `SessionManager.get_session` con token valido/invalido.
- `SessionManager.cleanup_expired`.
- `SimulationSession.load_script`.
- `SimulationSession.start/stop`.
- Serializacion de `SnapshotDTO`.
- DTO de mundo web.
- Validacion de path seguro para ejemplos/mundos.

### G.2 Integracion backend

- Crear sesion, cargar script, iniciar, recibir snapshot.
- Cargar mundo preset y verificar dimensiones.
- Subir mundo JSON y validar.
- Aplicar mundo a simulacion.
- Ejecutar script con `DriveBase`.
- Ejecutar script con sensores.
- Ejecutar script con EV3 Brick.
- Error de runtime se devuelve por snapshot/status.

### G.3 Concurrencia

- Dos sesiones ejecutan scripts diferentes.
- Sesion A se detiene; B sigue.
- Sesion A carga mundo; B conserva mundo original.
- Dos SSE conectadas reciben eventos de sesiones correctas.
- Cleanup no cierra sesion activa.

### G.4 Frontend E2E

Con Playwright:

1. Abrir `/`.
2. Crear sesion automaticamente.
3. Cargar ejemplo.
4. Ejecutar.
5. Confirmar canvas con robot.
6. Confirmar cambio de telemetria.
7. Detener.
8. Abrir segunda pestana.
9. Ejecutar otro ejemplo.
10. Confirmar independencia.

### G.5 Pruebas de mundos

- Crear mundo vacio.
- Colocar robot.
- Intentar colocar segundo robot.
- Colocar muro fuera de limites.
- Colocar linea con extremo abierto.
- Exportar JSON.
- Importar JSON exportado.
- Aplicar a simulacion.

### G.6 Smoke tests equivalentes a escritorio

- Seguidor de linea.
- Ultrasonido + obstaculos.
- Test pantalla/altavoz.
- Motores individuales.
- Laberinto.

## Anexo H - Checklist de implementacion

### H.1 Antes de codificar

- Confirmar version Python.
- Confirmar dependencias Flask/pytest.
- Confirmar rutas de `Documentos/Ejemplos` y `Documentos/Mundos`.
- Confirmar aislamiento Pybricks con `ContextVar` y sin registro compartido en `sys.modules`.

### H.2 Backend

- Crear paquete `simulador_ev3/web`.
- Crear app factory.
- Crear config.
- Crear manager de sesiones.
- Crear wrapper `SimulationSession`.
- Crear blueprints.
- Crear serializador de mundo.
- Crear errores HTTP consistentes.
- Crear cleanup periodico.

### H.3 Frontend

- Crear templates.
- Crear CSS base.
- Crear cliente API.
- Crear editor de codigo.
- Crear canvas.
- Crear panel telemetria.
- Crear panel EV3.
- Crear editor de mundos.
- Crear ayuda.

### H.4 Verificacion

- Unit tests backend.
- Integration tests Flask.
- E2E Playwright (`tests/e2e/test_web_playwright.py`), incluyendo dos perfiles de navegador.
- Prueba manual con dos navegadores para evidencia de release.
- Prueba de export/import de mundo.
- Prueba de error de script.

### H.5 Definicion de terminado

La migracion MVP se considera terminada cuando:

- Cumple criterios de aceptacion de la seccion 14.
- Pasa plan de pruebas minimo.
- La documentacion `/help` esta disponible.
- No hay cruce de estado entre sesiones.
- Los scripts y mundos existentes siguen siendo utiles.
