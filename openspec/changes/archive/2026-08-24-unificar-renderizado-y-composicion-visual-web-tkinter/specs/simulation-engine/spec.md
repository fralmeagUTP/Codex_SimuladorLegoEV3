## ADDED Requirements

### Requirement: Metadatos renderizables de placements

El modelo de mundo y sus adaptadores MUST conservar para cada placement el
identificador de asset, posición, orientación, capa y dimensiones lógicas
necesarias para que cualquier interfaz aplique la misma geometría física. El
motor NO DEBERÁ introducir compensaciones visuales específicas de Web o
Tkinter.

#### Scenario: Pose inicial del robot de un mundo editor

- DADO un `editor_spec` con un placement de robot válido
- CUANDO el mundo se aplica a una sesión
- ENTONCES el snapshot inicial informa la pose convertida con el contrato
  mm/píxel del mundo
- Y los metadatos del placement permiten dibujar la misma figura en ambas UI.
