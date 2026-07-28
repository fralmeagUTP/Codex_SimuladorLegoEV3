# Diseño: sistema visual único

## Fuente de verdad

La Web define tokens semánticos: fondo, superficie, texto, primario, peligro, éxito, foco, borde, tipografía, espaciado y estados. Se publicará una tabla de mapeo CSS a Tkinter (`bg`, `fg`, `activebackground` y estilos ttk).

## Composición

Ambas UI presentan el mismo orden: barra de simulación, mundo, editor y depuración, telemetría/brick, y menús de tema, fidelidad, trazas y ayuda. Las diferencias se limitan al renderizado nativo.

## Verificación

Pruebas de catálogo, tokens y estados; capturas patrón en tamaño de referencia y comparación visual con tolerancia documentada.
