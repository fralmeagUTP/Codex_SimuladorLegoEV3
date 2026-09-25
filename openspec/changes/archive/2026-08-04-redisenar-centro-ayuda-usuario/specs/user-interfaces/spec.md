## ADDED Requirements

### Requirement: Centro de ayuda orientado a tareas

Las interfaces Web y Tkinter MUST ofrecer un Centro de ayuda con rutas de
aprendizaje por tarea, categorías navegables, resultados esperados y pasos de
recuperación, usando el nombre visible `Simulador EV3 Pybricks`.

#### Scenario: Usuario inicia su primera simulación

- **WHEN** una persona abre el Centro de ayuda y selecciona `Mi primera simulación`
- **THEN** la interfaz muestra prerrequisitos, pasos ordenados, resultado
  esperado, recuperación y una acción para abrir la simulación
- **AND** la acción no anuncia ni invoca una capacidad no disponible.

#### Scenario: Paridad de guía entre interfaces

- **WHEN** una guía está disponible en Web y Tkinter
- **THEN** ambas presentan el mismo identificador, objetivo, pasos, resultado y
  recuperación
- **AND** solo pueden diferir los controles propios de la plataforma.

### Requirement: Navegación, búsqueda y accesibilidad

El Centro de ayuda MUST permitir navegar por categorías y buscar por título,
resumen, etiquetas y pasos, con uso completo de teclado y contraste válido en
los temas claro y oscuro.

#### Scenario: Búsqueda sin resultados

- **WHEN** el usuario busca un término que no coincide con ninguna guía
- **THEN** la interfaz informa que no hay resultados y conserva un camino para
  limpiar la búsqueda o volver a las categorías.

#### Scenario: Uso en Web móvil

- **WHEN** el Centro de ayuda se muestra en un viewport de 390×844
- **THEN** el índice se puede abrir y cerrar sin provocar scroll horizontal
- **AND** las acciones y el contenido siguen siendo utilizables mediante toque
  y teclado.

### Requirement: Ayuda contextual para operaciones críticas

Las interfaces MUST ofrecer acceso a una guía contextual desde los controles y
errores de ejecución, reinicio, límites de tiempo, ubicación, haces, trazas,
depuración, telemetría y validación de mundos.

#### Scenario: Error con recuperación disponible

- **WHEN** un error de script o validación tiene una guía de recuperación
  asociada
- **THEN** el usuario puede abrir esa guía desde el mensaje o control contextual
- **AND** la ayuda describe una solución verificable para el caso.
