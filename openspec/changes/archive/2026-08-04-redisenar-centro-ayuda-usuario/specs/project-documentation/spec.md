## ADDED Requirements

### Requirement: Documentación separada por audiencia

La documentación MUST separar las guías de uso orientadas a estudiantes y
docentes de la documentación técnica de instalación, operación, sesiones y
despliegue, conservando enlaces cruzados solo cuando sean necesarios.

#### Scenario: Usuario final consulta la ayuda

- **WHEN** un estudiante o docente abre la ayuda desde la aplicación
- **THEN** recibe instrucciones de interfaz y tareas sin requerir terminal,
  URL fija de despliegue ni conocimiento de la arquitectura interna.

#### Scenario: Personal técnico requiere operación

- **WHEN** una persona necesita instalar, desplegar o diagnosticar el servicio
- **THEN** puede acceder a la guía técnica actualizada desde una referencia
  explícita y separada de las rutas de aprendizaje.
