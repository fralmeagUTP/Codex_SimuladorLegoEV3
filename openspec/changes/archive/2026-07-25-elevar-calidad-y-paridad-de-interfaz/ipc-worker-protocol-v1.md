# Protocolo IPC del worker aislado v1

## Objetivo

Separar la ejecución de scripts del proceso que hospeda Web o Tkinter, sin
cambiar los casos de uso ni el contrato `SnapshotDTO` de las interfaces.

## Transporte y envoltura

La implementación inicial usará `multiprocessing` con contexto `spawn`, válido
en Windows y Linux. Cada mensaje será un objeto JSON serializable:

```json
{
  "protocol_version": 1,
  "session_id": "uuid",
  "sequence": 12,
  "kind": "command|event",
  "type": "start",
  "payload": {}
}
```

- `sequence` es monotónica por emisor; el receptor descarta mensajes anteriores.
- Mensajes desconocidos, versiones incompatibles o payloads no serializables se
  rechazan con un evento `error` de código `IPC_PROTOCOL_ERROR`.
- El proceso principal es autoritativo para el estado de sesión; el worker es
  autoritativo para ejecución, snapshot y contexto de depuración.

## Comandos al worker

| Tipo | Payload mínimo | Resultado |
| --- | --- | --- |
| `initialize` | `engine_config`, `execution_policy` | `ready` con snapshot inicial |
| `load_script` | `source` | `loaded` |
| `start` | `debug`, `step_mode` | `status: running` |
| `pause`, `resume`, `stop`, `reset` | ninguno | evento de estado correspondiente |
| `set_debug` | `breakpoints`, `watches` | `debug_configured` |
| `debug_continue`, `debug_step` | ninguno | `debug_command` con la accion aplicada |
| `set_robot_start` | `x_mm`, `y_mm`, `theta_deg` | snapshot actualizado |
| `load_world` | `source` con JSON validado | `world_loaded` y snapshot |
| `load_blank_world` | `width_mm`, `height_mm` | `world_loaded` |
| `shutdown` | `reason` | confirmación y salida limpia |

Todos los comandos incluyen un `command_id`; su respuesta o error debe incluir
el mismo identificador para permitir idempotencia y correlación.

## Eventos del worker

| Tipo | Payload |
| --- | --- |
| `snapshot` | `snapshot_version`, `snapshot_generation`, snapshot serializable |
| `status` | uno de `SessionStatus`, razón opcional |
| `debug` | línea, stack, locales permitidos y watches evaluados |
| `error` | `code`, mensaje seguro, traceback sólo para diagnóstico local |
| `heartbeat` | uso de recursos y último tick |
| `terminated` | razón `finished`, `stopped`, `timed_out`, `resource_limit` o `crashed` |

El evento `finished` debe preceder a `terminated`; el proceso principal conserva
el último snapshot y los eventos hasta que la UI solicite reset o cierre.

## Cancelación y recuperación

1. `stop` solicita cancelación cooperativa y espera el presupuesto configurado.
2. Si no llega `terminated`, el proceso principal termina el worker y publica
   `stopped`; si venció un límite publica `timed_out`.
3. Una salida inesperada publica `error` con `WORKER_CRASHED`; reiniciar crea un
   worker nuevo desde el último mundo, script y configuración persistidos.
4. Nunca se reinyecta un comando ya confirmado sin su `command_id` original.

## Compatibilidad

El feature flag `EV3_WORKER_ISOLATION_ENABLED=false` conserva temporalmente el
runtime actual. Ambos caminos deben emitir los mismos `SessionStatus`, snapshots
y eventos de depuración, cubiertos por pruebas de contrato.
