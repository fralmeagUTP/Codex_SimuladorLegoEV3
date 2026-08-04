# Resultados manuales parciales — QA Web

Fecha: 2026-08-03
URL: `http://127.0.0.1:5050/`
Modalidad: navegador gráfico visible controlado durante la campaña.

> Este registro es incremental. Un resultado **PASS** solo se anota cuando el
> flujo fue accionado y observado en la interfaz Web real.

| Caso | Acción ejercitada | Resultado observado | Estado |
|---|---|---|---|
| WEB-MAN-001 | Carga inicial de la aplicación | Se muestran los diez menús, canvas, editor, LCD, telemetría y barra de estado; sesión `ready`. | PASS |
| WEB-MAN-002 | Menú **Fidelidad** → **Calibrado** | El comando se ejecuta; la interfaz confirma `Perfil de simulacion aplicado: calibrated.` y permanece interactiva. | PASS |
| WEB-MAN-003 | Menú **Tiempo máximo** → **120 s** | El comando se ejecuta; la interfaz confirma `Tiempo maximo configurado: 120 s.` y permanece interactiva. | PASS |
| WEB-MAN-004 | Menú **Trazas** → **Iniciar registro** | El comando se ejecuta; la interfaz confirma `Registro de traza iniciado.` y la sesión continúa en `ready`. | PASS |
| WEB-MAN-005 | Menú **Tema** → **Oscuro** → **Claro** | Se accionaron ambos modos. Al reabrir el menú, el modo activo se expone como botón `pressed` (`Oscuro` y después `Claro`); la interfaz permaneció operable. | PASS |
| WEB-MAN-006 | Menú **Tiempo máximo** → 30 s, 60 s, 120 s, 300 s y **Sin límite** | Cada opción produjo su confirmación visible (`Tiempo maximo configurado: …`) y mantuvo la sesión en `ready`. Se restauró 120 s al finalizar el caso. | PASS |
| WEB-MAN-007 | Menú **Fidelidad** → Ideal, Realista y Calibrado | Los perfiles produjeron los mensajes visibles `ideal`, `realistic` y `calibrated`; la interfaz siguió interactiva. Se restauró Calibrado. | PASS |
| WEB-MAN-008 | Menú **Trazas** → Iniciar, avanzar un tick y detener | Se observaron las confirmaciones `Registro de traza iniciado.`, `Se avanzo un tick de simulacion.` y `Registro de traza detenido.`; la sesión siguió en `ready`. | PASS |
| WEB-MAN-009 | Menú **Trazas** → Exportar JSON / Exportar CSV | No ejercitado: ambos comandos descargan archivos y requieren confirmación explícita antes de iniciar la descarga. | BLOCKED |
| WEB-MAN-010 | Menú **Ayuda** → **Acerca de** | Se abrió el diálogo con el texto de producto y se cerró correctamente mediante el botón visible `Cerrar`. | PASS |
| WEB-MAN-011 | Cerrar **Acerca de** con Escape | No concluyente: el adaptador de navegador no pudo enviar la tecla al diálogo por pérdida de foco del objetivo. No se clasifica como defecto del producto sin una repetición manual directa. | BLOCKED |
| WEB-MAN-012 | Ejemplos → `01_intro_led.py` → Ejecutar | El selector actualizó `Programa actual: 01_intro_led.py` y la ejecución terminó en `finished`. | PASS |
| WEB-MAN-013 | Ejemplos → `05_drivebase_cuadrado.py` → Ejecutar | El programa usó `DriveBase`, transitó por `running` y finalizó en `finished`. | PASS |
| WEB-MAN-014 | Mundos → Mundos preestablecidos → `12_radar_ultrasonido_360.json` | El submenú mostró los doce mundos y el entorno confirmó `Mundo actual: 12_radar_ultrasonido_360.json`. | PASS |
| WEB-MAN-015 | Escenarios → `Radar 360 ultrasonido` | Cargó de forma conjunta el mundo `12_radar_ultrasonido_360.json` y el programa `23_radar_ultrasonido_5grados.py`. | PASS |
| WEB-MAN-016 | Misiones → `Evita obstáculos` | La interfaz confirmó `Misión cargada: Evita obstáculos`, con mundo `05_obstaculos_baliza_ir.json` y programa `15_esquiva_obstaculos.py`. | PASS |
| WEB-MAN-017 | Ejecutar misión → comprobar menús → Detener y reiniciar | En `running`, Archivo, Ejemplos y Mundos quedaron deshabilitados, mientras Pausar y Detener siguieron disponibles. Tras reiniciar, los menús volvieron a habilitarse. | PASS |
| WEB-MAN-018 | Depurar misión `Evita obstáculos` | El modo inició una ejecución real (`debug running`); Archivo y el campo de breakpoints quedaron bloqueados mientras el estado fue `running`. La detención manual respondió. | PASS |
| WEB-MAN-019 | Breakpoint escrito `30` durante depuración | No se observó pausa ni habilitación de Paso/Continuar antes de detener la ejecución. Debe repetirse con un breakpoint confirmado mediante la selección de línea del editor. | BLOCKED |
| WEB-MAN-020 | Recuperación posterior a detener una depuración | El primer reinicio dejó la interfaz en `resetting` y después `running.. t=29.00s`, con Archivo y Ejecutar deshabilitados y mensaje `HTTP 500 [worker=pid-21920, pid=21920]`. Un segundo reinicio restauró los controles y el estado `created`, pero el mensaje HTTP permaneció visible. | FAIL |
| WEB-MAN-021 | Editor de mundos → preajuste **Aula** | Cambió las dimensiones a 80 × 60 celdas y la equivalencia a 800 × 600 cm; el editor mostró `Mundo valido.` | PASS |
| WEB-MAN-022 | Editor de mundos → seleccionar **Muro A** | La biblioteca confirmó `Muro A seleccionado. Haz clic en el mapa para colocarlo.` | PASS |
| WEB-MAN-023 | Editor de mundos → ancho 0 → Aplicar tamaño | Se mostró `Dimensiones de mundo invalidas.`, pero el indicador persistente quedó en `Validacion: OK`. | FAIL |
| WEB-MAN-024 | Editor de mundos → Nuevo | Restablece un mundo sin nombre conservando la cuadrícula del preajuste Aula (80 × 60) y con validación inicial correcta. | PASS |
| WEB-MAN-025 | Editor de mundos → Abrir / Guardar / Guardar como | BLOCKED: Abrir requiere selector de archivo del sistema, que necesita confirmación explícita para elegir archivos. Guardar y Guardar como no expusieron un formulario o diálogo accesible durante esta sesión; debe repetirse con verificación del diálogo nativo. | BLOCKED |
| WEB-MAN-026 | Simulador → Haces ON/OFF | El botón cambió de `Haces ON` a `Haces OFF` y volvió a `Haces ON`, manteniendo la sesión `ready`. | PASS |
| WEB-MAN-027 | Simulador → Ubicar robot con theta 90° | El control entró en modo activo y mostró `Haz clic en el canvas para fijar la pose.` con theta 90°. La colocación final queda bloqueada porque el canvas no expone un objetivo accesible para clicar sin coordenadas no verificadas. | BLOCKED |
| WEB-MAN-028 | Editor → script `def :` → Ejecutar | La interfaz mostró `invalid syntax (<script>, line 1)`, traceback y estado terminal `error`, conservando el botón Ejecutar disponible. | PASS |
| WEB-MAN-029 | Editor → script mínimo válido con LCD → Ejecutar | El programa terminó en `finished` y el editor conservó el código ejecutado. No se observó la notificación de éxito dentro de los 0,7 s posteriores al snapshot terminal. | FAIL |
| WEB-MAN-030 | Recuperación tras script válido finalizado | Tras haber observado `finished`, la interfaz derivó a resumen `error`, barra `running.. t=0.02s`, menús bloqueados y `Timeout HTTP (1200 ms)`. Tras 1,6 s no se recuperó; Detener y reiniciar devolvió los controles a `created`, pero conservó el mensaje de timeout. | FAIL |
| WEB-MAN-031 | Recarga real después del estado inconsistente | La carga de `http://127.0.0.1:5050/` restableció una sesión limpia: mundo Básico, script predeterminado, telemetría y barra en `ready`, y menús habilitados. | PASS |
| WEB-MAN-032 | Bucle `while True: pass` → Detener y reiniciar | El primer reinicio no canceló la ejecución: siguió `running... t=5.28s`, con menús bloqueados y `HTTP 500`. Un segundo reinicio devolvió los controles a `created`, dejando el error visible. | FAIL |
| WEB-MAN-033 | Escenarios → `Seguidor de linea` | Cargó `11_siguelineas_basico.py` y mostró `Escenario cargado: Seguidor de linea`. | PASS |
| WEB-MAN-034 | Escenarios → `Test pantalla/altavoz` | Cargó `02_intro_pantalla_altavoz.py` y mostró `Escenario cargado: Test pantalla/altavoz`. | PASS |
| WEB-MAN-035 | Misiones → `Sigue líneas básico` | Cargó `11_siguelineas_basico.py` y mostró `Misión cargada: Sigue líneas básico`. | PASS |
| WEB-MAN-036 | Misiones → `Radar ultrasónico` | Cargó `23_radar_ultrasonido_5grados.py` y mostró `Misión cargada: Radar ultrasónico`. | PASS |
| WEB-MAN-037 | Ejemplos → `02_intro_pantalla_altavoz.py` | El nombre de programa se actualizó, pero el contenido se identificó internamente como `Ejemplo 12 - Prueba de pantalla y altavoz.` | FAIL |
| WEB-MAN-038 | Ejemplos → `03_movimiento_basico.py` | El nombre de programa se actualizó, pero el contenido se identificó internamente como `Ejemplo 01 - Movimiento basico con dos motores.` | FAIL |
| WEB-MAN-039 | Ejemplos → `04_movimiento_motores_individuales.py` | El nombre de programa se actualizó, pero el contenido se identificó internamente como `Ejemplo 08 - Motores individuales.` | FAIL |
| WEB-MAN-040 | Archivo → Nuevo script | Restableció el programa predeterminado, estado `ready` y mostró `Nuevo script creado.` | PASS |
| WEB-MAN-041 | Archivo → Abrir script / Guardar script | BLOCKED: Abrir requiere seleccionar un archivo local y Guardar inicia una descarga; ambas acciones requieren confirmación explícita en el momento de elegir/descargar el archivo. | BLOCKED |
| WEB-MAN-042 | Mundos preestablecidos → `01_linea_negra_basica.json` | FAIL: tras accionarlo, el entorno permaneció en `Mundo actual: Basico` y se mostró `HTTP 500 [worker=pid-21920, pid=21920]`. | FAIL |
| WEB-MAN-043 | Carga limpia → Mundos → Mundo en blanco | Tras la carga limpia, el comando directo actualizó el entorno a `Mundo actual: Mundo en blanco`, mostró `Mundo en blanco cargado.` y mantuvo estado `ready`. | PASS |
| WEB-MAN-044 | Acceso a submenú Mundos preestablecidos con teclado | BLOCKED: el submenú depende de interacción de puntero; ArrowRight dejó el control activo pero no expuso los elementos. El adaptador de navegador disponible no ofrece hover persistente verificable. | BLOCKED |
| WEB-MAN-045 | Enlace contextual `? Ejecución` | FAIL: el enlace recibió foco/clic, pero la vista y la URL permanecieron en el simulador en vez de navegar a `/help#guide-run-simulation`. | FAIL |
| WEB-MAN-046 | Tema oscuro → recarga → comprobar persistencia | Tras seleccionar Oscuro y recargar, el menú expuso `Oscuro` como botón `pressed`. Se restauró Claro al finalizar. | PASS |
| WEB-MAN-047 | Accesibilidad de Archivo con Enter/Escape | Enter abrió el menú Archivo y Escape lo cerró; ambos cambios fueron visibles mediante el estado `expanded` del botón. | PASS |
| WEB-MAN-048 | Navegación por Tab | BLOCKED: el envío de Tab no produjo un foco visible diferente en el adaptador actual; no se puede certificar el orden de tabulación sin una sesión que exponga el foco real. | BLOCKED |
| WEB-MAN-049 | Estabilidad tras recarga | FAIL: tras la recarga, la sesión derivó a `expired` y dejó Ejecutar deshabilitado sin una acción del usuario. | FAIL |
| WEB-MAN-050 | Editor de mundos → enlace principal Ayuda | FAIL: el enlace se activó visualmente, pero no cargó `/help`; el Editor de mundos permaneció visible. | FAIL |
| WEB-MAN-051 | Editor de mundos → preajuste Pequeño | Ajustó el mundo a 40 × 30 celdas (400 × 300 cm) y conservó validación correcta. | PASS |
| WEB-MAN-052 | Editor de mundos → preajuste Grande | Ajustó el mundo a 160 × 120 celdas (1600 × 1200 cm) y conservó validación correcta. | PASS |
| WEB-MAN-053 | Biblioteca → buscar `muro` | La biblioteca quedó filtrada a Muro A, Muro B y Muro C. | PASS |
| WEB-MAN-054 | Biblioteca → limpiar búsqueda | INCONCLUSO: tras solicitar limpiar el campo, el valor visible continuó como `muro`. Debe repetirse con teclado físico para separar un problema de control de formulario de una limitación del adaptador. | BLOCKED |
| WEB-MAN-055 | Editor de mundos → herramienta Seleccionar | El botón cambió a estado activo y el inspector mantuvo la indicación de seleccionar un elemento del lienzo. | PASS |
| WEB-MAN-056 | Editor de mundos → Tema oscuro | El menú reflejó Oscuro como `pressed`; se restauró Claro al finalizar. | PASS |
| WEB-MAN-057 | Depuración → activar línea 5 → Depurar | FAIL: al seleccionar la línea 5 y ejecutar Depurar, la ejecución terminó directamente en `finished`; no se observó pausa ni habilitación de Continuar. | FAIL |
| WEB-MAN-058 | Depuración → Paso después de finalización | FAIL: Paso inició una nueva ejecución continua (`debug running`) en lugar de una transición de un paso; el primer reinicio quedó en `running` con HTTP 500 y solo el segundo volvió a `created`. | FAIL |
| WEB-MAN-059 | Sesiones simultáneas de usuarios | BLOCKED: el navegador gráfico disponible no expone creación de una segunda pestaña/sesión controlable, por lo que no se puede certificar aislamiento multiusuario mediante interacción visible. |

