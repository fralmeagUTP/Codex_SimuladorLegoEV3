## ADDED Requirements

### Requirement: Campaña HTTP local de aislamiento concurrente

El proyecto SHALL proporcionar una campaña reproducible que inicie una instancia
Web local aislada y simule usuarios HTTP concurrentes con sesiones separadas.
La campaña SHALL comprobar tokens únicos, scripts aislados, acceso cruzado
denegado, límites de capacidad, métricas y cierre de recursos.

#### Scenario: Usuarios concurrentes dentro de capacidad

- **WHEN** una campaña crea varias sesiones en paralelo hasta el límite configurado
- **THEN** cada usuario recibe un ID y token distintos
- **AND** cada script queda asociado solo con la sesión de su propietario
- **AND** las métricas reflejan la cantidad activa antes del cierre

#### Scenario: Capacidad excedida y limpieza

- **WHEN** la campaña intenta crear una sesión adicional sobre el máximo activo
- **THEN** la API devuelve `429`
- **AND** tras cerrar las sesiones creadas el contador de sesiones activas vuelve a cero
