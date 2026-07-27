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
