## MODIFIED Requirements

### Requirement: Las sesiones Web anónimas deben resistir abuso básico

La aplicación MUST conservar sesiones anónimas autorizadas por token de
propietario, sin introducir autenticación de usuarios. MUST limitar la creación
de sesiones y comandos costosos por cliente, además de los límites globales.

#### Scenario: Un cliente excede su cuota de creación

- **WHEN** una dirección cliente supera la cuota configurada de creación
- **THEN** el servidor devuelve `429` con `Retry-After`
- **AND** no crea una sesión ni un worker adicional

#### Scenario: Un token ajeno accede a una sesión

- **WHEN** un cliente presenta un token que no es propietario de la sesión
- **THEN** el servidor rechaza la solicitud con `403` o `404`
- **AND** no revela datos de la sesión

### Requirement: Los comandos mutables deben validar el contexto de navegador

Las rutas mutables MUST rechazar una solicitud de navegador de origen cruzado,
salvo cuando se use un mecanismo operativo explícitamente configurado.

#### Scenario: Solicitud mutante de origen no permitido

- **WHEN** una solicitud `POST`, `DELETE` o equivalente llega con `Origin`
  distinto al origen configurado
- **THEN** el servidor responde `403`
- **AND** no cambia la sesión ni el mundo
