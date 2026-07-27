# Tareas: corregir regresiones QA de Tkinter

## Fase 1 — Diagnóstico

- [ ] 1.1 Reproducir TK-001, TK-002 y TK-003 en tres resoluciones y dos temas.
- [ ] 1.2 Registrar dimensiones efectivas de `PanedWindow`, telemetría, Brick y LCD.
- [ ] 1.3 Extender el capturador con resolución, DPI y captura de errores Tcl.

## Fase 2 — Layout responsive

- [ ] 2.1 Definir puntos de ruptura de telemetría y eliminar truncamiento.
- [ ] 2.2 Ajustar valores extensos de sensores con wrap/tooltip accesible.
- [ ] 2.3 Reservar o hacer alcanzable Robot/Estado junto a LCD.
- [ ] 2.4 Validar contraste y distribución en claro y oscuro.

## Fase 3 — Cierre seguro

- [ ] 3.1 Registrar callbacks de resize, layout e idle.
- [ ] 3.2 Cancelarlos de forma segura e idempotente antes de destruir la raíz.
- [ ] 3.3 Ejecutar capturador sin mensajes Tcl.

## Fase 4 — Regresión y evidencia

- [ ] 4.1 Añadir pruebas de geometría en 1024×768, 1280×800 y 1920×1080.
- [ ] 4.2 Añadir prueba de accesibilidad de Robot/Estado bajo la LCD.
- [ ] 4.3 Añadir prueba de cierre con callback pendiente.
- [ ] 4.4 Generar y comparar seis capturas reproducibles.
- [ ] 4.5 Actualizar informe QA con resultados honestos.

## Fase 5 — Validación interactiva pendiente

- [ ] 5.1 Ejecutar intro, menús, diálogos, mundos, misiones, scripts y controles en sesión Windows visible.
- [ ] 5.2 Adjuntar evidencia desde código fuente y ejecutable empaquetado.
- [ ] 5.3 Cambiar decisión de liberación solo después de 5.1 y 5.2.
