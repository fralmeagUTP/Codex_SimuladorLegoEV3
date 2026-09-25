## ADDED Requirements

### Requirement: experiencia guiada de autoría visual

El Editor de Mundos MUST presentar las acciones de Archivo, Edición y
Simulación en grupos distinguibles. MUST ofrecer una biblioteca categorizada de
assets con nombre, tooltip y nombre accesible, y MUST mostrar una guía de
primeros pasos mientras el lienzo no tenga elementos. La interfaz NO DEBE
exponer identificadores internos como `asset_key` ni píxeles internos como la
unidad principal de edición.

#### Scenario: crear un primer mundo desde lienzo vacío

- **Dado** un usuario que abre un mundo vacío
- **Cuando** consulta el lienzo y selecciona un asset de la biblioteca
- **Entonces** DEBERÁ ver una guía de colocación antes de añadir elementos
- **Y** DEBERÁ poder identificar el asset por nombre y ayuda visible.

#### Scenario: editar una propiedad del dominio

- **Dado** un muro seleccionado en el lienzo
- **Cuando** el usuario abre el inspector
- **Entonces** DEBERÁ ver tipo, posición, tamaño y rotación con nombres y
  unidades comprensibles
- **Y** NO DEBERÁ requerir editar claves internas ni coordenadas en píxeles.

### Requirement: tamaño y capas del mundo

El Editor de Mundos MUST permitir definir Ancho y Alto en celdas, usar presets
de tamaño y mostrar una equivalencia física. MUST proporcionar una lista de
capas para seleccionar objetos superpuestos y controlar su visibilidad y
bloqueo. Los cambios de tamaño que descarten elementos DEBERÁN requerir
confirmación.

#### Scenario: seleccionar objetos superpuestos

- **Dado** un sensor y una zona superpuestos en el lienzo
- **Cuando** el usuario selecciona uno desde la lista de capas
- **Entonces** el elemento correspondiente DEBERÁ quedar seleccionado en el
  lienzo y sus propiedades DEBERÁN aparecer en el inspector.

#### Scenario: cambiar a un preset menor

- **Dado** un mundo que contiene elementos fuera de los límites de un preset
  menor
- **Cuando** el usuario selecciona dicho preset
- **Entonces** el editor DEBERÁ advertir el efecto potencial antes de aplicar
  un cambio que descarte elementos.

### Requirement: paridad funcional del editor

Las interfaces Web y Tkinter MUST ofrecer las mismas operaciones de creación,
edición, validación, persistencia y prueba de mundos. Pueden usar componentes
nativos distintos, pero DEBEN compartir categorías, unidades, validaciones y
resultado de la conversión al mundo físico.

#### Scenario: mundo creado en una interfaz

- **Dado** un mundo creado y guardado mediante el editor Web o Tkinter
- **Cuando** se abre y valida desde la otra interfaz
- **Entonces** DEBERÁ conservar assets, dimensiones, propiedades y pose inicial
- **Y** DEBERÁ poder aplicarse a una sesión de simulación.
