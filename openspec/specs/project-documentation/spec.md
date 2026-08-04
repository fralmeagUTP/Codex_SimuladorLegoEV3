# project-documentation Specification

## Purpose
TBD - created by archiving change actualizar-documentacion-integral. Update Purpose after archive.
## Requirements
### Requirement: Documentacion operativa coherente
El proyecto MUST cumplir este requisito.

El proyecto DEBERA mantener documentacion en espanol para instalar, ejecutar,
probar, operar y diagnosticar las interfaces Web y Tkinter, con version, fecha
de revision y comandos reproducibles.

#### Scenario: Guia de inicio verificada

- DADO un entorno limpio soportado
- CUANDO una persona sigue la guia de instalacion e inicio
- ENTONCES DEBERA poder iniciar la interfaz indicada sin requerir pasos no
  documentados ni credenciales reales.

### Requirement: Evidencia actual e historica distinguible
El proyecto MUST cumplir este requisito.

Los resultados de pruebas, cobertura, versiones y capturas DEBERAN indicar su
fecha, entorno y comando. La evidencia historica no DEBERA presentarse como el
estado vigente.

#### Scenario: Resultado de calidad publicado

- DADO un documento que declara pruebas o cobertura
- CUANDO se valida la documentacion
- ENTONCES DEBERA enlazar al comando reproducible y marcar si el resultado es
  actual o historico fechado.

### Requirement: Verificacion automatizada de documentacion
CI MUST cumplir este requisito.

CI DEBERA comprobar enlaces locales, referencias de version, rutas de comandos
criticos y coherencia entre el indice documental y los archivos publicados.

#### Scenario: Enlace o comando obsoleto

- DADO un enlace local roto o un comando critico inexistente
- CUANDO se ejecuta la validacion documental
- ENTONCES la prueba DEBERA fallar con la referencia exacta que requiere correccion.

### Requirement: Documentación separada por audiencia

La documentación MUST separar las guías de uso orientadas a estudiantes y
docentes de la documentación técnica de instalación, operación, sesiones y
despliegue, conservando enlaces cruzados solo cuando sean necesarios.

#### Scenario: Usuario final consulta la ayuda

- **WHEN** un estudiante o docente abre la ayuda desde la aplicación
- **THEN** recibe instrucciones de interfaz y tareas sin requerir terminal,
  URL fija de despliegue ni conocimiento de la arquitectura interna.

#### Scenario: Personal técnico requiere operación

- **WHEN** una persona necesita instalar, desplegar o diagnosticar el servicio
- **THEN** puede acceder a la guía técnica actualizada desde una referencia
  explícita y separada de las rutas de aprendizaje.

### Requirement: Manual técnico HTML del producto

El proyecto SHALL mantener un manual técnico HTML independiente de la ayuda
rápida que describa el producto, las plataformas, la arquitectura, el alcance
Pybricks, la instalación, la configuración, la operación, la seguridad y la
verificación.

#### Scenario: Consulta sin servidor

- **WHEN** una persona abre el archivo HTML desde el repositorio local
- **THEN** puede navegar por el índice, leer el contenido y preparar una
  impresión sin requerir una aplicación web en ejecución

### Requirement: Evidencia para preparación de registro

El manual SHALL incluir una sección que enumere la evidencia técnica que el
titular debe completar para un trámite de derechos de autor, sin afirmar que
el documento por sí solo equivale a un registro legal.

#### Scenario: Preparación de expediente

- **WHEN** el titular prepara una solicitud de registro
- **THEN** identifica los campos de autoría, versión, hash, commit, licencia,
  dependencias y capturas que debe completar o verificar

