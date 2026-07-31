## ADDED Requirements

### Requirement: Telemetría inicialmente escaneable en escritorio

La interfaz Tkinter MUST mostrar una telemetría útil sin scroll vertical innecesario a 1280x800.

#### Scenario: Inicio de simulador a 1280x800

- **WHEN** el usuario abre el simulador Tkinter en 1280x800
- **THEN** la telemetría muestra resumen, motores A-D y sensores S1-S4 sin texto superpuesto, recortado ni contraste insuficiente

#### Scenario: Altura reducida

- **WHEN** la altura disponible no permite mostrar todas las tarjetas
- **THEN** el desplazamiento conserva orden, etiquetas y acceso a Robot/Estado
