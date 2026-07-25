# Delta: interfaces de usuario

## REQUISITO: navegación funcional equivalente

Las interfaces Web y Tkinter DEBERÁN exponer destinos descubribles para
Simulación, creación de mundos, ayuda didáctica y acerca de. Los destinos podrán
usar rutas Web o ventanas nativas, pero DEBERÁN conducir a la misma capacidad y
resultado funcional.

### Escenario: descubrir ayuda contextual

- DADO un usuario que necesita crear un mundo, ejecutar un script o depurar,
- CUANDO abre la ayuda desde Web o Tkinter,
- ENTONCES encuentra tutoriales para las tres tareas con pasos, resultado
  esperado y recuperación,
- Y PUEDE abrir el destino funcional correspondiente.

## REQUISITO: retorno de mundo guardado a simulación

Tras guardar un mundo válido, ambas interfaces DEBERÁN ofrecer una acción para
abrirlo inmediatamente en simulación.

### Escenario: simular mundo recién guardado

- DADO un mundo válido recién guardado desde el editor,
- CUANDO el usuario elige simularlo,
- ENTONCES la interfaz DEBERÁ cargar ese mismo archivo en la sesión de
  simulación,
- Y DEBERÁ mostrar la simulación con el mundo activo.

### Escenario: error al aplicar un mundo guardado

- DADO un error de lectura o aplicación del archivo guardado,
- CUANDO el usuario elige simularlo,
- ENTONCES la interfaz DEBERÁ informar el error,
- Y NO DEBERÁ reemplazar el mundo activo de la sesión.
