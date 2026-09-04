## ADDED Requirements

### Requirement: resultado versionado de misión

El sistema MUST emitir una vez por ejecución de misión un evento
`mission_result` versión 1 al finalizar, cancelar, fallar o agotar el tiempo.
El evento DEBE incluir el identificador y versión de misión, desenlace,
puntuación y evidencia de cada criterio.

#### Scenario: misión terminada correctamente

- **Dado** una misión activa y una traza que cumple los criterios
- **Cuando** el script finaliza
- **Entonces** el resultado informa `outcome: finished`, `passed: true` y la
  puntuación de la rúbrica.

#### Scenario: ejecución cancelada

- **Dado** una misión activa
- **Cuando** el usuario detiene la ejecución
- **Entonces** el resultado informa `outcome: cancelled`, `passed: false` y
  puntuación cero, preservando la evidencia disponible.

### Requirement: paridad de presentación

Tkinter y Web MUST presentar el mismo desenlace, criterios y puntuación sin
acoplar las interfaces al evaluador ni al motor.

#### Scenario: resultado visible en ambas interfaces

- **WHEN** una misión alcanza un estado terminal
- **THEN** Web y Tkinter MUST mostrar el mismo desenlace, criterios y puntuación.