## Observaciones que requieren contraste de expectativa

- Tras cargar `12_radar_ultrasonido_360.json` desde una ejecución ya terminada, la barra de estado siguió mostrando `finished`. Debe comprobarse si el cambio de mundo debe restablecer explícitamente la sesión a `ready`.

## Hallazgos conocidos revalidados previamente

| ID | Flujo | Estado | Evidencia resumida |
|---|---|---|---|
| WEB-M-001 | Pausar una ejecución no terminante | FAIL | La barra global cambia a `paused`, pero tras un segundo la telemetría continúa indicando `running`; al reanudar se sincroniza. |
| WEB-M-002 | Mapeo del catálogo de ejemplos | ALTA | Los nombres seleccionados no corresponden al contenido servido: `01_intro_led.py`→Ejemplo 11, `02_intro_pantalla_altavoz.py`→Ejemplo 12, `03_movimiento_basico.py`→Ejemplo 01, `04_movimiento_motores_individuales.py`→Ejemplo 08 y `05_drivebase_cuadrado.py`→Ejemplo 02. Debe verificarse el mapeo del catálogo o los archivos servidos antes de liberar. |
| WEB-M-003 | Reinicio de depuración / recuperación de worker | FAIL | Tras detener una sesión de depuración, el primer reinicio quedó atascado (`resetting` y luego `running.. t=29.00s`) con `HTTP 500 [worker=pid-21920, pid=21920]` y controles principales bloqueados. Un segundo reinicio recuperó a `created`, pero conservó el error visible. Reproducción: cargar `Evita obstáculos`, escribir `30` como breakpoint, pulsar Depurar y después Detener y reiniciar. |
| WEB-M-004 | Estado visual de validación en el editor de mundos | FAIL | Al ingresar ancho 0 y aplicar tamaño, se informa `Dimensiones de mundo invalidas.`, pero el indicador de pie continúa como `Validacion: OK`. La UI presenta simultáneamente éxito y error. |
| WEB-M-005 | Notificación de finalización exitosa Web | FAIL | Un script mínimo válido alcanzó `finished`, pero no apareció el aviso no modal `El programa se ejecutó correctamente.` en la interfaz durante la ventana de observación posterior al snapshot final. |
| WEB-M-006 | Desincronización y timeout después de finalización Web | CRÍTICO | Un script mínimo llegó a `finished`, pero posteriormente la misma sesión mostró resumen `error`, barra `running.. t=0.02s`, controles bloqueados y `Timeout HTTP (1200 ms)`. El reset recupera los controles pero no limpia el error. Este comportamiento revalida el riesgo de snapshots terminales/eventos tardíos desincronizados. |
| WEB-M-007 | Cancelación de bucle no cooperativo | CRÍTICO | Con `while True: pass`, el primer clic en Detener y reiniciar no cancela el worker: la UI sigue en `running`, bloquea menús y presenta `HTTP 500`. Solo un segundo reinicio devuelve controles, sin limpiar el error. Contradice el requisito de poder detener manualmente programas no terminantes. |
| WEB-M-008 | Carga de mundo preestablecido tras recuperación | ALTA | Al cargar `01_linea_negra_basica.json`, el entorno permaneció en Básico y mostró HTTP 500. La carga de mundos no es confiable en la misma sesión después de errores/reinicios del worker. |
| WEB-M-009 | Navegación de ayuda Web | MEDIA | Tanto el enlace contextual `? Ejecución` como el enlace principal Ayuda del Editor de mundos se activan, pero no navegan a sus rutas `/help…` anunciadas; la vista actual permanece visible. |
| WEB-M-010 | Sesión expirada tras carga Web | ALTA | Tras recargar en estado aparentemente limpio, la sesión puede pasar a `expired` y deshabilitar Ejecutar sin intervención. Impide continuar con pruebas de ejecución y degrada la recuperación de usuario. |
| WEB-M-011 | Breakpoints del depurador Web | ALTA | Un breakpoint seleccionado desde la línea 5 del editor no detiene la ejecución: Depurar finaliza directamente en `finished`, sin estado de pausa ni Continuar habilitado. |
| WEB-M-012 | Semántica de Paso y recuperación de depuración | CRÍTICA | Tras finalizar una depuración, Paso inicia una nueva ejecución continua en vez de realizar un paso controlado. El primer reinicio falla con HTTP 500 y mantiene `running`; solo un segundo recupera parcialmente a `created`. |

