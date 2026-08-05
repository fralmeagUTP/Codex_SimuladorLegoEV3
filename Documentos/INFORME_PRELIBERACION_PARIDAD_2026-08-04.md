# Informe de preliberación: paridad Web y Tkinter

**Cambio:** `cerrar-paridad-y-liberacion-ambas-apps`  
**Fecha de actualización:** 2026-08-05
**Entorno:** Windows, Python 3.12.5, Chrome 150.0.7871.188 y Edge 151.0.4129.59.  
**Commit base:** `63962e7` (`docs: registrar aprobacion de CI remoto`), más
la evidencia local de esta campaña.

## Decisión

**NO APTA PARA LIBERAR TODAVÍA.**

No existe un defecto crítico o alto confirmado en las campañas automatizadas
actuales. Sin embargo, no es posible declarar una liberación apta mientras haya
flujos críticos bloqueados: falta recorrido manual final de ambas interfaces y
la revisión manual final de ambas interfaces sigue pendiente.

## Evidencia aprobada

| Área | Evidencia | Resultado |
|---|---|---|
| Aplicación, UI, runtime, carga y contrato | `pytest tests/application tests/persistence tests/pybricks_api tests/shared tests/ui tests/release tests/runtime tests/load -q` | PASS: 392/392 en 37,96 s |
| Núcleo y dominio | `pytest tests/core tests/domain -q` | PASS: 243/243 en 0,84 s |
| Web backend y frontend | `pytest tests/web -q` | PASS: 137/137 en 14,22 s |
| Navegador Web real automatizado | `pytest tests/e2e/test_web_playwright.py -q` | PASS: 55/55 en 70,84 s |
| Escritorio gráfico real | `EV3_RUN_DESKTOP_E2E=1 pytest tests/e2e/test_desktop_pywinauto.py -q -rs` | PASS: 5/5 en 31,50 s |
| Calidad estática | Ruff, Mypy y Bandit medio/alto | PASS |
| CI remoto | GitHub Actions: flujos `calidad` y `tests` | PASS |
| Contenedor Linux | Build y smoke `/healthz` con variables efímeras de producción | PASS: imagen construida y HTTP 200 |
| Empaquetado Windows | Salida aislada `artifacts\qa-wheel\release-build`, recursos y arranque | PASS: EXE generado, Ejemplos/Mundos incluidos e inició correctamente |
| OpenSpec | `openspec validate cerrar-paridad-y-liberacion-ambas-apps --strict` | PASS |

## Correcciones verificadas en esta campaña

- **WEB-PAR-001:** el submenú de mundos ya permanece abierto al activarlo por
  clic, sin depender de hover; cubierto por regresión Playwright.
- **WEB-PAR-002:** el snapshot terminal ya actualiza de forma coherente el
  estado de sesión y la telemetría cuando el worker finaliza.
- **Cadencia de tiempo:** la prueba de espera admite exclusivamente hasta dos
  ticks de 20 ms de cuantización en el snapshot final, y mantiene el límite de
  duración de pared para detectar retrasos de renderizado.
- **Sandbox:** las excepciones Bandit para `exec` y `eval` son puntuales,
  justificadas y cubiertas por pruebas del runtime; no hay exclusión global de
  reglas de seguridad.

## Casos bloqueados y condición de cierre

| ID | Bloqueo | Riesgo | Acción necesaria |
|---|---|---|---|
| BLK-004 | Falta el recorrido manual exhaustivo de Tkinter en ambos temas y tamaños; el catálogo Web ya fue recorrido en navegador real. | La automatización no sustituye la experiencia de usuario. | Ejecutar y evidenciar el recorrido definido en `MATRIZ_PARIDAD_CIERRE_WEB_TKINTER.md` para escritorio. |

## Próxima decisión

Cuando se cierre BLK-004, se actualizará esta decisión a `apta` o
`apta con observaciones` según las incidencias restantes. La matriz detallada y
la evidencia técnica se conservan en `MATRIZ_PARIDAD_CIERRE_WEB_TKINTER.md` y
`LINEA_BASE_PARIDAD_2026-08-04.md`.
