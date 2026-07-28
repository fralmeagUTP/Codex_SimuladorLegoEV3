## ADDED Requirements

### Requirement: Perfiles de fidelidad configurables
El motor MUST cumplir este requisito.

El motor DEBERÁ admitir perfiles `ideal`, `realista` y `calibrado`. El perfil
ideal conservará comportamiento determinista educativo; los otros perfiles
podrán aplicar parámetros configurables de latencia, ruido, deriva, rangos,
fricción y limitaciones de movimiento.

#### Scenario: Clase introductoria en modo ideal

- DADO un mundo y programa de ejemplo
- CUANDO se ejecuta con perfil `ideal`
- ENTONCES el resultado DEBERÁ ser repetible para la misma entrada y semilla.

#### Scenario: Sensor realista

- DADO un perfil `realista` con ruido y latencia configurados
- CUANDO el motor actualiza un sensor
- ENTONCES el snapshot DEBERÁ reflejar los parámetros de ese perfil
- Y la traza DEBERÁ registrar la semilla y configuración usada.

### Requirement: Trazas reproducibles
El motor MUST cumplir este requisito.

El motor DEBERÁ registrar comandos, snapshots, errores y eventos en un formato
exportable JSON/CSV. Una traza DEBERÁ poder reproducirse para inspección y
comparación de ejecuciones.

#### Scenario: Exportar ejecución

- DADA una sesión que ejecutó un programa
- CUANDO el usuario exporta su traza
- ENTONCES el sistema DEBERÁ producir un archivo con secuencia, tiempo simulado,
  entradas y estados suficientes para reproducirla.
