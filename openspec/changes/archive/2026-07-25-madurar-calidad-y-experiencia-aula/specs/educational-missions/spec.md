## ADDED Requirements

### Requirement: Misiones evaluables locales
Las misiones MUST cumplir este requisito.

El simulador DEBERA permitir distribuir misiones versionadas con mundo, script
inicial, criterios de aceptacion y rubrica, disponibles de forma equivalente en
Web y Tkinter.

#### Scenario: Ejecucion y exportacion de una mision

- DADA una mision valida y un resultado de simulacion
- CUANDO el estudiante solicita su evaluacion y exportacion
- ENTONCES el sistema DEBERA producir un resultado local JSON o CSV con la
  version de mision, resultado, traza y criterios, sin datos personales por defecto.
