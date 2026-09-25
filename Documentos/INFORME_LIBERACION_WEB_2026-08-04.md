# Informe de liberación Web — 2026-08-04

## Dictamen

**No apta para liberar todavía en el servidor oficial.**

La versión de trabajo corregida supera la validación automatizada y las
revalidaciones visibles dirigidas. Sin embargo, las correcciones aún no están
desplegadas en la instancia oficial `http://127.0.0.1:5052/`, atendida por un
proceso Waitress/Miniforge distinto de la instancia limpia usada para validar.
No es correcto certificar la aplicación que el usuario tiene abierta hasta
reiniciar o desplegar ese servicio y repetir los casos de humo indicados.

## Entorno validado

- Código: rama `codex/desbloquear-menus-al-finalizar-ejecucion`, base
  `9708d1e` más los cambios no confirmados de esta campaña.
- Sistema: Windows; Python 3.12.5; Chromium Playwright.
- Instancia aislada de verificación: `http://127.0.0.1:5054/`, con
  `EV3_WORKER_ISOLATION_ENABLED=true`.
- Instancia oficial pendiente de despliegue: `http://127.0.0.1:5052/`.

## Casos revalidados en interfaz real

| ID | Resultado | Evidencia observada |
| --- | --- | --- |
| WEB-DBG-018 | PASS | Breakpoint pausa el tick; reiniciar devuelve la sesión a `created` y recupera controles. |
| WEB-WE-002 | PASS parcial | Se colocaron Robot y Muro, se validó y aplicó el mundo sin fallo de worker. El guardado con `prompt` nativo fue ejercitado por E2E Chromium; el navegador integrado no admite ese diálogo. |
| WEB-RT-011 | PASS | `1 / 0` llega a `error` y la interfaz recupera los controles. |
| WEB-PERF-017 | PASS | `wait(2000)` terminó con 2.10 s simulados en 2.32 s de pared (relación 1.11). |
| WEB-TRACE-019 | PASS | Una sesión nueva pasó de Tick 0 a Tick 1 y anunció el avance real. |
| WEB-RT-013 | PASS automatizado | La recarga de estados terminales y la restauración de controles aprobaron en E2E. |

También se verificó que un evento `ready` tardío ya no desbloquea los menús
mutables durante una ejecución activa.

## Ejecución automatizada

| Verificación | Resultado |
| --- | --- |
| Runtime aislado + Web + E2E Chromium | 221 PASS en 84.22 s |
| Cobertura Web | 81.83 %; umbral 70 % alcanzado |
| Ruff | PASS |
| Mypy de `simulador_ev3` | PASS, 114 archivos |
| Bandit | Sin hallazgos altos; 2 medios controlados por diseño (`exec` del sandbox) y 54 bajos históricos |
| Pip-Audit | Sin vulnerabilidades conocidas |
| OpenSpec | Validación estricta PASS |

## Correcciones incorporadas

1. La sesión aislada recibe su snapshot inicial desde el worker; el primer
   paso de trazas ya no compara dos ticks idénticos.
2. El stream SSE sondea la cola del worker cada 50 ms, en vez de demorar hasta
   un segundo el estado o snapshot nuevo.
3. La entrega de snapshots del worker se limita a 30 Hz y el navegador conserva
   la interpolación visual mediante `requestAnimationFrame`.
4. Los estados base retrasados (`ready`/`created`) no pueden desbloquear menús
   mientras la generación actual está ejecutándose.

## Condición para aprobar la liberación

1. Desplegar o reiniciar el proceso oficial de `5052` con este árbol de trabajo
   y las mismas dependencias de `.venv`.
2. Repetir en esa URL: depuración con breakpoint/reinicio, error `1 / 0`,
   guardado de mundo, tick de trazas, `wait(2000)`, menús durante ejecución y
   viewport 390×844.
3. Si esos siete humos pasan sin errores de consola o red, el dictamen puede
   actualizarse a **apta con observaciones**.

No se usaron datos productivos ni credenciales reales.
