# Propuesta: desbloquear menús al finalizar la ejecución

## Motivo

La aplicación debe impedir que el usuario cambie el contexto de una simulación mientras un script está ejecutándose o pausado. La comprobación funcional realizada en la Web confirmó que los menús se bloquean durante la ejecución y se reactivan al usar **Detener y reiniciar**, pero permanecen bloqueados después de que un script termina normalmente. Tkinter contiene una política de estados equivalente, por lo que puede presentar la misma regresión.

Esto deja a la persona usuaria sin acceso a ejemplos, mundos, escenarios o misiones después de una ejecución correcta, hasta que realiza una acción adicional de reinicio.

## Cambio propuesto

- Establecer una política única de bloqueo para las interfaces Web y Tkinter.
- Bloquear los comandos de menú mientras la sesión esté en los estados activos `running` o `paused`.
- Reactivar los comandos al llegar a un estado terminal o preparado: `created`, `ready`, `finished`, `stopped`, `timed_out`, `error` o `reset`.
- Aplicar la política de forma idempotente ante eventos de estado repetidos o recibidos tarde.
- Añadir regresiones automatizadas y una verificación funcional para los flujos de ejecución, finalización y reinicio.

## Alcance

Se incluyen las opciones de menú que cambian o cargan el contexto de la sesión: Archivo, Ejemplos, Mundos, Escenarios, Misiones, Tema, Fidelidad, Tiempo máximo y Trazas. Ayuda puede permanecer disponible únicamente si no altera la sesión; la decisión debe ser idéntica en Web y Tkinter y quedar cubierta por prueba.

No se modifica el motor de simulación, la compatibilidad Pybricks ni las reglas de ejecución de scripts.

## Evidencia inicial

En una sesión real de navegador se observó lo siguiente:

| Flujo | Resultado observado |
| --- | --- |
| Script en ejecución | Menús bloqueados (correcto) |
| Detener y reiniciar | Menús reactivados (correcto) |
| Finalización natural mediante `wait(100)` | Menús siguen bloqueados (defecto) |

