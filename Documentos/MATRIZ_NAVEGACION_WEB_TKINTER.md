# Matriz de navegación y atajos Web–Tkinter

El orden funcional común del menú es:

`Archivo → Ejemplos → Mundos → Escenarios → Misiones → Tema → Fidelidad → Tiempo máximo → Trazas → Ayuda`.

| Acción | Web | Tkinter | Resultado esperado |
| --- | --- | --- | --- |
| Ejecutar | `F5` | `F5` | Inicia el programa si no hay ejecución activa. |
| Pausar / reanudar | `F6` | `F6` | Alterna el estado activo de la simulación. |
| Detener y reiniciar | `Shift+F5` | `Shift+F5` | Detiene, limpia y restaura el mundo activo. |
| Ayuda | `F1` | `F1` | Abre el centro de ayuda correspondiente. |
| Nuevo / abrir / guardar | `Ctrl+N`, `Ctrl+O`, `Ctrl+S` | `Ctrl+N`, `Ctrl+O`, `Ctrl+S` | Opera sobre el programa actual. |
| Cerrar diálogo | `Escape` | `Escape` | Cierra el diálogo o menú auxiliar activo. |

Durante `running` o `paused`, los menús que modifican sesión se deshabilitan.
Al finalizar, fallar, detener o reiniciar, recuperan su disponibilidad.
