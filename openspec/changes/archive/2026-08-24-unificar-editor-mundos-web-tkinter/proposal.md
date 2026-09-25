# Cambio: unificar el Editor de Mundos Web y Tkinter

## Por qué

Los dos editores de mundos permiten trabajar sobre el mismo formato, pero hoy
presentan dos experiencias diferentes. La Web ofrece una biblioteca y una
orientación inicial más claras; Tkinter agrupa mejor las acciones de archivo,
edición y simulación, y expone más herramientas directas. Las diferencias de
composición, etiquetas, categorías, activos y estado del inspector hacen que
un mismo flujo sea más difícil de aprender, enseñar y verificar entre ambas
aplicaciones.

Este cambio convierte el Editor de Mundos en una capacidad única con dos
adaptadores visuales: Web y Tkinter. No sustituye los widgets nativos, sino
que iguala intención, arquitectura, funciones, datos, nombres, activos y
resultado visible.

## Qué cambia

- Definir un contrato común `WorldEditorSession` para el ciclo de archivo,
  selección, colocación, edición, validación, persistencia y simulación.
- Adoptar una composición común: barra superior agrupada, barra de tamaño y
  presets, Biblioteca a la izquierda, lienzo central, Inspector y Capas a la
  derecha, y estado/validación al pie.
- Unificar catálogo, categorías, nombres visibles, iconos, tooltips, atajos,
  activos, unidades y propiedades de dominio; eliminar etiquetas mezcladas
  como `Select`/`Delete` frente a etiquetas en español.
- Llevar a ambas plataformas lo mejor de cada interfaz: guía contextual y
  búsqueda de la Web; grupos de acciones, simulación directa, presets y
  edición explícita de escritorio.
- Establecer el mismo CRUD, validaciones, confirmaciones, importación,
  exportación, capas, duplicación, rotación y transición al simulador.
- Crear una matriz de paridad y pruebas reales Web/Tkinter para cada comando,
  estado, resolución, tema y mundo guardado.

## Capacidades afectadas

### Modificadas

- `world-authoring`: contrato, composición y operaciones equivalentes del
  editor de mundos.
- `user-interfaces`: tokens, navegación por teclado, accesibilidad, nombres y
  presentación homogénea del editor.
- `interface-parity`: evidencia obligatoria de paridad visual y funcional de
  la autoría de mundos.
- `project-documentation`: guías únicas de creación de mundos y matriz de
  comandos por plataforma.

## Impacto

Se modificarán la fachada de edición de mundos, controladores Flask y Tkinter,
plantillas, CSS, activos del catálogo, traducciones, pruebas Pytest,
Playwright y Pywinauto, documentación y CI. El formato JSON de mundos y el
motor de simulación se mantendrán compatibles.

## Criterio de éxito

Una persona podrá crear, editar, validar, guardar, exportar y simular el mismo
mundo desde cualquiera de las dos aplicaciones siguiendo la misma estructura,
etiquetas, categorías y reglas, con diferencias limitadas a los controles
nativos documentados.
