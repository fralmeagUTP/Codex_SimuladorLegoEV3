# Informe de testeo integral Web — 2026-08-04

## Dictamen

**No apta para liberar.** La regresión automatizada aprobó, pero existen
defectos manuales críticos y altos que bloquean depuración, autoría de mundos,
sincronización de errores y ritmo de simulación.

## Entorno y evidencia

- Sistema: Windows.
- Aplicación manual: `http://127.0.0.1:5052/` (Waitress/Miniforge).
- Automatización: Python 3.12.5, Chromium Playwright y Pytest.
- Regresión consolidada: `186 passed in 72.05s` (`tests/web`, E2E Web y
  fallback polling/SSE).
- Resolución manual revalidada: 390×844; también se ejecutaron recorridos de
  escritorio Web. Tema claro y oscuro cubiertos por E2E y pruebas manuales.
- Evidencia detallada y comandos: `Documentos/EVIDENCIA_QA_TOTAL_WEB_2026-08-03/REPORTE_EJECUCION_PARCIAL.md`.

## Cobertura ejercitada realmente

- 23 ejemplos; 12 mundos preestablecidos; 4 escenarios; 3 misiones.
- Carga, ejecución y reinicio de mundos, escenarios y misiones.
- Controles de simulación: ejecución, pausa/reanudar, reinicio, pose, haces,
  zoom, trazas, fidelidad y límite temporal.
- Pybricks: éxito, sensor ultrasónico, movimiento, giro, sintaxis inválida,
  excepción, importación no soportada y cancelación.
- Sesiones, fallback SSE/polling, recuperación, carga paralela, responsive,
  tema, teclado y notificación de finalización.

## Hallazgos que bloquean la liberación

| ID | Severidad | Resultado observado |
| --- | --- | --- |
| WEB-DBG-018 | Crítica | Detener y reiniciar no cancela una ejecución iniciada con Depurar; sesión y menús quedan bloqueados. |
| WEB-WE-002 | Alta | Guardar como en Editor de Mundos falla con error de worker; CRUD manual bloqueado. |
| WEB-RT-011 | Alta | `1 / 0` deja barra en `running`, telemetría anterior y Ejecutar deshabilitado hasta reiniciar. |
| WEB-PERF-017 | Alta | Tiempo de pared entre 1,47× y 2,46× el tiempo simulado en esperas, avance, giro y radar. |
| WEB-TRACE-019 | Media | Avanzar un tick informa éxito sin modificar Tick visible. |
| WEB-RT-013 | Media | Tras recarga, Detener y reiniciar puede permanecer habilitado en `ready`. |

## Aspectos aprobados

- Mundos, escenarios y misiones vuelven a `created` tras un reinicio normal.
- Menús mutables se bloquean durante ejecución normal y se restauran al
  finalizar.
- El aviso Web de finalización se muestra una vez tras `finished`; no aparece
  en error o cancelación. La verificación nativa equivalente de Tkinter pasó.
- A 390×844 no se reprodujo el recorte de Haces ni el canvas de ancho fijo.

## Limitaciones pendientes

- CRUD manual completo de mundos queda bloqueado por WEB-WE-002.
- Las pestañas de exportación JSON/CSV fueron bloqueadas por el navegador
  integrado (`ERR_BLOCKED_BY_CLIENT`), aunque los comandos generaron las URL
  correctas.
- Se generaron 13 capturas reproducibles en
  `Documentos/EVIDENCIA_QA_TOTAL_WEB_2026-08-03/capturas_automatizadas`; no hay
  vídeo disponible en este entorno.

## Recomendación

Corregir los cinco hallazgos prioritarios, ejecutar de nuevo los casos manuales
afectados y regenerar capturas/HAR antes de considerar una nueva liberación.
