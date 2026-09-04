## ADDED Requirements

### Requirement: Cancelación de depuración recuperable

La sesión Web MUST aplicar a una ejecución iniciada en depuración la misma
cancelación versionada que a una ejecución normal. Una solicitud de Detener y
reiniciar DEBERÁ terminar en un snapshot inicial `created`, aun cuando el worker
de depuración responda tarde o no responda.

#### Scenario: Detener una depuración activa

- DADO un script iniciado con Depurar y estado `running`
- CUANDO el usuario selecciona Detener y reiniciar
- ENTONCES la UI DEBERÁ quedar operable y el estado DEBERÁ ser `created` en un
  máximo de tres segundos
- Y eventos de la generación cancelada NO DEBERÁN restaurar `running`.

### Requirement: Error terminal coherente

La sesión Web MUST publicar el snapshot final y el estado `error` cuando un
script falla en tiempo de ejecución. No DEBERÁ conservar `running` ni datos de
una ejecución anterior como estado terminal.

#### Scenario: Excepción de división por cero

- DADO un script válido que evalúa `1 / 0`
- CUANDO el runtime produce la excepción
- ENTONCES la interfaz DEBERÁ mostrar `error`, el mensaje asociado y el snapshot
  de esa generación
- Y Ejecutar y los menús permitidos DEBERÁN quedar disponibles.

### Requirement: Recuperación de controles desde sesión

La UI Web MUST derivar los controles de ejecución del estado autoritativo al
cargar o recuperar una sesión.

#### Scenario: Recarga después de finalizar

- DADA una sesión que terminó correctamente
- CUANDO el navegador se recarga
- ENTONCES Detener y reiniciar NO DEBERÁ quedar habilitado si no hay operación
  cancelable en curso.
