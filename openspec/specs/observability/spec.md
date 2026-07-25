# observability Specification

## Purpose
TBD - created by archiving change elevar-arquitectura-a-9-5. Update Purpose after archive.
## Requirements
### Requirement: Métricas y trazas correlacionadas
La operación MUST cumplir este requisito.

La aplicación DEBERÁ exponer métricas Prometheus y trazas OpenTelemetry con
`session_id`, `command_id` y `worker_id` cuando existan.

#### Scenario: Operación trazable

- DADO un comando de inicio de simulación
- CUANDO atraviesa la sesión y el worker
- ENTONCES métricas y trazas DEBERÁN poder correlacionar la operación completa.

