## MODIFIED Requirements

### Requirement: Visualización LCD del EV3 Brick

La interfaz Tkinter MUST renderizar la pantalla LCD lógica de 178×128 en un área visual 30 % mayor, con canvas de referencia 390×130 px y sin alterar el contenido de telemetría o del Brick.

#### Scenario: Panel Brick visible

- **WHEN** el panel EV3 Brick se construye en la aplicación de escritorio
- **THEN** su canvas LCD usa una referencia de 390×130 px
- **AND** conserva la proporción de la pantalla lógica 178×128.
