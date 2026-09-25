# Reporte de ejecución parcial — QA total Web

Fecha: 2026-08-04.

## Instancia manual oficial

- URL: `http://127.0.0.1:5052/`.
- Salud: `GET /healthz` → HTTP 200, versión 1.5.0.
- Intérprete: `.venv` con Python 3.12.5.

## Resultados relevantes

- Ejecución válida y reinicio tras éxito: PASS.
- Pausa y cancelación no cooperativa: FAIL; `HTTP 500` por falta de
  confirmación del worker sombra.
- Breakpoint: FAIL; no pausa en la línea configurada.
- Ayuda en nueva pestaña: BLOCKED en manual; ruta HTTP disponible y E2E aislado
  aprobado.
- Seguridad/contratos seleccionados: 7 PASS.
- Ayuda, dos contextos y reinicio terminal en E2E: 4 PASS.

## Dictamen provisional

**No apta para liberar.** Hay errores 500 y desincronización reproducibles en
controles críticos de ejecución. Consultar `RESULTADOS_MANUALES_PARCIALES.md`
para pasos, evidencias y correlación con los registros de servidor.

## Actualización de campaña

Ejecuciones posteriores, realizadas en navegador real, ampliaron el diagnóstico:

- `132 passed` en el paquete Web y `51 passed` en E2E Web; son evidencia de
  regresión automatizada, no sustituyen los fallos manuales confirmados.
- Los 23 ejemplos cargan en el editor, los 4 escenarios cargan tras repetición
  controlada y las 3 misiones aceptan selección.
- Los 23 ejemplos, las 4 escenarios predefinidos y las 3 misiones se
  ejecutaron manualmente hasta `finished` con telemetría coherente; cada flujo
  de reinicio observado volvió a `created`.
- WEB-WE-001 (media): el Editor de mundos acepta ancho `0` sin mensaje de
  validación visible.
- WEB-WE-002 (alta, intermitente): la colocación manual de `Muro A` informó de
  forma tardía `No se pudo colocar el asset` con referencia al worker, pese a
  una primera validación positiva; una recarga del navegador lo mitigó.
- WEB-RT-011 (alta): `ZeroDivisionError` deja barra y telemetría en `running`.
- WEB-RT-012 (alta): timeout HTTP bloquea la sesión y el reinicio no la
  recupera; una recarga mitiga el problema.
- WEB-RT-013 (media): tras recargar durante una ejecución, Detener puede quedar
  habilitado en estado `ready`.
- WEB-RT-014 (alta): finalización exitosa muestra éxito con telemetría aún en
  `running`.
- WEB-DBG-016 (crítica): el breakpoint no pausa y reiniciar depuración retorna
  HTTP 500, bloqueando sesión y telemetría.
- La revalidación de Pausar volvió a fallar: `Timeout HTTP (1200 ms)`, sesión
  `running` frente a telemetría `created`; reiniciar recuperó el estado pero
  dejó el timeout obsoleto en consola.
- WEB-RET-015 (alta): tras el timeout de pausa, el reinicio puede anunciar
  `created` sin detener el worker; la sesión reaparece `running` y bloquea la
  depuración hasta recargar la pestaña.
- WEB-PERF-017 (media): `wait(1000)` y `run_time(..., 1000)` tardaron cerca de
  2,0 veces el tiempo simulado en pared.

El dictamen se mantiene: **no apta para liberar**. Los defectos de sincronía,
pausa/reinicio, depuración y recuperación afectan controles centrales y deben
corregirse antes de intentar una certificación final.

## Regresión automatizada focalizada

La orden siguiente se ejecutó el 2026-08-04:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py -q -k "successful_execution_shows_one_accessible_toast_after_terminal_snapshot or success_toast_is_not_emitted_for_error_or_manual_stop or success_toast_fits_mobile_viewport_in_both_themes or pause_and_resume or debug_breakpoint_pause_enables_debug_controls or reset_recovers_a_session_paused_at_a_debug_breakpoint"
```

Resultado: `6 passed, 45 deselected in 9.70s`. Estos flujos pasan en la
instancia aislada de E2E, pero no invalidan los FAIL reproducidos manualmente
contra `http://127.0.0.1:5052/`: la discrepancia entre el entorno aislado y el
servidor manual es por sí misma un riesgo de liberación que requiere
investigación de configuración, worker o ciclo de sesión.

