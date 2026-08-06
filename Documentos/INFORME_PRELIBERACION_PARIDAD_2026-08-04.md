# Informe final de liberación: paridad Web y Tkinter

**Cambio:** `cerrar-paridad-y-liberacion-ambas-apps`  
**Fecha de actualización:** 2026-08-05
**Entorno:** Windows, Python 3.12.5, Chrome 150.0.7871.188 y Edge 151.0.4129.59.  
**Rama:** `codex/desbloquear-menus-al-finalizar-ejecucion`

## Decisión

**APTA CON OBSERVACIONES.**

No quedan defectos críticos o altos ni bloqueos abiertos en el alcance del
cambio. Las campañas automatizadas, los recorridos gráficos reales de Web y
Tkinter, el contenedor Linux y el paquete Windows aprobaron. La observación
residual es una limitación de automatización: los menús owner-drawn de Tkinter
no exponen de manera estable su ventana emergente a Win32. La regresión verifica
por ello el estado aplicado y ejecuta físicamente un comando real del menú; no
es un defecto confirmado del producto.

## Evidencia aprobada

| Área | Evidencia | Resultado |
|---|---|---|
| Suite global | `pytest -q` | PASS: 829, 6 omitidas por compuerta gráfica, 111,87 s |
| Escritorio gráfico real | `EV3_RUN_DESKTOP_E2E=1 pytest tests/e2e/test_desktop_pywinauto.py -q -rs` | PASS: 6/6 en 34,84 s |
| Navegador Web real automatizado | `pytest tests/e2e/test_web_playwright.py -q` | PASS: 55/55 |
| Catálogo Web manual | 23 ejemplos, 12 mundos, 4 escenarios y 3 misiones | PASS: 42/42 recursos |
| Catálogo Tkinter real | 23 ejemplos y 12 mundos preestablecidos | PASS: 35/35 recursos |
| Navegación Tkinter | Ejecución, pausa, reinicio, depuración, ayuda, editor de mundos y menús | PASS |
| Diseño Tkinter | Claro/oscuro; 1920×1080, 1280×800, 1024×768; editor 1320×860 | PASS |
| Calidad estática | Ruff y Mypy global (109 archivos fuente) | PASS |
| CI remoto anterior | GitHub Actions: `calidad` y `tests` | PASS |
| Contenedor Linux | Build y smoke `/healthz` como usuario `ev3` | PASS: HTTP 200 |
| Empaquetado Windows | PyInstaller aislado, recursos y arranque | PASS |
| OpenSpec | Validación estricta del cambio | PASS |

## Correcciones y riesgos revalidados

- El snapshot terminal mantiene coherentes editor, canvas, LCD, telemetría y
  estado de sesión.
- `Detener y reiniciar` restaura la sesión y vuelve a habilitar los menús.
- Los menús permanecen bloqueados durante la ejecución y recuperan sus comandos
  tanto después del reinicio como de una finalización natural.
- El catálogo de mundos Tkinter se recorrió mediante interacción física, 12/12.
- La Web mantiene navegación, tema oscuro, diseño móvil 390×844 y notificación
  única de finalización sin errores de consola.
- La cadencia temporal conserva la tolerancia máxima documentada de dos ticks
  de 20 ms y el control de duración de pared.

## Bloqueos

**Ninguno.** `BLK-004` queda cerrado con la campaña Tkinter real, la evidencia
visual multirresolución y la regresión estable de bloqueo/desbloqueo de menús.

## Recomendación de publicación

El cambio puede integrarse y liberarse. Como mejora no bloqueante, conviene
mantener el E2E nativo en un runner Windows con escritorio interactivo y vigilar
las carreras de enumeración de ventanas ajenas al proceso probado.
