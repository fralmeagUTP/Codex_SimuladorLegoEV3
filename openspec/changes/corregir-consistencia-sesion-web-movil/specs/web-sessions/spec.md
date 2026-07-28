## ADDED Requirements

### Requirement: Consistencia terminal de snapshot

La sesión Web MUST publicar un snapshot completo, con estado de sesión y
generación, antes de publicar `finished`, `timed_out` o `error`. Canvas, LCD,
telemetría y estado visible DEBERÁN poder renderizar el mismo snapshot.

#### Scenario: Script terminado con salida LCD

- DADO un script que escribe en LCD y termina
- CUANDO el runtime publica `finished`
- ENTONCES la interfaz DEBERÁ recibir el snapshot con el contenido final de LCD
- Y la telemetría DEBERÁ indicar `finished` para esa misma generación.

### Requirement: Reinicio atómico por generación

La sesión Web MUST crear una nueva generación al reiniciar y publicar un
único snapshot inicial de esa generación. Eventos o callbacks de una ejecución
anterior NO DEBERÁN reemplazarlo.

#### Scenario: Cancelación de un bucle y reinicio

- DADO un script en ejecución que genera ticks continuamente
- CUANDO el usuario solicita Detener y reiniciar
- ENTONCES estado, tick, tiempo, LCD, canvas y telemetría DEBERÁN representar
  el inicio del mundo activo
- Y ningún snapshot posterior de la misión cancelada DEBERÁ aplicarse.
