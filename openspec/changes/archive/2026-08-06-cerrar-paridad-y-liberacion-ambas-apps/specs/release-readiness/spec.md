## ADDED Requirements

### Requirement: Compuerta de liberación basada en evidencia

El proyecto MUST evaluar cada candidato de liberación con una compuerta
reproducible que una resultado de pruebas, defectos abiertos, compatibilidad,
seguridad y evidencia manual de Web y Tkinter.

#### Scenario: Candidato apto para liberar

- **DADO** un commit candidato y los entornos soportados disponibles;
- **CUANDO** se ejecute la compuerta de liberación;
- **ENTONCES** el informe DEBERÁ registrar commit, versiones, comandos,
  resultados, duración, incidencias y decisión;
- **Y** sólo podrá indicar `apta` si no hay defectos críticos o altos abiertos,
  ni flujos críticos `BLOCKED` o `FAIL`.

### Requirement: Clasificación honesta de cobertura

El informe MUST diferenciar pruebas ejecutadas, no ejecutadas, bloqueadas y no
aplicables, sin convertir cobertura de código ni pruebas de contrato en una
afirmación de uso real de interfaz.

#### Scenario: Caso no ejercitable

- **DADO** un caso que requiere un entorno o una interacción no disponible;
- **CUANDO** se genere el informe;
- **ENTONCES** el caso se registrará como `BLOCKED` con su causa y riesgo;
- **Y** no contribuirá al porcentaje de completitud funcional.
