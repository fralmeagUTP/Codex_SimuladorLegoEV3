# Datos aislados de QA Web

- Todos los mundos creados por la campaña usarán el prefijo `QA_WEB_`.
- Los nombres, directorios y tokens se generarán por ejecución.
- La campaña se ejecutará contra una instancia configurada con directorios
  temporales para ejemplos/mundos cuando el caso requiera escritura.
- La limpieza validará que solo elimina recursos con prefijo `QA_WEB_` creados
  en el directorio temporal de la propia campaña.
- Si la limpieza falla, el resultado será FAIL de infraestructura y los datos
  se conservarán para evidencia; nunca se borrarán mundos del usuario.