Los demás flujos continúan en ejecución; no deben interpretarse como aprobados hasta su registro explícito en este documento y en el informe final.

## Verificación automatizada complementaria

| Fecha | Comando | Resultado | Observación |
|---|---|---|---|
| 2026-08-04 | `.\\.venv\\Scripts\\python.exe -m pytest tests\\web` | PASS: 132 aprobadas en 12.39 s | La suite Web pasa, pero no reproduce los defectos manuales de worker, expiración, cancelación, navegación de ayuda ni depuración registrados arriba. |
| 2026-08-04 | `.\\.venv\\Scripts\\python.exe -m pytest --cov=simulador_ev3 --cov-report=term-missing` | BLOCKED: timeout a 64.04 s | No produjo un resultado final ni una cobertura válida; no se informa cobertura como medida real. |
| 2026-08-04 | `.\\.venv\\Scripts\\python.exe -m ruff check simulador_ev3 tests` | PASS | Sin incidencias de lint. |
| 2026-08-04 | `.\\.venv\\Scripts\\python.exe -m mypy simulador_ev3` | FAIL: 2 errores | `ui/main_window.py:1977` y `:2062`: no se puede inferir el tipo de lambda. |
| 2026-08-04 | `.\\.venv\\Scripts\\python.exe -m bandit -r simulador_ev3 -q` | FAIL: 56 hallazgos | 54 bajos por `try/except` que silencian errores; 2 medios: `exec` del intérprete y `eval` de watches. |
| 2026-08-04 | `.\\.venv\\Scripts\\python.exe -m pip_audit -r requirements.txt` | PASS | No se encontraron vulnerabilidades conocidas en dependencias declaradas. |
| 2026-08-04 | `.\\.venv\\Scripts\\python.exe -m pytest tests\\web --cov=simulador_ev3 --cov-report=term` | FAIL de umbral | Las 132 pruebas aprobaron, pero la cobertura global real fue 38.1%, inferior al mínimo configurado de 70%; también se advirtió que no se pudo importar el trazador C de coverage. |
| 2026-08-04 | `.\\.venv\\Scripts\\python.exe -m pip wheel . --no-deps --wheel-dir artifacts\\qa-wheel` | PASS | Se generó `artifacts/qa-wheel/simulador_ev3-1.5.0-py3-none-any.whl` (246468 bytes). |
| 2026-08-04 | `docker build -t simulador-ev3-qa:local .` | PASS | La imagen de producción se construyó correctamente. |
| 2026-08-04 | Contenedor Docker sin variables de producción | PASS de validación | Finaliza con error explícito: exige `EV3_WEB_SECRET_KEY` robusta y cookie Secure para HTTPS. |
| 2026-08-04 | Contenedor Docker con configuración sintética válida → `/healthz` | PASS | `HTTP 200`, estado `ok`, versión 1.5.0 y worker activo. El contenedor temporal se detuvo tras la prueba. |
| 2026-08-04 | `.\\.venv\\Scripts\\python.exe -m pytest tests\\load\\test_web_session_load.py` | PASS | 3 pruebas aprobadas: creación paralela de sesiones, métricas de workers y carga paralela sostenida. |
| 2026-08-04 | `.\\.venv\\Scripts\\python.exe -m pytest tests\\e2e\\test_web_playwright.py` | PASS | 51 pruebas E2E aprobadas en 53.81 s, incluyendo móvil, ayuda, depuración y dos contextos de navegador independientes. |

> La aprobación E2E se ejecutó en un entorno de prueba aislado. No invalida los
> defectos manuales observados contra el servidor local vivo; evidencia una
> divergencia de entorno, de estado residual o de cobertura de la campaña E2E
> que debe investigarse antes de liberar.

## Diagnóstico de divergencia de entorno

El servidor manual que atendió `127.0.0.1:5050` durante la campaña corresponde
al proceso `pid 21920`, iniciado el 2026-08-03 con:

```text
C:\ProgramData\miniforge3\python.exe -m simulador_ev3.web.waitress_server
```

Las pruebas E2E y de unidad se ejecutaron con `.venv\Scripts\python.exe`.
Por tanto, la campaña manual y la automatizada **no se ejecutaron con el mismo
intérprete/entorno Python**, una causa probable de la discrepancia observada.
Este hallazgo no descarta los defectos manuales; exige reiniciar y repetir la
campaña contra el servidor oficial del entorno virtual antes de liberar.

## Repetición dirigida en instancia oficial `.venv`

Fecha: 2026-08-04
URL: `http://127.0.0.1:5052/`
Servidor: `start_local.ps1 -Port 5052 -Background`, worker `pid-8008`.
Salud: `GET /healthz` respondió `HTTP 200`, versión `1.5.0`.

| ID | Flujo ejercitado visualmente | Resultado observado | Estado |
|---|---|---|---|
| WEB-RET-001 | Carga inicial | Se creó una sesión nueva en estado `ready`; Ejecutar estaba disponible y la telemetría, Brick, canvas y editor presentaron el mismo mundo Básico. | PASS |
| WEB-RET-002 | Ejecutar script Pybricks válido predefinido | Tras esperar su terminación, el resumen, barra de estado, telemetría y Brick mostraron `finished`; Motor A quedó en 194.40°, la posición final fue X=24.2 cm, Y=18.2 cm, theta=-47.75°. Apareció una sola notificación accesible: `El programa se ejecutó correctamente.` | PASS |
| WEB-RET-003 | Detener y reiniciar después de finalización | El primer clic restauró X=20 cm, Y=20 cm, theta=0°, motores a 0°, LCD apagada, tiempo 0.02 s y tick 1, sin error HTTP visible. `Ejecutar` quedó habilitado. El botón de reinicio siguió deshabilitado en estado `created`, comportamiento coherente al no haber ejecución activa. | PASS |
| WEB-RET-004 | Enlace contextual `? Ejecución` | BLOCKED: el enlace usa `target="_blank"`; la pestaña original conservó su URL como es esperado y el adaptador no expuso la nueva pestaña para validarla. No hay evidencia suficiente para afirmar un fallo de navegación. | BLOCKED |
| WEB-RET-005 | Ejecutar `while True: pass` y pulsar Detener y reiniciar una vez | El script pasó a `running`; tras el primer reinicio, permaneció en `resetting`/`running`, con menús y Ejecutar bloqueados y el mensaje `HTTP 500 [worker=pid-8008, pid=8008]`. | FAIL |
| WEB-RET-006 | Breakpoint visual en línea 5 y Depurar | El selector añadió `5` al campo Breakpoints. Al pulsar Depurar, el programa terminó en `finished` (0.56 s) sin estado de pausa ni botón Continuar habilitado. | FAIL |
| WEB-RET-007 | Pausar `wait(20000)` | Pausar habilitó Reanudar y la barra final mostró `paused`, pero el resumen de telemetría siguió en `running` con tiempo/tick avanzados (13.44 s / 672). También se mostró `HTTP 500 [worker=pid-8008, pid=8008]`. | FAIL |
| WEB-RET-008 | Reanudar después de WEB-RET-007 | Reanudar restauró controles de ejecución y telemetría a `running` (14.26 s / 713), pero conservó `HTTP 500 [worker=pid-8008, pid=8008]`. La recuperación es parcial y deja un error obsoleto visible. | FAIL |
| WEB-RET-009 | Detener y reiniciar después de la pausa fallida | Restauró datos a `created`, tick 1, tiempo 0.02 s y pose inicial, pero dejó visible `HTTP 500 [worker=pid-8008, pid=8008]`. | FAIL |

