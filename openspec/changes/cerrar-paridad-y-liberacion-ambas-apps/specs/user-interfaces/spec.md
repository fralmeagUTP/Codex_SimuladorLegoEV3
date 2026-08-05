## ADDED Requirements

### Requirement: Coherencia visible de la sesión

Cada interfaz MUST actualizar el estado terminal o de reinicio de una sesión
como una unidad coherente antes de habilitar comandos dependientes o mostrar una
notificación terminal.

#### Scenario: Finalización correcta del programa

- **DADO** un programa que finaliza correctamente;
- **CUANDO** la interfaz recibe su snapshot terminal actual;
- **ENTONCES** editor, barra de estado, robot, canvas, LCD y telemetría
  representarán ese mismo estado;
- **Y** la notificación de éxito se emitirá una sola vez después de actualizar
  la interfaz.
