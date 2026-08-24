# Política de observabilidad Web y Tkinter

La observabilidad se expresa mediante el DTO versionado `ObservabilitySnapshot`.
Cada registro puede correlacionar `session_id`, `command_id` y `worker_id`, junto
con estado, tick, tiempo simulado y código de error. No incluye código fuente,
tokens de sesión, contraseñas, correos ni nombres de estudiantes.

## Retención y acceso

- Los diagnósticos operativos se conservan un máximo de 30 días en la operación
  del servidor; las exportaciones locales las controla el titular del equipo.
- El panel Web solo expone el diagnóstico de la sesión autorizada. Tkinter
  muestra/exporta únicamente su sesión local.
- Los identificadores permiten investigar una ejecución sin asociarla a una
  identidad personal.

## Correlación

Una ejecución, error, límite de tiempo, cancelación, recuperación de worker o
resultado de misión debe conservar los identificadores disponibles en sus
eventos. Los datos agregados de `/metrics` no contienen identificadores de
sesión.
