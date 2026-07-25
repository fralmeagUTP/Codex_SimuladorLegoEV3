# Especificación: API Pybricks virtual

## Propósito

Exponer una API Python similar a Pybricks, aislada por sesión, que traduzca programas del estudiante a comandos de simulación y lea el estado EV3 simulado.

## Requisitos

### Requisito: Árbol de módulos virtual por sesión

El sistema DEBERÁ construir módulos virtuales para `pybricks`, `pybricks.hubs`, `pybricks.ev3devices`, `pybricks.parameters`, `pybricks.robotics` y `pybricks.tools` para cada ejecución. No DEBERÁ registrar esos módulos virtuales de sesión globalmente en `sys.modules`.

#### Escenario: Sesiones web concurrentes importan Pybricks

- DADO que dos sesiones ejecutan programas diferentes
- CUANDO cada programa importa un módulo Pybricks soportado
- ENTONCES cada uno DEBERÁ utilizar el contexto de su propia simulación
- Y sus estados de motor, sensores y brick NO DEBERÁN cruzarse entre sesiones.

### Requisito: Comandos y lecturas de motor

La API `Motor` DEBERÁ admitir construcción por puerto EV3 y los métodos `run`, `dc`, `stop`, `brake`, `hold`, `run_time`, `run_angle`, `run_target`, `track_target`, `run_until_stalled`, `angle`, `speed`, `reset_angle`, `done`, `stalled` y `load` en el alcance del modelo virtual implementado.

#### Escenario: Movimiento angular bloqueante

- DADO un motor con modelo virtual adjunto
- CUANDO un programa invoca `run_angle(..., wait=True)`
- ENTONCES el hilo del script DEBERÁ esperar la finalización del comando o su timeout
- Y el encoder DEBERÁ reflejar el movimiento simulado.

### Requisito: Comandos de drivebase

La API `DriveBase` DEBERÁ proporcionar `drive`, `stop`, `brake`, `straight`, `turn`, `curve`, `settings`, `done`, `stalled`, `state` y `use_gyro`. Los comandos DEBERÁN usar milímetros, grados y milisegundos de acuerdo con sus firmas virtuales documentadas.

#### Escenario: Conducción no bloqueante

- DADO que un programa invoca `drive(speed, turn_rate)`
- CUANDO ocurren ticks posteriores del motor
- ENTONCES el robot DEBERÁ moverse conforme a la configuración actual del drivebase
- HASTA que otro comando cambie o detenga ese movimiento.

### Requisito: Acceso a sensores y brick

La API DEBERÁ exponer sensores de color, tacto, ultrasónico, infrarrojo y gyro, y un `EV3Brick` con pantalla, altavoz, luz y botones virtuales. Las lecturas DEBERÁN reflejar el último tick completado.

#### Escenario: Reflexión de una línea negra

- DADO un sensor de color ubicado sobre una celda negra
- CUANDO el programa solicita la reflexión
- ENTONCES DEBERÁ recibir la reflectancia configurada para esa superficie.

## Notas de compatibilidad actuales

- La cobertura de API es parcial e incluye aproximaciones.
- `DriveBase.use_gyro()` no tiene efecto y aún no aplica corrección de giro en lazo cerrado.
- El temporizado de curvas y parte de los modos de parada son aproximados.
- Estancamiento, duty cycle y carga son aproximaciones del modelo, no mediciones eléctricas de un motor físico.
