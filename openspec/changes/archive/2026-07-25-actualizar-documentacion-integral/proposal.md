# Propuesta: actualizar documentacion integral

## Motivo

El proyecto ha evolucionado con worker aislado, contrato de sesion comun,
observabilidad, contenedor Linux, paridad visual y una suite de pruebas mayor.
Parte de la documentacion conserva afirmaciones, prioridades o resultados de
iteraciones anteriores. Esto puede confundir a estudiantes, docentes,
operadores y contribuidores.

## Cambio propuesto

Realizar una actualizacion documental integral, en espanol y con evidencia
reproducible, que alinee el repositorio con el estado real del producto. La
actualizacion incluira guias de uso Web/Tkinter, arquitectura, instalacion,
operacion, despliegue, seguridad, calidad, API Pybricks, aula y OpenSpec.

## Alcance

- Normalizar la fuente de version, fechas, comandos y resultados de pruebas.
- Documentar arquitectura actual, contratos de sesion, worker y limites.
- Documentar ambos flujos de interfaz y su matriz de paridad.
- Consolidar instalacion y operacion en Windows local y Linux con contenedor.
- Publicar guias de pruebas, seguridad, observabilidad y respuesta a fallos.
- Mantener un indice documental y reglas automaticas de consistencia.

## Fuera de alcance

- Cambiar reglas de negocio, arquitectura o API solamente para actualizar texto.
- Eliminar evidencia historica valida; se conservara marcada con fecha y contexto.
- Traducir documentacion de dependencias externas no mantenida por el proyecto.

## Criterios de exito

- Cada documento operativo identifica audiencia, fecha, version y fuente de verdad.
- Un usuario puede instalar, iniciar, probar y diagnosticar Web o Tkinter con comandos reproducibles.
- Ninguna cifra de calidad historica se presenta como resultado actual.
- Los limites simulador-robot y de seguridad son claros antes de ejecutar scripts.
- CI valida enlaces locales, referencias OpenSpec, version y comandos criticos.
