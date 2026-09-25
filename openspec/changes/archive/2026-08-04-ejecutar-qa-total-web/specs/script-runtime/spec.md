## ADDED Requirements

### Requirement: Verificación temporal de ejecución y renderizado Web

La campaña Web MUST medir y registrar la relación entre reloj de pared,
`sim_time_s`, ticks, snapshots y frames. El renderizado no MUST modificar la
semántica temporal de Pybricks.

#### Scenario: Espera y movimiento de duración conocida

- DADO un programa que usa `wait`, motor o DriveBase
- CUANDO se ejecuta en navegador real
- ENTONCES el informe DEBERÁ registrar su duración de pared, tiempo simulado y
  ticks, comparados con una tolerancia declarada
- Y una desviación deberá clasificarse con causa y evidencia.

#### Scenario: Interpolación visual activa

- DADO dos snapshots consecutivos de una ejecución
- CUANDO el canvas interpola posición u orientación
- ENTONCES tick, LCD, sensores, motores, tiempo y estado DEBERÁN conservar el
  último snapshot autoritativo
- Y la interpolación NO DEBERÁ adelantar la finalización del programa.
