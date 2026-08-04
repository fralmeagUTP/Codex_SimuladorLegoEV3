# Especificación: creación de mundos

## Purpose

Crear, validar, persistir, cargar y aplicar mundos 2D utilizados por el simulador EV3.
## Requirements
### Requirement: Modelo de mundo físico
El modelo MUST cumplir este requisito.

Un mundo físico DEBERÁ contener dimensiones en milímetros, un modelo de superficie, obstáculos poligonales y balizas infrarrojas opcionales. DEBERÁ proporcionar ray casting para sensores de distancia y validación de límites para colisiones del robot.

#### Scenario: Rayo impacta el muro más cercano

- DADO un origen y dirección de rayo frente a múltiples obstáculos
- CUANDO el mundo ejecuta ray casting
- ENTONCES DEBERÁ devolver la intersección válida más cercana dentro del rango solicitado.

### Requirement: Datos de superficie y líneas
La superficie MUST cumplir este requisito.

La superficie DEBERÁ representar color y reflectancia por celda. DEBERÁ soportar construcción de líneas negras para escenarios de aprendizaje con sensor de color.

#### Scenario: Consulta sin celda sobrescrita

- DADA una coordenada de superficie sin sobrescritura explícita
- CUANDO el motor consulta esa coordenada
- ENTONCES DEBERÁ devolver el color y reflectancia predeterminados configurados.

### Requirement: Compatibilidad de persistencia JSON
El repositorio MUST cumplir este requisito.

El repositorio DEBERÁ guardar y cargar mundos físicos como JSON UTF-8 con versión de formato `1`. Las versiones no soportadas DEBERÁN rechazarse explícitamente.

#### Scenario: Recorrido completo de mundo

- DADO un mundo válido con celdas, obstáculos y balizas
- CUANDO se guarda y carga mediante `WorldRepository`
- ENTONCES el mundo restaurado DEBERÁ preservar su contenido físico serializable.

### Requirement: Validación visual de mundo
El editor MUST cumplir este requisito.

La capa de editor DEBERÁ validar los datos antes de aplicarlos a la simulación. La validación DEBERÁ cubrir integridad de esquema, assets soportados, límites, solapes, ubicación del robot y reglas de conexión requeridas.

#### Scenario: Colocación inválida solapada

- DADA una colocación que se solapa con un asset existente prohibido
- CUANDO se ejecuta la validación
- ENTONCES el servicio DEBERÁ informar la colocación como inválida
- Y NO DEBERÁ producir silenciosamente un mundo físico inválido.

### Requirement: Conversión de editor a mundo físico
El editor MUST cumplir este requisito.

El editor DEBERÁ convertir assets validados en el modelo físico usado por el motor, incluidos pose inicial, geometría de colisión, superficies y balizas.

#### Scenario: Aplicar mundo guardado

- DADO un mundo de editor válido con pose inicial de robot
- CUANDO se aplica a una sesión de simulación
- ENTONCES el siguiente snapshot DEBERÁ usar dicho mundo y pose inicial.

### Requirement: continuidad editor–simulación

La creación de mundos MUST conservar una transición directa y verificable al
simulador en ambas interfaces después de validación y persistencia correctas.

#### Scenario: navegación después de guardar

- DADO un usuario que ha creado, validado y guardado un mundo,
- CUANDO decide continuar en simulación,
- ENTONCES no necesita localizar manualmente el archivo guardado,
- Y el sistema aplica el archivo guardado a la sesión de simulación.

### Requirement: Verificación completa de autoría de mundos Web

La campaña Web MUST ejercitar creación, validación, guardado, carga, edición,
cancelación y eliminación segura de mundos con datos sintéticos aislados.

#### Scenario: Mundo guardado y reabierto

- DADO un mundo QA con posición inicial, obstáculos y sensores
- CUANDO se guarda, se recarga el navegador y se vuelve a cargar
- ENTONCES sus elementos y configuración DEBERÁN persistir
- Y el simulador DEBERÁ iniciar el robot en la pose definida sin restos de un
  mundo anterior.

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

### Requirement: Colocación de assets fiable

El editor Web MUST colocar un asset usando el worker y contexto de sesión
vigentes. Un fallo de worker DEBERÁ conservar el modelo previo, mostrar un error
accionable y permitir reintentar; no DEBERÁ bloquear Guardar como de un mundo
válido por un error no relacionado.

#### Scenario: Crear mundo con obstáculo y sensor

- DADO un mundo nuevo válido
- CUANDO el usuario coloca un muro, una meta y un sensor desde el editor
- ENTONCES cada elemento DEBERÁ aparecer una sola vez en canvas y modelo
- Y Guardar como DEBERÁ permitir nombrar y persistir el mundo.

### Requirement: CRUD manual persistente de mundos

La aplicación Web MUST permitir crear, validar, guardar, recargar, editar,
cancelar y eliminar mundos sintéticos mediante la interfaz.

#### Scenario: Editar y recargar mundo guardado

- DADO un mundo guardado con pose inicial y assets
- CUANDO el usuario lo edita, guarda y recarga el navegador
- ENTONCES el mundo DEBERÁ recuperar exactamente sus assets y pose
- Y no DEBERÁ conservar entidades del mundo anterior.
