# Delta: interfaces de usuario

## REQUISITO: paridad visual entre interfaces

Tkinter DEBE implementar el sistema visual y la organización de controles de la Web, que actúa como fuente de verdad.

### Escenario: acción equivalente

- Dado un usuario en Web o Tkinter,
- cuando consulta una acción de simulación, mundo, editor, depuración, perfil o traza,
- entonces encuentra la misma etiqueta, orden, estado y atajo aplicable.

### Escenario: tema y estado

- Dado un tema o estado de sesión,
- cuando cambie a ejecución, pausa, error o deshabilitado,
- entonces ambas interfaces comunican el estado con tokens semánticos equivalentes.
