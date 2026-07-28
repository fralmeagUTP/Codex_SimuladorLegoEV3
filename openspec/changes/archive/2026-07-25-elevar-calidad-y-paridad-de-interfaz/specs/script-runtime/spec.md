## ADDED Requirements

### Requirement: Protocolo IPC versionado del worker
El runtime MUST cumplir este requisito.

El runtime aislado DEBERÁ intercambiar comandos y eventos mediante mensajes
serializables con `protocol_version`, `session_id`, secuencia monotónica y
correlación `command_id`. DEBERÁ soportar inicialización, carga, inicio, pausa,
reanudación, parada, reinicio, depuración, mundo, snapshots, errores y cierre.

#### Scenario: Cancelación no cooperativa

- DADO un worker que no confirma `stop` dentro de su presupuesto
- CUANDO el proceso principal agota la espera
- ENTONCES DEBERÁ terminar el worker
- Y publicar `stopped` o `timed_out` conservando el último snapshot válido.

### Requirement: Aislamiento de ejecución y política de watchdog
El runtime MUST cumplir este requisito.

El runtime DEBERÁ ejecutar programas de usuario en un worker aislado del proceso
de interfaz/API. El worker DEBERÁ aplicar límite positivo de tiempo en producción,
límites de CPU y memoria, filesystem temporal restringido, red deshabilitada y
terminación forzada. El filtro de imports del runtime DEBERÁ mantenerse como
defensa adicional y no como única frontera de seguridad.

#### Scenario: Programa no cooperativo

- DADO un programa que no responde al evento de parada
- CUANDO supera el límite de recursos o se solicita detenerlo
- ENTONCES el proceso principal DEBERÁ terminar el worker de forma segura
- Y la sesión DEBERÁ informar estado `timed_out` o `stopped` sin afectar otras sesiones.
