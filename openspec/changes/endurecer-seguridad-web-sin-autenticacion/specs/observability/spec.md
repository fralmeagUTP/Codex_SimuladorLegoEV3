## MODIFIED Requirements

### Requirement: La observabilidad pública no debe revelar datos operativos sensibles

La aplicación MUST exponer métricas y salud según una política configurable. En
modo público, las respuestas MUST NOT incluir PID, rutas locales, tokens,
configuración interna ni errores de infraestructura.

#### Scenario: Consulta pública de salud restringida

- **WHEN** la política operativa es `local` o `token` y un cliente no autorizado
  consulta `/healthz`, `/metrics` u `/operations`
- **THEN** el servidor devuelve una respuesta de acceso denegado

#### Scenario: Registro de solicitud de sesión

- **WHEN** se registra una solicitud que contiene un token de propietario
- **THEN** el registro conserva solo identificadores correlacionables seguros
- **AND** no incluye el token ni el contenido completo del script
