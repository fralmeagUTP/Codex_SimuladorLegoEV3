# Campaña visible Web — 2026-07-28

## Entorno

- Sistema: Windows.
- Navegador: navegador gráfico integrado de Codex (Chromium).
- URL de validación: `http://127.0.0.1:5053/`.
- Servidor: `scripts/start_web.ps1 -Port 5053`, ejecutado desde el árbol de trabajo actual.
- Resolución móvil ejercitada: 390×844 px.

> La instancia preexistente de `:5050` servía una versión anterior de la
> plantilla y no contenía el aviso de éxito. No se usó como evidencia de
> producto. La campaña se repitió contra `:5053`, que sirve la plantilla y los
> recursos del árbol de trabajo actual.

## Casos ejercitados en interfaz real

| Caso | Acción y verificación observada | Resultado |
|---|---|---|
| WEB-V-001 | Carga inicial de la aplicación y paneles principales. | PASS |
| WEB-V-002 | Ejecutar el programa Pybricks inicial (`EV3Brick`, LCD, LED, Motor A, `wait`). | PASS |
| WEB-V-003 | Finalización: editor `finished`, telemetría `finished`, Motor A detenido con ángulo final, LED `GREEN`, posición final del robot y estado global coherentes. | PASS |
| WEB-V-004 | Aviso de éxito tras `finished`: región accesible `status`, mensaje exacto y botón de cierre. | PASS |
| WEB-V-005 | Detener y reiniciar después de una ejecución correcta. Se restauraron `created`, tick 1, tiempo 0.02 s, motores a 0, LED apagado, LCD vacío y pose 20 cm/20 cm/0°. El aviso quedó oculto. | PASS |
| WEB-V-006 | Modo oscuro desde el menú Tema. `data-theme=dark`, fondo `rgb(15, 23, 36)` y texto `rgb(219, 229, 245)`. | PASS |
| WEB-V-007 | Diseño móvil 390×844. `Haces ON` quedó entre x=177 y x=261; `scrollWidth` fue 375 px para viewport de 390 px. | PASS |
| WEB-V-008 | Consola del navegador tras los flujos anteriores. | PASS: sin errores ni advertencias. |
| WEB-V-009 | Ejecutar código con sintaxis inválida (`def mal(:`). Estado global y telemetría pasaron a `error`; no se mostró aviso de éxito. | PASS |
| WEB-V-010 | Ejecutar `wait(5000)` y revisar controles durante `running`. Archivo, ejemplos, mundos, escenarios, misiones, tema, fidelidad, tiempo máximo, trazas y edición quedaron bloqueados; Ayuda continuó disponible. | PASS |
| WEB-V-011 | Cancelar la ejecución activa mediante “Detener y reiniciar”. Se recuperaron controles, `created`, tick 1, tiempo 0.02 s, motores, LCD y pose inicial. | PASS |
| WEB-V-012 | Ayuda → Acerca de: abrió el diálogo con versión, autores, aliados y logotipos; se cerró mediante su botón visible. | PASS |
| WEB-V-013 | Tiempo máximo → 60 s: se mostraron las opciones 30/60/120/300/sin límite y la interfaz confirmó “Tiempo máximo configurado: 60 s.” | PASS |
| WEB-V-014 | Mundos → Mundo en blanco: actualizó “Mundo actual: Mundo en blanco”, mantuvo telemetría inicial y confirmó “Mundo en blanco cargado.” | PASS |
| WEB-V-015 | Escenarios → Test pantalla/altavoz: cargó el mundo `05_obstaculos_baliza_ir.json`, la pose 35/75/0° y el programa `02_intro_pantalla_altavoz.py`. | PASS |
| WEB-V-016 | Misiones → Radar ultrasónico: cargó `12_radar_ultrasonido_360.json`, S4 ultrasónico y el programa `23_radar_ultrasonido_5grados.py`; durante ejecución, telemetría reflejó motores B/C, S4 y rotación. | PASS |
| WEB-V-017 | Cancelar manualmente la misión Radar ultrasónico. La sesión volvió a `created`, pero se conservó el mensaje “Misión completada: 40 puntos. ✓ lecturas”. | **FAIL histórico — QA-REG-006, corregida y cubierta por Playwright el 2026-07-30** |
| WEB-V-018 | Pausar una ejecución larga. Los controles y barra de estado indicaron `paused`, pero el resumen de telemetría se mantuvo en `running` tras 800 ms. | **FAIL histórico — QA-REG-007, corregida y cubierta por Playwright el 2026-07-30** |
| WEB-V-019 | Reanudar después de WEB-V-018. Volvieron `running`, tick y tiempo a avanzar; cancelar después restauró `created` sin errores ni advertencias de consola. | PASS |
| WEB-V-020 | Alternar “Haces ON/OFF”. El control pasó a `Haces OFF` y permaneció accesible. | PASS |
| WEB-V-021 | Trazas: iniciar registro y avanzar un tick. La interfaz confirmó el registro y tick/tiempo avanzaron de 1/0.02 s a 2/0.04 s. | PASS |
| WEB-V-022 | Fidelidad → Realista. La aplicación confirmó “Perfil de simulación aplicado: realistic.” sin alterar el estado de sesión. | PASS |
| WEB-V-023 | Matriz responsiva 1920×1080, 1280×800 y 1024×768. `scrollWidth` coincidió con el ancho de viewport y Ejecutar, Detener, Haces ON y el editor quedaron dentro de los límites. | PASS |
| WEB-V-024 | Móvil 390×844. `scrollWidth=375` para viewport de 390; Ejecutar, Detener y Haces ON quedaron dentro del viewport. Telemetría y editor se apilan verticalmente, sin recorte horizontal. | PASS |
| WEB-V-025 | Editor Web de mundos: mundo nuevo vacío, validación y estado “Mundo válido”; biblioteca, inspector, capas y tema oscuro disponibles. | PASS |
| WEB-V-026 | Pulsar “Nuevo” en el editor Web de mundos, sin elemento de biblioteca seleccionado. El editor permanece vacío, pero registra “No se pudo colocar el asset.” | **FAIL histórico — QA-REG-008, corregida y cubierta por Playwright el 2026-07-30** |
| WEB-V-027 | Menú Ejemplos: catálogo visible de 23 scripts; carga de `04_movimiento_motores_individuales.py` actualizó el editor y el nombre de programa. Durante ejecución, motor C mostró `RUN_ANGLE`, ángulo, telemetría y pose actualizadas; el reinicio canceló la sesión. | PASS |
| WEB-V-028 | Script con error de ejecución real (`resultado = 1 / 0`). La sesión y el resumen de telemetría llegaron a `error`; el editor mostró `ZeroDivisionError: division by zero` y el aviso de éxito no fue visible. | PASS |
| WEB-V-029 | Script con importación bloqueada (`import os`). El intérprete rechazó el módulo con `ImportError: Módulo bloqueado por la política: os`, terminó en `error` y no mostró aviso de éxito. | PASS |
| WEB-V-030 | Navegación por teclado: Escape cerró el menú Ayuda y, después de abrir “Acerca de”, cerró su diálogo modal. El diálogo se expone con rol accesible `dialog`. | PASS |
| WEB-V-031 | Navegación de navegador: el enlace al Editor de mundos abrió `/worlds`; Atrás volvió al simulador y Adelante devolvió al editor sin paneles duplicados. | PASS |
| WEB-V-032 | Recarga del simulador. Tras el estado transitorio `iniciando`, recuperó `ready`, una telemetría, un panel EV3 Brick y los dos canvas esperados (mapa y LCD), sin representaciones duplicadas del robot. | PASS |
| WEB-V-033 | Depurar un programa de dos `wait(500)` con breakpoint en la línea 2. No se pausó ni finalizó tras más de 31 s simulados; Depurar/Paso/Continuar quedaron deshabilitados y “Detener y reiniciar” no recuperó la sesión. Una recarga sí la llevó a `ready`. | **FAIL histórico — QA-REG-009, corregida y cubierta por Playwright el 2026-07-30** |
| WEB-V-034 | Editor Web de mundos: la biblioteca cargó Robot, obstáculos, zonas, líneas y suelos; seleccionar Robot EV3 no creó capas y Validar devolvió `Validación: OK` / “Mundo válido”. Antes de validar se presentó espontáneamente “No se pudo colocar el asset.” en un mundo vacío. | **FAIL histórico — QA-REG-008, corregida y cubierta por Playwright el 2026-07-30** |
| WEB-V-035 | Tiempo máximo: el menú expuso 30/60/120/300/sin límite; “Sin límite” confirmó el ajuste. Un bucle infinito con `wait(100)` quedó en ejecución y “Detener y reiniciar” lo canceló, restaurando el resumen a `created`. Se dejó de nuevo 120 s al finalizar la prueba. | PASS |
| WEB-V-036 | Escenario “Ultrasonido + obstáculos”: cargó `05_obstaculos_baliza_ir.json`, programa `15_esquiva_obstaculos.py`, S4 ultrasónico y motores en `RUN`. Al pulsar “Detener y reiniciar” quedó en `resetting` más de un minuto, con tick/tiempo anteriores; solo recargar el navegador recuperó `ready`. | **FAIL histórico — QA-REG-010, revalidada por Playwright el 2026-07-30** |
| WEB-V-037 | Ubicar robot: tras fijar Theta en 90°, activar el modo y hacer clic en el canvas, la telemetría actualizó pose a X=108.4 cm / Theta=90° y confirmó “Pose inicial actualizada.”. El reinicio devolvió `created` y mantuvo esa pose como el nuevo inicio configurado. | PASS |
| WEB-V-038 | Motores A/B/C/D: un programa real ejecutó los cuatro puertos y dejó ángulos 72°/79.20°/86.40°/93.60° con estado final IDLE. “Detener y reiniciar” restauró todos los ángulos y velocidades a cero en `created`. | PASS |
| WEB-V-039 | Sensor táctil: un programa creó `TouchSensor(Port.S1)`, terminó en `finished` y la telemetría mostró `TouchSensorModel` con `pressed: no`. Al reiniciar, S1 temporal desapareció y la sesión volvió a `created`. | PASS |
| WEB-V-040 | DriveBase: `straight(100)` y `turn(90)` llevaron la pose de 20/20/0° a 30/20/90°; motores B/C estuvieron activos y finalizaron IDLE. El reinicio restauró 20/20/0° en `created`. | PASS |
| WEB-V-041 | Archivo → Nuevo script: expuso Nuevo/Abrir/Guardar; Nuevo script restauró la plantilla Pybricks inicial, `editor_actual.py` y estado `ready`, dejando el editor ejecutable. | PASS |
| WEB-V-042 | Ayuda → Manual de uso: la opción cerró el menú, pero no abrió URL, pestaña, diálogo ni mensaje; simulador y estado quedaron sin cambios. | **FAIL histórico — QA-REG-011, revalidada por Playwright el 2026-07-30** |
| WEB-V-043 | Tema: modo oscuro aplicó `data-theme=dark` y fondo oscuro, persistió tras recargar el navegador; se restauró explícitamente a `light` al cerrar el caso. | PASS |
| WEB-V-044 | Trazas: se inició el registro, se ejecutó el programa hasta `finished` con tick 28 y se detuvo el registro. Las confirmaciones “iniciado”/“detenido” aparecieron sin alterar el estado terminal. | PASS |
| WEB-V-045 | Misión “Sigue líneas básico”: cargó `01_linea_negra_basica.json` y `11_siguelineas_basico.py`; durante ejecución creó `ColorSensorModel` y activó motores. Detener y reiniciar volvió a `created` con telemetría inicial. | PASS |
| WEB-V-046 | Accesibilidad Web: el árbol visible expone navegación principal, etiquetas de controles, encabezados, regiones de telemetría y el diálogo de ayuda. Abrir Archivo y pulsar Escape ocultó “Nuevo script”, verificando el cierre por teclado. | PASS parcial |
| WEB-A-001 | E2E de teclado: Flecha abajo sobre Archivo abrió el menú y llevó el foco a Nuevo script; Escape ocultó el menú y devolvió el foco a Archivo. | PASS automatizado |
| WEB-A-003 | Aviso de éxito: se expone como `role=status`, `aria-live=polite`, `aria-atomic=true` y su cierre tiene etiqueta accesible. | PASS automatizado |
| WEB-A-002 | Contraste WCAG AA automatizado para controles y estados críticos en ambos temas. `#telemetryStatus` en oscuro midió 1.29:1. | **FAIL — QA-REG-012** |

## Revalidación de defectos históricos

| Defecto | Resultado actual | Evidencia |
|---|---|---|
| WEB-F-001: snapshot terminal desincronizado | No reproducido en el programa visible ejercitado. | WEB-V-003. |
| WEB-F-002: reinicio visual incompleto | No reproducido en el programa visible ejercitado. | WEB-V-005. |
| WEB-F-003: `Haces ON` recortado y canvas fijo en móvil | No reproducido para el control; no hay scroll horizontal del documento. | WEB-V-007. |

## Alcance pendiente

La campaña visible es una muestra de regresión prioritaria, no sustituye la
matriz integral. Quedan pendientes en navegador los CRUD completos de mundos,
todos los escenarios/misiones, orden y foco visible de tabulación exhaustivos,
y la recuperación ante fallos de red.
