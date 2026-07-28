## ADDED Requirements

### Requirement: Matriz de conformidad Pybricks
La API MUST cumplir este requisito.

El proyecto DEBERÁ mantener una matriz versionada que clasifique cada clase y
método Pybricks como completo, aproximado, parcial o no soportado. Cada método
declarado completo o aproximado DEBERÁ tener pruebas de conformidad.

#### Scenario: Consulta de método soportado

- DADO un usuario o mantenedor que consulta un método Pybricks
- CUANDO revisa la matriz de conformidad
- ENTONCES DEBERÁ poder identificar su estado, limitaciones y pruebas asociadas.

### Requirement: Semántica centralizada de movimiento
La API MUST cumplir este requisito.

El dominio DEBERÁ implementar una semántica única para `COAST`, `BRAKE`, `HOLD`,
curvas y comandos bloqueantes. La API virtual NO DEBERÁ modificar atributos
privados de modelos de dominio.

#### Scenario: Modo de parada HOLD

- DADO un motor o drivebase que termina una maniobra con `Stop.HOLD`
- CUANDO una perturbación simulada intenta modificar su posición
- ENTONCES el modelo DEBERÁ aplicar la semántica HOLD definida por el perfil activo.
