# Especificación: creación de mundos

## Propósito

Crear, validar, persistir, cargar y aplicar mundos 2D utilizados por el simulador EV3.

## Requisitos

### Requisito: Modelo de mundo físico

Un mundo físico DEBERÁ contener dimensiones en milímetros, un modelo de superficie, obstáculos poligonales y balizas infrarrojas opcionales. DEBERÁ proporcionar ray casting para sensores de distancia y validación de límites para colisiones del robot.

#### Escenario: Rayo impacta el muro más cercano

- DADO un origen y dirección de rayo frente a múltiples obstáculos
- CUANDO el mundo ejecuta ray casting
- ENTONCES DEBERÁ devolver la intersección válida más cercana dentro del rango solicitado.

### Requisito: Datos de superficie y líneas

La superficie DEBERÁ representar color y reflectancia por celda. DEBERÁ soportar construcción de líneas negras para escenarios de aprendizaje con sensor de color.

#### Escenario: Consulta sin celda sobrescrita

- DADA una coordenada de superficie sin sobrescritura explícita
- CUANDO el motor consulta esa coordenada
- ENTONCES DEBERÁ devolver el color y reflectancia predeterminados configurados.

### Requisito: Compatibilidad de persistencia JSON

El repositorio DEBERÁ guardar y cargar mundos físicos como JSON UTF-8 con versión de formato `1`. Las versiones no soportadas DEBERÁN rechazarse explícitamente.

#### Escenario: Recorrido completo de mundo

- DADO un mundo válido con celdas, obstáculos y balizas
- CUANDO se guarda y carga mediante `WorldRepository`
- ENTONCES el mundo restaurado DEBERÁ preservar su contenido físico serializable.

### Requisito: Validación visual de mundo

La capa de editor DEBERÁ validar los datos antes de aplicarlos a la simulación. La validación DEBERÁ cubrir integridad de esquema, assets soportados, límites, solapes, ubicación del robot y reglas de conexión requeridas.

#### Escenario: Colocación inválida solapada

- DADA una colocación que se solapa con un asset existente prohibido
- CUANDO se ejecuta la validación
- ENTONCES el servicio DEBERÁ informar la colocación como inválida
- Y NO DEBERÁ producir silenciosamente un mundo físico inválido.

### Requisito: Conversión de editor a mundo físico

El editor DEBERÁ convertir assets validados en el modelo físico usado por el motor, incluidos pose inicial, geometría de colisión, superficies y balizas.

#### Escenario: Aplicar mundo guardado

- DADO un mundo de editor válido con pose inicial de robot
- CUANDO se aplica a una sesión de simulación
- ENTONCES el siguiente snapshot DEBERÁ usar dicho mundo y pose inicial.
