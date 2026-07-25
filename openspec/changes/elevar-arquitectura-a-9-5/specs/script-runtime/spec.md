## MODIFIED Requirements

### Requisito: Worker como ruta predeterminada

La ejecución de scripts DEBERÁ realizarse en un worker aislado por defecto. El
modo local DEBERÁ requerir una configuración explícita de desarrollo o pruebas.

#### Escenario: Ejecución estándar

- DADO una sesión creada sin configuración de compatibilidad local
- CUANDO se inicia un script
- ENTONCES los comandos y eventos DEBERÁN atravesar el worker versionado.