La repetición demuestra que WEB-M-005 y WEB-M-006 **no son reproducibles en
esta instancia limpia del entorno oficial**. Se conservan como fallos de la
campaña previa contra `pid-21920` hasta repetir sus variantes de depuración,
bucle no cooperativo, ayuda y carga de mundo en la instancia oficial. No se
deben cerrar los defectos WEB-M-003, WEB-M-007 a WEB-M-012 solamente con esta
evidencia parcial. WEB-M-009 y WEB-M-007 sí se reproducen en la instancia
oficial mediante WEB-RET-005, por lo que deben mantenerse como
defectos confirmados de producto. WEB-M-009 se reclasifica como BLOCKED por
la apertura en una nueva pestaña. WEB-M-011 también se reproduce mediante
WEB-RET-006 y permanece confirmado. WEB-M-001 se reproduce mediante
WEB-RET-007 y permanece confirmado.

## Correlación técnica de los HTTP 500 observados

Los registros de la instancia oficial `.venv` (`C:\tmp\ev3_web_err.log`) vinculan
directamente los fallos manuales con excepciones del backend:

- `POST /api/sessions/<id>/pause` termina en `TimeoutError: El worker sombra no confirmó pause`.
- `POST /api/sessions/<id>/reset` termina en `TimeoutError: El worker sombra no confirmó reset`.

La espera está implementada en
`simulador_ev3/web/services/simulation_session.py:870-896`: envía el comando y
espera hasta 20 recepciones de 0.2 s. Si no llega la confirmación, eleva la
excepción y Flask responde 500. El worker aislado sí define la emisión de
`paused` y `reset` (`simulador_ev3/runtime/isolated_worker.py:393-418`), por lo
que el defecto se concentra en la disponibilidad/orden de consumo de comandos
durante una ejecución activa, la política de espera y la recuperación que debe
seguir al timeout.

### Brecha confirmada de pruebas automáticas

Las pruebas existentes de pausa/reinicio usan bucles cooperativos, por ejemplo
`while True: wait(100)` en `tests/web/test_web_app.py` y
`tests/e2e/test_web_playwright.py`. No hay una prueba que ejecute el caso
manual reproducible `while True: pass`, ni una que exija que `pause` y `reset`
no devuelvan 500 al agotarse la confirmación del worker sombra. Por eso la
suite automática aprobada no detectó WEB-RET-005, WEB-RET-007, WEB-RET-008 ni
WEB-RET-009.

Comando de contraste ejecutado el 2026-08-04:

```text
.\.venv\Scripts\python.exe -m pytest tests\web\test_web_app.py -k
"pause_does_not_consume_runtime_timeout_budget or reset_snapshot_is_a_complete_created_state" -q
```

Resultado: `2 passed, 85 deselected in 1.96s`. Este resultado confirma la
brecha: las pruebas cooperativas existentes pasan, pero no representan la
cancelación/pausa no cooperativa ejercitada manualmente.

## Revisión móvil dirigida

| ID | Flujo ejercitado visualmente | Resultado observado | Estado |
|---|---|---|---|
| WEB-RET-010 | Recarga limpia a 390×844 y control Haces ON | Tras 1.2 s la sesión se estabilizó en `ready`, tick 1 y telemetría coherente. El botón Haces ON fue visible y su borde derecho quedó en x=261 px dentro de un viewport de 390 px. | PASS parcial |

La medición geométrica completa del lienzo y la revisión de los demás tamaños
de viewport continúan pendientes; WEB-RET-010 no sustituye esa validación.

## Limitación de mutación

El 2026-08-04 se verificó la disponibilidad de `mutmut`: no está instalado ni
expuesto como comando en el entorno virtual. Por tanto, no se ejecutó análisis
de mutación y no se informa un resultado inexistente. La fase 5.1 conserva
como evidencia válida Ruff, Mypy, Bandit, Pip-Audit, cobertura y las suites
ejecutadas; mutación queda pendiente de una decisión explícita sobre la
dependencia y un presupuesto de ejecución.

## Rectificación de navegación de Ayuda

La inspección de las plantillas confirma que Centro de ayuda y los enlaces
contextuales relevantes se sirven con `target="_blank"`. Por ello, que la
pestaña original no cambiase de URL no era evidencia de error. La ruta
`GET http://127.0.0.1:5052/help` respondió `HTTP 200` y contiene el Centro de
ayuda. La disponibilidad de la nueva pestaña queda pendiente de una sesión de
navegador que la exponga; los casos respectivos se mantienen `BLOCKED`.

## Complemento aislado: ayuda, reinicio y sesiones

Comando ejecutado el 2026-08-04:

```text
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -k
"two_browser_contexts or help or reset_replaces_terminal_snapshot" -q
```

Resultado: `4 passed, 47 deselected in 7.90s`. Cubre, en un servidor E2E
aislado, el Centro de ayuda, la ruta de ayuda, la sustitución del snapshot
terminal tras reinicio y el aislamiento entre dos contextos de navegador. Es
evidencia automatizada complementaria para fases 4 y 6; no convierte en PASS
los casos manuales que el navegador visible no pudo ejercer.

## Complemento de seguridad y contratos

Comando ejecutado el 2026-08-04:

```text
.\.venv\Scripts\python.exe -m pytest tests\web\test_web_app.py -k
"session_token_is_required_for_wrong_token or session_cannot_modify_another_session_with_own_token or active_session_limit_is_enforced or api_session_creation_returns_429_at_capacity_without_eviction or api_session_creation_wait_ms_invalid_payload_returns_400 or editor_rejects_invalid_asset_payloads or debug_breakpoints_reject_invalid_payload" -q
```

Resultado: `7 passed, 80 deselected in 0.80s`. Verifica autenticación por token
de sesión, aislamiento de modificación entre sesiones, límites/429 de capacidad
y validaciones de payload en creación de sesión, editor y breakpoints. Es
evidencia automatizada de las fases 4.5 y 5.5; no utiliza credenciales reales
ni datos de producción.

## Fase 7 — Aviso de finalización exitosa

Comandos ejecutados el 2026-08-04:

```text
.\.venv\Scripts\python.exe -m pytest tests\web\test_web_app.py -k "success_notification" -q
.\.venv\Scripts\python.exe -m pytest tests\ui\test_ui.py -k "success_notification_is_emitted_once_only_for_finished_execution" -q
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -k "success_toast" -q
```

Resultado: 1 prueba Web + 1 prueba Tkinter + 3 pruebas E2E Web aprobadas. La
cobertura verifica el mensaje `El programa se ejecutó correctamente.`, su
deduplicación, la ausencia de aviso en error/detención manual y el ajuste del
toast en móvil para ambos temas. WEB-RET-002 añade evidencia manual Web de que
el toast aparece después del snapshot final. Falta todavía la comprobación
manual visible de Tkinter para cerrar completamente 7.1 y 7.3.

Revisión estructural complementaria: `simulation_app.js:315-318` programa la
notificación únicamente para `finished` e invalida su ciclo para `stopped`,
`timed_out`, `error` y `created`. La comprobación diferida conserva además el
identificador de ejecución y exige que el estado siga siendo `finished`
(`:348-358`), evitando que un evento tardío anterior muestre un aviso.

## Actualización de mutación y escenarios críticos

El 2026-08-04 se instaló `mutmut 3.7.0` en `.venv` y se incorporó su
configuración reproducible en `pyproject.toml`. En Windows, Mutmut rechaza la
ejecución nativa y solicita WSL; por eso se ejecutó en un contenedor Linux
efímero con Python 3.12. La primera réplica aislada no incluía las plantillas
de Flask y falló al recopilar estadísticas con `TemplateNotFound: index.html`.
Tras incorporar las plantillas, recursos estáticos y mundos a `also_copy`, una
campaña limpia de hasta 180 s no terminó antes del límite del comando.

No se informa una puntuación de mutación: no hay un resultado completo y
fiable. Esta limitación no invalida la ejecución de 5.1, que sí completó los
análisis estáticos y los escenarios críticos ya registrados, pero deja la
medición integral de mutación como trabajo pendiente.

Se reejecutó el escenario de regresión cooperativo:

```text
.\.venv\Scripts\python.exe -m pytest tests\web\test_web_app.py -k
"pause_does_not_consume_runtime_timeout_budget or reset_snapshot_is_a_complete_created_state" -q
```

Resultado: `2 passed, 85 deselected`. Este PASS no contradice los defectos
manuales `WEB-RET-005`, `WEB-RET-007`, `WEB-RET-008` y `WEB-RET-009`: aquellos
requieren un bucle no cooperativo que el worker no consigue pausar o reiniciar
sin devolver HTTP 500.

## Accesibilidad y tema: comprobación visible parcial

El 2026-08-04, en la instancia Web real a `1280x720`, se abrió el menú
`Tema`, se seleccionó `Claro` y después `Oscuro`. La página actualizó el
atributo de tema en ambos sentidos y conservó `scrollWidth = innerWidth =
1280`, sin scroll horizontal. La notificación de finalización permaneció como
una única región `role="status" aria-live="polite"`, con un único control de
cierre accesible.

Resultado: **PASS parcial** para cambio de tema, aviso accesible y ausencia de
desbordamiento horizontal en escritorio. Siguen pendientes la navegación real
por teclado y la revisión manual de los cuatro viewports, por lo que 5.2 y 5.3
no se marcan como concluidas.

