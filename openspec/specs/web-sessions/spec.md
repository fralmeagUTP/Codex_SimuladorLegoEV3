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

### Requirement: Consistencia terminal de snapshot

La sesión Web MUST publicar un snapshot completo, con estado de sesión y
generación, antes de publicar `finished`, `timed_out` o `error`. Canvas, LCD,
telemetría y estado visible DEBERÁN poder renderizar el mismo snapshot.

#### Scenario: Script terminado con salida LCD

- DADO un script que escribe en LCD y termina
- CUANDO el runtime publica `finished`
- ENTONCES la interfaz DEBERÁ recibir el snapshot con el contenido final de LCD
- Y la telemetría DEBERÁ indicar `finished` para esa misma generación.

### Requirement: Reinicio atómico por generación

La sesión Web MUST crear una nueva generación al reiniciar y publicar un
único snapshot inicial de esa generación. Eventos o callbacks de una ejecución
anterior NO DEBERÁN reemplazarlo.

#### Scenario: Cancelación de un bucle y reinicio

- DADO un script en ejecución que genera ticks continuamente
- CUANDO el usuario solicita Detener y reiniciar
- ENTONCES estado, tick, tiempo, LCD, canvas y telemetría DEBERÁN representar
  el inicio del mundo activo
- Y ningún snapshot posterior de la misión cancelada DEBERÁ aplicarse.

### Requirement: Verificación de aislamiento multiusuario Web

La aplicación Web MUST demostrar mediante pruebas concurrentes que sesiones de
usuarios distintos no comparten token, script, mundo, snapshot, eventos, LCD,
telemetría ni estado de ejecución.

#### Scenario: Dos simulaciones concurrentes

- DADO dos sesiones autenticadas con tokens distintos
- CUANDO cargan mundos y scripts diferentes y se ejecutan en paralelo
- ENTONCES cada interfaz DEBERÁ mostrar solo su propio snapshot y resultado
- Y cancelar o reiniciar una sesión NO DEBERÁ afectar la otra.

### Requirement: Recuperación de canal de actualización

La sesión Web MUST mantener coherencia al alternar entre SSE y polling, al
recargar el navegador y ante eventos tardíos o reinicio recuperable del worker.

#### Scenario: SSE interrumpido durante ejecución

- DADO una simulación activa con SSE
- CUANDO el canal se interrumpe y el cliente usa polling o se reconecta
- ENTONCES canvas, LCD, telemetría y estado DEBERÁN converger al mismo snapshot
- Y no DEBERÁN duplicarse robots, trazas, mensajes ni notificaciones.

### Requirement: Cadencia de snapshots Web configurable

La aplicación Web SHALL publicar snapshots de simulación a una cadencia
configurable, con valor predeterminado de 30 Hz y un rango válido de 10 a 60 Hz.
La frecuencia del motor SHALL mantenerse independiente a 50 Hz.

#### Scenario: Configuración predeterminada

- **WHEN** el servidor Web inicia sin una variable de entorno de cadencia
- **THEN** limita los eventos de snapshot a 30 Hz como máximo
- **AND** mantiene los ticks del motor a 50 Hz

#### Scenario: Configuración inválida

- **WHEN** EV3_WEB_WEB_SNAPSHOT_MAX_HZ está fuera del rango de 10 a 60 Hz
- **THEN** el servidor rechaza la configuración con un mensaje accionable

### Requirement: Snapshot final coherente

La sesión SHALL publicar y conservar el último snapshot autoritativo antes de
comunicar un estado terminal.

#### Scenario: Programa finalizado

- **WHEN** un programa termina correctamente
- **THEN** canvas, LCD, telemetría y estado reciben el snapshot final
- **BEFORE** la interfaz muestra finished

### Requirement: Cancelación de depuración recuperable

La sesión Web MUST aplicar a una ejecución iniciada en depuración la misma
cancelación versionada que a una ejecución normal. Una solicitud de Detener y
reiniciar DEBERÁ terminar en un snapshot inicial `created`, aun cuando el worker
de depuración responda tarde o no responda.

#### Scenario: Detener una depuración activa

- DADO un script iniciado con Depurar y estado `running`
- CUANDO el usuario selecciona Detener y reiniciar
- ENTONCES la UI DEBERÁ quedar operable y el estado DEBERÁ ser `created` en un
  máximo de tres segundos
- Y eventos de la generación cancelada NO DEBERÁN restaurar `running`.

### Requirement: Error terminal coherente

La sesión Web MUST publicar el snapshot final y el estado `error` cuando un
script falla en tiempo de ejecución. No DEBERÁ conservar `running` ni datos de
una ejecución anterior como estado terminal.

#### Scenario: Excepción de división por cero

- DADO un script válido que evalúa `1 / 0`
- CUANDO el runtime produce la excepción
- ENTONCES la interfaz DEBERÁ mostrar `error`, el mensaje asociado y el snapshot
  de esa generación
- Y Ejecutar y los menús permitidos DEBERÁN quedar disponibles.

### Requirement: Recuperación de controles desde sesión

La UI Web MUST derivar los controles de ejecución del estado autoritativo al
cargar o recuperar una sesión.

#### Scenario: Recarga después de finalizar

- DADA una sesión que terminó correctamente
- CUANDO el navegador se recarga
- ENTONCES Detener y reiniciar NO DEBERÁ quedar habilitado si no hay operación
  cancelable en curso.

### Requirement: Recuperación verificable de la sesión Web

La sesión Web MUST conservar o restaurar un estado documentado ante recarga,
interrupción recuperable del worker y transición terminal, sin aplicar eventos
de una generación anterior a la interfaz actual.

#### Scenario: Evento retrasado después de reiniciar

- **DADO** una ejecución cancelada y una nueva generación de sesión iniciada;
- **CUANDO** llegue un evento terminal retrasado de la generación anterior;
- **ENTONCES** la interfaz lo ignorará;
- **Y** no cambiará el estado ni mostrará una notificación de éxito incorrecta.

## Notas operativas

- La capacidad predeterminada actual es 20 sesiones activas y 8 simulaciones ejecutándose.
- El timeout de inactividad predeterminado actual es 45 minutos.
- El backend actual es memoria, con espejo opcional Redis o archivo.
- Recuperar metadatos no equivale a continuar de forma durable un proceso Python en ejecución.
