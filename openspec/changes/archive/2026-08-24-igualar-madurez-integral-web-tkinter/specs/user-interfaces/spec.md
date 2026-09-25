## ADDED Requirements

### Requirement: Sistema de diseño y navegación compartidos

Web y Tkinter MUST consumir tokens y catálogos comunes para nombre de
acción, jerarquía, estado, foco, color semántico, atajo y recuperación. Podrán
diferir los widgets nativos, pero no la intención ni la accesibilidad.

#### Scenario: Control de ejecución en tema oscuro

- DADO el control equivalente de ejecución en ambas interfaces;
- CUANDO una sesión cambia a ejecución, pausa, error o estado deshabilitado en
  tema oscuro;
- ENTONCES el usuario distingue el estado con contraste suficiente y foco
  visible;
- Y el control produce la misma transición de sesión.

### Requirement: Ayuda contextual equivalente

Las dos interfaces MUST presentar la misma ayuda por tarea, objetivo,
resultado esperado y recuperación para operaciones aplicables.

#### Scenario: Usuario recibe un error recuperable

- DADO un error de script, mundo, límite de tiempo o depuración;
- CUANDO la interfaz muestra el error;
- ENTONCES ofrece la guía contextual equivalente;
- Y la guía no recomienda una acción ausente de la plataforma actual.

### Requirement: Catálogo visual único de assets

Web y Tkinter MUST renderizar las mismas figuras, imágenes, sprites,
texturas e iconos definidos por un catálogo versionado común. Un recurso solo
podrá diferir por escalado, antialiasing o mecanismo de empaquetado documentado,
no por contenido, versión o significado.

#### Scenario: Asset actualizado para un obstáculo

- DADO un `asset_id` de obstáculo actualizado;
- CUANDO se publica una versión del producto;
- ENTONCES Web y Tkinter muestran la misma figura y variante del catálogo;
- Y las pruebas comprueban el hash o la procedencia de ambos recursos.

#### Scenario: Asset ausente en una distribución

- DADO un asset requerido por un mundo, ayuda o pantalla de inicio;
- CUANDO se construye Web, ejecutable, ZIP o instalador;
- ENTONCES la validación falla si el recurso no está presente o no corresponde
  a la versión declarada del catálogo.
