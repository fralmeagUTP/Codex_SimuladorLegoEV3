## ADDED Requirements

### Requirement: Telemetría Tkinter responsive y legible

La interfaz Tkinter DEBERÁ mantener la telemetría legible en 1024×768,
1280×800 y 1920×1080, en tema claro y oscuro. Ninguna etiqueta, valor,
encabezado o estado crítico podrá quedar recortado, solapado o fuera de su
celda visible.

#### Scenario: Ancho reducido de telemetría

- DADO un panel cuyo ancho no permite el diseño preferido
- CUANDO Tkinter recalcula el layout
- ENTONCES DEBERÁ aplicar reflujo, punto de ruptura o scroll interno accesible
  antes de recortar texto
- Y los valores extensos deberán conservar acceso completo mediante ajuste o
  tooltip.

### Requirement: Estado del robot accesible desde Brick

El panel EV3 Brick DEBERÁ mostrar o permitir alcanzar claramente la tabla
Robot/Estado junto con la LCD, sin deformar esta última.

#### Scenario: Alto reducido de Brick

- DADO que la altura disponible no permite mostrar LCD y Robot/Estado a la vez
- CUANDO se renderiza el Brick
- ENTONCES el panel DEBERÁ proporcionar scroll vertical independiente o una
  composición responsive
- Y X, Y y Theta deberán permanecer accesibles.

### Requirement: Cierre Tkinter libre de callbacks pendientes

La ventana Tkinter DEBERÁ cancelar de forma segura callbacks de layout, resize
e idle antes de destruir la raíz; el cierre deberá ser idempotente.

#### Scenario: Cierre con layout pendiente

- DADO un callback responsive programado
- CUANDO el usuario o el capturador cierra la ventana
- ENTONCES no DEBERÁ aparecer un error Tcl ni una invocación contra widgets
  destruidos.
