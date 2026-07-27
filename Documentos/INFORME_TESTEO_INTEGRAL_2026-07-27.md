# Informe de testeo integral — aplicación de escritorio Tkinter

Fecha: 2026-07-27  
Rama evaluada: `agent/release-1-5-0`  
Último commit al inicio de la campaña: `f0802f4`  
Sistema: Windows 10 22H2 (10.0.19045), sesión de automatización no interactiva  
Python: 3.12.5 (conda-forge)  
Comando de inicio evaluado: `\.venv\Scripts\python.exe -m simulador_ev3.ui.main_window`

## 1. Resumen ejecutivo

Resultado: **no apta para liberar sin correcciones visuales**.

Se ejecutó una instancia real de Tkinter y se generaron capturas de la ventana
en 1280×800, con tema claro y oscuro. La aplicación construye la interfaz y la
mayoría de las pruebas automatizadas existentes pasan, pero la evidencia visual
demuestra regresiones importantes de distribución: telemetría truncada y la
tabla Robot/Estado no visible en el panel Brick. La automatización de entrada
real mediante `pywinauto` no pudo conectarse a un escritorio Windows visible,
por lo que los recorridos de clics, menús y diálogos quedan bloqueados y no se
declaran como aprobados.

## 2. Entorno y evidencia

- Dependencias de prueba: `pytest 9.1.1`, `pywinauto 0.6.9`, Pillow.
- Captura real de ventana Tkinter:
  - [Tema claro](EVIDENCIA_TESTEO_INTEGRAL_2026-07-27/simulacion_light_1280x800.png)
  - [Tema oscuro](EVIDENCIA_TESTEO_INTEGRAL_2026-07-27/simulacion_dark_1280x800.png)
- Automatización de escritorio: `EV3_RUN_DESKTOP_E2E=1 pytest tests/e2e/test_desktop_pywinauto.py -q`.
  Resultado: 2 pruebas omitidas porque el entorno no expone un escritorio
  interactivo a `pywinauto`.
- Captura: `python scripts/capture_desktop_evidence.py --output-dir
  Documentos/EVIDENCIA_TESTEO_INTEGRAL_2026-07-27 --theme all`.
  Resultado: capturas generadas; al cierre se registró un callback Tcl inválido.

## 3. Matriz resumida

| ID | Área | Resultado | Evidencia / observación |
|---|---|---|---|
| TK-START-01 | Construcción Tkinter desde código | PASS | La ventana se construyó y fue capturada en ambos temas. |
| TK-START-02 | Intro BotLab, 3 s, centrado | BLOCKED | No pudo verificarse visualmente: el capturador instancia `EV3SimulatorApp` directamente y el escritorio no admite automatización interactiva. |
| TK-START-03 | Ejecutable empaquetado | BLOCKED | Binario disponible, pero sin canal interactivo para comprobar intro, foco y transición. |
| TK-LAYOUT-01 | Escenario, editor y Brick visibles | PASS | Ambos temas muestran las áreas principales. |
| TK-LAYOUT-02 | Telemetría legible a 1280×800 | FAIL | Títulos y valores truncados; ver TK-001. |
| TK-LAYOUT-03 | Robot/Estado debajo de LCD visible | FAIL | No aparece en el área visible; ver TK-002. |
| TK-THEME-01 | Tema claro | PASS con observaciones | Renderiza, pero conserva los fallos de distribución. |
| TK-THEME-02 | Tema oscuro | PASS con observaciones | Renderiza, pero conserva los fallos de distribución. |
| TK-MENU-01 | Menús Archivo–Ayuda y diálogos | BLOCKED | `pywinauto` no obtuvo escritorio visible; no se simularon clics. |
| TK-WORLD-01 | Crear/editar/guardar/cargar mundos | BLOCKED | Requiere interacción real con diálogos; no se falsificó el resultado. |
| TK-MISSION-01 | Éxito, fallo y cancelación de misiones | BLOCKED | Requiere recorrido interactivo completo. |
| TK-SCRIPT-01 | Scripts válidos, errores, puertos, límite y detención | BLOCKED | No se pudo inyectar texto/clicar controles en escritorio real. |
| TK-CONTROL-01 | Ejecutar, pausar, reanudar, reiniciar y ubicación | BLOCKED | Igual limitación de automatización. |
| TK-CANVAS-01 | Colisiones, sensores, trazas y representación única | BLOCKED | No hubo control de entrada disponible. |
| TK-CLOSE-01 | Cierre de ventana temporal | FAIL | Error Tcl tras la captura; ver TK-003. |
| AUTO-01 | Suite existente completa | No ejecutada en esta campaña | No sustituye validación manual; se ejecutaron los subconjuntos de escritorio. |

