## ADDED Requirements

### Requirement: Diagnóstico exportable seguro

El sistema MUST proporcionar a las interfaces un diagnóstico serializable y
seguro de la sesión actual que incluya estado operativo, métricas permitidas y
correlación disponible, sin código de programa, credenciales ni información de
sesiones ajenas.

#### Scenario: Diagnóstico de una sesión activa

- **WHEN** una interfaz solicita el diagnóstico de su sesión activa
- **THEN** recibe una estructura JSON estable, asociada únicamente a esa sesión
- **AND** la estructura se puede mostrar y exportar sin consultar atributos
  privados del motor o del worker.
