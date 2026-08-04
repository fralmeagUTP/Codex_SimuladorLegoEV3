# Matriz de trazabilidad — QA total Web

| Requisito | Riesgo | Casos | Automatización | Evidencia manual | Estado |
|---|---|---|---|---|---|
| Navegación y menús completos | Alto | MAN-WEB-MENU-* | E2E menús | Captura/consola por comando | Pendiente |
| Ejemplos, mundos, escenarios y misiones | Crítico | MAN-WEB-CAT-* | E2E/API catálogo | Snapshot terminal por elemento | Pendiente |
| Ejecución, pausa, reanudar y reinicio | Crítico | MAN-WEB-RUN-* | pruebas Web/E2E | Canvas, LCD y telemetría | Pendiente |
| Depuración | Alto | MAN-WEB-DBG-* | E2E depuración | Breakpoint, paso, watches | Pendiente |
| Autoría y persistencia de mundos | Crítico | MAN-WEB-WORLD-* | integración editor/API | CRUD aislado | Pendiente |
| Sesiones y multiusuario | Crítico | WEB-SESSION-* | contratos/concurrencia | Dos contextos reales | Pendiente |
| Tiempo real y renderizado | Alto | WEB-TIME-* | unidad/E2E/rendimiento | Reloj, ticks, frames | Pendiente |
| Seguridad y resiliencia | Alto | WEB-SEC-*, WEB-REC-* | estático/API/carga | Logs y red | Pendiente |
| Accesibilidad y responsive | Medio | MAN-WEB-A11Y-* | E2E | Escritorio/móvil, claro/oscuro | Pendiente |
