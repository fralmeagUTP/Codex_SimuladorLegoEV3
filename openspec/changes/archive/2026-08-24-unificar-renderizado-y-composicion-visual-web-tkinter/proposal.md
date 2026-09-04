# Propuesta: unificar renderizado y composición visual Web–Tkinter

## Motivo

Al cargar el mismo mundo, Web y Tkinter no comunican la misma escena visual:
la figura del robot, la pista del seguidor de línea, los obstáculos y las
proporciones difieren. Además, canvas, telemetría, Brick/LCD, editor y estados
se distribuyen de manera distinta, lo que aumenta la carga cognitiva en aula.

La aplicación de escritorio posee assets más recientes para el robot y las
líneas de seguimiento. Esta propuesta los toma como línea base visual, pero
los convierte en recursos canónicos versionados: no se copiarán archivos de
manera ad hoc entre interfaces.

## Cambio propuesto

1. Establecer un manifiesto único de assets para robot, líneas, obstáculos,
   pisos, metas y haces; incluir versión, hash, tamaño lógico y destinos Web,
   Tkinter y empaquetado.
2. Migrar la Web a las variantes visuales actuales verificadas en escritorio,
   manteniendo los mismos `asset_id` y la misma escala física de mundo.
3. Unificar el contrato de renderizado de mundos: capas, origen, anclaje del
   robot, rotación, tamaño lógico, color semántico de líneas y orden de dibujo.
4. Rediseñar la composición principal con una estructura común: canvas como
   foco, telemetría legible, Brick/LCD y Robot/Estado agrupados, y editor sin
   competir por el área de trabajo. Cada plataforma podrá adaptar widgets
   nativos, pero no cambiar información, jerarquía o semántica.
5. Normalizar estados visibles (`Listo`, `Ejecutando`, `Pausado`, `Finalizado`,
   `Error`, `Detenido`) y la presentación del editor.
6. Añadir pruebas de manifiesto, contrato geométrico, capturas de referencia y
   pruebas E2E para impedir que un asset o mundo vuelva a divergir.

## Alcance

- Web, Tkinter, renderizadores de mundo, catálogo de assets, empaquetado y
  pruebas visuales/de interfaz.
- Mundos existentes, especialmente los de seguidor de línea.
- Tema claro y oscuro en resoluciones de referencia.

## Fuera de alcance

- Cambiar reglas de física, cinemática o lógica de sensores.
- Exigir igualdad píxel a píxel entre Canvas HTML y widgets nativos.
- Rediseñar el editor de mundos fuera de los assets y la vista previa
  necesarios para preservar la equivalencia.

## Impacto

- `simulador_ev3/shared/asset_catalog.py` y recursos asociados.
- Renderizadores Web y Tkinter, CSS y composición de paneles.
- Configuración de PyInstaller/paquete y pruebas de integridad.
- Especificaciones `user-interfaces`, `interface-parity` y
  `simulation-engine`.

## Criterios de aceptación

- El mismo `asset_id` se resuelve a una variante equivalente y verificable en
  ambas aplicaciones.
- Al abrir el mismo mundo, robot, línea, obstáculos, origen y orientación
  coinciden dentro de la tolerancia geométrica documentada.
- La línea de los mundos de seguidor se ve con la figura, grosor, color y
  conectividad canónicos, no como un obstáculo visual diferente.
- Telemetría, Brick/LCD, Robot/Estado, canvas y editor conservan la misma
  jerarquía informativa en Web y Tkinter.
- La UI usa nomenclatura de estados equivalente y conserva contraste en ambos
  temas.
- CI detecta recursos obsoletos, faltantes o desalineados antes de liberar.
