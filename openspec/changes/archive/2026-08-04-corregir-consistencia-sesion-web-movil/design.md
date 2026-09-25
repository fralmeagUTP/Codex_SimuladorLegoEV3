# Diseño: consistencia de sesión Web y diseño móvil

## Decisiones

1. `SimulationSession` es la fuente de verdad de cada snapshot. Todo snapshot
   incluirá `snapshot_generation` y el estado de sesión que representa.
2. Un reinicio abre una nueva generación y activa una barrera temporal: los
   callbacks de parada, reset y snapshots pendientes no pueden publicar datos
   de la ejecución anterior.
3. El worker emitirá el snapshot terminal antes de `finished`, `timed_out` o
   `error`. El adaptador de sesión publicará asimismo un snapshot sin
   throttling al transicionar a estado terminal.
4. La UI rechaza generaciones antiguas y ticks decrecientes dentro de una misma
   generación. Tras reset debe aceptar el snapshot inicial aun cuando su tick
   sea menor que el de la generación precedente.
5. El canvas tendrá un ancho máximo igual al contenedor y la barra de mapa hará
   wrap en móvil, preservando botones visibles y operables.

## Flujo de reinicio

1. Marcar la sesión como `resetting` y bloquear callbacks intermedios.
2. Drenar/invalidar eventos de worker de la generación previa.
3. Reiniciar motor y worker.
4. Borrar snapshot, errores, estado de depuración, script y resultado de misión.
5. Crear y publicar el único snapshot inicial con estado `created`.
6. Desbloquear callbacks para la nueva generación.

## Verificación

- E2E Web para finalización, error, cancelación y reset.
- Prueba de contrato de `SimulationSession` que comprueba estado y snapshot
  inicial completos.
- E2E responsive en 1920×1080, 1280×800, 1024×768 y 390×844.
- Validación manual visible en Chrome o Edge con DevTools y capturas.
