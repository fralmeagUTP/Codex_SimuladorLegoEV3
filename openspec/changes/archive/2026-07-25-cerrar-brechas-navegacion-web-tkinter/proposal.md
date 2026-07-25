# Propuesta: cerrar brechas de navegación Web–Tkinter

## Motivo

La evaluación de navegación de la versión 1.4.0 confirma que los flujos
principales de la Web funcionan mediante 20 recorridos Playwright y que los
contratos de sesión y los controles de Tkinter pasan sus pruebas. Sin embargo,
hay dos brechas verificables frente al requisito de funcionalidad equivalente:

1. La ayuda Web es una guía navegable con tres tutoriales y enlaces directos a
   **Simulación** y **Mundos**; Tkinter abre el manual general en una ventana de
   texto, sin esos tutoriales ni navegación contextual equivalente.
2. El recorrido de edición de mundos se prueba con interacción real en la Web,
   mientras que en Tkinter solo se comprueba mediante pruebas unitarias con
   dobles. Por tanto, no hay evidencia reproducible de que el usuario pueda
   completar con ratón y teclado el mismo flujo de navegación, edición,
   validación, guardado y retorno a simulación.

## Cambio propuesto

Definir y aplicar una navegación funcional común para Simulación, Mundos y
Ayuda. Tkinter conservará sus ventanas nativas, pero deberá ofrecer el mismo
contenido de ayuda orientado a tareas, los mismos destinos funcionales y un
retorno explícito a la simulación tras guardar un mundo. Se añadirá automatización
de escritorio Windows para verificar el catálogo de navegación contra una
aplicación real, no solo contra dobles.

## Fuera de alcance

- No se cambia el motor de simulación, el formato de mundos ni el contrato de
  sesión.
- La página `/operations` no se duplica en Tkinter: es un panel operativo del
  servidor Web, no una capacidad de simulación para alumnado.
- No se exige identidad pixel a pixel; la paridad visual vigente sigue siendo
  responsabilidad del cambio `paridad-visual-web-tkinter`.

## Impacto

Se afectan las plantillas y JavaScript de ayuda Web, `ui/main_window.py`, la
ventana del editor de mundos, documentación, catálogo de casos de uso y suites
E2E/UI. La Web continúa siendo la referencia de etiquetas, orden y contenido
didáctico.
