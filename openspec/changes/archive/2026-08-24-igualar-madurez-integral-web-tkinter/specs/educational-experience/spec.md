## ADDED Requirements

### Requirement: Ruta de aprendizaje común

El producto MUST proporcionar en Web y Tkinter el mismo catálogo versionado
de actividades educativas, con objetivo, prerrequisitos, programa/mundo,
criterio de éxito, retroalimentación y siguiente paso.

#### Scenario: Actividad completada correctamente

- DADO un estudiante que completa una actividad evaluable en cualquiera de las
  interfaces;
- CUANDO el criterio común se satisface;
- ENTONCES recibe un resultado formativo, el objetivo alcanzado y la siguiente
  actividad sugerida;
- Y el progreso queda disponible para la misma plataforma al reiniciar.

### Requirement: Recuperación pedagógica ante error

La retroalimentación ante un error MUST explicar el problema, preservar la
seguridad del estudiante y ofrecer una práctica o guía de recuperación.

#### Scenario: Script con error de sintaxis

- DADO un script con sintaxis inválida;
- CUANDO termina con error;
- ENTONCES ambas UI muestran un mensaje comprensible, una referencia a la
  línea o causa y un enlace a la guía de corrección;
- Y no registran la actividad como completada.
