## ADDED Requirements

### Requirement: Cobertura exhaustiva del catálogo Web

La campaña de QA Web MUST descubrir el catálogo disponible de la instancia y
ejecutar en navegador real cada menú, comando, ejemplo, mundo, escenario y
misión que forme parte de ese catálogo.

#### Scenario: Elemento descubierto en el catálogo

- DADO un elemento visible o devuelto por el catálogo Web
- CUANDO se ejecute la campaña
- ENTONCES DEBERÁ existir un caso con estado PASS, FAIL o BLOCKED
- Y PASS DEBERÁ incluir interacción real y evidencia del resultado observado.

### Requirement: Evidencia manual verificable

La campaña MUST conservar evidencia de navegador para cada flujo crítico y
para cada fallo: entorno, pasos, captura, consola, red y estado de sesión.

#### Scenario: Defecto manual confirmado

- DADO un comportamiento observado que difiere del esperado
- CUANDO sea reproducible en navegador
- ENTONCES el informe DEBERÁ incluir severidad, impacto, pasos exactos y
  resultado esperado/observado
- Y se DEBERÁ crear una regresión automatizada cuando sea viable.
