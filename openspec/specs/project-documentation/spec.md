# project-documentation Specification

## Purpose
Definir cómo el proyecto mantiene documentación en español, reproducible,
separada por audiencia y verificable, distinguiendo el estado vigente de la
evidencia histórica y de los materiales para derechos de autor.
## Requirements
### Requirement: Documentacion operativa coherente

El proyecto MUST cumplir este requisito.

El proyecto DEBERA mantener documentación canónica en español para instalar,
ejecutar, probar, operar, desplegar y diagnosticar Web y Tkinter, identificando
versión, fecha de revisión y fuente ejecutable de cada comando crítico.

#### Scenario: Guia de inicio verificada

- DADO un entorno limpio soportado
- CUANDO una persona sigue la guia de instalacion e inicio
- ENTONCES DEBERA poder iniciar la interfaz indicada sin requerir pasos no
  documentados ni credenciales reales.

#### Scenario: Actualización posterior a liberación

- **DADO** un cierre de cambio o una nueva versión verificable;
- **CUANDO** se actualiza la documentación integral;
- **ENTONCES** README, índice, estado actual, arquitectura, roadmap, changelog y
  guías operativas reflejan la misma versión y estado de liberación;
- **Y** los informes anteriores permanecen identificados como históricos.

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

CI DEBERA comprobar que los documentos canónicos existen, usan la versión
distribuible, aparecen en el índice y no contienen enlaces Markdown locales
rotos ni comandos críticos referidos a scripts inexistentes.

#### Scenario: Enlace o comando obsoleto

- DADO un enlace local roto o un comando critico inexistente
- CUANDO se ejecuta la validacion documental
- ENTONCES la prueba DEBERA fallar con la referencia exacta que requiere correccion.

#### Scenario: Referencia documental obsoleta

- **DADO** un enlace local, script o documento canónico referenciado;
- **CUANDO** se ejecutan las pruebas documentales;
- **ENTONCES** cualquier destino inexistente produce un fallo con la ruta de
  origen y la referencia problemática.

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

### Requirement: Documentación de paridad integral

La documentación canónica MUST publicar el modelo MMI, la matriz de
capacidad, las adaptaciones aceptadas, la evidencia de calidad y las guías de
uso equivalentes para estudiantes, docentes, soporte y operación.

#### Scenario: Consulta de capacidad por plataforma

- DADO un docente que necesita saber si una capacidad existe en Web y Tkinter;
- CUANDO consulta el manual o matriz vigente;
- ENTONCES encuentra disponibilidad, diferencias nativas, pasos y evidencia;
- Y el documento distingue una afirmación vigente de un informe histórico.

### Requirement: Guía única de autoría de mundos

El proyecto MUST mantener una guía de creación de mundos que describa el mismo
flujo, categorías, activos, validaciones, atajos y transición al simulador para
Web y Tkinter. Sólo podrá diferir la interacción propia de cada widget nativo.

#### Scenario: Usuario consulta cómo crear un mundo

- DADO un usuario que abre la documentación o ayuda;
- CUANDO sigue la guía para crear un mundo;
- ENTONCES puede completar el flujo en cualquiera de las interfaces sin
  encontrar instrucciones, nombres o activos contradictorios.