## Accesibilidad y responsividad: complemento E2E

Comando ejecutado el 2026-08-04:

```text
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -k
"critical_web_text_keeps_wcag_aa_contrast_in_each_theme or
success_toast_fits_mobile_viewport_in_both_themes or
map_canvas_and_tools_stay_inside_viewport or
menu_keyboard_opens_items_and_escape_restores_trigger_focus or
secondary_web_controls_are_operable_with_keyboard" -q
```

Resultado: `18 passed, 33 deselected in 18.97s`. La suite ejercitó navegador
con teclas Tab, Shift+Tab, Enter y Escape; contraste WCAG AA en claro y oscuro;
toast en `390x844`; y canvas junto con herramientas en `1920x1080`, `1280x800`,
`1024x768` y `390x844`. Es evidencia automatizada que completa las tareas 5.2
y 5.3; la comprobación visual manual de todas las pantallas de catálogo sigue
pendiente en la fase 2.

## Renderizado y snapshots: comprobación parcial

Comandos ejecutados el 2026-08-04:

```text
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -k
"ultrasonic_radar_sweep_keeps_canvas_rendering_between_snapshots or
terminal_snapshot_synchronizes_status_telemetry_and_lcd" -q
.\.venv\Scripts\python.exe -m pytest tests\web\test_web_units.py -k
"web_session_throttles_snapshot_events_without_stalling_engine" -q
.\.venv\Scripts\python.exe -m pytest tests\web\test_render_interpolation_controller.py -q
```

Resultado: `2 passed` E2E, `1 passed` de limitación de snapshots y `1 passed`
del controlador de interpolación. Se verificó que el radar mantiene cuadros
renderizados entre snapshots y que LCD, telemetría y estado terminal conservan
el snapshot autoritativo. La medición de FPS, CPU, memoria y carga concurrente
con métricas cuantitativas sigue pendiente; 5.4 continúa abierta.

### Carga HTTP de lectura controlada

El 2026-08-04 se usó Python 3.12 y `ThreadPoolExecutor(max_workers=20)` contra
`GET /healthz`, sin crear sesiones ni modificar datos. Cada lote tuvo 20
solicitudes concurrentes:

| Lote | Estados | Pared (ms) | Media (ms) | Máximo (ms) |
|---|---|---:|---:|---:|
| 1 | 20 × HTTP 200 | 139.15 | 53.16 | 136.69 |
| 2 | 20 × HTTP 200 | 37.20 | 19.12 | 31.93 |
| 3 | 20 × HTTP 200 | 41.14 | 20.92 | 36.89 |

Tras la prueba, `/metrics` informó `requests_total=259`,
`responses_5xx=2` y `average_duration_ms=21.494`. Los dos 5xx son históricos
de los defectos manuales no cooperativos ya documentados; esta carga no produjo
errores. `worker_memory_bytes`, `worker_cpu_seconds` y la cola eran cero al no
haber sesiones activas. Falta una carga con simulaciones simultáneas y
observación de recursos del worker para concluir 5.4.

## Seguridad: batería marcada

Comando ejecutado el 2026-08-04:

```text
.\.venv\Scripts\python.exe -m pytest -m security -q
```

Resultado: `9 passed, 807 deselected in 1.19s`. Complementa los siete
contratos selectivos ya registrados con autorización de token, límites de
sesiones, payloads inválidos y aislamiento de rutas. Junto con Bandit y
Pip-Audit de 5.1, la tarea 5.5 queda ejecutada. El resultado no elimina los
errores funcionales HTTP 500 confirmados para cancelación no cooperativa.

## Recuperación: comprobación parcial

Comandos ejecutados el 2026-08-04:

```text
.\.venv\Scripts\python.exe -m pytest tests\web\test_web_units.py -k
"session_manager_recovers_session_from_metadata_mirror or
session_manager_recovery_fails_with_invalid_owner_token or
session_manager_recovers_script_world_and_debug_state_from_mirror or
redis_primary_degrades_to_memory_when_mirror_write_fails" -q
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -k
"reset_recovers_the_ultrasonic_obstacle_scenario or
reset_recovers_a_session_paused_at_a_debug_breakpoint" -q
```

Resultado: `4 passed` de recuperación/degradación de sesión y `2 passed` E2E
de reinicio desde escenario y depuración. No hay evidencia de una caída real de
worker, corte SSE ni reinicio de servidor. Esos flujos permanecen pendientes y
5.6 continúa abierta; además, los defectos no cooperativos confirmados impiden
considerar la recuperación robusta.

## Navegación y depuración: complemento E2E parcial

Comando ejecutado el 2026-08-04:

```text
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -k
"simulation_menus_load_examples_worlds_and_scenarios or
reset_hides_the_terminal_mission_result or
debug_breakpoint_pause_enables_debug_controls or
loading_new_example_clears_stale_breakpoints" -q
```

Resultado: `4 passed, 47 deselected in 8.26s`. Cubre carga de un ejemplo, un
mundo y un escenario desde menús, ocultación del resultado de misión tras
reinicio, breakpoint/continuar y limpieza de breakpoints al cambiar de ejemplo.
No acredita el recorrido individual de cada ejemplo, mundo, escenario, misión,
diálogo y control en navegador visible; las tareas de fase 2 continúan
pendientes.

## Catálogos ejercitados en navegador real

El 2026-08-04 se interactuó mediante clic con los catálogos de la instancia
Web oficial:

| Catálogo | Casos | Resultado |
|---|---:|---|
| Ejemplos | 23 | PASS: cada elemento cargó código no vacío en el editor. |
| Escenarios | 4 | PASS: cada escenario cargó editor, mundo y confirmación. |
| Misiones | 3 | PASS: cada selección mostró `Misión cargada`. |
| Mundos preestablecidos | 12 | BLOCKED: el submenú depende de hover y el controlador visible disponible sólo expone clic/teclado; al hacer clic el submenú se cierra. |

La primera selección de `Seguidor de linea` coincidió con una reconexión de
sesión y conservó el estado anterior. Se repitió después de cargar el escenario
de ultrasonido: cargó 1.212 caracteres de código, el mundo
`01_linea_negra_basica.json` y el mensaje `Escenario cargado: Seguidor de
linea`. Por tanto, no se registra como defecto confirmado.

Los resultados de carga no equivalen a ejecutar cada ejemplo o misión; esas
ejecuciones siguen pendientes en las tareas 2.3 y 2.4.

## Editor de mundos: validación visible parcial

Se abrió `Mundos` → `Editor de mundos` en navegador real y se creó un mundo
temporal sin guardarlo. El lienzo inició en `40x40` y mostró `Mundo valido.`.
Después se cambió el ancho a `0`, se pulsó `Aplicar tamano` y luego `Validar`.
El campo conservó `0`, no se mostró aviso, texto de estado ni región de alerta.
Finalmente se restauró el ancho a `40`; no se guardó ni eliminó ningún archivo.

### WEB-WE-001 — Validación de tamaño inválido no comunica el error

- Severidad: media.
- Pasos: en Editor de mundos, asignar `World W = 0`; pulsar `Aplicar tamano` y
  `Validar`.
- Esperado: rechazar o corregir el valor y mostrar un mensaje de validación
  visible y accesible.
- Observado: el valor `0` permanece y no aparece ningún mensaje visible ni
  `role="alert"`.
- Impacto: el usuario no puede saber si el tamaño fue aplicado o si el mundo
  queda inválido antes de guardarlo.

La prueba de CRUD completo, importación y persistencia sigue pendiente.

### Complemento automatizado de CRUD

Comandos ejecutados el 2026-08-04:

```text
.\.venv\Scripts\python.exe -m pytest tests\web\test_qa_world_crud.py
tests\web\test_world_deletion_api.py -q
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -k
"world_editor_updates_selected_asset_properties or world_editor_drags_selected_asset
or world_editor" -q
```

Resultado: `3 passed` de CRUD/API con archivos temporales y `4 passed` E2E de
editor visual. Cubren crear, colocar, actualizar, guardar/cargar, borrar,
seleccionar y arrastrar activos. No sustituyen los mensajes visibles ausentes
para el tamaño inválido, registrado como WEB-WE-001.

## Errores del intérprete ejercitados en navegador real

- Error de sintaxis: el script `def invalida(:` terminó en `error`, mostró la
  traza `SyntaxError` y no activó el toast de éxito. PASS.
- Error de ejecución: el script `resultado = 1 / 0` mostró correctamente la
  traza `ZeroDivisionError`, pero dejó el estado visual incoherente. FAIL.

### WEB-RT-011 — Error de ejecución deja la sesión visualmente en ejecución

- Severidad: alta.
- Pasos: reiniciar; escribir `resultado = 1 / 0`; pulsar `Ejecutar`; esperar
  más de 3,8 s.
- Esperado: estado de sesión y telemetría `error`, botón Ejecutar habilitado y
  ausencia de notificación de éxito.
