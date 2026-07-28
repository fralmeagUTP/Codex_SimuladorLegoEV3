# Delta: interfaces de usuario

## ADDED Requirements

### Requirement: navegación funcional equivalente

Web y Tkinter MUST exponer destinos descubribles para simulación, creación de
mundos, ayuda didáctica y acerca de. Los destinos pueden ser rutas Web o
ventanas nativas, pero DEBEN conducir a la misma capacidad funcional.

#### Scenario: descubrir ayuda contextual

- DADO un usuario que necesita crear un mundo, ejecutar un script o depurar,
- CUANDO abre la ayuda desde Web o Tkinter,
- ENTONCES encuentra tutoriales para las tres tareas con pasos, resultado
  esperado y recuperación,
- Y PUEDE abrir el destino funcional correspondiente.

### Requirement: retorno de mundo guardado a simulación

Tras guardar un mundo válido, ambas interfaces MUST ofrecer una acción para
abrirlo inmediatamente en simulación.

#### Scenario: simular mundo recién guardado

- DADO un mundo válido recién guardado desde el editor,
- CUANDO el usuario elige simularlo,
- ENTONCES la interfaz carga ese mismo archivo en la sesión de simulación,
- Y muestra la simulación con el mundo activo.

#### Scenario: error al aplicar un mundo guardado

- DADO un error de lectura o aplicación del archivo guardado,
- CUANDO el usuario elige simularlo,
- ENTONCES la interfaz informa el error,
- Y NO reemplaza el mundo activo de la sesión.
