# Verificación

## Pruebas funcionales

- Crear un mundo vacío y comprobar que aparece la guía inicial.
- Buscar y colocar assets de Robot, Obstáculos, Suelos, Líneas, Zonas y metas,
  y Sensores.
- Seleccionar, mover, rotar, duplicar y eliminar un objeto.
- Verificar que la eliminación se habilita solo con selección y que las
  confirmaciones se limitan a acciones destructivas de alcance mayor.
- Editar propiedades de robot, muro, zona, línea, meta y sensor con unidades
  legibles; confirmar que se preservan después de guardar y abrir.
- Usar presets Pequeño, Aula y Grande, además de dimensiones personalizadas.
- Seleccionar objetos superpuestos desde el lienzo y desde la lista de capas.
- Ocultar, bloquear y reordenar capas cuando aplique.
- Validar y probar el mundo guardado; confirmar pose inicial y transición a
  simulación.

## Regresión y compatibilidad

- Cargar mundos JSON existentes y comprobar que su geometría, assets, sensores
  y pose inicial se conservan.
- Verificar que los mundos creados con el editor se cargan en Web y Tkinter.
- Confirmar que no cambian las reglas de validación, colisión ni conversión al
  mundo físico.
- Probar claro y oscuro en 1920x1080, 1280x800, 1024x768 y 390x844.
- Confirmar ausencia de texto cortado, solapes, controles inaccesibles y
  desplazamiento horizontal global.
- Recorrer por teclado cabecera, biblioteca, lienzo, inspector y barra de
  estado; confirmar foco visible, tooltips y nombres accesibles.

## Criterio de aceptación

La propuesta se considera verificada cuando el editor permite crear, editar,
guardar, cargar, validar y probar mundos con una biblioteca e inspector
comprensibles, preserva compatibilidad JSON y mantiene paridad funcional entre
Web y Tkinter.
