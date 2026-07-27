# Diseño: correcciones QA de Tkinter

## Decisiones

1. La telemetría usará el ancho real disponible y puntos de ruptura explícitos;
   no dependerá de tamaños rígidos que recorten texto.
2. Los sensores ajustarán valores a varias líneas o usarán truncado controlado
   con tooltip; ningún texto escapará de su celda.
3. Brick reservará espacio para LCD y Robot/Estado. Con alto insuficiente,
   tendrá scroll vertical propio o composición responsive accesible.
4. Se registrarán todos los identificadores `after`/`after_idle` de layout.
   El cierre los cancelará antes de destruir la raíz y será idempotente.
5. El capturador producirá seis evidencias (3 resoluciones × 2 temas),
   registrará DPI y fallará ante mensajes Tcl de cierre.

## Verificación

- Pruebas de geometría: texto crítico dentro del área visible de cada celda.
- Pruebas de cierre con callback responsive pendiente.
- Capturas reales de Tkinter en las tres resoluciones y ambos temas.
- Recorridos `pywinauto` o manuales documentados únicamente desde un escritorio
  Windows realmente interactivo.
