# quality-assurance Specification

## Purpose
TBD - created by archiving change ejecutar-qa-total-web. Update Purpose after archive.
## Requirements
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

### Requirement: Campaña integral para ambas interfaces

La campaña de calidad MUST ejercitar en interfaz real el catálogo de menús,
ejemplos, mundos, escenarios, misiones, controles, depuración y errores en Web
y Tkinter, siempre que el elemento sea aplicable.

#### Scenario: Ejecución de campaña integral

- **DADO** el catálogo de capacidades de una versión candidata;
- **CUANDO** se ejecute la campaña en navegador y escritorio activos;
- **ENTONCES** cada elemento tendrá un resultado `PASS`, `FAIL`, `BLOCKED` o
  `N/A` junto con evidencia y entorno;
- **Y** ningún elemento no ejercitado será comunicado como aprobado.

### Requirement: Calidad visual y de accesibilidad antes de liberar

Web y Tkinter MUST comprobar legibilidad, foco, teclado, contraste, temas,
redimensionamiento y ausencia de recorte en los tamaños soportados.

#### Scenario: Tema y tamaño soportados

- **DADO** una resolución y un tema soportados;
- **CUANDO** se recorra la pantalla de simulación, los diálogos y el editor de
  mundos;
- **ENTONCES** los controles críticos serán legibles, enfocables y operables;
- **Y** cualquier recorte o contraste insuficiente se registrará como defecto.

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

