# Informe de evaluación de menús

## Alcance

Revisión de la navegación web y de los controles equivalentes del editor de escritorio, contrastando el nombre de cada opción con la acción implementada y su valor para el usuario final.

## Hallazgos

| Opción | Evaluación | Recomendación |
|---|---|---|
| Archivo | Útil: crear, abrir y guardar scripts. | Mantener; añadir indicador de cambios sin guardar y confirmación al reemplazar código. |
| Ejemplos | Útil, pero contiene 24 entradas técnicas y se solapa con Escenarios. | Mantener como biblioteca completa; agrupar por nivel y tema. |
| Mundos | Útil para cargar, crear y seleccionar mapas. | Mantener; separar claramente “Editor”, “En blanco” y “Preestablecidos”. |
| Escenarios | Parcialmente redundante: cada escenario carga simultáneamente un mundo y un ejemplo. | Renombrar a “Prácticas guiadas” y mostrar objetivo, mundo y programa antes de cargar. |
| Misiones | Útil para actividades evaluables. | Mantener; diferenciar visualmente de ejemplos y mostrar progreso. |
| Tema | Útil, pero de bajo impacto funcional. | Mantener como ajuste de apariencia dentro de Preferencias, no como menú principal. |
| Fidelidad | Configuración técnica poco clara para usuarios nuevos. | Integrar en “Configuración de simulación” con explicación de precisión y rendimiento. |
| Tiempo máximo | Útil para evitar ejecuciones infinitas, pero demasiado técnico. | Mover a Configuración y mostrar valor actual, unidad y recomendación. |
| Trazas | Útil para diagnóstico, no para uso cotidiano. | Mover a Diagnóstico/Desarrollador; incluir niveles y botón de exportar. |
| Ayuda | Centro, guía, diagnóstico, exportación, libro y acerca de. | Mantener; agrupar en “Aprender”, “Diagnosticar” y “Información”. |

## Redundancias detectadas

1. Escenarios y Ejemplos se superponen: ambos permiten llegar a un programa ejecutable; Escenarios añade el mundo asociado.
2. Mundos preestablecidos dentro de Mundos y los mundos implícitos de Escenarios pueden confundir sobre cuál es la fuente activa.
3. Diagnóstico y Trazas cumplen funciones relacionadas, pero están separados sin explicar la diferencia.
4. Tema, Fidelidad y Tiempo máximo son preferencias persistentes y no deberían ocupar el mismo nivel que Archivo o Ejecutar.

## Opciones con valor limitado o confuso

- Fidelidad: el usuario final no conoce el efecto de cambiarla.
- Trazas: sin niveles o ejemplos, parece una opción sin resultado visible.
- Tiempo máximo: requiere una unidad y una indicación del impacto.
- Acerca de: debe mostrar versión, licencia y enlaces, no solo un cuadro informativo mínimo.

## Propuesta de menú final

**Archivo · Aprender · Mundos · Prácticas guiadas · Misiones · Configuración · Diagnóstico · Ayuda**

- **Aprender** contiene Ejemplos, agrupados por dificultad.
- **Prácticas guiadas** reemplaza Escenarios y declara mundo, programa y objetivo.
- **Configuración** contiene Tema, Fidelidad y Tiempo máximo.
- **Diagnóstico** contiene Trazas, diagnóstico de sesión y exportación.
- **Ayuda** contiene centro de ayuda, guía rápida, libro y acerca de.

## Prioridad

1. Corregir la caducidad de sesión al cargar ejemplos y mostrar errores reales.
2. Reorganizar Escenarios como prácticas guiadas, evitando duplicar nombres.
3. Agrupar preferencias técnicas y añadir ayuda contextual.
4. Separar diagnóstico de las opciones didácticas.
5. Alinear la navegación web y Tkinter con la misma taxonomía y etiquetas.

## Criterios de aceptación

- Cada acción tiene un único lugar principal.
- El nombre del menú describe el resultado que verá el usuario.
- Ninguna opción técnica carece de explicación o valor visible.
- Web y escritorio presentan las mismas categorías, orden y comportamiento.
- Las acciones de carga muestran éxito o error verificable y no dejan estados silenciosos.
