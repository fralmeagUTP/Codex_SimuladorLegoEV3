## ADDED Requirements

### Requirement: Cadencia de snapshots Web configurable

La aplicación Web SHALL publicar snapshots de simulación a una cadencia
configurable, con valor predeterminado de 30 Hz y un rango válido de 10 a 60 Hz.
La frecuencia del motor SHALL mantenerse independiente a 50 Hz.

#### Scenario: Configuración predeterminada

- **WHEN** el servidor Web inicia sin una variable de entorno de cadencia
- **THEN** limita los eventos de snapshot a 30 Hz como máximo
- **AND** mantiene los ticks del motor a 50 Hz

#### Scenario: Configuración inválida

- **WHEN** EV3_WEB_WEB_SNAPSHOT_MAX_HZ está fuera del rango de 10 a 60 Hz
- **THEN** el servidor rechaza la configuración con un mensaje accionable

### Requirement: Snapshot final coherente

La sesión SHALL publicar y conservar el último snapshot autoritativo antes de
comunicar un estado terminal.

#### Scenario: Programa finalizado

- **WHEN** un programa termina correctamente
- **THEN** canvas, LCD, telemetría y estado reciben el snapshot final
- **BEFORE** la interfaz muestra finished
