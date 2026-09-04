## MODIFIED Requirements

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
