## ADDED Requirements

### Requisito: Documentacion operativa coherente

El proyecto DEBERA mantener documentacion en espanol para instalar, ejecutar,
probar, operar y diagnosticar las interfaces Web y Tkinter, con version, fecha
de revision y comandos reproducibles.

#### Escenario: Guia de inicio verificada

- DADO un entorno limpio soportado
- CUANDO una persona sigue la guia de instalacion e inicio
- ENTONCES DEBERA poder iniciar la interfaz indicada sin requerir pasos no
  documentados ni credenciales reales.

### Requisito: Evidencia actual e historica distinguible

Los resultados de pruebas, cobertura, versiones y capturas DEBERAN indicar su
fecha, entorno y comando. La evidencia historica no DEBERA presentarse como el
estado vigente.

#### Escenario: Resultado de calidad publicado

- DADO un documento que declara pruebas o cobertura
- CUANDO se valida la documentacion
- ENTONCES DEBERA enlazar al comando reproducible y marcar si el resultado es
  actual o historico fechado.

### Requisito: Verificacion automatizada de documentacion

CI DEBERA comprobar enlaces locales, referencias de version, rutas de comandos
criticos y coherencia entre el indice documental y los archivos publicados.

#### Escenario: Enlace o comando obsoleto

- DADO un enlace local roto o un comando critico inexistente
- CUANDO se ejecuta la validacion documental
- ENTONCES la prueba DEBERA fallar con la referencia exacta que requiere correccion.
