## ADDED Requirements

### Requirement: bloqueo de menús durante una ejecución activa

Las interfaces Web y Tkinter MUST deshabilitar de manera coherente los comandos de menú que alteran el contexto de simulación mientras el estado de sesión sea `running` o `paused`.

#### Scenario: script ejecutándose

- **WHEN** la persona usuaria inicia un script y la sesión pasa a `running`
- **THEN** los comandos de menú de contexto quedan deshabilitados
- **AND** los controles Pausar, Reanudar y Detener y reiniciar conservan el comportamiento permitido por su estado.

#### Scenario: script pausado

- **WHEN** una sesión pasa de `running` a `paused`
- **THEN** los comandos de menú de contexto permanecen deshabilitados
- **AND** no es posible cargar ni cambiar un mundo, ejemplo, escenario o misión.

### Requirement: reactivación de menús al finalizar o restablecer una sesión

Las interfaces Web y Tkinter MUST habilitar los comandos de menú de contexto al recibir cualquiera de los estados `created`, `ready`, `finished`, `stopped`, `timed_out`, `error` o `reset`.

#### Scenario: finalización natural

- **WHEN** un script termina correctamente y la sesión informa `finished`
- **THEN** los comandos de menú vuelven a estar disponibles sin recargar la interfaz
- **AND** la persona usuaria puede seleccionar otro ejemplo, mundo, escenario o misión.

#### Scenario: detener y reiniciar

- **WHEN** la persona usuaria solicita Detener y reiniciar
- **THEN** la sesión llega a un estado preparado o restablecido
- **AND** los comandos de menú quedan habilitados.

#### Scenario: finalización excepcional

- **WHEN** la sesión termina con `error` o `timed_out`
- **THEN** los comandos de menú quedan habilitados
- **AND** el mensaje de error o tiempo agotado permanece visible conforme al comportamiento actual.

### Requirement: paridad de política entre interfaces

Web y Tkinter MUST aplicar la misma matriz de disponibilidad para un mismo estado de sesión.

#### Scenario: transición terminal repetida

- **WHEN** una interfaz recibe de forma repetida un snapshot terminal
- **THEN** el estado de los menús permanece habilitado
- **AND** no se producen comandos duplicados ni errores de interfaz.