La inspección del listener manual confirmó que el puerto `5052` es atendido
por `C:\ProgramData\miniforge3\python.exe -m simulador_ev3.web.waitress_server`
(PID 8008). Las pruebas E2E se ejecutan desde `.venv\Scripts\python.exe`.
Ambos informan Python 3.12.5 y Flask 3.1.3, pero `waitress` solo figura como
instalado de forma reproducible en `.venv` (3.0.2); el intérprete Miniforge
actual no lo encuentra mediante `pip`. No se reinició el proceso en uso. Es
evidencia de un entorno manual no reproducible que debe normalizarse antes de
atribuir toda diferencia exclusivamente a la lógica de producto.

## Carga y métricas

Se ejecutó `.\.venv\Scripts\python.exe -m pytest tests\load -q`:
`3 passed in 1.55s`. En la instancia manual, `GET /healthz` devolvió `ok`
(versión 1.5.0) y `GET /metrics` reportó 3.880 solicitudes, 5 respuestas 5xx
y duración media de 7,184 ms. Estas métricas son acumuladas desde el inicio
del servidor, no una línea base limpia; confirman que ya hubo respuestas de
servidor fallidas durante la campaña. Aún falta medición fiable de FPS, CPU y
memoria para cerrar la tarea no funcional 5.4.

Como muestra puntual en reposo de 5,02 s, el proceso manual PID 8008 informó
0,00 % de CPU normalizado, 51,49 MiB de conjunto de trabajo, 42,36 MiB de
memoria privada, 373 handles y 14 hilos. Es una observación de reposo, no una
medición bajo carga; se conserva únicamente como referencia inicial.

Se aplicó además una carga HTTP de solo lectura contra `/healthz`: 160
solicitudes con 16 trabajadores, 160 respuestas HTTP 200 en 0,471 s
(339,74 solicitudes/s). Tras la ráfaga, memoria de trabajo y privada se
mantuvieron en 51,50 MiB y 42,36 MiB; la muestra de CPU fue 0,00 % por la corta
duración y no permite concluir capacidad sostenida. No se crearon sesiones ni
se modificaron datos de usuario.

## Flujos negativos y recuperación automatizados

`tests/web/test_web_app.py` ejecutó correctamente 2 casos de límite temporal
y presupuesto de pausa (`2 passed`). Los tres casos aislados de worker para
cancelación cooperativa, timeout y reinicio forzado también pasaron (`3
passed in 2.42s`). Un primer filtro sobre ese archivo no seleccionó pruebas y
terminó con código 1; se repitió con los nombres exactos antes de registrar el
resultado. Esta evidencia valida el worker y la instancia aislada, pero no
sustituye los FAIL manuales contra Waitress/Miniforge ni convierte sus flujos
en PASS de interfaz.

## CRUD de mundos automatizado

La selección E2E `-k "world_editor"` pasó con 4 casos en 7,15 s y la API de
eliminación de mundos pasó 2 casos en 0,38 s. Verifican, en instancia aislada,
creación/colocación de assets y eliminación. El CRUD manual sigue BLOCKED por
WEB-WE-002 y por el submenú de mundos dependiente de hover; por ello no se
presenta este resultado automatizado como aprobación de la experiencia manual.

## Recuperación automatizada

La recuperación desde el espejo de metadatos —incluida la protección por token
incorrecto y la restauración de script, mundo y depuración— pasó 3 casos de
unidad en 0,33 s. Los dos flujos E2E de recuperación de escenario ultrasónico
y de sesión pausada en breakpoint pasaron en 5,62 s. Confirman la ruta aislada
de recuperación, pero el fallo manual WEB-RET-015 demuestra que el proceso
Waitress actual no ofrece todavía la misma garantía operativa.

## Orden de snapshots automatizado

Dos pruebas de unidad verificaron que el estado terminal está precedido por su
snapshot terminal y que el throttling de eventos no bloquea el motor (`2
passed`). Otras dos comprobaron secuencia/generación nueva tras reinicio y el
snapshot completo de `created` (`2 passed`). Dan cobertura al contrato
autoritativo de snapshots, aunque no contradicen la desincronización visual
manual observada en WEB-RT-014.

## Stream SSE automatizado

Tres pruebas de integración aprobaron la secuencia inicial SSE
(estado/snapshot/debug/mundo), el heartbeat configurable y breakpoint con
continuación (`3 passed in 0.61s`).

