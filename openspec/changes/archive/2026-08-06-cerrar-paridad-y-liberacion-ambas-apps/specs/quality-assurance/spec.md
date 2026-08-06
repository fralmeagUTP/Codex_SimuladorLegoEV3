## ADDED Requirements

### Requirement: Campaña integral para ambas interfaces

La campaña de calidad MUST ejercitar en interfaz real el catálogo de menús,
ejemplos, mundos, escenarios, misiones, controles, depuración y errores en Web
y Tkinter, siempre que el elemento sea aplicable.

#### Scenario: Ejecución de campaña integral

- **DADO** el catálogo de capacidades de una versión candidata;
- **CUANDO** se ejecute la campaña en navegador y escritorio activos;
- **ENTONCES** cada elemento tendrá un resultado `PASS`, `FAIL`, `BLOCKED` o
  `N/A` junto con evidencia y entorno;
- **Y** ningún elemento no ejercitado será comunicado como aprobado.

### Requirement: Calidad visual y de accesibilidad antes de liberar

Web y Tkinter MUST comprobar legibilidad, foco, teclado, contraste, temas,
redimensionamiento y ausencia de recorte en los tamaños soportados.

#### Scenario: Tema y tamaño soportados

- **DADO** una resolución y un tema soportados;
- **CUANDO** se recorra la pantalla de simulación, los diálogos y el editor de
  mundos;
- **ENTONCES** los controles críticos serán legibles, enfocables y operables;
- **Y** cualquier recorte o contraste insuficiente se registrará como defecto.
