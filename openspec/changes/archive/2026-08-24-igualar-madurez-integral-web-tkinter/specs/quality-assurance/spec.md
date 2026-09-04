## ADDED Requirements

### Requirement: Compuerta de madurez gemela

CI MUST ejecutar y publicar una compuerta común para Web y Tkinter que cubra
contrato, comportamiento, accesibilidad, regresión visual, calidad estática,
seguridad, rendimiento, resiliencia y empaquetado aplicables.

#### Scenario: Candidato de liberación

- DADO un commit candidato;
- CUANDO se prepara la liberación;
- ENTONCES el informe MMI publica resultados por dimensión y plataforma;
- Y un flujo crítico FAIL o BLOCKED impide declarar equivalencia integral.

### Requirement: Pruebas de interfaz con manifiesto común

Playwright y Pywinauto MUST ejecutar los mismos identificadores de caso
cuando el flujo sea aplicable, conservando evidencia de UI real.

#### Scenario: Caso de reinicio

- DADO el caso común de detener y reiniciar;
- CUANDO se ejecuta en Web y Tkinter;
- ENTONCES las dos pruebas verifican pose inicial, telemetría, LCD, trazas y
  estado usando el mismo oráculo de snapshot.
