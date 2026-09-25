## ADDED Requirements

### Requirement: Avance de tick verificable

Cuando la interfaz Web confirme que avanzó un tick, MUST haber recibido y
aplicado un snapshot de la generación activa con tick estrictamente mayor. Si el
motor no puede avanzar en el estado actual, el control DEBERÁ estar deshabilitado
o explicar que no se realizó avance.

#### Scenario: Avanzar un tick con traza activa

- DADA una sesión preparada para avance manual y una traza iniciada
- CUANDO el usuario selecciona Avanzar un tick
- ENTONCES el tick visible DEBERÁ incrementarse
- Y la traza DEBERÁ contener la transición correspondiente.

### Requirement: Ritmo observable de simulación

La interfaz Web MUST mantener el progreso visible alineado con el tiempo
simulado, sin que la interpolación altere la semántica de estados, LCD o
telemetría.

#### Scenario: Espera de un segundo

- DADO un script que ejecuta `wait(1000)`
- CUANDO se ejecuta en el entorno de referencia
- ENTONCES la relación entre tiempo de pared y `sim_time_s` DEBERÁ cumplir el
  presupuesto de rendimiento documentado
- Y el canvas DEBERÁ seguir produciendo frames mientras la sesión esté activa.
