## ADDED Requirements

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
