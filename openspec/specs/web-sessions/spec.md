# Especificación: sesiones web

## Propósito

Proporcionar sesiones de simulación aisladas para navegador, controles REST, snapshots, streaming, gestión de capacidad y metadatos recuperables.

## Requisitos

### Requisito: Creación de sesión con propietario

La API web DEBERÁ crear un identificador UUID de sesión y un token aleatorio criptográficamente seguro para cada sesión. El servidor DEBERÁ guardar el hash del token y enviarlo al navegador en una cookie HttpOnly, SameSite=Lax.

#### Escenario: Se crea una sesión

- CUANDO un cliente publica en `/api/sessions` dentro de la capacidad configurada
- ENTONCES la API DEBERÁ devolver ID de sesión, token de propietario y estado `created`
- Y DEBERÁ establecer las cookies de propiedad correspondientes.

### Requisito: Control de acceso de sesión

Toda operación web específica de sesión DEBERÁ requerir el ID y token de propietario coincidentes. Las solicitudes con token ausente, expirado, desconocido o incorrecto NO DEBERÁN acceder a la sesión.

#### Escenario: Token de propietario incorrecto

- DADA una sesión existente de otro navegador
- CUANDO una solicitud proporciona un token diferente
- ENTONCES la API DEBERÁ responder con error de sesión prohibida.

### Requisito: Capacidad y expiración

El gestor DEBERÁ aplicar máximos configurados de sesiones activas y simulaciones ejecutándose. DEBERÁ expirar sesiones inactivas después del timeout configurado y liberar sus recursos.

#### Escenario: Capacidad de sesiones alcanzada

- DADO que la cantidad de sesiones activas iguala el máximo configurado
- CUANDO un cliente solicita otra sesión sin capacidad disponible
- ENTONCES la API DEBERÁ devolver error de capacidad con guía de reintento.

### Requisito: Controles de script y ejecución

La API DEBERÁ permitir al propietario cargar un script de tamaño limitado, iniciar, pausar, reanudar, detener, reiniciar, configurar debug y pose inicial. Las solicitudes de inicio con el mismo identificador de idempotencia válido DEBERÁN devolver el resultado original sin duplicar la ejecución.

#### Escenario: Reintento duplicado de inicio

- DADO que una sesión aceptó un ID de solicitud de inicio dentro de su TTL
- CUANDO el navegador reintenta ese mismo ID
- ENTONCES la API DEBERÁ devolver la respuesta de inicio almacenada
- Y NO DEBERÁ crear una segunda ejecución.

### Requisito: Snapshots y stream de eventos

La API DEBERÁ exponer el estado más reciente mediante snapshots y un stream SSE. La inicialización del stream DEBERÁ enviar estado actual y datos de snapshot, debug y mundo disponibles antes de eventos posteriores secuenciados.

#### Escenario: Reconexión al stream

- DADO que un navegador abre el stream de sesión
- CUANDO se establece la conexión
- ENTONCES DEBERÁ recibir el estado actual de sesión
- Y DEBERÁ recibir el último snapshot si existe.

### Requisito: Recuperación de metadatos

Cuando se configure almacenamiento espejo en archivo o Redis, el gestor DEBERÁ intentar recuperar metadatos elegibles tras un fallo local de worker. La recuperación DEBERÁ preservar la verificación de propietario y nunca conceder acceso con metadatos inválidos.

#### Escenario: Recuperación de sesión espejo válida

- DADO un registro de metadatos válido de una sesión
- CUANDO un worker compatible recibe una solicitud de esa sesión
- ENTONCES PODRÁ reconstruir una sesión elegible tras verificar el token
- Y DEBERÁ actualizar métricas de recuperación.

## Notas operativas

- La capacidad predeterminada actual es 20 sesiones activas y 8 simulaciones ejecutándose.
- El timeout de inactividad predeterminado actual es 45 minutos.
- El backend actual es memoria, con espejo opcional Redis o archivo.
- Recuperar metadatos no equivale a continuar de forma durable un proceso Python en ejecución.
