## ADDED Requirements

### Requirement: Movimiento Web visualmente fluido

El canvas Web SHALL renderizar movimiento continuo mediante interpolación entre
snapshots compatibles y requestAnimationFrame, sin modificar los datos
autoritativos de telemetría.

#### Scenario: Giro continuo

- **WHEN** el robot recibe snapshots consecutivos de un giro
- **THEN** el robot y sus haces se dibujan con orientaciones intermedias
- **AND** la telemetría conserva el último tick recibido sin valores inventados

#### Scenario: Reinicio o cambio de mundo

- **WHEN** el usuario detiene y reinicia o carga otro mundo
- **THEN** se descarta el buffer de interpolación y la vista muestra la pose
  inicial correspondiente sin trazas ni movimiento residual
