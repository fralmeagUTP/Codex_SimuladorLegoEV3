## ADDED Requirements

### Requirement: Manifiesto versionado de visuales didácticos

El proyecto SHALL conservar un manifiesto versionado para cada recurso visual
usado por la ayuda, con guía, plataforma, tema, resolución de referencia,
origen, fecha, versión de interfaz, texto alternativo, transcripción y estado
de revisión. El manifiesto SHALL excluir datos personales, código de
estudiantes y secretos.

#### Scenario: Cambio de interfaz requiere revisar una captura

- **WHEN** cambia una superficie mostrada por una guía o cambia la versión de
  interfaz asociada a una captura
- **THEN** la validación identifica el recurso para revisión antes de declarar
  actualizada la documentación.

### Requirement: Evidencia reproducible de ayuda

El proyecto SHALL documentar cómo generar, revisar y validar las capturas Web
y Tkinter de la ayuda, y SHALL publicar evidencia de tema claro, oscuro y
resoluciones objetivo.

#### Scenario: Validación de liberación

- **WHEN** se prepara una liberación que modifica la ayuda o una pantalla
  referenciada por ella
- **THEN** la evidencia registra los comandos, plataformas, resultados de
  pruebas y recursos visuales revisados.
