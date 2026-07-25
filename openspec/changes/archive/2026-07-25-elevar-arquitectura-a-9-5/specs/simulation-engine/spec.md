## ADDED Requirements

### Requirement: Puertos de aplicación
El motor MUST cumplir este requisito.

#### Scenario: acceso mediante puerto público

- DADO un adaptador de interfaz,
- CUANDO solicita una operación de simulación,
- ENTONCES MUST usar un puerto de aplicación documentado.

El motor DEBERÁ exponerse mediante puertos públicos de simulación, mundo y
telemetría. Las UI y rutas API NO DEBERÁN depender de atributos privados.
