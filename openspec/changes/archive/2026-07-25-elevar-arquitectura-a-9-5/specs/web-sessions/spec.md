## ADDED Requirements

### Requirement: Contrato versionado de sesión
La sesión MUST cumplir este requisito.

Las sesiones DEBERÁN publicar comandos, eventos, errores, snapshots y trazas con
versión, `session_id` y correlación `command_id`.

#### Scenario: Recuperación correlacionada

- DADO un worker recuperado
- CUANDO la sesión reanuda una operación idempotente
- ENTONCES DEBERÁ conservar la correlación y el último snapshot válido.
