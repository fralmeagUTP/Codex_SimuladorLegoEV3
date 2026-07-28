# Diseño: arquitectura 9.5

## Sesión unificada

`SimulationSession` define comandos, eventos, snapshots, errores, depuración,
trazas y recuperación. Web y Tkinter consumen el mismo contrato; el worker es
la única ruta de scripts cuando el aislamiento está activo.

## Límites de capas

La aplicación coordina puertos de runtime, mundos y observabilidad. Las UI no
acceden a atributos privados de dominio. El editor de mundos no ejecuta scripts.

## Operación

Prometheus expone métricas de sesión/worker/tick; OpenTelemetry propaga
`session_id`, `command_id` y `worker_id`. El despliegue Linux usa contenedor sin
privilegios; Windows conserva la guía de aula local.
