# Registro de defectos de paridad MMI

Este registro conserva diferencias encontradas durante el cambio OpenSpec
`igualar-madurez-integral-web-tkinter`. Cada fila requiere evidencia
reproducible y una regresión automatizada o un protocolo manual explícito.

| ID | Severidad | Plataforma | Estado | Evidencia y corrección | Regresión |
|---|---|---|---|---|---|
| MMI-WEB-001 | Alta | Web | Corregido | Después de `Detener y reiniciar`, `SimulationSession.reset()` usaba `get_snapshot()`, que avanza el motor un tick; el estado visible podía mostrar tick 1 en lugar del estado inicial. Se sustituyó por `current_snapshot()`, una lectura sin avance. | `tests/shared/test_interface_execution_parity.py::test_web_and_desktop_reset_restore_the_configured_robot_start_snapshot` |
| MMI-WEB-002 | Media | Web / worker | Corregido | La captura Web cerró una sesión mientras su stream SSE seguía leyendo eventos; `drain_events()` propagaba `ValueError` al encontrar una cola IPC ya cerrada y Werkzeug registraba un error de solicitud. El drenaje ahora reconoce el cierre normal como cola vacía. | `tests/runtime/test_isolated_worker.py::test_isolated_worker_ignores_a_queue_closed_during_session_shutdown` |
| MMI-WEB-003 | Alta | Web / worker | Corregido | Tras recuperar un worker, la sesión conservaba la secuencia IPC del proceso anterior y descartaba eventos válidos del nuevo proceso. Además, su política podía volver al límite global en vez del valor configurado por el usuario. La recuperación ahora inicia una nueva secuencia IPC y repone el límite propio de sesión. | `tests/runtime/test_isolated_worker.py::test_web_session_recovery_preserves_its_configured_runtime_limit` |
| MMI-DESK-001 | Alta | Tkinter / sesión local | Corregido | `DesktopSessionAdapter.presentation_state()` podía conservar `created` después de cancelar una ejecución local, aunque el motor ya estuviera detenido. El adaptador ahora registra cada transición local y reenvía el callback de estado a la UI. | `tests/shared/test_interface_execution_parity.py::test_web_and_desktop_cancel_expose_the_same_terminal_presentation_state` |

## Reproducción de MMI-WEB-001

1. Crear una sesión Web y cargar un mundo vacío.
2. Definir una posición inicial distinta de la predeterminada.
3. Ejecutar **Detener y reiniciar**.
4. Consultar el snapshot visible de la sesión.

Resultado corregido: Web y Tkinter informan la misma pose inicial, `tick = 0`,
`sim_time_s = 0.0` y LCD sin líneas. La regresión se ejecutó el 2026-08-23 con
Python 3.12.5 y runtime local de pruebas; el worker aislado queda cubierto por
la suite de resiliencia pendiente de la tarea 4.4.

## Reproducción de MMI-WEB-003

1. Crear una sesión Web aislada con límite de 30 segundos.
2. Configurar el límite de la sesión en 300 segundos.
3. Forzar `recover_worker()`.
4. Revisar la política confirmada por el nuevo worker.

Resultado corregido: la política restaurada conserva `max_runtime_s = 300` y
los eventos iniciales del nuevo proceso se procesan como pertenecientes a la
nueva secuencia IPC.

## Política de cierre

- Un defecto crítico o alto no puede declararse cerrado sin reproducirlo y
  ejecutar su regresión.
- Las diferencias exclusivas de una plataforma se registran como `N/A` con una
  adaptación equivalente documentada, no como un PASS implícito.
- Los fallos de infraestructura de pruebas se registran como `BLOCKED`; no se
  interpretan como un PASS del producto.
