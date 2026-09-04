## MODIFIED Requirements

### Requirement: Límites de sesión y ejecución configurables por entorno

La aplicación Web MUST obtener sus límites de sesión activa, simulaciones
concurrentes y duración máxima desde configuración `EV3_WEB_*`. El perfil de
producción inicial para un VPS de 2 vCPU y 8 GB MUST configurar como máximo 20
sesiones activas, 4 simulaciones en ejecución y 120 segundos por script.

#### Scenario: Capacidad inicial del VPS agotada

- **WHEN** existen cuatro simulaciones en ejecución y un cliente intenta iniciar una quinta
- **THEN** el servidor rechaza la nueva ejecución según el contrato de capacidad
- **AND** no crea un worker adicional
- **AND** las sesiones ya en curso conservan su aislamiento

#### Scenario: Cambio de capacidad sustentado

- **WHEN** se propone un valor mayor de simulaciones concurrentes
- **THEN** el despliegue conserva evidencia de una prueba de carga y de consumo de recursos
- **AND** no se modifica el límite productivo únicamente por edición del cliente Web
