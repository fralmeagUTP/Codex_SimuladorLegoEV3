## ADDED Requirements

### Requirement: Catálogo verificable de paridad

Las interfaces MUST mantener un catálogo versionado de los casos de uso
aplicables, con identificador, entrada, resultado de dominio, estado visual y
resultado observado por plataforma.

#### Scenario: Capacidad disponible en una interfaz

- **DADO** un comando, menú, diálogo o flujo disponible en Web o Tkinter;
- **CUANDO** se actualice el catálogo de paridad;
- **ENTONCES** se clasificará como equivalente, adaptación aceptada o brecha;
- **Y** una brecha impedirá declarar paridad completa hasta corregirla o
  aprobar explícitamente su no aplicabilidad.

### Requirement: Equivalencia de estados críticos

Para el mismo mundo, programa y perfil, Web y Tkinter MUST reflejar un estado
equivalente al iniciar, pausar, reanudar, finalizar, fallar y reiniciar.

#### Scenario: Reinicio desde ejecución activa

- **DADO** una simulación activa que cambió pose, telemetría y LCD;
- **CUANDO** el usuario selecciona detener y reiniciar en cualquiera de las UI;
- **ENTONCES** canvas, robot, LCD, telemetría y estado se restauran al snapshot
  inicial del mundo;
- **Y** no quedan trazas, robots o eventos de la ejecución anterior.
