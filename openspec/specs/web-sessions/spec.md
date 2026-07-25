# Especificación: sesiones web

## Purpose

Proporcionar sesiones de simulación aisladas para navegador, controles REST, snapshots, streaming, gestión de capacidad y metadatos recuperables.
## Requirements
### Requirement: Creación de sesión con propietario
La API MUST cumplir este requisito.

La API web DEBERÁ crear un identificador UUID de sesión y un token aleatorio criptográficamente seguro para cada sesión. El servidor DEBERÁ guardar el hash del token y enviarlo al navegador en una cookie HttpOnly, SameSite=Lax.

#### Scenario: Se crea una sesión

- CUANDO un cliente publica en `/api/sessions` dentro de la capacidad configurada
- ENTONCES la API DEBERÁ devolver ID de sesión, token de propietario y estado `created`
- Y DEBERÁ establecer las cookies de propiedad correspondientes.

### Requirement: Control de acceso de sesión
La API MUST cumplir este requisito.

Toda operación web específica de sesión DEBERÁ requerir el ID y token de propietario coincidentes. Las solicitudes con token ausente, expirado, desconocido o incorrecto NO DEBERÁN acceder a la sesión.

#### Scenario: Token de propietario incorrecto

- DADA una sesión existente de otro navegador
- CUANDO una solicitud proporciona un token diferente
- ENTONCES la API DEBERÁ responder con error de sesión prohibida.

### Requirement: Capacidad y expiración
El gestor MUST cumplir este requisito.

El gestor DEBERÁ aplicar máximos configurados de sesiones activas y simulaciones ejecutándose. DEBERÁ expirar sesiones inactivas después del timeout configurado y liberar sus recursos.

#### Scenario: Capacidad de sesiones alcanzada

- DADO que la cantidad de sesiones activas iguala el máximo configurado
- CUANDO un cliente solicita otra sesión sin capacidad disponible
- ENTONCES la API DEBERÁ devolver error de capacidad con guía de reintento.

### Requirement: Controles de script y ejecución
La API MUST cumplir este requisito.

La API DEBERÁ permitir al propietario cargar un script de tamaño limitado, iniciar, pausar, reanudar, detener, reiniciar, configurar debug y pose inicial. Las solicitudes de inicio con el mismo identificador de idempotencia válido DEBERÁN devolver el resultado original sin duplicar la ejecución.

#### Scenario: Reintento duplicado de inicio

- DADO que una sesión aceptó un ID de solicitud de inicio dentro de su TTL
- CUANDO el navegador reintenta ese mismo ID
- ENTONCES la API DEBERÁ devolver la respuesta de inicio almacenada
- Y NO DEBERÁ crear una segunda ejecución.

### Requirement: Snapshots y stream de eventos
La API MUST cumplir este requisito.

La API DEBERÁ exponer el estado más reciente mediante snapshots y un stream SSE. La inicialización del stream DEBERÁ enviar estado actual y datos de snapshot, debug y mundo disponibles antes de eventos posteriores secuenciados.

#### Scenario: Reconexión al stream

- DADO que un navegador abre el stream de sesión
- CUANDO se establece la conexión
- ENTONCES DEBERÁ recibir el estado actual de sesión
- Y DEBERÁ recibir el último snapshot si existe.

### Requirement: Recuperación de metadatos
El gestor MUST cumplir este requisito.

Cuando se configure almacenamiento espejo en archivo o Redis, el gestor DEBERÁ intentar recuperar metadatos elegibles tras un fallo local de worker. La recuperación DEBERÁ preservar la verificación de propietario y nunca conceder acceso con metadatos inválidos.

#### Scenario: Recuperación de sesión espejo válida

- DADO un registro de metadatos válido de una sesión
- CUANDO un worker compatible recibe una solicitud de esa sesión
- ENTONCES PODRÁ reconstruir una sesión elegible tras verificar el token
- Y DEBERÁ actualizar métricas de recuperación.

### Requirement: Estado de sesión y entrega final
La sesión MUST cumplir este requisito.

La sesión DEBERÁ aplicar una máquina de estados versionada con `created`, `ready`,
`running`, `paused`, `finished`, `stopped`, `error`, `timed_out` y `resetting`.
Al finalizar naturalmente, DEBERÁ conservar el snapshot y eventos finales hasta
que una interfaz confirme su presentación o solicite reinicio explícito.

#### Scenario: Finalización con estado de brick

- DADO un programa que deja una salida visible en LED, LCD o altavoz
- CUANDO el programa finaliza
- ENTONCES el estado final DEBERÁ entregarse a ambas interfaces antes de cualquier reinicio
- Y no DEBERÁ reemplazarse por el estado inicial de manera prematura.

### Requirement: Contrato versionado de snapshots
La sesión MUST cumplir este requisito.

Todo snapshot y evento DEBERÁ incluir versión de contrato, secuencia monotónica y
estado de sesión. El backend y ambas interfaces DEBERÁN rechazar o adaptar
versiones incompatibles de forma explícita.

#### Scenario: Evento fuera de orden

- DADO un cliente que recibe eventos con secuencia inferior al último aplicado
- CUANDO procesa el stream
- ENTONCES DEBERÁ ignorar el evento obsoleto
- Y mantener el snapshot más reciente coherente.

### Requirement: Contrato versionado de sesión
La sesión MUST cumplir este requisito.

Las sesiones DEBERÁN publicar comandos, eventos, errores, snapshots y trazas con
versión, `session_id` y correlación `command_id`.

#### Scenario: Recuperación correlacionada

- DADO un worker recuperado
- CUANDO la sesión reanuda una operación idempotente
- ENTONCES DEBERÁ conservar la correlación y el último snapshot válido.

## Notas operativas

- La capacidad predeterminada actual es 20 sesiones activas y 8 simulaciones ejecutándose.
- El timeout de inactividad predeterminado actual es 45 minutos.
- El backend actual es memoria, con espejo opcional Redis o archivo.
- Recuperar metadatos no equivale a continuar de forma durable un proceso Python en ejecución.
