## ADDED Requirements

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
