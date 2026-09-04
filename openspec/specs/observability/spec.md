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

### Requirement: Diagnóstico común de sesión

Cada ejecución MUST producir un `ObservabilitySnapshot` común con estado,
duración, tick, error, `session_id`, `command_id` y `worker_id` cuando existan.
Web y Tkinter DEBERÁN exponer todos los datos aplicables mediante un adaptador
seguro para su plataforma.

#### Scenario: Ejecución con timeout

- DADO un programa que alcanza el límite de tiempo;
- CUANDO la sesión entrega `timed_out`;
- ENTONCES Web publica el diagnóstico en sus métricas/trazas y Tkinter lo
  muestra o exporta localmente;
- Y ambos registros contienen el mismo estado, límite configurado y
  correlaciones disponibles.

### Requirement: Privacidad de diagnóstico

La exportación de observabilidad MUST excluir secretos, tokens de sesión y
contenido sensible no necesario para diagnóstico.

#### Scenario: Exportar diagnóstico de escritorio

- DADO un docente que exporta un diagnóstico local;
- CUANDO se genera el archivo;
- ENTONCES incluye identificadores técnicos seguros y eventos relevantes;
- Y no incluye el token propietario de sesión ni secretos de configuración.