## 4. Inconsistencias priorizadas

### TK-001 — Telemetría truncada en tamaño de referencia

- Severidad: **alta**.
- Funcionalidad: tablero de telemetría.
- Precondición: ventana Tkinter a 1280×800, tema claro u oscuro.
- Pasos:
  1. Abrir la aplicación temporal con `capture_desktop_evidence.py`.
  2. Capturar la ventana a 1280×800.
  3. Observar la cabecera de Sensores y los valores de motores/sensores.
- Esperado: tres columnas legibles, sin texto cortado ni celdas superpuestas.
- Observado: la cabecera de sensores se corta (`...NRS S1–S4 (2...`), las
  etiquetas de ángulo comienzan fuera del bloque y estados como `Sin conectar`
  aparecen recortados. Ocurre en ambos temas.
- Evidencia: capturas claro y oscuro enlazadas en la sección 2.
- Hipótesis: anchos mínimos, márgenes de bloques y fuente no se adaptan al
  espacio real disponible del `PanedWindow`.
- Recomendación: diseñar puntos de ruptura del tablero; limitar márgenes,
  redistribuir con `grid` y validar visualmente 1024×768, 1280×800 y 1920×1080.

### TK-002 — Tabla `ROBOT / ESTADO` no visible bajo la LCD

- Severidad: **alta**.
- Funcionalidad: panel EV3 Brick / estado del robot.
- Precondición: ventana a 1280×800.
- Pasos:
  1. Abrir la aplicación y revisar el panel Brick inferior.
  2. Desplazarse visualmente hasta el límite inferior del panel.
- Esperado: tabla Robot/Estado con X, Y y Theta visible debajo de la LCD.
- Observado: la LCD ocupa el final del panel visible; la tabla no se observa.
- Evidencia: capturas de la sección 2.
- Hipótesis: altura fija de LCD más altura limitada del panel inferior, sin
  scroll independiente o estrategia responsive para el Brick.
- Recomendación: reservar altura para la tabla, o introducir scroll del Brick
  con encabezado/LCD/table visibles y probado en tamaños de referencia.

### TK-003 — Callback Tcl inválido al cierre de la ventana de evidencia

- Severidad: **media**.
- Funcionalidad: ciclo de vida y redimensionamiento.
- Pasos:
  1. Ejecutar `scripts/capture_desktop_evidence.py`.
  2. Esperar a que la ventana temporal se cierre con `_on_close()`.
- Esperado: cierre silencioso, sin callbacks pendientes contra widgets ya
  destruidos.
- Observado: `invalid command name "..._apply_responsive_layout"`.
- Evidencia: salida de consola de la ejecución de captura.
- Hipótesis: callback programado con `after_idle` no se cancela durante cierre.
- Recomendación: conservar y cancelar el identificador de todos los callbacks
  de resize/idle antes de destruir la raíz; añadir prueba de cierre real.

### TK-004 — Intro BotLab no validada visualmente

- Severidad: **media** (riesgo de aceptación).
- Funcionalidad: inicio.
- Resultado: BLOCKED, no FAIL.
- Motivo: la prueba de entrada nativa se omite sin escritorio interactivo y el
  capturador existente crea la aplicación directamente, sin pasar por `main()`.
- Recomendación: añadir un capturador específico de intro que tome una imagen
  entre 0.5 y 2 segundos, y una prueba `pywinauto` en una sesión Windows visible.

