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

