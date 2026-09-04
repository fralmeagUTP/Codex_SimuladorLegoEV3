## Why

Las dos interfaces comparten el motor de simulación, pero aún no existe una
evidencia de liberación que demuestre, de forma completa y repetible, que Web y
Tkinter ofrecen los mismos casos de uso críticos, una presentación utilizable y
una recuperación coherente. Alcanzar el 100 % significa cerrar esas brechas con
criterios verificables, no asignar un porcentaje subjetivo.

## What Changes

- Crear una matriz ejecutable de paridad para los flujos de simulación, mundos,
  misiones, depuración, tema, límites de ejecución y recuperación.
- Corregir las divergencias confirmadas entre Web y Tkinter, priorizando estado
  terminal, reinicio, telemetría, canvas, LCD, menús y diálogos.
- Establecer un catálogo de pruebas manuales reales para ambas interfaces y
  automatizar todos los recorridos críticos que sean estables.
- Incorporar compuertas de calidad y una decisión de liberación basada en
  evidencia: pruebas, accesibilidad, rendimiento, seguridad y compatibilidad.
- Documentar explícitamente capacidades no equivalentes por restricción de
  plataforma, con una decisión de producto o un adaptador equivalente.

## Capabilities

### New Capabilities

- `release-readiness`: compuerta reproducible y evidencia objetiva para declarar
  una versión apta para liberar en Web y escritorio.

### Modified Capabilities

- `interface-parity`: exige catálogo de paridad, equivalencia de estado y
  tratamiento explícito de excepciones por plataforma.
- `quality-assurance`: exige campañas manuales reales de ambas interfaces y
  criterios de salida cuantificables.
- `user-interfaces`: exige estados, controles, temas, telemetría y diálogos
  coherentes antes de una liberación.
- `web-sessions`: exige recuperación y sincronización verificadas de la sesión
  Web durante ejecución, error y reinicio.
- `desktop-runtime`: exige verificación real de los flujos críticos Tkinter.

## Impact

Se verán afectados los adaptadores de UI Web/Tkinter, sesión de simulación,
runtime aislado, pruebas pytest/Playwright/pywinauto, documentación de calidad,
CI y los informes de liberación. No se cambia la semántica de Pybricks ni el
modelo físico salvo para corregir un defecto reproducible.
