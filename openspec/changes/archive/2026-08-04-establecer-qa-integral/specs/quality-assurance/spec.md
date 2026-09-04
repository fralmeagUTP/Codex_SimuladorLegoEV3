## ADDED Requirements

### Requirement: Estrategia de calidad trazable

El proyecto MUST mantener una estrategia de calidad versionada que relacione
requisitos documentados o inferidos, funcionalidades, riesgos, componentes,
casos de prueba, automatizaciones y evidencia de ejecución.

#### Scenario: Funcionalidad crítica nueva o modificada

- DADO un cambio que afecte ejecución, mundo, sesión, interfaz, persistencia o
  seguridad
- CUANDO se prepare para integración
- ENTONCES DEBERÁ tener un riesgo asignado, casos positivos y negativos,
  automatización apropiada y criterio de aceptación verificable
- Y sus resultados DEBERÁN quedar incorporados a la matriz de trazabilidad.

### Requirement: Evidencia de interfaz real

Las capacidades visibles de Web y Tkinter MUST aprobarse únicamente tras una
interacción real en navegador o escritorio activo, con evidencia conservada.

#### Scenario: Flujo crítico de simulación

- DADO un flujo de ejecutar, pausar, reanudar, detener, reiniciar, cargar mundo
  o finalizar programa
- CUANDO se ejecute como prueba de interfaz
- ENTONCES la evidencia DEBERÁ mostrar que editor, estado, canvas, LCD,
  telemetría y robot representan un snapshot coherente
- Y un caso no ejecutable DEBERÁ registrarse como `BLOCKED`, sin marcarse PASS.

### Requirement: Cobertura de calidad multidimensional

La campaña de calidad MUST incluir, cuando sean aplicables, pruebas unitarias,
integración, contrato, API, UI/E2E, accesibilidad, seguridad, rendimiento,
resiliencia, compatibilidad e instalación/despliegue.

#### Scenario: Preparación de liberación

- DADO un candidato a liberación
- CUANDO se ejecute la compuerta de calidad
- ENTONCES DEBERÁN ejecutarse las suites obligatorias configuradas y registrarse
  sus comandos, resultados, duración y advertencias
- Y la decisión DEBERÁ ser apta, apta con observaciones o no apta según los
  defectos abiertos y la evidencia disponible.

### Requirement: Regresión de defectos confirmados

Todo defecto confirmado MUST tener una prueba de regresión o, si no es
automatizable de forma segura, una verificación manual reproducible documentada.

#### Scenario: Error terminal de script

- DADO un script con error sintáctico, de ejecución o de importación
- CUANDO el runtime entregue el estado terminal
- ENTONCES las interfaces DEBERÁN reflejar `ERROR` de forma coherente y permitir
  la recuperación prevista
- Y no DEBERÁN conservar `EJECUTANDO` ni emitir una notificación de éxito.
