# Especificación: motor de simulación

## Purpose

Avanzar una simulación EV3 2D determinista y exponer un snapshot coherente a las capas de aplicación e interfaz.
## Requirements
### Requirement: Actualización con paso fijo
El motor MUST cumplir este requisito.

El sistema DEBERÁ avanzar el estado mediante `SimulationEngine.update(dt)`. El paso nominal predeterminado DEBERÁ ser 0,02 segundos, equivalente a 50 Hz. El motor DEBERÁ procesar comandos, actualizar actuadores y drivebase, actualizar la pose, resolver colisiones, actualizar sensores y brick, avanzar el tiempo simulado y publicar un snapshot en cada actualización.

#### Scenario: Actualización manual determinista

- DADO un motor en estado inicial conocido
- CUANDO un llamador invoca repetidamente `update(0.02)` con los mismos comandos en cola
- ENTONCES el motor DEBERÁ producir el mismo estado de modelo y snapshot resultante
- Y el tiempo simulado DEBERÁ avanzar 0,02 segundos por actualización exitosa.

### Requirement: Cinemática de tracción diferencial
El motor MUST cumplir este requisito.

El sistema DEBERÁ modelar traslación y orientación del robot a partir de la velocidad lineal y angular del drivebase. El diámetro de rueda y la distancia entre ejes DEBERÁN ser configurables en milímetros. Los encoders asociados al drivebase DEBERÁN ser consistentes con el movimiento simulado de las ruedas.

#### Scenario: Movimiento recto

- DADO un robot detenido en espacio libre
- CUANDO finaliza un comando recto del drivebase
- ENTONCES el robot DEBERÁ cambiar su pose por la distancia con signo solicitada dentro de la tolerancia del modelo
- Y el drivebase DEBERÁ volver a un estado inactivo.

#### Scenario: Giro sobre el eje

- DADO un robot detenido en espacio libre
- CUANDO finaliza un comando de giro del drivebase
- ENTONCES la orientación DEBERÁ cambiar por el ángulo con signo solicitado dentro de la tolerancia del modelo.

### Requirement: Colisiones y límites del mundo
El motor MUST cumplir este requisito.

El sistema DEBERÁ impedir que un robot con radio configurado entre a obstáculos o salga de los límites del mundo. El estado de colisión DEBERÁ exponerse mediante snapshots.

#### Scenario: Movimiento hacia un muro

- DADO un robot moviéndose hacia un obstáculo
- CUANDO la siguiente pose se solaparía con el obstáculo
- ENTONCES el motor DEBERÁ bloquear el movimiento inválido
- Y el snapshot DEBERÁ indicar colisión.

### Requirement: Snapshots de estado
El motor MUST cumplir este requisito.

El sistema DEBERÁ exponer un snapshot serializable con tiempo de simulación, pose, estado de motores, sensores, brick, colisiones y telemetría requerida por las interfaces.

#### Scenario: La UI lee el estado actual

- DADO que el motor completó una o más actualizaciones
- CUANDO la capa de aplicación solicita su snapshot
- ENTONCES DEBERÁ recibir una representación coherente del último tick completado.

### Requirement: Dispositivos virtuales del brick
El motor MUST cumplir este requisito.

El sistema DEBERÁ actualizar LED, buffer LCD, botones y estado del altavoz como parte del paso de simulación. Un evento de altavoz DEBERÁ mantenerse observable durante su duración simulada configurada salvo reinicio o parada explícita.

#### Scenario: Beep activo

- DADO que un script solicita un beep con frecuencia, duración y volumen
- CUANDO el tiempo simulado aún es inferior a la duración solicitada
- ENTONCES los snapshots DEBERÁN informar esa configuración de altavoz como activa.

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

### Requirement: Puertos de aplicación
El motor MUST cumplir este requisito.

#### Scenario: acceso mediante puerto público

- DADO un adaptador de interfaz,
- CUANDO solicita una operación de simulación,
- ENTONCES MUST usar un puerto de aplicación documentado.

El motor DEBERÁ exponerse mediante puertos públicos de simulación, mundo y
telemetría. Las UI y rutas API NO DEBERÁN depender de atributos privados.

### Requirement: Metadatos renderizables de placements

El modelo de mundo y sus adaptadores MUST conservar para cada placement el
identificador de asset, posición, orientación, capa y dimensiones lógicas
necesarias para que cualquier interfaz aplique la misma geometría física. El
motor NO DEBERÁ introducir compensaciones visuales específicas de Web o
Tkinter.

#### Scenario: Pose inicial del robot de un mundo editor

- DADO un `editor_spec` con un placement de robot válido
- CUANDO el mundo se aplica a una sesión
- ENTONCES el snapshot inicial informa la pose convertida con el contrato
  mm/píxel del mundo
- Y los metadatos del placement permiten dibujar la misma figura en ambas UI.

## Notas de compatibilidad actuales

- El modelo es cinemático y no un motor completo de física de cuerpos rígidos.
- La colisión es un bloqueo geométrico; no simula masa, torque, rebote, deslizamiento por fricción ni descarga de batería.
- La exactitud física DEBERÁ tratarse como aproximación educativa hasta contar con una suite de calibración y conformidad con tolerancias medidas.
