## ADDED Requirements

### Requirement: Despliegue Web operable en un VPS

La distribución MUST proporcionar un perfil de despliegue reproducible para un
VPS Linux con proxy TLS, proceso Web no privilegiado, temporales privados y
endpoints operativos protegidos. La configuración pública MUST NOT contener
secretos ni publicar directamente el puerto de la aplicación.

#### Scenario: Inicio de producción seguro

- **WHEN** el servicio se inicia con `EV3_WEB_APP_ENV=production`
- **THEN** valida secretos, cookies HTTPS, HSTS y límites antes de aceptar solicitudes
- **AND** expone la aplicación al proxy solo por una interfaz privada

#### Scenario: Consulta operativa autorizada

- **WHEN** el monitor autorizado consulta salud o métricas
- **THEN** recibe el estado necesario para operar el servicio
- **AND** un cliente público sin autorización no recibe PIDs, rutas, tokens ni configuración interna
