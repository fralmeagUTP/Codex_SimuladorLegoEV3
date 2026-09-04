# Propuesta: consistencia de sesión Web y diseño móvil

## Motivo

La campaña de QA Web identificó tres regresiones críticas para la experiencia
de aula: el estado terminal no se reflejaba de igual forma en editor, canvas,
LCD y telemetría; el reinicio podía conservar información de la ejecución
anterior; y a 390×844 el canvas y el control de haces excedían el viewport.

Aunque existen pruebas automatizadas de corrección, falta una revalidación
gráfica visible con navegador y DevTools para cerrar la evidencia de liberación.

## Cambio propuesto

Establecer una barrera de generación para snapshots durante reinicios, publicar
un snapshot terminal completo antes de cada estado terminal y hacer que la UI
Web aplique únicamente snapshots coherentes con la generación activa. Ajustar
la composición responsive de mapa y herramientas, y completar la campaña de
validación gráfica en las resoluciones y temas soportados.

## Fuera de alcance

- Cambiar las reglas físicas, semántica Pybricks o formato de mundos.
- Rediseñar la telemetría o la interfaz Tkinter.
- Añadir nuevas capacidades de simulación, sensores o misiones.

## Riesgo de no realizarlo

El alumnado puede ver una misión terminada como activa, interpretar datos
obsoletos como actuales o no poder utilizar controles esenciales desde móvil.
