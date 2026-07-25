# Delta: creación de mundos

## ADDED Requirements

### Requirement: continuidad editor–simulación

La creación de mundos MUST conservar una transición directa y verificable al
simulador en ambas interfaces después de validación y persistencia correctas.

#### Scenario: navegación después de guardar

- DADO un usuario que ha creado, validado y guardado un mundo,
- CUANDO decide continuar en simulación,
- ENTONCES no necesita localizar manualmente el archivo guardado,
- Y el sistema aplica el archivo guardado a la sesión de simulación.
