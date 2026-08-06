## ADDED Requirements

### Requirement: Verificación real de flujos críticos de escritorio

La aplicación Tkinter MUST disponer de una campaña reproducible de interfaz
gráfica que ejerza sus comandos críticos y documente los casos que requieran
validación manual.

#### Scenario: Menú y ejecución de escritorio

- **DADO** la ventana Tkinter visible y una simulación activa;
- **CUANDO** se prueben ejecutar, pausar, reanudar, detener y reiniciar;
- **ENTONCES** los menús y controles reflejarán el estado permitido;
- **Y** al llegar a un estado terminal recuperarán su disponibilidad esperada.
