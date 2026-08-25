## MODIFIED Requirements

### Requirement: La ejecución Web debe usar una frontera de aislamiento verificable

La ejecución de scripts Web MUST mantener el worker aislado y, en producción
Linux, MUST documentar y verificar límites externos de CPU, memoria, PIDs,
filesystem temporal y salida de red. La aplicación MUST NOT afirmar que el
sandbox Python por sí solo protege contra código hostil.

#### Scenario: Worker con perfil productivo Linux

- **WHEN** la aplicación se inicia con el perfil productivo Linux
- **THEN** el worker se ejecuta como usuario no privilegiado con límites de
  recursos configurados
- **AND** un intento de exceder dichos límites finaliza o cancela el worker sin
  afectar las demás sesiones

#### Scenario: Diagnóstico de worker

- **WHEN** se publica un diagnóstico de ejecución
- **THEN** informa únicamente capacidad, estado y métricas agregadas permitidas
- **AND** no expone rutas temporales, variables de entorno ni secretos
