# Tareas: cerrar brechas de navegación Web–Tkinter

## Fase 1 — Contrato y contenido

- [ ] 1.1 Documentar el mapa de destinos y transiciones de navegación para
  `UC-WORLD-01`, `UC-WORLD-02`, `UC-WORLD-03` y `UC-HELP-01`.
- [ ] 1.2 Extraer el contenido de los tutoriales a una fuente compartida en
  español, con pasos, resultado esperado y recuperación.
- [ ] 1.3 Actualizar la matriz de paridad y la guía de uso con diferencias
  nativas permitidas.

## Fase 2 — Experiencia de usuario

- [ ] 2.1 Renderizar en Tkinter los tres tutoriales y acciones contextuales
  equivalentes a la ayuda Web.
- [ ] 2.2 Añadir en el editor de mundos Tkinter la acción visible **Simular
  mundo guardado** después de un guardado válido.
- [ ] 2.3 Asegurar que la acción use la fachada pública, active la simulación y
  preserve el mensaje de error sin modificar la sesión ante fallos.
- [ ] 2.4 Homologar etiquetas, foco y atajos de esos destinos con la Web.

## Fase 3 — Pruebas y evidencia

- [ ] 3.1 Extender Playwright para enlaces de ayuda, tutoriales y navegación
  Mundo → Simulación.
- [ ] 3.2 Incorporar automatización Windows real de Tkinter para menús, ayuda,
  editor, interacción de assets, guardado y retorno a simulación.
- [ ] 3.3 Mantener pruebas de contrato de contenido y transiciones compartidas.
- [ ] 3.4 Ejecutar las suites en CI y guardar evidencia de cualquier omisión por
  falta de escritorio interactivo.

## Criterios de aceptación

- Cada destino del mapa tiene una entrada descubierta por usuario en ambas UI.
- Los tres tutoriales tienen pasos, resultado esperado y recuperación iguales
  en significado en ambas UI.
- Un mundo guardado desde cualquiera de las UI puede llegar a simulación sin
  seleccionar de nuevo el archivo.
- Web y Tkinter tienen evidencia automatizada de interacción para los cuatro
  casos de uso afectados.
