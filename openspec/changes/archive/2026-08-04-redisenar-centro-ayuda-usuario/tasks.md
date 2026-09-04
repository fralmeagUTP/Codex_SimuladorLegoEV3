# Tareas: rediseñar el centro de ayuda orientado al usuario

## Fase 1 — Investigación y contenido

- [x] 1.1 Inventariar contenidos de ayuda, manuales, mensajes de error,
  tutoriales e información técnica existente; clasificar por audiencia y tarea.
- [x] 1.2 Unificar marca, terminología, tono, unidades y URLs; retirar enlaces
  fijos que no dependan de la instancia activa.
- [x] 1.3 Definir el modelo compartido de entradas de ayuda, categorías,
  acciones de destino y relaciones entre guías.
- [x] 1.4 Redactar rutas iniciales: primera simulación, crear mundo, usar
  sensores, ejecutar/detener, depurar y recuperar errores frecuentes.
- [x] 1.5 Crear o seleccionar capturas anotadas y recursos visuales accesibles,
  con texto alternativo y licencia/documentación de origen.

## Fase 2 — Centro de ayuda Web

- [x] 2.1 Rediseñar `/help` con cabecera, buscador, tarjetas de inicio,
  navegación por categorías y contenido por tarea.
- [x] 2.2 Implementar filtrado accesible, enlaces internos, resultados vacíos y
  rutas relacionadas sin depender de servicios externos.
- [x] 2.3 Implementar acciones directas que abran simulación, mundos o la
  guía de depuración conservando la sesión cuando aplique.
- [x] 2.4 Adaptar todos los estados al tema claro/oscuro y a 390×844, 1024×768,
  1280×800 y 1920×1080 sin desbordamiento horizontal.

## Fase 3 — Centro de ayuda Tkinter

- [x] 3.1 Sustituir el visor de Markdown plano por ventana navegable con índice,
  búsqueda, tarjetas, contenido estructurado y acciones de destino.
- [x] 3.2 Renderizar recursos visuales, advertencias, resultados esperados y
  recuperación con widgets nativos accesibles.
- [x] 3.3 Hacer la ventana reutilizable, redimensionable y navegable con Tab,
  Shift+Tab, Enter y Escape, sin bloquear la simulación.
- [x] 3.4 Aplicar tokens de tema a todos los widgets estáticos y dinámicos del
  centro de ayuda, incluidos enlaces, foco y paneles desplazables.

## Fase 4 — Ayuda contextual y documentación

- [x] 4.1 Añadir accesos contextuales para controles críticos y mensajes de
  error, con enlace estable a la entrada de ayuda correcta.
- [x] 4.2 Separar el manual de usuario guiado de la guía técnica de instalación,
  despliegue, sesiones y trazas; cruzarlos solo cuando sea necesario.
- [x] 4.3 Actualizar README, manual de usuario y documentación de paridad para
  reflejar rutas, atajos y limitaciones reales.

## Fase 5 — Calidad y validación

- [x] 5.1 Añadir pruebas unitarias para el catálogo, búsqueda, categorías,
  destinos, terminología y ausencia de URLs fijas obsoletas.
- [x] 5.2 Añadir pruebas de integración y E2E Web para búsqueda, navegación,
  acciones, tema, teclado, `aria-live` y viewport móvil.
- [x] 5.3 Añadir pruebas de interfaz Tkinter para apertura, búsqueda, acciones,
  tema, foco, Escape y ausencia de ventanas duplicadas.
- [x] 5.4 Ejecutar revisión manual con estudiantes/docentes representativos o
  protocolo equivalente; registrar comprensión, bloqueos y ajustes.
- [x] 5.5 Publicar evidencia visual clara/oscura y reporte de paridad Web/Tkinter.
