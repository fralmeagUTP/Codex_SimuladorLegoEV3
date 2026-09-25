## 1. Línea base y catálogo de paridad

- [x] 1.1 Inventariar todas las capacidades visibles y API de Web y Tkinter, marcando aplicabilidad y propietario.
- [x] 1.2 Definir matriz de paridad con oráculos de dominio, sesión y presentación para cada flujo crítico.
- [x] 1.3 Registrar entornos soportados: Windows/Tkinter, Chrome o Edge, resoluciones, temas y versiones de Python.

## 2. Diagnóstico reproducible

- [x] 2.1 Ejecutar campañas reales Web y Tkinter contra un commit limpio y registrar evidencia de cada caso crítico. *(Catálogo Web completo y 6/6 recorridos nativos Tkinter aprobados.)*
- [x] 2.2 Clasificar todos los hallazgos por severidad, impacto y reproducibilidad; crear regresión viable por defecto confirmado. *(WEB-PAR-001, WEB-PAR-002 y menú terminal Tkinter corregidos y cubiertos.)*
- [x] 2.3 Medir latencia de controles, cadencia de snapshots/renderizado y coherencia de tiempo de simulación en Web. *(Playwright y control de interpolación aprobados; se admite como máximo dos ticks de cuantización en el snapshot terminal.)*
- [x] 2.4 Verificar flujos de worker, recarga, eventos tardíos, cancelación, límite de tiempo y recuperación de sesión. *(Contratos, E2E Web, resiliencia y recorridos terminales aprobados.)*

## 3. Corrección de paridad y experiencia

- [x] 3.1 Corregir divergencias de resultados de dominio o snapshot entre ambas UI antes de ajustes visuales. *(Snapshot terminal compartido y contratos de paridad aprobados.)*
- [x] 3.2 Corregir problemas confirmados de controles, menús, diálogos, telemetría, LCD, canvas, robot y trazas. *(Regresiones confirmadas corregidas; sin defectos críticos o altos abiertos.)*
- [x] 3.3 Asegurar temas, teclado, foco, contraste, redimensionamiento y móvil Web en los entornos definidos. *(E2E Web y evidencia visual Tkinter claro/oscuro en tamaños objetivo aprobados.)*
- [x] 3.4 Documentar o adaptar toda diferencia no aplicable por plataforma. *(Matriz de paridad documenta selectores nativos, persistencia, notificaciones y móvil.)*

## 4. Automatización y compuertas

- [x] 4.1 Implementar pruebas de contrato de paridad para estados iniciar, pausar, reanudar, terminal y reiniciar. *(17/17 contratos de sesión y adaptador de escritorio aprobados.)*
- [x] 4.2 Ampliar Playwright para catálogo Web, resoluciones, tema, depuración, mundos y sesiones aisladas.
- [x] 4.3 Ampliar pywinauto para menú, ejecución, reinicio, tema, mundo y telemetría Tkinter. *(5/5 E2E nativas PASS en 31,50 s.)*
- [x] 4.4 Configurar compuerta CI de lint, tipos, seguridad, cobertura, contratos y E2E por plataforma. *(GitHub Actions aprobó los flujos `calidad` y `tests` del commit actual.)*

## 5. Validación de liberación

- [x] 5.1 Ejecutar las suites obligatorias y registrar comandos, versiones, duración y resultados por commit. *(Campaña local por capas aprobada: 392 + 243 + 137 + 55 + 5; contenedor Docker y empaquetado Windows aislado aprobados.)*
- [x] 5.2 Ejecutar revisión manual final en Web y Tkinter con evidencia visual y consola/red cuando corresponda. *(Web: 23 ejemplos, 12 mundos, 4 escenarios y 3 misiones; Tkinter: catálogo, 12 mundos y evidencia visual.)*
- [x] 5.3 Actualizar matriz de trazabilidad, informe de liberación y manuales con límites conocidos. *(Matriz, línea base e informe de preliberación actualizados con casos BLOCKED.)*
- [x] 5.4 Emitir decisión `apta`, `apta con observaciones` o `no apta` sin ocultar casos FAIL o BLOCKED. *(Decisión final: apta con observaciones; no quedan bloqueos críticos.)*
