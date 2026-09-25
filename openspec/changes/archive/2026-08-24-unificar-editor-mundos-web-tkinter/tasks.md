# Tareas: unificar el Editor de Mundos Web y Tkinter

## Fase 1 — Línea base y contrato

- [x] 1.1 Inventariar todos los comandos, atajos, diálogos, validaciones,
  categorías, assets y propiedades visibles en ambos editores.
- [x] 1.2 Crear la matriz de paridad de autoría: equivalente, brecha o N/A
  justificado, incluyendo evidencia visual actual.
- [x] 1.3 Definir DTOs versionados de `WorldEditorSession`, comandos,
  selección, capas, validación, estado de persistencia y acciones habilitadas.
- [x] 1.4 Extraer/adaptar la fachada común sin cambiar el formato JSON ni las
  reglas físicas existentes.

## Fase 2 — Catálogo, lenguaje y activos

- [x] 2.1 Consolidar catálogo canónico de assets desde las variantes actuales
  de escritorio y sincronizarlo con la entrega Web mediante hashes.
- [x] 2.2 Unificar categorías, nombres en español, descripciones, tooltips,
  iconos, unidades y reglas de colocación.
- [x] 2.3 Mantener alias para nombres históricos de mundos y validar el
  catálogo completo incluido antes de reemplazar cualquier recurso.

## Fase 3 — Composición y operaciones equivalentes

- [x] 3.1 Implementar en Web la barra agrupada Archivo/Edición/Simulación,
  presets, acciones de inspección, capas y atajos equivalentes.
- [x] 3.2 Implementar en Tkinter búsqueda y guía contextual de biblioteca,
  categorías y composición de tres columnas equivalentes.
- [x] 3.3 Implementar en ambas UI el mismo CRUD: nuevo, abrir, guardar,
  guardar como, importar, exportar, cancelar y eliminación segura.
- [x] 3.4 Igualar selección, arrastre, colocar, rotar, duplicar, eliminar,
  propiedades, robot inicial, tamaño/presets, snap, zoom y paneo.
- [x] 3.5 Igualar validación, confirmaciones, capas/bloqueo/visibilidad y la
  transición de un mundo guardado al simulador.

## Fase 4 — Diseño, accesibilidad y resiliencia

- [x] 4.1 Aplicar tokens comunes de espaciado, tipografía, contraste, foco,
  bordes, estados y tema claro/oscuro.
- [x] 4.2 Implementar puntos de ruptura y paneles acoplables/colapsables sin
  recortar el lienzo ni controles en 1024×768 y 1280×800.
- [x] 4.3 Garantizar navegación por teclado, foco visible, Escape, ayudas
  contextualizadas y mensajes recuperables equivalentes.
- [x] 4.4 Impedir que errores de sesión o worker pierdan el modelo editable;
  ofrecer reintento seguro y conservar cambios sin guardar.

## Fase 5 — Pruebas y evidencia

- [x] 5.1 Añadir pruebas unitarias y de contrato para `WorldEditorSession`,
  catálogo, alias, validaciones y conversiones.
- [x] 5.2 Crear Playwright que ejecute todos los comandos y un CRUD real en
  Web, con persistencia, tema y resoluciones de referencia.
- [x] 5.3 Crear Pywinauto que ejecute el mismo catálogo en Tkinter, incluidos
  menús, atajos, diálogos, foco y acciones de lienzo.
- [x] 5.4 Añadir comparación visual por regiones y prueba cruzada: mundo
  guardado en una UI, abierto, validado y simulado en la otra.
- [x] 5.5 Documentar resultados, cobertura, diferencias nativas aceptadas y
  bloquear en CI las brechas no justificadas.

## Fase 6 — Cierre

- [x] 6.1 Actualizar guía de creación de mundos, manual técnico, matriz de
  paridad y arquitectura de interfaces.
- [x] 6.2 Ejecutar la campaña de liberación Web/Tkinter, validar OpenSpec en
  modo estricto y archivar el cambio con evidencia.
