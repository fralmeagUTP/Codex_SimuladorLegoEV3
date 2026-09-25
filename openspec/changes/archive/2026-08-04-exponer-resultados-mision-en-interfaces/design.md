# Diseño: resultados de misión

## Contrato

Las interfaces reciben un evento `mission_result` con `event_version: 1`,
`outcome`, `mission` y `result`. Los valores permitidos de `outcome` son
`finished`, `cancelled`, `error` y `timed_out`.

El campo `result` conserva el DTO exportable de `MissionResult`. Para una
cancelación, error o tiempo agotado se conserva la evidencia de los criterios,
pero `passed` es falso y la puntuación es cero: una ejecución interrumpida no
puede acreditar una misión.

## Flujo

1. Al cargar una misión, la interfaz activa la misión en `SimulationService`.
2. El servicio inicia una traza limpia y el adaptador incorpora snapshots del
   worker aislado a dicha traza.
3. El primer estado terminal evalúa una única vez los criterios declarativos.
4. Tkinter muestra el resultado en un diálogo y en el estado del editor; Web
   lo publica por SSE y lo mantiene visible en el panel de telemetría.

No se altera el catálogo, la física ni los scripts de misión.
