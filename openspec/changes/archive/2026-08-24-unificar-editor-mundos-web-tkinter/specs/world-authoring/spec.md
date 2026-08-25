## ADDED Requirements

### Requirement: Experiencia de editor de mundos unificada

Web y Tkinter MUST exponer el mismo flujo de autoría sobre `WorldEditorSession`:
archivo, edición, simulación, biblioteca, lienzo, inspector, capas, validación
y estado. Las diferencias de widget nativo no DEBEN cambiar una operación,
validación, activo, unidad ni resultado persistido.

#### Scenario: Crear y simular el mismo mundo desde ambas interfaces

- DADO un mundo nuevo y la misma selección de assets;
- CUANDO una persona lo crea, valida, guarda y prueba desde Web o Tkinter;
- ENTONCES el JSON persistido, sus validaciones y la pose inicial aplicada al
  simulador DEBEN ser equivalentes;
- Y la otra interfaz DEBE abrirlo y permitir continuar su edición.

### Requirement: Catálogo de biblioteca y activos común

El editor MUST usar el catálogo canónico para categorías, nombres localizados,
tooltips, iconos, imágenes, reglas y alias. Web y Tkinter MUST mostrar la
misma variante semántica de cada activo incluido.

#### Scenario: Obstáculo actualizado disponible en ambas interfaces

- DADO un asset de obstáculo del catálogo actual;
- CUANDO se abre la Biblioteca en Web y Tkinter;
- ENTONCES se muestra bajo la misma categoría y nombre;
- Y ambas interfaces resuelven el mismo hash o variante declarada.

### Requirement: Composición de autoría estable y accesible

El Editor de Mundos MUST mantener acciones agrupadas, Biblioteca, Lienzo,
Inspector, Capas y estado de validación en una jerarquía equivalente. Ante una
resolución reducida DEBE usar paneles colapsables o scroll interno antes de
recortar contenido crítico.

#### Scenario: Editor a 1024×768

- DADO el editor abierto a 1024×768;
- CUANDO el usuario navega por barra, Biblioteca, lienzo e Inspector con Tab;
- ENTONCES el foco visible sigue un orden coherente;
- Y los controles conservan nombre, acceso y contraste suficiente.
