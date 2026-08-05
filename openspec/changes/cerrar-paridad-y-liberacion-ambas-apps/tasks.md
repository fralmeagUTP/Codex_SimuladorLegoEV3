## 1. Línea base y catálogo de paridad

- [x] 1.1 Inventariar todas las capacidades visibles y API de Web y Tkinter, marcando aplicabilidad y propietario.
- [x] 1.2 Definir matriz de paridad con oráculos de dominio, sesión y presentación para cada flujo crítico.
- [x] 1.3 Registrar entornos soportados: Windows/Tkinter, Chrome o Edge, resoluciones, temas y versiones de Python.

## 2. Diagnóstico reproducible

- [ ] 2.1 Ejecutar campañas reales Web y Tkinter contra un commit limpio y registrar evidencia de cada caso crítico.
- [ ] 2.2 Clasificar todos los hallazgos por severidad, impacto y reproducibilidad; crear regresión viable por defecto confirmado. *(WEB-PAR-001 corregido y cubierto; falta cerrar todo el catálogo.)*
- [x] 2.3 Medir latencia de controles, cadencia de snapshots/renderizado y coherencia de tiempo de simulación en Web. *(Playwright y control de interpolación aprobados; se admite como máximo dos ticks de cuantización en el snapshot terminal.)*
- [ ] 2.4 Verificar flujos de worker, recarga, eventos tardíos, cancelación, límite de tiempo y recuperación de sesión. *(Cobertura automatizada Web aprobada; pendiente verificación manual de catálogo.)*

## 3. Corrección de paridad y experiencia

- [ ] 3.1 Corregir divergencias de resultados de dominio o snapshot entre ambas UI antes de ajustes visuales. *(WEB-PAR-002 corregido y validado; quedan por descubrir/cerrar las demás brechas.)*
- [ ] 3.2 Corregir problemas confirmados de controles, menús, diálogos, telemetría, LCD, canvas, robot y trazas. *(WEB-PAR-001 corregido; faltan resultados de campaña completa.)*
- [ ] 3.3 Asegurar temas, teclado, foco, contraste, redimensionamiento y móvil Web en los entornos definidos.
- [ ] 3.4 Documentar o adaptar toda diferencia no aplicable por plataforma.

## 4. Automatización y compuertas

- [x] 4.1 Implementar pruebas de contrato de paridad para estados iniciar, pausar, reanudar, terminal y reiniciar. *(17/17 contratos de sesión y adaptador de escritorio aprobados.)*
- [x] 4.2 Ampliar Playwright para catálogo Web, resoluciones, tema, depuración, mundos y sesiones aisladas.
- [x] 4.3 Ampliar pywinauto para menú, ejecución, reinicio, tema, mundo y telemetría Tkinter. *(5/5 E2E nativas PASS en 31,50 s.)*
- [x] 4.4 Configurar compuerta CI de lint, tipos, seguridad, cobertura, contratos y E2E por plataforma. *(GitHub Actions aprobó los flujos `calidad` y `tests` del commit actual.)*

## 5. Validación de liberación

- [x] 5.1 Ejecutar las suites obligatorias y registrar comandos, versiones, duración y resultados por commit. *(Campaña local por capas aprobada: 392 + 243 + 137 + 55 + 5; contenedor Docker y empaquetado Windows aislado aprobados.)*
- [ ] 5.2 Ejecutar revisión manual final en Web y Tkinter con evidencia visual y consola/red cuando corresponda.
- [x] 5.3 Actualizar matriz de trazabilidad, informe de liberación y manuales con límites conocidos. *(Matriz, línea base e informe de preliberación actualizados con casos BLOCKED.)*
- [x] 5.4 Emitir decisión `apta`, `apta con observaciones` o `no apta` sin ocultar casos FAIL o BLOCKED. *(Informe de preliberación: `no apta` hasta cerrar BLK-001 a BLK-004.)*