- Observado: consola con `ZeroDivisionError: division by zero`, mientras la
  barra permaneció `running... t=0.02s`, telemetría `running`, Ejecutar quedó
  deshabilitado y Detener y reiniciar habilitado. No se mostró toast de éxito.
- Recuperación: al pulsar `Detener y reiniciar`, estado y telemetría volvieron
  a `created`, Ejecutar quedó habilitado y Detener y reiniciar deshabilitado.

Este defecto confirma que una traza de error no basta para considerar
sincronizados el editor, el estado global y la telemetría.

### WEB-RT-012 — Timeout HTTP deja la sesión bloqueada y el reinicio no la recupera

- Severidad: alta.
- Pasos: con una sesión creada, cargar `from pybricks.tools import wait` seguido
  de `wait(20)`; pulsar Ejecutar y esperar. Después pulsar Detener y reiniciar.
- Esperado: el script corto finaliza con `finished` o, ante un timeout de red,
  la interfaz recupera un estado terminal coherente; el reinicio debe llevar a
  `created`.
- Observado: consola `Timeout HTTP (1200 ms)`, estado global `running`,
  telemetría `created` y Ejecutar deshabilitado. Después de Detener y reiniciar
  persistieron los mismos estados incoherentes y el botón Ejecutar siguió
  deshabilitado.
- Impacto: una sesión Web puede quedar inutilizable sin que el usuario pueda
  recuperarla desde los controles de simulación.
- Mitigación observada: una recarga real de la pestaña restableció `ready` en
  sesión y telemetría, habilitó Ejecutar y limpió la consola. No sustituye la
  recuperación requerida de Detener y reiniciar.

La recarga permite continuar la campaña, pero el hallazgo impide considerar
robusta la recuperación del comando.

### WEB-RT-013 — Recarga durante ejecución conserva Detener y reiniciar habilitado en `ready`

- Severidad: media.
- Pasos: ejecutar `wait(5000)`; recargar la pestaña durante la ejecución;
  esperar más de cinco segundos tras la recarga.
- Esperado: al quedar la nueva página en `ready`, los controles representan ese
  estado: Ejecutar habilitado y Detener y reiniciar deshabilitado.
- Observado: sesión y telemetría mostraron `ready`, Ejecutar quedó habilitado,
  pero Detener y reiniciar permaneció habilitado incluso tras 5,2 s.
- Impacto: el usuario recibe señales contradictorias sobre si existe una
  ejecución activa después de recargar.

La recarga no produjo errores de consola visibles y permitió seguir operando,
pero no dejó una recuperación de controles completamente coherente.

## Sesiones y concurrencia: contratos y E2E

Comandos ejecutados el 2026-08-04:

```text
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -k
"two_browser_contexts" -q
.\.venv\Scripts\python.exe -m pytest tests\web\test_web_app.py -k
"session_creation or session_reuse or session_token or
session_cannot_modify_another_session or active_session_limit or
start_is_idempotent" -q
.\.venv\Scripts\python.exe -m pytest tests\web\test_web_units.py -k
"session_manager_closes or session_manager_expires" -q
```

Resultado: `1 passed` E2E de dos contextos de navegador, `6 passed` de
creación/reutilización/token/límite/idempotencia y `1 passed` de cierre o
expiración. Es evidencia aislada de la independencia entre sesiones; no usa
usuarios, credenciales ni datos externos.

## Eventos tardíos y contratos Web completos

Comandos ejecutados el 2026-08-04:

```text
.\.venv\Scripts\python.exe -m pytest tests\web\test_web_units.py -k
"discards_late_transition or terminal_status_is_preceded" -q
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -k
"reset_replaces_terminal_snapshot_without_late_updates" -q
.\.venv\Scripts\python.exe -m pytest tests\web -q
```

Resultado: `2 passed` de transiciones tardías/orden de snapshot, `1 passed`
E2E de reinicio frente a actualizaciones tardías y `132 passed in 12.64s` para
todo el paquete Web. La tarea 4.5 queda completada. La tarea 4.4 sigue parcial:
no se ha simulado de forma real la pérdida de SSE, fallback a polling ni una
recarga de navegador durante ejecución.

## Regresión E2E Web completa

Comando ejecutado el 2026-08-04:

```text
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -q
```

Resultado: `51 passed in 53.70s`. La suite ejercitó una instancia Web aislada
en navegador para los recorridos cubiertos de simulación, menús, editor,
mundos, misiones, depuración, temas, teclado, responsividad, renderizado y
sesiones. No invalida los defectos manuales WEB-WE-001 y WEB-RT-011, que la
suite aún no representa.

## Controles de simulación: comprobación manual parcial

- `Haces ON/OFF`: PASS. El botón cambió a `Haces OFF` tras el clic y se
  restauró a `Haces ON` al repetirlo.
- Zoom: el botón `+` respondió al clic y se aplicó `[]` para restaurar; el
  lienzo no expone nivel de zoom ni cambió su geometría CSS, por lo que la
  comprobación visual detallada queda parcial.
- Theta/Ubicar robot: Theta aceptó `90`, pero Ubicar robot no mostró un estado
  visible hasta completar la ubicación sobre el lienzo. Theta se restauró a
  `0` sin mover el robot.

No se registran defectos confirmados de estos controles con esta evidencia;
queda pendiente validar el zoom y la ubicación mediante interacción completa
con el canvas.

## Fidelidad y tiempo máximo: comprobación manual

- Fidelidad: al seleccionar `Realista` la consola mostró `Perfil de simulacion
  aplicado: realistic.`; se restauró `Ideal` y la confirmación fue correcta.
- Tiempo máximo: al seleccionar `30 s` la consola confirmó el valor; se
  restauró a `120 s` y la consola indicó `Tiempo maximo configurado: 120 s.`.

Resultado: PASS para selección y confirmación visible de estos ajustes. No se
ejecutó una misión de 30+ segundos en este paso; la comprobación de watchdog
continúa en los flujos de intérprete.

## Trazas: comprobación manual

En estado `ready` se ejecutaron `Trazas` → `Iniciar registro`, `Avanzar un
tick` y `Detener registro`. La consola confirmó, respectivamente, `Registro de
traza iniciado.`, `Se avanzo un tick de simulacion.` y `Registro de traza
detenido.`; la telemetría mostró tick `1`. Después, Detener y reiniciar llevó
la sesión a `created`, dejó su botón deshabilitado y conservó tick inicial `1`.

Resultado: PASS para inicio, avance y detención de trazas. Exportación JSON y
CSV no se ejercitó para evitar crear descargas durante la campaña visible.

## Ayuda: diálogo Acerca de

Se abrió `Ayuda` → `Acerca de` en navegador real. El diálogo mostró la versión
`1.5.0`, la descripción y la autoría, con un control `aria-label="Cerrar"`.
El cierre mediante ese control ocultó el diálogo correctamente. Resultado:
PASS para apertura y cierre de Acerca de.

### Exportación de trazas

Se generó una traza mínima (iniciar, avanzar un tick y detener) y se pulsaron
`Exportar JSON` y `Exportar CSV` desde el menú real. Ambos controles aceptaron
el clic, conservaron el estado `created` y no generaron error visible, pero no
mostraron confirmación de descarga ni expusieron el archivo resultante a este
controlador de navegador. Estado: **BLOCKED** para validación del contenido y
recepción de los archivos; no se declaran PASS sin esa evidencia.

## Archivo: Nuevo script

`Archivo` → `Nuevo script` fue ejercitado en navegador real. El editor cargó
la plantilla Pybricks base (EV3Brick, Motor, Port y `wait`) y la consola mostró
`Nuevo script creado.`. Resultado: PASS. Abrir y guardar archivos locales
quedan pendientes de una campaña con diálogo nativo de archivos controlable.

## Ejecución positiva manual: desincronización terminal

Se ejecutó la plantilla creada por `Nuevo script` (incluye `wait(500)`). Tras
2,2 s la barra indicó `finished` y se mostró el toast de éxito, pero la
telemetría conservó `running`; además, Detener y reiniciar seguía habilitado.

### WEB-RT-014 — Finalización exitosa anuncia éxito antes de sincronizar telemetría

- Severidad: alta.
- Pasos: crear Nuevo script; Ejecutar; esperar estado terminal.
- Esperado: antes del toast, barra de estado, telemetría, LCD y canvas muestran
  el snapshot terminal `finished`; Detener y reiniciar queda deshabilitado.
- Observado: `sessionStatus=finished`, toast visible y
  `telemetryStatus=running`; Detener y reiniciar habilitado.
- Recuperación: al pulsar Detener y reiniciar, ambos estados pasaron a
  `created`, Ejecutar quedó habilitado, Detener se deshabilitó y el toast se
  ocultó.

Este resultado vuelve a confirmar el riesgo de desincronización terminal de la
interfaz Web.

## Depuración manual: breakpoint y recuperación

