# Tareas: corregir regresiones funcionales QA

- [x] 1. Reproducir y localizar TK-005, TK-006, TK-007 y TK-008.
- [x] 2. Hacer que `wait()` respete pausa, reanudación y cancelación.
- [x] 3. Registrar snapshots emitidos por el worker aislado en la traza.
- [x] 4. Sincronizar el nombre visible del mundo cargado.
- [x] 5. Centrar Acerca de respecto a la ventana principal.
- [x] 6. Añadir pruebas unitarias, de UI y de integración con worker real.
- [x] 7. Repetir la validación visual manual de pausa, trazas, mundos y Acerca de.
  - [x] 7.1 Ejecutar E2E nativo con `EV3_RUN_DESKTOP_E2E=1` en una sesión Windows que exponga el escritorio al proceso de pruebas. *(2026-07-30: 4/4 aprobadas en 17.60 s. La suite detecta la ventana Tk creada por el proceso hijo del lanzador y limpia su árbol al finalizar.)*
  - [x] 7.2 Validar visualmente pausa/reanudación con script multilineal real y cierre limpio.
  - [x] 7.3 Validar registro y exportación JSON de trazas desde la interfaz real.
  - [x] 7.4 Validar que el encabezado identifica el mundo preestablecido cargado.
  - [x] 7.5 Validar que Acerca de abre sobre la ventana principal y cierra limpiamente.
- [x] 8. Actualizar la decisión de liberación después de la validación manual.