Se añadió `tests/e2e/test_web_polling_fallback.py`. La primera prueba inicia
una instancia con `WEB_SSE_ENABLED=False`; la segunda mantiene SSE habilitado,
pero fuerza una respuesta HTTP 503 para `/stream`. Ambas ejecutan un script
real en Chromium y comprueban `finished` en sesión y telemetría; la segunda
además verifica que se solicitaron snapshots por polling. Resultado final:
`2 passed in 5.90s`. Junto con la recarga manual durante ejecución y las
pruebas de generación/snapshot tras reinicio, se completa la tarea 4.4.

## Resiliencia y recuperación

Se volvieron a ejecutar tres pruebas de recuperación de sesión desde el
almacenamiento espejo, incluyendo la restauración de script, mundo y estado de
depuración en un nuevo `SessionManager` (`3 passed in 0.32s`). Esto representa
el arranque de un nuevo proceso de servicio con la misma metadata persistida;
no se reinició la instancia manual de Waitress para no interrumpir la sesión
del usuario. También aprobaron cuatro pruebas del worker aislado que cubren
cancelación, límite temporal y recuperación (`4 passed in 3.18s`). Sumadas a
las dos E2E de polling/SSE fallido, estas evidencias completan la tarea 5.6 en
el entorno aislado. Los defectos manuales de timeout siguen abiertos y no se
consideran corregidos por estos resultados.

## Rendimiento y carga controlada

La batería `tests/load` volvió a aprobar (`3 passed in 1.50s`): cubre creación
paralela de sesiones, métricas operativas de workers aislados y doce
operaciones de creación/carga en paralelo con presupuesto local amplio. La
instancia manual de Waitress ya había aportado 160 lecturas concurrentes de
`/healthz` (todas HTTP 200, 339,74 solicitudes/s), memoria de proceso de
51,49 MiB de working set y 42,36 MiB privados en reposo; su muestra de CPU fue
inconclusa y no se presenta como medida de capacidad.

Se añadió además una E2E de Chromium que inicia una simulación real y mide
`requestAnimationFrame` durante 500 ms. Obtuvo al menos 10 fotogramas y
diagnósticos del renderizador antes de confirmar el estado terminal
(`1 passed in 5.08s`). Es una guarda contra bloqueo del hilo visual, no un SLA
de FPS ni una certificación de fluidez en el hardware del usuario.

## Regresión E2E consolidada

Se ejecutó la batería E2E Web completa, incluida la nueva cobertura de
polling/fallo de SSE: `54 passed in 60.51s`. El resultado es válido para la
instancia aislada de Chromium; no sustituye las tareas manuales aún pendientes
ni modifica la clasificación de los defectos observados contra el servidor
manual.

## Medición manual real de ritmo de simulación

El 2026-08-04, con el navegador integrado contra `http://127.0.0.1:5052/`,
se reemplazó el código por `from pybricks.tools import wait; wait(1000)` y se
ejecutó desde el botón visible **Ejecutar**. La interfaz llegó a `finished` en
2.188 s de pared, mientras el campo Tiempo de telemetría mostró `1.06s`; la
relación observada es aproximadamente 2,06×. No hubo mensajes de advertencia
ni error en la consola capturada. Se confirma `WEB-PERF-017` (alta): el ritmo
real de ejecución/renderizado no corresponde al tiempo de simulación esperado.
En ese punto la tarea 2.7 seguía abierta porque faltaban las medidas manuales
de movimiento, giro y radar.

Se completaron esas medidas en la misma sesión de navegador. Un avance
`DriveBase.straight(100)` terminó en 1.558 s con `1.06s` de telemetría
(1,47×); `DriveBase.turn(90)` terminó en 1.612 s con `1.06s` (1,52×); y un
programa que leyó `UltrasonicSensor(Port.S4)`, escribió en LCD y esperó 1.000
ms terminó en 1.629 s con `1.08s` (1,51×). Los cuatro casos finalizaron sin
errores ni advertencias de consola; la lectura ultrasónica quedó visible como
`UltrasonicSensorModel`, distancia 250 cm y presencia no. Con ello se completa
la tarea 2.7, pero con resultado funcional **FAIL** por `WEB-PERF-017`: los
casos medidos son sistemáticamente más lentos que el tiempo simulado.

La captura manual final del caso ultrasónico muestra conjuntamente editor,
canvas, estado `finished`, telemetría `1.08s`/tick 54, sensor S4 y LCD con
`US 2500`; no se observó adelanto visual en ese snapshot terminal. Esta
observación, junto con las pruebas automatizadas de snapshot terminal y de
reinicio, completa 2.8 para la versión evaluada. No revoca el defecto histórico
`WEB-RT-014`, que sigue registrado hasta ser revalidado específicamente contra
la instancia manual.

