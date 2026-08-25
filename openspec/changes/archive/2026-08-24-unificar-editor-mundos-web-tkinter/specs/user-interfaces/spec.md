## ADDED Requirements

### Requirement: Lenguaje y acciones equivalentes en el Editor de Mundos

Las dos interfaces MUST usar etiquetas, orden, estado de habilitación y atajos
equivalentes para las acciones Archivo, Edición y Simulación del editor. No
DEBEN mezclar nombres en inglés y español para una misma acción visible.

#### Scenario: Seleccionar y eliminar un objeto

- DADO el Editor de Mundos abierto en cualquiera de las interfaces;
- CUANDO el usuario consulta las acciones de selección y eliminación;
- ENTONCES encuentra `Seleccionar` y `Eliminar` con ayuda accesible;
- Y ambas acciones producen la misma transición de selección o modelo.
