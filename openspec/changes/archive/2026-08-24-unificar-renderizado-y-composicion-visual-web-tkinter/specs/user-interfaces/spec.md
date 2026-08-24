## ADDED Requirements

### Requirement: Composición visual equivalente del simulador

Web y Tkinter MUST presentar una jerarquía equivalente de controles,
canvas, editor, telemetría y EV3 Brick. El Brick DEBERÁ agrupar LCD y
Robot/Estado; la telemetría DEBERÁ conservar bloques legibles de motores y
sensores. Las diferencias de widget nativo o viewport DEBERÁN documentarse y
NO podrán ocultar ni cambiar información.

#### Scenario: Área de trabajo en escritorio

- DADO el mismo mundo abierto en Web y Tkinter a 1280×800 o mayor
- CUANDO se muestra la simulación en estado listo o ejecutando
- ENTONCES el usuario encuentra canvas, editor, telemetría y Brick con la
  misma jerarquía informativa
- Y LCD, Robot/Estado, motores y sensores permanecen visibles o accesibles
  mediante un ajuste o scroll interno explícito.

### Requirement: Estados visibles normalizados

Las interfaces MUST renderizar el mismo texto localizado y token semántico
para `ready`, `running`, `paused`, `finished`, `error`, `timed_out` y
`stopped`. Los valores técnicos internos NO DEBERÁN aparecer como etiquetas
inconsistentes para el usuario final.

#### Scenario: Ejecución activa

- DADA una sesión cuyo estado interno es `running`
- CUANDO se actualizan la barra de estado y la telemetría en Web y Tkinter
- ENTONCES ambas muestran `Ejecutando` y el mismo color semántico accesible.
