## Requisito: resultado versionado de misión

El sistema DEBE emitir una vez por ejecución de misión un evento
`mission_result` versión 1 al finalizar, cancelar, fallar o agotar el tiempo.
El evento DEBE incluir el identificador y versión de misión, desenlace,
puntuación y evidencia de cada criterio.

### Escenario: misión terminada correctamente

- **Dado** una misión activa y una traza que cumple los criterios
- **Cuando** el script finaliza
- **Entonces** el resultado informa `outcome: finished`, `passed: true` y la
  puntuación de la rúbrica.

### Escenario: ejecución cancelada

- **Dado** una misión activa
- **Cuando** el usuario detiene la ejecución
- **Entonces** el resultado informa `outcome: cancelled`, `passed: false` y
  puntuación cero, preservando la evidencia disponible.

## Requisito: paridad de presentación

Tkinter y Web DEBEN presentar el mismo desenlace, criterios y puntuación sin
acoplar las interfaces al evaluador ni al motor.
