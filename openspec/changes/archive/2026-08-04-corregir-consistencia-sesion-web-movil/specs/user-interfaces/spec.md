## ADDED Requirements

### Requirement: Controles de mapa utilizables en móvil

La interfaz Web MUST ajustar canvas y controles del mapa al ancho disponible
del viewport, sin scroll horizontal no intencional ni controles recortados.

#### Scenario: Viewport de 390×844

- DADO un navegador de 390×844 píxeles
- CUANDO se carga el simulador Web
- ENTONCES el canvas NO DEBERÁ exceder el ancho de su contenedor
- Y el botón de haces DEBERÁ permanecer completamente visible y operable.

### Requirement: Coherencia visual de snapshot

La interfaz Web MUST ignorar snapshots de generaciones antiguas y ticks fuera
de orden dentro de la generación activa.

#### Scenario: Evento tardío tras reset

- DADO que el cliente ya aplicó el snapshot inicial de una nueva generación
- CUANDO recibe un snapshot de una generación anterior
- ENTONCES NO DEBERÁ modificar canvas, LCD, telemetría ni controles.
