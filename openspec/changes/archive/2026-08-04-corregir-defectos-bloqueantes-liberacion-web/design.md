# Diseño: corrección de bloqueantes Web

## Principios

1. `SimulationSession` conserva la fuente de verdad: cada transición terminal
   publica el snapshot, estado, error y generación de la misma ejecución.
2. Depuración y ejecución normal usan el mismo protocolo de cancelación. Un
   reinicio invalida eventos, temporizadores y callbacks del worker anterior.
3. El runtime conserva el tiempo simulado como referencia. La UI interpola solo
   la presentación visual; no puede retrasar el fin observable más allá de un
   margen definido ni adelantar estados autoritativos.
4. El editor de mundos trata la colocación como una operación atómica: una
   respuesta de worker fallida no modifica el estado local ni habilita Guardar
   como si el modelo no es válido.

## Flujos corregidos

### Depuración y cancelación

`stop_and_reset` incrementa la generación, solicita cancelación al worker y
espera un acuse con límite. Tanto si el acuse llega como si expira, libera los
controles, descarta eventos antiguos y publica el snapshot inicial `created`.
El cierre tardío del worker no puede restaurar `running`.

### Error de script

Toda excepción no controlada se convierte en un evento `error` de la generación
activa. Antes de emitirlo se publica un snapshot terminal consistente. La UI
limpia el estado de ejecución, muestra el error y vuelve a habilitar Ejecutar y
los menús permitidos.

### Mundo y assets

La operación de colocar asset debe usar el worker/sesión activos y devolver un
DTO validado. El cliente solo actualiza canvas, selección y modelo después de
recibir éxito. Guardar como abre su diálogo cuando el mundo es válido; errores
conservan el editor operativo y exponen un mensaje accionable.

### Cadencia y trazas

Se instrumenta el desfase pared/simulación. Los waits y movimientos deben
progresar a velocidad configurada, sin acumulación de snapshots que duplique el
tiempo de pared. `Avanzar un tick` invoca una transición de motor observable y
espera el snapshot con tick mayor; si no es posible fuera de ejecución, el
comando queda deshabilitado con explicación y no anuncia éxito.

### Recuperación de UI

Al cargar o recuperar una sesión, la UI deriva todos los controles del estado
autoritativo recibido. En `ready`, `created`, `finished`, `error`, `stopped` y
`timed_out`, Detener y reiniciar no queda habilitado salvo que exista una
operación cancelable en curso.

## Umbrales de aceptación

- Cancelación de Debug: UI operable y `created` en ≤ 3 s de pared.
- Error de runtime: estado `error` coherente y sin controles bloqueados en ≤ 2 s.
- Ritmo: para `wait(1000)`, avance y giro de referencia, la relación
  pared/`sim_time_s` estará entre 0,85 y 1,25 en el entorno de prueba, excluyendo
  el arranque de servidor; el radar se evalúa con una tolerancia documentada de
  1,35 por carga gráfica.
- Tick: éxito solo si se observa incremento de tick y snapshot actualizado.

## Evidencia

Se almacenarán capturas, consola y HAR por cada FAIL/BLOCKED bajo un directorio
fechado. La decisión se basará en Chrome o Edge visible, además de la suite
automatizada aislada.
