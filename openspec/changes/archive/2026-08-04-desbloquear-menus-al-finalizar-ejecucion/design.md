# Diseño: política de disponibilidad de menús por estado de sesión

## Decisión

La disponibilidad de los menús se derivará exclusivamente del estado público de la sesión de simulación. No dependerá de temporizadores de la interfaz, del texto visible en la barra de estado ni de si una operación anterior llamó manualmente a un método de desbloqueo.

La predicación compartida es:

```text
ejecución_activa = estado en {running, paused}
menús_bloqueados = ejecución_activa
```

| Estado de sesión | Menús de contexto |
| --- | --- |
| `created`, `ready`, `reset` | Habilitados |
| `running`, `paused` | Deshabilitados |
| `finished`, `stopped`, `timed_out`, `error` | Habilitados |

## Adaptación Web

`simulation_app.js` centralizará la predicación en una función con nombre explícito, invocada desde el procesamiento de cada snapshot o evento de estado. La actualización debe afectar los botones y subopciones de menú, así como los manejadores que impiden acciones programáticas durante el bloqueo.

La implementación no debe conservar un bloqueo heredado de `finished`, `timed_out` o `stopped`. Un evento terminal repetido debe dejar el mismo resultado: los menús habilitados.

## Adaptación Tkinter

`MainWindow` calculará el bloqueo desde el mismo conjunto de estados al recibir `_on_status`. Los menús y comandos registrados deberán recibir el estado calculado en el hilo de interfaz mediante `after_idle` cuando corresponda.

No se introducirán actualizaciones directas de widgets desde hilos de ejecución. Las operaciones de reset conservarán la reactivación, pero esta será consecuencia de la política de estado y no una excepción aislada.

## Seguridad de interacción

Durante `running` o `paused`, la interfaz debe rechazar tanto clics como invocaciones de comandos de menú que cambien el contexto. El bloqueo no debe impedir los controles propios de la sesión: pausar, reanudar o detener y reiniciar.

Una vez terminal, los comandos deben poder abrir sus diálogos o cargar el recurso solicitado sin necesitar recargar la aplicación.

## Pruebas

Las pruebas validarán la matriz completa para Web y Tkinter. La regresión Web debe ejercitar una ejecución real que finalice naturalmente y confirmar que al menos Archivo, Ejemplos y Mundos vuelven a estar disponibles. La prueba Tkinter validará la misma transición a través de su adaptador de estado y sus comandos registrados.

