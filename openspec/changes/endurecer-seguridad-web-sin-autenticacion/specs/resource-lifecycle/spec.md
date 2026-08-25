## ADDED Requirements

### Requirement: Los workers deben liberarse de forma verificable

La aplicación MUST registrar el ciclo de vida de cada worker propio y MUST
detener, esperar y comprobar su salida al cerrar una sesión, expirar por
inactividad o finalizar la aplicación. Si la salida no ocurre dentro del tiempo
configurado, MUST aplicar una terminación controlada y registrar el incidente
sin secretos.

#### Scenario: Cierre normal de una sesión

- **WHEN** una sesión Web o de escritorio se cierra normalmente
- **THEN** su worker y sus colas se liberan antes de eliminar la sesión
- **AND** las métricas de workers activos disminuyen de forma coherente

#### Scenario: Apagado con worker no cooperativo

- **WHEN** un worker no responde al cierre dentro del tiempo configurado
- **THEN** la aplicación lo termina de forma controlada
- **AND** deja una evidencia diagnóstica sin rutas temporales ni secretos

### Requirement: Los temporales propios deben limpiarse de forma segura

La aplicación MUST borrar archivos temporales propios al terminar la operación
que los creó, incluso si ocurre un error. MUST realizar un barrido de inicio o
mantenimiento limitado a recursos identificados como propios y expirados.

#### Scenario: Carga de mundo JSON

- **WHEN** se carga un mundo JSON por la API o una ruta interna temporal
- **THEN** el archivo temporal se elimina en un bloque de limpieza garantizado
- **AND** no permanece después de una carga exitosa o fallida

#### Scenario: Residuo temporal ajeno

- **WHEN** el barrido encuentra un archivo o proceso sin marca de propiedad EV3
- **THEN** no lo elimina ni lo termina

### Requirement: Las trazas deben tener memoria acotada

La aplicación MUST limitar el número o presupuesto de memoria de snapshots por
traza. Cuando alcance el límite, MUST conservar el comportamiento de simulación
y señalar que la exportación fue truncada.

#### Scenario: Traza extensa

- **WHEN** una simulación activa trazas por encima de la capacidad configurada
- **THEN** la memoria usada por la traza permanece acotada
- **AND** el resultado exportado informa el truncamiento

### Requirement: La persistencia de preferencias debe ser resistente a interrupciones

La aplicación de escritorio MUST escribir preferencias mediante un temporal y
reemplazo atómico. MUST recuperar valores seguros por defecto si una escritura
previa quedó incompleta.

#### Scenario: Interrupción durante guardado de preferencias

- **WHEN** se interrumpe la escritura de preferencias antes del reemplazo
- **THEN** el archivo previamente válido se conserva
- **AND** el siguiente arranque no falla
