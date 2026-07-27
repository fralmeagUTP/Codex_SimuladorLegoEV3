# Tareas: corregir regresiones QA de Tkinter

## Fase 1 — Diagnóstico

- [x] 1.1 Reproducir TK-001, TK-002 y TK-003 en tres resoluciones y dos temas.
- [x] 1.2 Registrar dimensiones efectivas de `PanedWindow`, telemetría, Brick y LCD.
- [x] 1.3 Extender el capturador con resolución y captura de errores Tcl.

## Fase 2 — Layout responsive

- [x] 2.1 Definir puntos de ruptura de telemetría y eliminar truncamiento.
- [x] 2.2 Ajustar valores extensos de sensores con wrap/tooltip accesible.
- [x] 2.3 Reservar o hacer alcanzable Robot/Estado junto a LCD.
- [x] 2.4 Validar contraste y distribución en claro y oscuro.

## Fase 3 — Cierre seguro

- [x] 3.1 Registrar callbacks de resize, layout e idle.
- [x] 3.2 Cancelarlos de forma segura e idempotente antes de destruir la raíz.
- [x] 3.3 Ejecutar capturador sin mensajes Tcl.

## Fase 4 — Regresión y evidencia

- [x] 4.1 Añadir pruebas de geometría en 1024×768, 1280×800 y 1920×1080.
- [x] 4.2 Añadir prueba de accesibilidad de Robot/Estado bajo la LCD.
- [x] 4.3 Añadir prueba de cierre con callback pendiente.
- [x] 4.4 Generar y comparar seis capturas reproducibles.
- [x] 4.5 Actualizar informe QA con resultados honestos.

## Fase 5 — Validación interactiva pendiente

- [ ] 5.1 Ejecutar intro, menús, diálogos, mundos, misiones, scripts y controles en sesión Windows visible.
  - [x] 5.1.1 Validar intro, temas, menús, Manual, Acerca de y Editor de mundos con entrada visible.
  - [x] 5.1.2 Validar ejecución, error de sintaxis, tiempo máximo, controles de canvas y reinicio.
  - [x] 5.1.3 Registrar fallos reproducibles de Reanudar, trazas y sincronización del nombre de mundo.
  - [ ] 5.1.4 Completar crear/guardar/cargar/editar/eliminar mundos con rutas temporales aisladas.
    - [x] 5.1.4a Crear y guardar un mundo temporal; validar su JSON.
    - [ ] 5.1.4b Confirmar recarga, edición y eliminación con estado visible y sin afectar mundos de usuario.
  - [ ] 5.1.5 Ejecutar misiones con resultado de éxito, fallo y cancelación; comprobar sus criterios.
- [ ] 5.2 Adjuntar evidencia desde código fuente y ejecutable empaquetado.
  - [x] 5.2.1 Adjuntar evidencia visual de intro y flujo fuente; validar el artefacto PyInstaller.
  - [ ] 5.2.2 Capturar visualmente intro y ventana principal desde el ejecutable empaquetado.
- [ ] 5.3 Cambiar decisión de liberación solo después de 5.1 y 5.2.