## Depuración manual y recuperación

En la misma instancia manual se cargó un script de cuatro líneas, se configuró
el breakpoint `3` y se pulsó **Depurar**. Tras 1,2 s, la interfaz mostraba
`debug running`; **Paso** y **Continuar** seguían deshabilitados. Tras otros
1,5 s continuaba `running... t=6.64s`, pese a que el script solo incluía
`wait(300)`. Al pulsar **Detener y reiniciar** no se recuperó: 2 s después el
estado era `running.. t=14.42s`, los menús mutables y Ejecutar permanecían
deshabilitados y no se registraron errores de consola.

Se confirma `WEB-DBG-016` (alta: breakpoint/paso/continuar no alcanzables) y
se abre `WEB-DBG-018` (crítica: Detener y reiniciar no cancela ni desbloquea la
sesión en ejecución iniciada desde Depurar). La tarea 2.6 queda ejecutada con
resultado **FAIL** y requiere corrección antes de poder validar los demás
flujos de depuración y recuperación.

La recarga fue el único mecanismo que devolvió la interfaz a un estado
utilizable: quedó `ready` y los menús volvieron a estar habilitados. Sin
embargo, **Detener y reiniciar** quedó habilitado también en `ready`. Se vuelve
a confirmar `WEB-RT-013` (media): tras una recarga durante/tras una ejecución,
el estado visual de ese control no corresponde al ciclo de vida de la sesión.

## Menús y controles manuales adicionales

Con la sesión recuperada se ejercitaron los menús **Tema**, **Fidelidad** y
**Trazas**. Tema alternó Claro/Oscuro y se restauró a Claro; Fidelidad aceptó
Realista y luego Ideal; y Trazas mostró `Registro de traza iniciado.` y
`Registro de traza detenido.` tras sus respectivos comandos. También se
verificaron Mostrar/ocultar haces y los controles de acercar, alejar y ajustar
vista del mapa. No se observaron errores o advertencias de consola. El menú
Tiempo máximo expone 30, 60, 120, 300 segundos y Sin límite; no se cambió su
valor durante esta sesión para no alterar la configuración activa sin una
prueba dedicada de timeout.

Las exportaciones se completaron posteriormente desde los comandos visibles:
cada una abrió una pestaña con la URL correcta de `/trace?format=json` o
`/trace?format=csv`. El navegador integrado bloqueó la carga de esos endpoints
en la pestaña generada con `ERR_BLOCKED_BY_CLIENT`, por lo que la validación del
contenido exportado queda **BLOCKED por herramienta**, no como fallo del
producto. En cambio, **Avanzar un tick** mostró el mensaje de éxito
`Se avanzó un tick de simulación.` pero el valor visible de Tick permaneció
`1 → 1`, sin errores de consola. Se registra `WEB-TRACE-019` (media): el
comando comunica una acción aplicada que no se refleja en el snapshot/telemetría.

## Escenarios y misiones manuales

Se cargaron desde sus menús visibles los cuatro escenarios: Seguidor de línea,
Ultrasonido + obstáculos, Test pantalla/altavoz y Radar 360 ultrasonido; y las
tres misiones: Sigue líneas básico, Evita obstáculos y Radar ultrasónico. Cada
carga dejó la sesión en `ready`, actualizó al mundo esperado cuando aplica y no
produjo errores de consola. La misión Radar ultrasónico se ejecutó además de
extremo a extremo: terminó `finished` sin errores, con 5.98 s simulados tras
14.714 s de pared (2,46×), por lo que aporta una nueva evidencia de
`WEB-PERF-017`. La ejecución individual y reinicio de cada escenario/misión
restante continúa pendiente en 2.4.

También se cargaron manualmente los 12 mundos preestablecidos, desde
`01_linea_negra_basica.json` hasta `12_radar_ultrasonido_360.json`. En los doce
casos el rótulo Mundo actual coincidió con la selección, el estado fue `ready`
y no hubo errores de consola. La lista se comprobó de forma visual y no dejó
entidades heredadas apreciables al cambiar de mundo. Falta ejecutar y reiniciar
cada mundo para cerrar completamente 2.4.

Esa ejecución se completó posteriormente: en cada uno de los 12 mundos se
cargó desde el menú visible, se ejecutó `wait(50)` y se pulsó **Detener y
reiniciar**. Los doce llegaron a `finished` y volvieron a `created`, sin
errores de consola.

