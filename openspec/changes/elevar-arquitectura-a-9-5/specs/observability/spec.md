## ADDED Requirements

### Requisito: Métricas y trazas correlacionadas

La aplicación DEBERÁ exponer métricas Prometheus y trazas OpenTelemetry con
`session_id`, `command_id` y `worker_id` cuando existan.

#### Escenario: Operación trazable

- DADO un comando de inicio de simulación
- CUANDO atraviesa la sesión y el worker
- ENTONCES métricas y trazas DEBERÁN poder correlacionar la operación completa.