### TK-005 — Nombre de mundo mostrado no se sincroniza al cargar un preestablecido

- Severidad: **media**.
- Funcionalidad: gestión y contexto visible del mundo activo.
- Pasos:
  1. Abrir **Mundos > Mundos preestablecidos**.
  2. Seleccionar `07_laberinto_v1.json`.
  3. Revisar el encabezado y la posición inicial mostrada.
- Esperado: el encabezado identifica el mundo seleccionado y coincide con el
  escenario y su posición de inicio.
- Observado: el canvas carga los obstáculos y la posición cambia a `(45.0 cm,
  95.0 cm)`, pero el encabezado conserva `Mundo actual: Básico`.
- Evidencia: capturas de la validación interactiva posterior, sección 9.
- Hipótesis: la carga de mundo actualiza el motor/canvas, pero no la variable
  enlazada a la etiqueta del encabezado.
- Recomendación: sincronizar el nombre visible con el identificador o nombre
  mostrado del mundo cargado y añadir una prueba de regresión de selección.

### TK-006 — Reanudar finaliza prematuramente un script pausado

- Severidad: **alta**.
- Funcionalidad: controles de ejecución Pausar/Reanudar y semántica de
  `pybricks.tools.wait`.
- Pasos:
  1. Ejecutar el script `from pybricks.tools import wait; wait(8000)`.
  2. Pulsar Pausar aproximadamente al segundo 1.
  3. Confirmar estado `PAUSADO` y pulsar Reanudar.
- Esperado: el programa continúa los aproximadamente 7 segundos restantes y
  solo entonces llega a `FINALIZADO`.
- Observado: a los `1.120 s` la telemetría indicó `PAUSADO`; tras Reanudar, el
  estado cambió inmediatamente a `FINALIZADO` y el tiempo/tick permanecieron
  en `1.120 s`/`56`.
- Evidencia: capturas de la validación interactiva posterior, sección 9.
- Hipótesis: la pausa interrumpe el mecanismo de espera y Reanudar no conserva
  el trabajo pendiente ni la duración restante.
- Recomendación: tratar la pausa como detención del reloj de simulación, no
  como finalización de la corrutina; añadir una prueba de regresión con
  `wait()` y una operación de motor.

### TK-007 — El registro de trazas exporta listas de snapshots vacías

- Severidad: **alta**.
- Funcionalidad: Trazas > Iniciar registro / Detener registro / Exportar JSON.
- Pasos:
  1. Iniciar el registro desde el menú Trazas.
  2. Ejecutar `wait(1500)` hasta finalizar (81 ticks observados).
  3. Exportar JSON, y repetir tras detener el registro.
- Esperado: el JSON contiene snapshots del ciclo de simulación ejecutado.
- Observado: ambos archivos JSON se crearon y fueron válidos, pero contenían
  exactamente `{"trace_version":1,"snapshots":[]}`.
- Evidencia: ejecución interactiva del 2026-07-27; archivos temporales de
  exportación inspeccionados con tamaño de 34 bytes.
- Hipótesis: el menú activa un indicador o buffer distinto del recopilador de
  snapshots, o el runtime no entrega eventos al servicio de trazas.
- Recomendación: enlazar el colector a los ticks reales y añadir una prueba de
  integración que ejecute una misión y valide un JSON con al menos un snapshot.

## 5. Accesibilidad, estabilidad y rendimiento

- Accesibilidad: no fue posible validar foco de teclado, atajos, orden de tab,
  lector de pantalla ni apertura de menús con interacción nativa.
- Tema: los dos temas renderizan sin traceback, pero la legibilidad se degrada
  por truncamiento, no por contraste en las áreas observables.
- Estabilidad: la instancia real no mostró traceback durante la creación; sí
  se detectó TK-003 al cerrar la instancia temporal.
- Rendimiento: no se realizaron mediciones de ticks ni carga manual; no se
  declara conformidad de rendimiento.
- Persistencia: no cubierta, por ausencia de interacción con menús/diálogos.

## 6. Riesgos para lanzamiento

