# Registro de defectos MMI — 2026-08-23

Este registro conserva las diferencias encontradas durante el cambio
`igualar-madurez-integral-web-tkinter`, su severidad, evidencia y regresión.
No incluye fallos del arnés de prueba como defectos del producto.

| ID | Severidad | Diferencia observada | Causa raíz | Corrección | Evidencia de regresión | Estado |
|---|---|---|---|---|---|---|
| MMI-001 | Media | En modo local, `DesktopSessionAdapter.presentation_state()` podía permanecer en `running` tras un error de programa, mientras Web publicaba `error`. | El adaptador delegaba el callback de error al servicio sin normalizar su estado de presentación. | Se añadió `_on_service_error` y `set_error_callback` al adaptador; normaliza `error` y `timed_out` antes de notificar a la UI. | `tests/shared/test_interface_execution_parity.py::test_web_and_desktop_runtime_errors_expose_the_same_terminal_presentation_state` | Corregido / PASS |

## Incidencias del arnés, sin defecto de producto

- El recorrido Tkinter de catálogo identificó que las coordenadas fijas de los
  menús son frágiles. El arnés ahora obtiene la geometría de los botones reales
  una vez la ventana está mapeada y convierte su posición al rectángulo Win32.
- El recorrido Web de mundos identificó que el submenú conserva su estado entre
  aperturas. El arnés consulta `aria-expanded` antes de alternarlo; no se
  modificó el comportamiento de la aplicación.

Ambas incidencias disponen de ejecución aprobada en
`Documentos/MATRIZ_E2E_MMI_2026-08-23.md`.
