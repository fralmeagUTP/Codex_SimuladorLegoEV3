# Especificación: motor de simulación

## Propósito

Avanzar una simulación EV3 2D determinista y exponer un snapshot coherente a las capas de aplicación e interfaz.

## Requisitos

### Requisito: Actualización con paso fijo

El sistema DEBERÁ avanzar el estado mediante `SimulationEngine.update(dt)`. El paso nominal predeterminado DEBERÁ ser 0,02 segundos, equivalente a 50 Hz. El motor DEBERÁ procesar comandos, actualizar actuadores y drivebase, actualizar la pose, resolver colisiones, actualizar sensores y brick, avanzar el tiempo simulado y publicar un snapshot en cada actualización.

#### Escenario: Actualización manual determinista

- DADO un motor en estado inicial conocido
- CUANDO un llamador invoca repetidamente `update(0.02)` con los mismos comandos en cola
- ENTONCES el motor DEBERÁ producir el mismo estado de modelo y snapshot resultante
- Y el tiempo simulado DEBERÁ avanzar 0,02 segundos por actualización exitosa.

### Requisito: Cinemática de tracción diferencial

El sistema DEBERÁ modelar traslación y orientación del robot a partir de la velocidad lineal y angular del drivebase. El diámetro de rueda y la distancia entre ejes DEBERÁN ser configurables en milímetros. Los encoders asociados al drivebase DEBERÁN ser consistentes con el movimiento simulado de las ruedas.

#### Escenario: Movimiento recto

- DADO un robot detenido en espacio libre
- CUANDO finaliza un comando recto del drivebase
- ENTONCES el robot DEBERÁ cambiar su pose por la distancia con signo solicitada dentro de la tolerancia del modelo
- Y el drivebase DEBERÁ volver a un estado inactivo.

#### Escenario: Giro sobre el eje

- DADO un robot detenido en espacio libre
- CUANDO finaliza un comando de giro del drivebase
- ENTONCES la orientación DEBERÁ cambiar por el ángulo con signo solicitado dentro de la tolerancia del modelo.

### Requisito: Colisiones y límites del mundo

El sistema DEBERÁ impedir que un robot con radio configurado entre a obstáculos o salga de los límites del mundo. El estado de colisión DEBERÁ exponerse mediante snapshots.

#### Escenario: Movimiento hacia un muro

- DADO un robot moviéndose hacia un obstáculo
- CUANDO la siguiente pose se solaparía con el obstáculo
- ENTONCES el motor DEBERÁ bloquear el movimiento inválido
- Y el snapshot DEBERÁ indicar colisión.

### Requisito: Snapshots de estado

El sistema DEBERÁ exponer un snapshot serializable con tiempo de simulación, pose, estado de motores, sensores, brick, colisiones y telemetría requerida por las interfaces.

#### Escenario: La UI lee el estado actual

- DADO que el motor completó una o más actualizaciones
- CUANDO la capa de aplicación solicita su snapshot
- ENTONCES DEBERÁ recibir una representación coherente del último tick completado.

### Requisito: Dispositivos virtuales del brick

El sistema DEBERÁ actualizar LED, buffer LCD, botones y estado del altavoz como parte del paso de simulación. Un evento de altavoz DEBERÁ mantenerse observable durante su duración simulada configurada salvo reinicio o parada explícita.

#### Escenario: Beep activo

- DADO que un script solicita un beep con frecuencia, duración y volumen
- CUANDO el tiempo simulado aún es inferior a la duración solicitada
- ENTONCES los snapshots DEBERÁN informar esa configuración de altavoz como activa.

## Notas de compatibilidad actuales

- El modelo es cinemático y no un motor completo de física de cuerpos rígidos.
- La colisión es un bloqueo geométrico; no simula masa, torque, rebote, deslizamiento por fricción ni descarga de batería.
- La exactitud física DEBERÁ tratarse como aproximación educativa hasta contar con una suite de calibración y conformidad con tolerancias medidas.
