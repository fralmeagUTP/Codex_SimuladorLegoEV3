## ADDED Requirements

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