1. Alto: la telemetría no cumple su objetivo educativo en 1280×800 por texto
   truncado y datos incompletos visualmente.
2. Alto: el estado del robot solicitado no es visible en el Brick en el tamaño
   de referencia.
3. Medio: callbacks pendientes al cierre pueden generar ruido de consola o
   errores durante ciclos de apertura/cierre.
4. Medio: no existe evidencia automatizada visual de la intro ni de los menús
   en una sesión gráfica interactiva.

## 7. Recomendaciones y regresión

1. Corregir TK-001 y TK-002 antes de liberar; no usar capturas como sustituto
   de validación a varios tamaños.
2. Crear pruebas de regresión visual de telemetría/Brick para 1024×768,
   1280×800 y 1920×1080, claro y oscuro.
3. Corregir TK-003 y añadir una prueba que cierre la raíz con callbacks de
   resize pendientes.
4. Ejecutar los recorridos nativos `pywinauto` en una cuenta Windows de sesión
   gráfica real; ampliar allí menús, mundos, misiones, scripts y controles.
5. Añadir un caso de evidencia para la intro tanto desde fuente como desde el
   ejecutable empaquetado.

## 8. Conclusión

**No apta para liberar** en el estado observado para la interfaz de escritorio.
El motor y las pruebas unitarias no se evalúan como sustituto de la experiencia
real: la campaña detectó dos regresiones visuales de alta severidad y una de
ciclo de vida. La aprobación debe requerir corrección, nueva evidencia visual
y recorridos interactivos de escritorio no bloqueados.

## 9. Seguimiento de corrección — 2026-07-27

Se implementó el cambio OpenSpec `corregir-regresiones-qa-tkinter` después de
la campaña inicial. No altera los resultados históricos anteriores; registra
la verificación posterior de las tres regresiones confirmadas.

| Hallazgo | Resultado posterior | Evidencia |
|---|---|---|
| TK-001 | PASS visual: a menos de 560 px el tablero se apila y evita recortar celdas; desde ese ancho conserva tres columnas. | [Seis capturas](EVIDENCIA_QA_REGRESION_2026-07-27/final/) en 1024×768, 1280×800 y 1920×1080, claro y oscuro. |
| TK-002 | PASS por accesibilidad: Brick incorpora desplazamiento vertical independiente y la tabla `ROBOT / ESTADO` queda después de la LCD, siempre alcanzable. | Capturas finales con barra vertical del panel Brick. |
| TK-003 | PASS: el cierre cancela de forma idempotente callbacks de tick, resize y layout. | El capturador de seis imágenes finalizó con código 0 y sin `invalid command name`. |

Pruebas automatizadas posteriores: `pytest tests/ui/test_ui.py
tests/shared/test_desktop_evidence_script.py -q` — **84 PASS**. Se añadieron
casos específicos de cierre con callback de layout pendiente e invocación de
cierre repetida.

La validación visual se ejecutó con `python scripts/capture_desktop_evidence.py
--theme all --size 1024x768 --size 1280x800 --size 1920x1080
--verify-layout`; el modo verifica la geometría de telemetría/LCD y que
`ROBOT / ESTADO` es visible o desplazable desde el panel Brick.

Mediciones registradas por el capturador (96 DPI): 1024×768 → telemetría
369×320, Brick 321×320, LCD 289×192; 1280×800 → 432×334, 300×334, 268×192;
1920×1080 solicitado (1061 px de área cliente por la barra del sistema) →
655×443, 448×443, 399×192.

La decisión de liberación permanece **apta con observaciones**, no aprobación
plena: siguen pendientes los recorridos de la fase 5 (intro, menús, diálogos,
mundos, misiones y scripts) en una sesión Windows realmente interactiva, y las
pruebas de geometría automatizadas sin mocks de Tkinter.

Se añadió el recorrido E2E `test_desktop_startup_shows_intro_before_main_window`.
Con `EV3_RUN_DESKTOP_E2E=1` la campaña actual reportó 3 pruebas **BLOCKED**
(omitidas), ya que Windows no expuso ventanas visibles al proceso de
automatización. El mismo recorrido quedará activo, sin cambios manuales, en
una sesión gráfica local o de CI con escritorio interactivo.

