# Delta: creación de mundos

## REQUISITO: continuidad editor–simulación

La creación de mundos DEBERÁ conservar una transición directa y verificable al
simulador en ambas interfaces, después de validación y persistencia correctas.

### Escenario: navegación después de guardar

- DADO un usuario que ha creado, validado y guardado un mundo,
- CUANDO decide continuar en simulación,
- ENTONCES no DEBERÁ necesitar localizar manualmente el archivo guardado,
- Y EL sistema DEBERÁ aplicar el archivo guardado a la sesión de simulación.
