# Propuesta: modernizar la ayuda interactiva y sus capturas reales

## Motivo

El Centro de ayuda tiene una buena base: catálogo compartido, búsqueda,
categorías, recuperación ante errores y paridad textual entre Web y Tkinter.
Su valor didáctico disminuye por problemas verificables:

- siete guías reutilizan solo tres ilustraciones SVG genéricas
  (`tutorial_simulacion.svg`, `tutorial_mundo.svg` y `tutorial_debug.svg`), por
  lo que varias no representan el control, panel o flujo que explican;
- las imágenes no tienen metadatos de versión, resolución, tema, plataforma o
  fecha de captura, así que no existe un mecanismo para detectar que quedaron
  obsoletas tras cambiar la interfaz;
- Tkinter presenta esquemas dibujados, no capturas del producto real, y no
  ayuda a reconocer sus controles actuales;
- las guías describen pasos, pero no permiten seguir progreso, comprobar el
  resultado, copiar un ejemplo seguro ni volver con contexto a la práctica.

## Cambio propuesto

Evolucionar la ayuda a una experiencia de aprendizaje guiado común para Web y
Tkinter:

1. Sustituir ilustraciones genéricas por capturas reales, anotadas y
   versionadas de cada plataforma, usando la interfaz actual y assets canónicos.
2. Ampliar el modelo compartido de guía con objetivo, nivel, pasos verificables,
   precondiciones, resultado, recuperación, ejemplo opcional y contexto.
3. Añadir un recorrido con progreso por pasos, reinicio, persistencia local y
   acceso directo al área de práctica.
4. Mostrar una imagen apropiada por plataforma sin perder secuencia didáctica
   ni paridad de contenido.
5. Crear rutas para estudiante, docente y soporte: inicio, programación,
   sensores, depuración, mundos, misiones y errores frecuentes.
6. Definir una cadena reproducible para capturar, revisar y actualizar assets
   visuales cuando cambie la interfaz.

## Alcance

- Centro de ayuda Web, ventana de ayuda Tkinter, catálogo compartido,
  documentación de uso y pruebas de accesibilidad/paridad.
- Capturas y anotaciones propias del proyecto, en claro y oscuro cuando el
  tema afecte el control mostrado.
- Manual de uso y referencias técnicas enlazadas desde la ayuda.

## Fuera de alcance

- Modificar la lógica de simulación o la API Pybricks.
- Usar imágenes de terceros sin licencia o material que revele datos de
  estudiantes, tokens o rutas privadas.
- Convertir la ayuda en un sistema de cuentas o analítica remota.

## Éxito esperado

Una persona nueva puede completar una primera simulación, crear un mundo y
depurar un error usando la ayuda sin explicación externa; una persona docente
puede recomendar una ruta por nivel; y cada imagen visible describe fielmente
la versión actual de la interfaz correspondiente.
