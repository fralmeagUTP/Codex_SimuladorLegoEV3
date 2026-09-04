## ADDED Requirements

### Requirement: Confirmación de ejecución exitosa

Las interfaces Web y Tkinter MUST informar `El programa se ejecutó correctamente.` exactamente una vez cuando la ejecución activa alcance el estado terminal `finished`, después de reflejar el snapshot terminal en sus vistas.

#### Scenario: Script válido termina correctamente

- **WHEN** un usuario ejecuta un programa Pybricks válido y este alcanza `finished`
- **THEN** la interfaz muestra una única confirmación de ejecución correcta
- **AND** canvas, LCD, telemetría y barra de estado ya representan el snapshot terminal.

#### Scenario: Estado no exitoso

- **WHEN** una ejecución alcanza `error`, `timed_out`, `stopped` o `reset`
- **THEN** la interfaz no muestra la confirmación de ejecución correcta.

### Requirement: Presentación accesible y no bloqueante en Web

La interfaz Web MUST mostrar la confirmación como un toast no modal, con región `aria-live`, cierre manual, desaparición automática y contraste válido en temas claro y oscuro.

#### Scenario: Cierre y viewport móvil

- **WHEN** el toast de éxito está visible en un viewport móvil
- **THEN** el usuario puede cerrarlo mediante un control accesible
- **AND** el toast no cubre ni desborda los controles críticos.
