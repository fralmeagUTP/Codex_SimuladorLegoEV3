# Tareas: corregir defectos bloqueantes de liberación Web

## Fase 1 — Reproducción y contratos

- [x] 1.1 Reproducir y congelar evidencia de los seis defectos, con sesión,
  generación, logs de worker, consola y red.
- [x] 1.2 Definir pruebas de contrato para transición `error`, cancelación de
  debug, reset, colocación de asset y avance de tick.
- [x] 1.3 Añadir telemetría de desfase pared/simulación y presupuesto de
  rendimiento para los flujos de referencia.

## Fase 2 — Sesión, runtime y depuración

- [x] 2.1 Unificar cancelación normal/debug y barrera de generación al reiniciar.
- [x] 2.2 Asegurar limpieza de worker, tareas pendientes y controles tras
  cancelación o timeout de cancelación.
- [x] 2.3 Propagar errores de script como `error` terminal con snapshot
  consistente y recuperación de controles.
- [x] 2.4 Derivar controles de la UI desde estado recuperado tras recarga.
- [x] 2.5 Añadir pruebas unitarias, de sesión y E2E para WEB-DBG-018,
  WEB-RT-011 y WEB-RT-013.

## Fase 3 — Autoría de mundos y trazas

- [x] 3.1 Corregir la resolución de worker/sesión al colocar assets en el Editor
  de mundos y mostrar errores recuperables.
- [x] 3.2 Implementar o reparar el CRUD manual: validar, guardar, recargar,
  editar, cancelar, duplicar y eliminar datos sintéticos.
- [x] 3.3 Hacer que Avanzar un tick produzca snapshot y tick incrementado, o
  deshabilitarlo fuera de un contexto válido sin mensaje de éxito falso.
- [x] 3.4 Añadir pruebas de contrato, API y E2E para WEB-WE-002 y WEB-TRACE-019.

## Fase 4 — Tiempo real y renderizado

- [x] 4.1 Perfilar la cola de runtime, frecuencia de snapshots, SSE/polling y
  requestAnimationFrame durante waits, avance, giro y radar.
- [x] 4.2 Corregir la causa del desfase sin violar el orden de snapshots ni la
  semántica Pybricks.
- [x] 4.3 Añadir pruebas deterministas de reloj y E2E de rendimiento con los
  umbrales definidos; registrar hardware/entorno.

## Fase 5 — Puerta de liberación

- [x] 5.1 Ejecutar Ruff, Mypy, Bandit, Pip-Audit y cobertura sin ocultar fallos.
- [x] 5.2 Ejecutar la suite Web, contratos, API, E2E Chromium y fallback
  SSE/polling; conservar resultados y artefactos.
- [x] 5.3 Ejecutar en navegador visible todos los menús, CRUD de mundos,
  depuración, errores, trazas, recarga, claro/oscuro y 390×844.
- [x] 5.4 Revalidar cada ID de defecto y actualizar sus estados a PASS, FAIL o
  BLOCKED con pasos, capturas, consola y HAR.
- [x] 5.5 Emitir informe de liberación: `apta` solo si no quedan defectos
  críticos/altos abiertos ni casos críticos BLOCKED; en otro caso documentar el
  dictamen real.
