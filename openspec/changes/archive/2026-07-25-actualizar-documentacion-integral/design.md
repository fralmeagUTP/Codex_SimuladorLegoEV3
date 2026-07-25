# Diseno: documentacion como producto verificable

## Principios

La documentacion vive junto al codigo, se redacta en espanol, distingue hechos
actuales de evidencia historica y no afirma una capacidad sin enlace a su
implementacion, prueba o especificacion. `README.md` sera la puerta de entrada;
`Documentos/` reunira guias extensas y `openspec/` conservara decisiones.

## Taxonomia documental

| Area | Fuente principal | Audiencia |
|---|---|---|
| Inicio, instalacion y comandos | `README.md` | Estudiante y contribuidor |
| Uso de simulacion y mundos | `Documentos/MANUAL_DE_USO.md` | Estudiante y docente |
| Arquitectura y contratos | `Documentos/ARQUITECTURA_C4.md` | Desarrollo y arquitectura |
| Despliegue y fallos | Guias Windows/Linux | Operacion docente |
| Pruebas y calidad | `docs/testing/` y controles de calidad | QA y desarrollo |
| Compatibilidad EV3 | Matriz Pybricks y diferencias simulador-robot | Docente y estudiante |
| Cambios y decisiones | `openspec/changes/` | Todo el equipo |

## Control de consistencia

Una prueba documental leera la version desde la fuente unica, comprobara enlaces
relativos, verificara que los comandos de inicio/prueba existen y detectara
resultados actuales sin fecha. Los documentos historicos usaran encabezado con
fecha, entorno y comando ejecutado.

## Mantenimiento

Cada cambio funcional debera actualizar las secciones afectadas antes de
cerrarse. El checklist de contribucion incluira documentacion, pruebas y delta
OpenSpec. Las capturas y reportes se enlazaran como evidencia, sin sustituir los
comandos reproducibles.