Se configuró el script `x = 1; wait(1000); x = 2` con breakpoint en línea 3 y
se pulsó Depurar. La línea 3 fue resaltada, pero el estado permaneció `debug
running`, la sesión siguió `running`, Paso y Continuar continuaron
deshabilitados y el tiempo simulado avanzó hasta 9,32 s. Al usar Detener y
reiniciar, la consola mostró `HTTP 500 [worker=pid-8008, pid=8008]`; tras 2 s,
la sesión seguía `running`, telemetría `resetting` y Ejecutar bloqueado.

### WEB-DBG-016 — Breakpoint no pausa y el reinicio de depuración deja la sesión bloqueada

- Severidad: crítica.
- Esperado: el breakpoint pausa la ejecución, habilita Paso/Continuar y
  Detener y reiniciar devuelve una sesión coherente a `created`.
- Observado: se resalta la línea sin pausar; el reinicio devuelve HTTP 500 y
  deja sesión/depurador bloqueados.
- Mitigación: una recarga de pestaña devolvió sesión y telemetría a `ready`,
  pero Detener y reiniciar continuó habilitado de forma inconsistente.

Por ello, 2.6 no puede aprobarse y los flujos de depuración dependientes se
consideran bloqueados hasta corregir el worker o su coordinación con la sesión.

## Tiempo de pared frente a tiempo simulado

En navegador real se ejecutó `wait(1000)` y se muestreó barra/telemetría cada
200 ms. El estado terminal coherente llegó a los **2.184 ms** de pared, con
`sim_time_s=1.08 s`, estado y telemetría `finished`. La relación observada fue
aproximadamente 2,02× más lenta que el tiempo simulado. Después, Detener y
reiniciar devolvió ambos estados a `created`.

### WEB-PERF-017 — Espera simulada no se reproduce en tiempo real

- Severidad: media.
- Esperado: una espera de 1.000 ms simulados debe aproximarse razonablemente a
  1.000 ms de pared, considerando la tolerancia de renderizado.
- Observado: 1,08 s simulados requirieron 2,184 s de pared.
- Impacto: misiones y animación se perciben lentas y el tiempo de código deja
  de corresponder con el tiempo que espera el usuario.

Es una muestra única; se requieren más mediciones de movimiento, giro y radar
para cerrar 2.7 y cuantificar la desviación por tipo de operación.

Se repitió la medición con `Motor(Port.A).run_time(360, 1000, wait=True)`:
alcanzó `finished` coherente en **2.154 ms** de pared para `sim_time_s=1.04 s`
(≈2,07×). El patrón no se limita a `wait`; también afecta una operación de
motor. Detener y reiniciar restauró `created` en estado y telemetría.

## Pausa y reanudación: reproducción actualizada

Con `wait(5000)`, Pausar dejó la barra en `paused`, telemetría en `running`
con tiempo `0.04 s`, Reanudar habilitado y la consola con
`HTTP 500 [worker=pid-8008, pid=8008]`. Al pulsar Reanudar, barra y telemetría
volvieron a `running` y el tiempo avanzó a `0.9 s`, pero el HTTP 500 siguió
visible. Una recarga de la pestaña restableció estado y telemetría a `ready` y
limpió la consola.

Resultado: confirmación manual actualizada de WEB-RET-007/008. La recuperación
mediante pausa/reanudación sigue parcial y no es apta mientras expone HTTP 500.

## Bloqueo de menús durante ejecución

Con un script cooperativo `wait(5000)` en estado `running`, los disparadores
principales Archivo, Ejemplos, Mundos, Escenarios, Misiones, Fidelidad, Tiempo
máximo y Trazas mostraron `disabled=true`, `aria-disabled=true` y la clase
`is-disabled`. Después de Detener y reiniciar, la sesión volvió a `created` y
los disparadores se reactivaron. Los elementos internos no cambian su atributo
individual, pero quedan inaccesibles porque el menú padre no puede abrirse.

Resultado: PASS para el bloqueo de menús durante ejecución y su restauración
tras reiniciar. Se retira la observación preliminar WEB-UI-015.

## Aviso de finalización correcta (Web)

En la instancia real se ejecutó el siguiente programa:

```python
from pybricks.hubs import EV3Brick
from pybricks.tools import wait

ev3 = EV3Brick()
ev3.screen.print("QA OK")
wait(100)
```

Después de reiniciar la sesión y esperar 900 ms, la barra de sesión y la
telemetría mostraron `finished`. A continuación se observó un único aviso
visible, con `role="status"`, `aria-live="polite"` y el texto
`El programa se ejecutó correctamente.`. Este caso **PASS** demuestra el flujo
Web exitoso y su orden de actualización en esta ejecución.

Como control negativo, se ejecutó `def roto(:\n    pass\n`. La barra alcanzó
`error` y el mismo aviso de éxito no quedó visible. Este caso **PASS** cubre
el error de sintaxis. La verificación de timeout, detención manual, eventos
tardíos y el diálogo equivalente de Tkinter permanecen pendientes; por ello
la validación de paridad completa del aviso aún no se declara aprobada.

## Autoría de mundos: colocación de assets

En el editor abierto desde `Mundos → Editor de mundos` se seleccionó `Nuevo`,
se eligió `Muro A` y se pulsó el canvas en dos posiciones distintas. En ambos
intentos, el editor mostró inicialmente `Validación: OK` / `Mundo válido.`;
sin embargo, al cabo de aproximadamente dos segundos la consola cambió a
`No se pudo colocar el asset. [worker=pid-8008, pid=8008]`. La selección seguía
mostrando `Muro A`, sin confirmación visual de que la colocación hubiera sido
persistida.

### WEB-WE-002 — La colocación de un asset falla de forma asíncrona

- Severidad: alta.
- Pasos: abrir `Mundos → Editor de mundos`; `Nuevo`; seleccionar `Muro A`;
  hacer clic en el canvas; esperar al menos dos segundos.
- Esperado: el muro se coloca y la consola confirma un mundo válido, sin error
  tardío; el resultado puede aplicarse y persistirse.
- Observado: tras una validación inicial positiva, se informa el fallo de
  colocación con referencia al worker `pid-8008`.
- Impacto: bloquea el CRUD manual de mundos y, por tanto, los casos de
  creación con obstáculos, meta o sensores quedan BLOCKED hasta recuperar el
  worker o corregir la coordinación del editor.

Una recarga del navegador devolvió el editor a `created`/`Mundo válido.` y un
tercer intento de colocar el mismo muro esperó 2,3 s sin error. Por tanto, el
defecto se clasifica como **intermitente y dependiente del estado del worker**,
no como un fallo determinista de cada colocación. La prueba de CRUD no se
puede marcar PASS hasta reproducirlo con una sesión limpia y aislar la causa.

El intento posterior de `Guardar` tampoco llegó al diálogo de nombre: la
consola volvió a mostrar el mismo error de colocación. El botón intenta
persistir la pose del robot antes de solicitar el nombre, por lo que el ciclo
manual guardar/recargar/eliminar queda **BLOCKED** por WEB-WE-002. No se creó
ningún archivo temporal ni se modificaron mundos guardados del usuario.

## Tema Web y persistencia

En el simulador se abrió `Tema`, se seleccionó `Oscuro` y se comprobó que el
atributo de tema del documento pasó a `dark` con la telemetría aún visible. Tras
recargar la pestaña, el tema oscuro permaneció seleccionado. Finalmente se
seleccionó `Claro` y el atributo volvió a `light`. Resultado: **PASS** para
alternancia y persistencia manual del tema Web; esta verificación no sustituye
las pruebas de contraste automatizadas ya registradas.

## Misiones disponibles

En la pestaña real del simulador se abrió `Misiones` y se ejercitaron, una a
una, `Sigue líneas básico`, `Evita obstáculos` y `Radar ultrasónico`. Cada
acción cerró el menú y la consola confirmó respectivamente `Misión cargada:`
con el nombre seleccionado. Resultado: **PASS** para la carga individual de
las tres misiones. Su ejecución completa, evaluación y reinicio siguen
pendientes dentro del catálogo de recorridos de la campaña.

La misión `Radar ultrasónico` se ejecutó además en el navegador real. A los
12 s de pared seguía en `running.. t=5.70s` / telemetría `running`; a los 27 s
alcanzó `finished` tanto en la sesión como en la telemetría, sin errores de
consola. Posteriormente `Detener y reiniciar` dejó ambos estados en `created`.
Resultado: **PASS** para este recorrido terminal y su reinicio. El toast ya no
era visible en la segunda lectura, realizada 15 s después, por lo que no se
usa esta ejecución para evaluar su duración.

También se ejecutaron `Sigue líneas básico` y `Evita obstáculos` desde el menú
Web. La primera terminó con sesión y telemetría en `finished` antes de los
15 s de observación. La segunda permanecía en `running... t=13.86s` a los
15 s y terminó correctamente después de otros 15 s, igualmente con ambos
estados en `finished` y sin mensajes en consola. Tras cada una, `Detener y
reiniciar` devolvió sesión y telemetría a `created`. Resultado: **PASS** para
ejecución y reinicio de las tres misiones disponibles en esta campaña.

