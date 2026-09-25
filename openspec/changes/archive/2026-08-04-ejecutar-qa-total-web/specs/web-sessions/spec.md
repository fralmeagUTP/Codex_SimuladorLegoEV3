## ADDED Requirements

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
