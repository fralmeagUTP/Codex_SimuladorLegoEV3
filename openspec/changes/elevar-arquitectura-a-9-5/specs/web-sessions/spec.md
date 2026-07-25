## MODIFIED Requirements

### Requisito: Contrato versionado de sesión

Las sesiones DEBERÁN publicar comandos, eventos, errores, snapshots y trazas con
versión, `session_id` y correlación `command_id`.

#### Escenario: Recuperación correlacionada

- DADO un worker recuperado
- CUANDO la sesión reanuda una operación idempotente
- ENTONCES DEBERÁ conservar la correlación y el último snapshot válido.
