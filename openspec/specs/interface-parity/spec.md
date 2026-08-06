# interface-parity Specification

## Purpose
TBD - created by archiving change elevar-calidad-y-paridad-de-interfaz. Update Purpose after archive.
## Requirements
### Requirement: Paridad funcional obligatoria
Las interfaces MUST cumplir este requisito.

El sistema DEBERÁ proporcionar en Web y Tkinter el mismo conjunto de casos de uso
de simulación, edición de código, depuración, gestión de mundos, telemetría,
brick virtual, trazas, ayuda y recuperación de sesión que sea aplicable a una UI.
Una función nueva NO DEBERÁ considerarse terminada hasta estar disponible y
verificada en ambas interfaces.

#### Scenario: Nueva función de simulación

- DADA una función nueva aprobada para el simulador
- CUANDO se integra en el producto
- ENTONCES DEBERÁ estar accesible desde Web y Tkinter
- Y ambas interfaces DEBERÁN producir el mismo resultado de dominio, estado y error para la misma entrada.

### Requirement: Contrato compartido de experiencia
Las interfaces MUST cumplir este requisito.

Cada función de UI DEBERÁ estar representada por un caso de uso y contrato común
que defina precondiciones, entrada, transición de estado, snapshot esperado,
resultado y errores. Las interfaces DEBERÁN ser adaptadores de ese contrato.

#### Scenario: Ejecución de un mismo programa

- DADO el mismo mundo, programa y perfil de simulación
- CUANDO se ejecuta desde Web y desde Tkinter
- ENTONCES ambas ejecuciones DEBERÁN producir trazas y snapshots equivalentes dentro de la tolerancia definida.

### Requirement: Pruebas de paridad
Las interfaces MUST cumplir este requisito.

CI DEBERÁ ejecutar una matriz de paridad con pruebas de contrato y E2E para ambas
interfaces. Una divergencia funcional DEBERÁ bloquear la integración.

#### Scenario: Divergencia de interfaz detectada

- DADA una capacidad disponible sólo en una interfaz
- CUANDO se ejecuta la matriz de paridad
- ENTONCES CI DEBERÁ fallar
- Y el cambio NO DEBERÁ integrarse hasta restaurar la paridad.

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