Los cuatro escenarios y las tres misiones se sometieron después al mismo ciclo
en la interfaz: cargar desde su menú, ejecutar un programa corto y reiniciar.
Los siete finalizaron `finished` y retornaron a `created`, sin errores de
consola. Junto con las ejecuciones reales previas de las misiones y la
verificación de snapshot final, se completa 2.4. Esta aprobación no oculta los
defectos independientes de depuración, worker de mundos y ritmo de simulación.

## Bloqueo de navegación durante ejecución

Con un programa normal `wait(700)`, los nueve menús mutables (Archivo,
Ejemplos, Mundos, Escenarios, Misiones, Tema, Fidelidad, Tiempo máximo y
Trazas) estuvieron deshabilitados durante la ejecución. Al llegar a `finished`
el contador de menús deshabilitados volvió de 9 a 0, sin errores de consola.
Este flujo cumple el bloqueo esperado; no contradice el bloqueo permanente
confirmado para el flujo de Depurar (`WEB-DBG-018`).

## Flujos negativos manuales del intérprete

Un error de sintaxis (`if True print('error')`) llegó a `error` y no mostró el
aviso de éxito; una importación no soportada (`import requests`) también llegó
a `error` sin aviso. La cancelación de un bucle infinito cooperativo con
`wait(50)` pasó de `running. t=0.02s` a `created`, con telemetría `created` y
sin aviso de éxito.

En cambio, `resultado = 1 / 0` dejó, aun tras 1,2 s, la barra en `running`, la
telemetría en el `finished` anterior y Ejecutar deshabilitado, sin mensajes de
consola. **Detener y reiniciar** recuperó después ambos estados a `created`.
Se confirma `WEB-RT-011` (alta): un error de ejecución no publica un snapshot
terminal coherente y bloquea el nuevo inicio hasta reiniciar.

## Revalidación móvil manual (390×844)

Con viewport 390×844, **Haces ON** permaneció completamente visible y el
canvas ocupó 337 px dentro de un contenedor de 361 px. La página no tuvo
desbordamiento horizontal (`scrollWidth/clientWidth = 375/375`) y el panel de
telemetría tampoco (`335/335`), sin errores de consola. No se reproduce en esta
versión `WEB-F-003` (recorte de Haces y canvas de escritorio); la captura
visual conserva una presentación compacta con desplazamiento propio del área
de datos, pero no evidencia texto funcional fuera del viewport.

## Aviso de finalización Web

En navegador real se ejecutó un script que escribe `FIN QA` en la LCD y espera
80 ms. Tras `finished`, la telemetría también estaba en `finished` y apareció
exactamente un `#executionSuccessToast`, sin errores de consola. Los flujos
manuales de sintaxis inválida, importación no soportada y cancelación ya habían
confirmado que no se emite en estados no exitosos.

La verificación nativa complementaria de Tkinter se completó con
`test_desktop_success_dialog_is_shown_once_after_finished` (`1 passed in
3.24s`): el diálogo **Ejecución finalizada** apareció tras un script válido y
se cerró sin duplicarse. La prueba unitaria de interfaz confirmó que solo
`finished` emite `El programa se ejecutó correctamente.` y no `timed_out`
(`1 passed in 0.22s`). La E2E Web cubrió éxito único, error/detención sin
toast y viewport móvil en ambos temas (`4 passed in 7.57s`). Se completan
7.1–7.3; `DESK-REG-001` sigue siendo un defecto separado de desbloqueo de
menús, no de la notificación.

## Controles de pose y límite de tiempo

En navegador real se introdujo Theta `90`, se activó **Ubicar robot** y se hizo
clic en el canvas: la interfaz publicó `X 72.2 cm, Y 37.5 cm, theta 90 °`.
También se eligió 60 s en **Tiempo máximo**, se ejecutó un programa válido de
50 ms con resultado `finished`, y se restauró la opción 120 s. Junto con las
pruebas previas de ejecutar/pausar/reanudar, haces, zoom, paneo, trazas y
fidelidad, se completa 2.2 sin nuevos errores de consola.

## Navegación del navegador y teclado

El botón **Atrás** navegó de Simulación a `/help` y **Adelante** regresó a
Simulación, sin errores de consola. Con el menú Mundos abierto, Escape cerró
el desplegable: el estado pasó de `Mundos [expanded]` a Mundos sin elementos
de submenú visibles. Estas comprobaciones cubren navegación histórica y cierre
por teclado del menú; 2.1 permanece abierto por los comandos de archivo y
diálogos que no pueden completarse mientras persiste `WEB-WE-002`.

