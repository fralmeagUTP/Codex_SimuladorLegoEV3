# Tareas: unificar renderizado y composición visual Web–Tkinter

## Fase 1 — Diagnóstico y línea base

- [x] 1.1 Inventariar assets de robot, líneas, obstáculos, pisos, metas, haces
  e iconos usados por ambas aplicaciones, con origen y uso por mundo.
- [x] 1.2 Comparar visualmente los mundos comunes, empezando por
  `03_linea_negra_v2` y demás seguidores de línea; registrar diferencias de
  forma, capa, escala, anclaje, color y rotación.
- [x] 1.3 Seleccionar y documentar las variantes de escritorio aprobadas como
  referencia inicial para robot y líneas.
- [x] 1.4 Capturar línea base Web/Tkinter en claro y oscuro, 1920×1080,
  1280×800 y 1024×768.

## Fase 2 — Catálogo y recursos canónicos

- [x] 2.1 Extender `AssetCatalog` con versión, hash, dimensiones lógicas,
  ancla, capa, variantes y destino de empaquetado.
- [x] 2.2 Consolidar los recursos canónicos y sincronizar la entrega Web sin
  sustituir silenciosamente assets de mundos existentes.
- [x] 2.3 Declarar alias/migraciones para nombres históricos y validar todos
  los mundos y escenarios incluidos.
- [x] 2.4 Actualizar la configuración de paquete/PyInstaller para incluir los
  recursos canónicos y el manifiesto.

## Fase 3 — Renderizado equivalente

- [x] 3.1 Extraer o reforzar el adaptador compartido placement→geometría para
  coordenada, conversión mm/píxel, ancla, rotación y capas.
- [x] 3.2 Actualizar el renderizador Web para usar el robot y líneas canónicos,
  sin fondos, rectángulos ni escalas sustitutas no declaradas.
- [x] 3.3 Ajustar el renderizador Tkinter al mismo contrato de geometría y
  capas; conservar solo diferencias nativas documentadas.
- [x] 3.4 Corregir limpieza de trazas, haces y marcadores al cambiar de mundo,
  misión y reinicio, sin eliminar elementos del nuevo mundo.
- [x] 3.5 Verificar manualmente que la pose inicial, telemetría y robot visual
  coinciden al abrir cada mundo o misión.

## Fase 4 — Composición y sistema visual

- [x] 4.1 Definir tokens comunes de tamaño, densidad, borde, espaciado,
  tipografía y color semántico para canvas, editor, telemetría y Brick.
- [x] 4.2 Implementar la composición equivalente canvas/editor/telemetría/
  Brick/LCD/Robot-Estado en Web, con puntos de ruptura documentados.
- [x] 4.3 Implementar la misma jerarquía en Tkinter con paneles ajustables y
  scroll interno accesible como último recurso.
- [x] 4.4 Normalizar etiquetas y colores visibles de todos los estados de
  sesión en ambas interfaces.
- [x] 4.5 Unificar el mapa de resaltado sintáctico del editor y mantener el
  contenido pedagógico como guía contextual, no como panel fijo.

## Fase 5 — Pruebas, evidencia y liberación

- [x] 5.1 Añadir pruebas unitarias de manifiesto, hashes, alias y geometría.
- [x] 5.2 Añadir pruebas de contrato Web/Tkinter para mundos de líneas,
  robot inicial, orientación, capas y reinicio.
- [x] 5.3 Añadir Playwright y Pywinauto para composición, estados, temas y
  accesibilidad en resoluciones de referencia.
- [x] 5.4 Generar evidencia visual por regiones, documentar tolerancias y
  bloquear regresiones no aprobadas en CI.
- [x] 5.5 Actualizar matriz de paridad, arquitectura, guía de assets y manual
  de desarrollo; ejecutar la campaña de liberación y registrar resultados.

## Cierre

- [x] 6.1 Validar el cambio con `openspec validate`.
- [x] 6.2 Confirmar que no existe diferencia funcional ni semántica visual
  abierta para el mismo mundo, asset y estado de sesión.