Validación de empaquetado posterior: `python -m PyInstaller --noconfirm
SimuladorEV3.spec` finalizó con código 0. El artefacto
`dist/SimuladorEV3/SimuladorEV3.exe` contiene
`_internal/simulador_ev3/assets/Intro.png`; al iniciarlo, el proceso continuó
activo tras 6 segundos y pudo cerrarse limpiamente. La inspección visual de la
intro del ejecutable permanece BLOCKED por la misma limitación de escritorio.

Validación funcional de intro desde código fuente: el nuevo capturador
`scripts/capture_desktop_intro.py` ejecutó el flujo real de
`_launch_after_intro()` y generó [intro](EVIDENCIA_INTRO_2026-07-27/intro.png)
y [ventana principal](EVIDENCIA_INTRO_2026-07-27/ventana_principal.png). La
captura ocurrió a los 500 ms de la intro y, tras los 3.000 ms configurados,
tomó la ventana principal y la cerró limpiamente. El flujo de evidencia crea
una sesión efímera: no restaura ni persiste la sesión de la persona usuaria.

Validación interactiva parcial posterior: mediante entrada real de mouse y
teclado se abrió el catálogo **Ejemplos**, se cargó un script Pybricks, se
ejecutó hasta finalizar y se verificaron el LED, la LCD, tick, tiempo y estado
de telemetría. También se pulsó **Detener y reiniciar** durante la ejecución:
el resultado fue `IDLE`, tick `0`, tiempo `0.000 s`, LED apagado y robot en su
posición inicial. La aplicación se cerró sin proceso residual. Evidencia:
[ejecutando](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/ejemplo_ejecutando.png),
[finalizado](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/ejemplo_terminado.png) y
[reiniciado](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/detener_reiniciar_durante_ejecucion.png).

Esta validación elimina el bloqueo de entrada para los recorridos cubiertos,
pero la fase 5 continúa pendiente para el resto del catálogo de menús,
diálogos, mundos y misiones.

Menús verificados con interacción visible: **Ayuda** se desplegó y abrió
`Manual de uso`; **Mundos** se desplegó con las acciones Mundo en blanco,
Cargar JSON, Editor de mundos y preestablecidos. Evidencia:
[Ayuda](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/ayuda_abierto.png),
[Manual](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/manual_uso.png) y
[Mundos](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/mundos_abierto.png).
No se declara aprobado el editor de mundos aún: la selección por coordenadas
fijas no produjo una evidencia concluyente y debe repetirse por un selector
semántico o una ruta de teclado fiable.

Validación interactiva de tema: se alternó el menú **Tema** de claro a oscuro
y de oscuro a claro en una ventana de escritorio visible. Los cambios se
aplicaron al escenario, telemetría, panel EV3, controles y editor, sin texto
oscuro sobre fondo oscuro ni una excepción visible. La restauración a claro
fue correcta. Evidencia: [oscuro](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/tema_oscuro.png)
y [claro restaurado](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/tema_claro_restaurado.png).
La persistencia del tema entre reinicios sigue fuera del alcance de este
recorrido y permanece pendiente.

Validación interactiva de límite de script: el menú **Tiempo máximo** mostró
las opciones `30 s`, `60 s`, `120 s`, `300 s` y `Sin límite`. Tras seleccionar
`120 s`, se ejecutó el script `wait(35000)`: a los 30,3 s permanecía en estado
`EJECUTANDO` y terminó normalmente a los 36,3 s. Por tanto, se confirma que el
límite no sigue fijado rígidamente en 30 s. Evidencia:
[menú](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/tiempo_maximo_menu.png),
[en ejecución a 30 s](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/limite_120s_ejecutando_31s.png)
y [finalizado](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/limite_120s_detenido.png).