## Escenarios disponibles

Se cargaron y ejecutaron desde el menú Web los cuatro escenarios: `Seguidor de
linea`, `Ultrasonido + obstaculos`, `Test pantalla/altavoz` y `Radar 360
ultrasonido`. En los cuatro, la consola confirmó la carga, sesión y telemetría
alcanzaron `finished` y no se mostraron errores de consola. El escenario de
pantalla/altavoz además dejó el valor `262 Hz, 200 ms, vol 50` en el panel del
altavoz. Tras cada recorrido, `Detener y reiniciar` devolvió sesión y
telemetría a `created`. Resultado: **PASS** para los cuatro escenarios
predefinidos en este entorno de prueba.

## Ejemplos Pybricks

La interfaz presentó 23 ejemplos disponibles. Se ejercitaron con ejecución
real `01_intro_led.py`, `03_movimiento_basico.py` y
`08_sensor_ultrasonido_frenado.py`. Los tres terminaron con sesión y
telemetría en `finished`, sin errores de consola, y cada reinicio posterior
devolvió la sesión a `created`. Resultado: **PASS** para esos ejemplos
representativos de LED, motores y ultrasonido. Los otros 20 ejemplos han sido
cargados previamente, pero su ejecución individual sigue pendiente y no se
declara aprobada por inferencia.

Se añadieron ejecuciones reales de `02_intro_pantalla_altavoz.py`,
`04_movimiento_motores_individuales.py` y `05_drivebase_cuadrado.py`. Todos
terminaron con sesión y telemetría en `finished`, y se reiniciaron a `created`;
el ejemplo de pantalla/altavoz actualizó el panel del altavoz a `262 Hz, 200
ms, vol 50`. Con ello quedan seis ejemplos ejecutados manualmente. Los 17
restantes siguen pendientes de ejecución individual.

Se ejecutaron además `06_drivebase_perfiles_aceleracion.py`,
`07_sensor_tacto_reaccion.py`, `09_sensor_color_stop.py` y
`10_sensores_combinados.py`. Los cuatro finalizaron en `finished` tanto en la
sesión como en telemetría, sin consola de error, y cada uno se reinició a
`created`. La campaña acumula diez ejemplos ejecutados manualmente; quedan 13
pendientes de ejecución individual.

Se ejecutaron `11_siguelineas_basico.py`, `12_siguelineas_robusto.py` y
`13_colision_controlada.py`. El primero y el tercero finalizaron dentro de
15 s; el robusto continuaba en ejecución a `t=13.54s` y finalizó tras otros
15 s. Los tres alcanzaron `finished` en sesión y telemetría, sin errores de
consola, y se reiniciaron a `created`. Acumulado: 13 ejemplos ejecutados
manualmente; quedan 10 pendientes.

Se ejecutaron también `14_navegacion_hasta_pared.py`,
`15_esquiva_obstaculos.py` y `17_gyro_correccion_rumbo.py`. Navegación y gyro
terminaron dentro de 15 s; evasión siguió en marcha a `t=13.52s` y llegó a
`finished` tras otros 15 s. Los tres mantuvieron sesión y telemetría en
`finished`, sin error de consola, y se reiniciaron a `created`. Acumulado: 16
ejemplos ejecutados manualmente; quedan 7 pendientes.

Se ejecutaron `18_infrarrojo_beacon_seguidor.py`,
`19_motor_encoder_objetivos.py` y `20_motor_run_until_stalled.py`. El ejemplo
infrarrojo necesitó más de 15 s y terminó durante la segunda ventana de
observación; encoder y bloqueo finalizaron en la primera. Los tres quedaron en
`finished` en sesión y telemetría, sin error de consola, y se reiniciaron a
`created`. Acumulado: 19 ejemplos ejecutados manualmente; quedan 4 pendientes.

Se completaron los cuatro ejemplos restantes:
`16_resolver_laberinto.py`, `21_drivebase_curva_estado.py`,
`22_stopwatch_mision_etapas.py` y `23_radar_ultrasonido_5grados.py`.
Curva y temporizador terminaron dentro de 15 s; el radar terminó en la segunda
ventana de observación. El laberinto continuaba en `running` a `t=66.02s` y
finalizó correctamente después de una tercera ventana, sin consola de error.
Todos alcanzaron `finished` en sesión y telemetría, y el reinicio final dejó
ambos estados en `created`. Resultado: **PASS para la ejecución manual de los
23 ejemplos disponibles** en esta instancia, con la salvedad de que esta
campaña no certifica rendimiento en tiempo real (WEB-PERF-017).

## Mundos predefinidos

El menú Web enumeró los 12 mundos predefinidos (`01_linea_negra_basica.json`
hasta `12_radar_ultrasonido_360.json`). La herramienta de navegador visible no
pudo activar su submenú, que se expone por *hover*: los botones estaban en el
DOM pero permanecían ocultos y el clic agotó el plazo de interacción. También
falló el intento de activar el disparador del submenú por clic. Este resultado
es **BLOCKED de la campaña manual**, no un FAIL del producto. La carga de
mundos desde este menú cuenta con cobertura E2E aprobada; para certificación
manual resta repetirlo en un navegador con control de hover físico.

## Revalidación de error de ejecución

En una sesión creada y estable se ejecutó `resultado = 1 / 0`. A diferencia de
la reproducción histórica WEB-RT-011, la interfaz actualizó sesión y
telemetría a `error`, mostró el `ZeroDivisionError` con traza en consola y
volvió a habilitar `Ejecutar`. `Detener y reiniciar` restauró ambos estados a
`created`. Resultado: **PASS en esta repetición**. WEB-RT-011 se conserva como
defecto histórico/intermitente hasta aislar por qué la primera campaña lo
reprodujo y esta sesión limpia no.

## Revalidación de pausa y recuperación

Con `wait(5000)` en una sesión limpia, `Pausar` agotó el plazo de HTTP y dejó
la sesión en `running` mientras la telemetría mostraba `created`; la consola
indicó `Timeout HTTP (1200 ms)`. `Detener y reiniciar` devolvió ambos estados a
`created`, pero conservó el mensaje de timeout en consola. Resultado: **FAIL**
para pausa coherente; confirma de nuevo la familia WEB-RET-007/008 y añade que
la recuperación de estado es parcial porque la consola queda obsoleta.

## Revalidación de depuración y worker

Después del timeout de pausa, la sesión reapareció como `running` aunque antes
había mostrado `created`; breakpoints y Depurar quedaron deshabilitados. Un
nuevo reinicio no la recuperó (`running` frente a telemetría `created`), pero
recargar la pestaña sí devolvió ambos a `ready`.

Con la sesión limpia se configuró un breakpoint en la línea 3 de
`x = 1; wait(1000); x = 2` y se pulsó `Depurar`. Tras 1,5 s la sesión siguió
en `running. t=0.06s`; `Paso` y `Continuar` tenían el atributo `disabled`, por
lo que el breakpoint no permitió pausar ni avanzar paso a paso. Resultado:
**FAIL**, nueva confirmación manual de WEB-DBG-016. La recarga volvió a ser la
única recuperación observada.

### WEB-RET-015 — Reinicio puede anunciar `created` sin detener el worker

- Severidad: alta.
- Pasos: ejecutar `wait(5000)`; pulsar Pausar; reiniciar; esperar; intentar
  editar los breakpoints.
- Esperado: el reinicio cancela el worker y deja interfaz, sesión y telemetría
  en `created`, habilitando edición y depuración.
- Observado: la sesión volvió a `running`, los campos quedaron deshabilitados
  y otro reinicio no la recuperó; recargar la pestaña la mitiga.

## Recarga durante ejecución

Se inició `wait(5000)` y se recargó la pestaña con la sesión en
`running... t=0.02s`. Después de la recarga, sesión y telemetría mostraron
`ready`, pero `Detener y reiniciar` no tenía atributo `disabled`. Resultado:
**FAIL**, reproducción actualizada de WEB-RT-013: el estado disponible tras
recarga conserva un control de detención habilitado indebidamente.

## Cancelación manual y aviso de éxito

Se inició `wait(5000)` y se pulsó `Detener y reiniciar` mientras la sesión
estaba en `running... t=0.02s`. Después de 1,2 s, sesión y telemetría quedaron
en `created`, la consola estaba vacía y el aviso `El programa se ejecutó
correctamente.` no era visible. Resultado: **PASS** para cancelación manual
coherente y ausencia de falso aviso de éxito en esta ejecución.

En modo oscuro se ejecutó `wait(100)`: sesión y telemetría llegaron a
`finished` y el toast accesible mostró `El programa se ejecutó correctamente.`.
Tras reiniciar y volver a modo claro, la sesión quedó en `created`. Resultado:
**PASS** para el aviso exitoso Web en modo oscuro, sin reemplazar la pendiente
verificación manual en viewport móvil.
