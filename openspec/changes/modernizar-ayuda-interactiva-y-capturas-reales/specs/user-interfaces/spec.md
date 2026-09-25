## ADDED Requirements

### Requirement: Ayuda guiada por pasos y plataforma

El sistema SHALL presentar guías didácticas comunes en Web y Tkinter con
objetivo, nivel, tiempo estimado, precondiciones, pasos verificables,
resultado, recuperación y siguiente acción. Cada guía SHALL mostrar una
captura real de la plataforma correspondiente o una transcripción textual
equivalente cuando el recurso visual no esté disponible.

#### Scenario: Estudiante completa una primera simulación

- **WHEN** una persona abre la guía de primera simulación y marca un paso como
  realizado
- **THEN** la interfaz muestra el siguiente paso, conserva el avance local y
  ofrece el destino contextual correcto sin ejecutar código automáticamente.

#### Scenario: Recurso visual no disponible

- **WHEN** una captura no puede cargarse
- **THEN** la ayuda conserva la secuencia mediante texto alternativo,
  transcripción de anotaciones y acción de recuperación sin ocultar el paso.

### Requirement: Ayuda accesible y visualmente actualizada

El sistema SHALL mantener una ayuda navegable con teclado, contraste AA en los
dos temas y visuales canónicos que correspondan a la interfaz publicada.

#### Scenario: Persona navega con teclado en tema oscuro

- **WHEN** la persona usa Tab, Enter, Espacio o Escape dentro de una guía en
  tema oscuro
- **THEN** el foco es visible, el avance se puede operar y textos, acciones y
  anotaciones mantienen contraste legible.
