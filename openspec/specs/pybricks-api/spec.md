# Especificación: API Pybricks virtual

## Purpose

Exponer una API Python similar a Pybricks, aislada por sesión, que traduzca programas del estudiante a comandos de simulación y lea el estado EV3 simulado.
## Requirements
### Requirement: Árbol de módulos virtual por sesión
El sistema MUST cumplir este requisito.

El sistema DEBERÁ construir módulos virtuales para `pybricks`, `pybricks.hubs`, `pybricks.ev3devices`, `pybricks.parameters`, `pybricks.robotics` y `pybricks.tools` para cada ejecución. No DEBERÁ registrar esos módulos virtuales de sesión globalmente en `sys.modules`.

#### Scenario: Sesiones web concurrentes importan Pybricks

- DADO que dos sesiones ejecutan programas diferentes
- CUANDO cada programa importa un módulo Pybricks soportado
- ENTONCES cada uno DEBERÁ utilizar el contexto de su propia simulación
- Y sus estados de motor, sensores y brick NO DEBERÁN cruzarse entre sesiones.

### Requirement: Comandos y lecturas de motor
El sistema MUST cumplir este requisito.

La API `Motor` DEBERÁ admitir construcción por puerto EV3 y los métodos `run`, `dc`, `stop`, `brake`, `hold`, `run_time`, `run_angle`, `run_target`, `track_target`, `run_until_stalled`, `angle`, `speed`, `reset_angle`, `done`, `stalled` y `load` en el alcance del modelo virtual implementado.

#### Scenario: Movimiento angular bloqueante

- DADO un motor con modelo virtual adjunto
- CUANDO un programa invoca `run_angle(..., wait=True)`
- ENTONCES el hilo del script DEBERÁ esperar la finalización del comando o su timeout
- Y el encoder DEBERÁ reflejar el movimiento simulado.

### Requirement: Comandos de drivebase
El sistema MUST cumplir este requisito.

La API `DriveBase` DEBERÁ proporcionar `drive`, `stop`, `brake`, `straight`, `turn`, `curve`, `settings`, `done`, `stalled`, `state` y `use_gyro`. Los comandos DEBERÁN usar milímetros, grados y milisegundos de acuerdo con sus firmas virtuales documentadas.

#### Scenario: Conducción no bloqueante

- DADO que un programa invoca `drive(speed, turn_rate)`
- CUANDO ocurren ticks posteriores del motor
- ENTONCES el robot DEBERÁ moverse conforme a la configuración actual del drivebase
- HASTA que otro comando cambie o detenga ese movimiento.

### Requirement: Acceso a sensores y brick
El sistema MUST cumplir este requisito.

La API DEBERÁ exponer sensores de color, tacto, ultrasónico, infrarrojo y gyro, y un `EV3Brick` con pantalla, altavoz, luz y botones virtuales. Las lecturas DEBERÁN reflejar el último tick completado.

#### Scenario: Reflexión de una línea negra

- DADO un sensor de color ubicado sobre una celda negra
- CUANDO el programa solicita la reflexión
- ENTONCES DEBERÁ recibir la reflectancia configurada para esa superficie.

### Requirement: Conformidad Pybricks declarada
La API MUST cumplir este requisito.

Cada metodo Pybricks expuesto por el simulador DEBERA declarar su nivel de
conformidad, perfiles compatibles, limites y pruebas asociadas.

#### Scenario: Metodo avanzado soportado

- DADO un metodo avanzado marcado como soportado
- CUANDO se invoca con entradas nominales, limite e invalida
- ENTONCES DEBERA producir el efecto documentado o el error compatible declarado.

### Requirement: Matriz de conformidad Pybricks
La API MUST cumplir este requisito.

El proyecto DEBERÁ mantener una matriz versionada que clasifique cada clase y
método Pybricks como completo, aproximado, parcial o no soportado. Cada método
declarado completo o aproximado DEBERÁ tener pruebas de conformidad.

#### Scenario: Consulta de método soportado

- DADO un usuario o mantenedor que consulta un método Pybricks
- CUANDO revisa la matriz de conformidad
- ENTONCES DEBERÁ poder identificar su estado, limitaciones y pruebas asociadas.

### Requirement: Semántica centralizada de movimiento
La API MUST cumplir este requisito.

El dominio DEBERÁ implementar una semántica única para `COAST`, `BRAKE`, `HOLD`,
curvas y comandos bloqueantes. La API virtual NO DEBERÁ modificar atributos
privados de modelos de dominio.

#### Scenario: Modo de parada HOLD

- DADO un motor o drivebase que termina una maniobra con `Stop.HOLD`
- CUANDO una perturbación simulada intenta modificar su posición
- ENTONCES el modelo DEBERÁ aplicar la semántica HOLD definida por el perfil activo.

## Notas de compatibilidad actuales

- La cobertura de API es parcial e incluye aproximaciones.
- `DriveBase.use_gyro()` no tiene efecto y aún no aplica corrección de giro en lazo cerrado.
- El temporizado de curvas y parte de los modos de parada son aproximados.
- Estancamiento, duty cycle y carga son aproximaciones del modelo, no mediciones eléctricas de un motor físico.