Validación interactiva de mundos: el submenú **Mundos preestablecidos** se
desplegó y se seleccionó `07_laberinto_v1.json`. El canvas pasó a mostrar sus
obstáculos y el mensaje de posición inicial cambió a `(45.0 cm, 95.0 cm)`;
por tanto, el mundo activo fue aplicado. Se detectó una inconsistencia menor:
el encabezado mantuvo el texto `Mundo actual: Básico` después del cambio.
Debe actualizarse el nombre mostrado o aclararse que el texto representa otra
propiedad. Evidencia: [submenú](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/mundos_preestablecidos.png)
y [mundo aplicado](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/mundo_preestablecido_laberinto.png).

Validación de catálogos: el menú **Escenarios** expuso Seguidor de línea,
Ultrasonido + obstáculos, Test pantalla/altavoz y Radar 360 ultrasónico. Al
seleccionar Radar 360 se cargaron su escenario, posición inicial `(195.0 cm,
185.0 cm)` y código Pybricks asociado sin excepción. El menú **Misiones**
también se desplegó con Sigue líneas básico, Evita obstáculos y Radar
ultrasónico. Evidencia: [escenarios](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/escenarios_menu.png),
[Radar aplicado](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/escenario_radar_aplicado.png)
y [misiones](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/misiones_menu.png).

Validación de error de sintaxis: al ejecutar `if True print("error")`, la
aplicación conservó la respuesta de la interfaz, informó el estado `ERROR` en
telemetría y mostró el diálogo modal `Línea 1: invalid syntax (<script>, line
1)`. El diálogo se cerró y la aplicación terminó sin proceso residual.
Evidencia: [error de sintaxis](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/error_sintaxis.png).

Validación de navegación restante: **Archivo** se desplegó con Nuevo script,
Abrir script, Guardar script y Salir; al usar Nuevo script se sustituyó el
contenido por la plantilla `# Nuevo script`. **Trazas** mostró iniciar/detener
registro, avanzar un tick y exportaciones JSON/CSV. **Fidelidad** mostró los
perfiles Ideal, Realista y Calibrado. No hubo excepciones ni bloqueo al abrir
estos menús. Evidencia: [Archivo](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/archivo_menu.png),
[nuevo script](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/nuevo_script.png),
[Trazas](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/trazas_menu.png) y
[Fidelidad](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/fidelidad_menu.png).
Las operaciones de abrir, guardar y exportar con archivos del sistema siguen
pendientes para una ejecución aislada con rutas temporales explícitas.

Validación de ciclo de ejecución: con `wait(8000)`, el botón **Pausar** dejó
la interfaz en `PAUSADO` a `1.120 s`/tick `56`, demostrando que el control es
alcanzable y actualiza la telemetría. Sin embargo, **Reanudar** hizo que la
misión terminara de inmediato, sin consumir el tiempo restante; se registró
como TK-006. Evidencia: [pausado](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/ejecucion_pausada.png),
[resultado tras reanudar](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/ejecucion_reanudada.png)
y [estado posterior al reinicio](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/ejecucion_cancelada_reiniciada.png).

Validación de controles de escenario: un clic en el canvas reubicó el robot a
`(118.4 cm, 20.6 cm)` y actualizó el texto de posición inicial. Arrastrar desde
el robot hacia abajo actualizó la orientación a `90°`, tanto en la etiqueta
superior como en el marcador visual. El control Haces cambió de `Haces ON` a
`Haces OFF`; el haz no es distinguible en este mundo sin sensores configurados.
Evidencia: [reubicación](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/robot_reubicado_canvas.png)
y [orientación](EVIDENCIA_INTERACCION_TKINTER_2026-07-27/robot_orientado_arrastre.png).

Validación de trazas: se inició el registro, se ejecutó `wait(1500)` hasta
`FINALIZADO` (1.620 s y tick 81), se exportó JSON y se repitió la exportación
después de detener el registro. Los dos JSON temporales fueron válidos pero
contenían `{"trace_version":1,"snapshots":[]}`. Se registra como TK-007; el
problema no es un fallo del diálogo de archivo, pues ambos archivos se crearon
correctamente fuera del repositorio.
