## ADDED Requirements

### Requirement: Worker como ruta predeterminada
El runtime MUST cumplir este requisito.

La ejecución de scripts DEBERÁ realizarse en un worker aislado por defecto. El
modo local DEBERÁ requerir una configuración explícita de desarrollo o pruebas.

#### Scenario: Ejecución estándar

- DADO una sesión creada sin configuración de compatibilidad local
- CUANDO se inicia un script
- ENTONCES los comandos y eventos DEBERÁN atravesar el worker versionado.
