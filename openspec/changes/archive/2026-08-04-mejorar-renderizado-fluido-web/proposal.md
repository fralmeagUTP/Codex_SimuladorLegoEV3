# Propuesta: mejorar el renderizado fluido de la aplicación Web

## Problema

El motor de simulación opera a 50 Hz, pero la sesión Web limita los snapshots
publicados a 12 Hz y el canvas dibuja cada snapshot de forma inmediata. El
robot, sus haces y las trayectorias se perciben entrecortados, sobre todo en
giros y programas de barrido como el radar ultrasónico. La ruta terminal puede
además exponer un estado de sesión final con un snapshot visual anterior.

## Objetivo

Conseguir un movimiento Web fluido sin modificar la física, la semántica de
Pybricks ni la cadencia del motor. Separar explícitamente:

1. simulación autoritativa a 50 Hz;
2. transporte de snapshots configurable y eficiente;
3. renderizado visual mediante requestAnimationFrame, con interpolación
   acotada de pose y haces;
4. publicación obligatoria del snapshot terminal antes de estados terminales.

## Alcance

- Aplicación Web Flask y JavaScript del canvas.
- Configuración documentada de la tasa máxima de snapshots Web.
- Pruebas unitarias, de integración y E2E de cadencia, interpolación,
  coherencia terminal y rendimiento visual.

## Fuera de alcance

- No aumentar artificialmente la velocidad física de motores o DriveBase.
- No cambiar el comportamiento de Tkinter ni el contrato funcional Pybricks.
- No eliminar límites de tiempo, aislamiento ni control de cancelación.