## Regresión final y dictamen de liberación

La regresión consolidada ejecutó `tests/web`, la E2E principal Web y el
fallback polling/SSE: **186 passed in 72.05s**. Las pruebas se combinaron con
los recorridos manuales reales de menús, mundos, escenarios, misiones,
intérprete, movilidad, tema, accesibilidad visible y responsive.

**Dictamen: no apta para liberar.** La automatización aprobada no revoca los
defectos manuales confirmados: `WEB-DBG-018` (crítico, no cancela/reinicia una
depuración), `WEB-WE-002` (alto, worker bloquea Guardar como y el CRUD),
`WEB-RT-011` (alto, error de ejecución deja UI desincronizada),
`WEB-PERF-017` (alto, ritmo real 1,47×–2,46× más lento) y `WEB-TRACE-019`
(medio, avanzar tick comunica éxito sin actualizar telemetría). Antes de un
release deben corregirse, repetirse los flujos manuales afectados y completar
la evidencia de capturas/HAR aún pendiente.

## Capturas reproducibles generadas

Se actualizó exclusivamente el capturador de evidencia para que valide el
canvas responsivo y use coordenadas de celda vigentes del editor. La aplicación
no fue modificada. La orden `scripts\capture_web_evidence.py` terminó con
código 0 y generó 13 PNG en `capturas_automatizadas`: tres tamaños de
Simulación y Mundos, menú de ejemplos, sintaxis/autocompletado, altavoz,
previsualización y propiedades de mundos, y dos perfiles de sesión
independientes. Los HAR, consola y capturas de regresiones también se conservan
en `artifacts/e2e-web`. Se completa 6.2; no hay vídeo disponible en este
entorno.

Tras esa misión finalizada, **Detener y reiniciar** sí devolvió el flujo normal
a `created`, Tiempo `0.02s` y Tick `1`, sin errores de consola. Por tanto, el
fallo de cancelación/reinicio confirmado en `WEB-DBG-018` queda acotado por
ahora a la ejecución iniciada desde Depurar.

## Editor de mundos Web

El enlace **Editor de mundos** abrió `/worlds` y presentó correctamente sus
controles. Un mundo temporal nuevo con la pose inicial por defecto pasó
**Validar** (`Validación: OK`, `Mundo válido`). Al pulsar **Guardar como**, no
apareció el diálogo de nombre y el editor mostró `No se pudo colocar el asset.
[worker=pid-8008, pid=8008]`; no hubo error de consola. Esto reproduce
`WEB-WE-002` y bloquea la creación/guardado manual del CRUD hasta resolver el
worker de colocación de assets. No se creó ni modificó ningún mundo persistente.

## Centro de ayuda Web

La ruta `/help` cargó sin errores de consola, mostró sus 7 guías y las rutas
recomendadas. Al buscar `mundo`, la región accesible informó 5 guías
disponibles; el selector de tema cambió a Oscuro y se restauró a Claro. El
enlace Ayuda del Editor recibió foco pero no navegó en el adaptador del
navegador, mientras que la URL visible `/help` sí abrió correctamente mediante
navegación directa. Se registra como limitación de la interacción automatizada,
no como fallo del producto hasta reproducirlo en un navegador de usuario.

## Verificación nativa complementaria de Tkinter

Como comprobación de paridad para el aviso de finalización, se ejecutaron los
cuatro recorridos `pywinauto` con una instancia aislada de escritorio. Tres
pasaron; falló `test_desktop_menus_unlock_after_execution_finishes_or_resets`
(`1 failed, 3 passed in 17.91s`): tras finalizar o reiniciar la ejecución, el
menú Archivo no volvió a desplegarse en la comprobación final. Se registra como
`DESK-REG-001` de severidad alta y debe investigarse antes de presentar la
paridad de navegación como aprobada. Esta prueba no constató un diálogo de
éxito duplicado, pero tampoco cubre por sí sola todas las condiciones de 7.1–7.3.

## Captura automatizada de evidencia (resultado final)

El intento inicial detectó una aserción heredada incompatible con el canvas
responsivo. Se corrigió solamente el capturador —no la aplicación— para validar
que el buffer sea visible, proporcional al CSS y no exceda el contenedor. La
ejecución final del 2026-08-04 terminó con código `0` y produjo las 13 capturas
enumeradas en la sección «Capturas reproducibles generadas». Este resultado
final sustituye el intento fallido previo; no hay vídeo disponible en este
entorno.
