# Propuesta: corregir defectos bloqueantes de liberación Web

## Contexto

La campaña QA integral de 2026-08-04 concluyó que la aplicación Web no es apta
para liberar. Se confirmaron fallos en depuración, autoría de mundos, manejo de
errores terminales, ritmo temporal, trazas y recuperación de controles tras una
recarga. Los resultados y evidencia están en
`Documentos/INFORME_TESTEO_INTEGRAL_WEB_2026-08-04.md`.

## Objetivo

Corregir los defectos `WEB-DBG-018`, `WEB-WE-002`, `WEB-RT-011`,
`WEB-PERF-017`, `WEB-TRACE-019` y `WEB-RT-013`; establecer pruebas de regresión
y ejecutar una campaña de liberación reproducible en navegador real.

## Alcance

- Cancelación y reinicio fiables de depuración, incluido worker aislado.
- Propagación coherente de errores de script al estado terminal y a la UI.
- CRUD manual de mundos, incluida colocación de assets y validaciones.
- Cadencia de simulación coherente con `sim_time_s` y renderizado fluido sin
  alterar la semántica del runtime.
- Trazas que reflejen un avance de tick real o informen inequívocamente que no
  lo han realizado.
- Estados habilitado/deshabilitado correctos tras recarga.
- Pruebas de unidad, integración, E2E y manuales visibles que permitan un
  dictamen de liberación.

## Fuera de alcance

- No se rediseña la interfaz ni se cambian reglas de simulación o compatibilidad
  Pybricks salvo lo imprescindible para que los estados y tiempos sean correctos.
- No se usan datos, sesiones ni credenciales de producción.

## Resultado esperado

Una versión Web que complete los flujos afectados y una evidencia fechada que
permita clasificarla como `apta`, `apta con observaciones` o `no apta` con base
en casos realmente ejecutados.
