# Guía del Editor de Mundos EV3

Esta guía aplica tanto al Editor de Mundos Web como al de escritorio Tkinter.
Ambos consumen el mismo formato JSON y validan con las mismas reglas físicas.

## Flujo recomendado

1. Seleccione **Nuevo** o **Abrir**.
2. Defina el tamaño o use un preajuste: Pequeño, Aula o Grande.
3. Elija un asset de la Biblioteca: Robot, Obstáculos, Suelos, Líneas, Zonas y
   metas o Sensores; después haga clic en el lienzo para colocarlo.
4. Seleccione un elemento para moverlo, rotarlo 90°, duplicarlo, editar sus
   propiedades o eliminarlo. Las Capas permiten ocultarlo o bloquearlo.
5. Fije la posición inicial del robot y use **Validar**.
6. Guarde el mundo. Finalmente use **Probar mundo guardado** para abrirlo en
   el simulador.

## Operaciones comunes

| Acción | Web | Escritorio |
|---|---|---|
| Nuevo, Abrir, Guardar y Guardar como | Barra Archivo | Barra Archivo |
| Importar/exportar | Abrir JSON / Guardar como | Diálogos nativos JSON |
| Seleccionar, mover, rotar, duplicar y eliminar | Barra Edición, clic y arrastre | Barra Edición, clic y arrastre |
| Tamaño, preajustes y zoom | Barra de tamaño | Barra de tamaño |
| Capas y propiedades | Inspector derecho | Inspector derecho |
| Aplicar al simulador | Aplicar / Probar mundo guardado | Probar mundo guardado |

## Seguridad de edición

- En Web, **Cambios sin guardar** aparece después de una modificación. Nuevo u
  Abrir solicitan confirmación antes de descartar el contenido actual.
- Al reducir el tamaño, ambas aplicaciones rechazan el cambio si algún asset
  queda fuera del mapa; el mundo que estaba editando se conserva intacto.
- Los mundos incorporados no se pueden eliminar. Solo se eliminan JSON
  personalizados en el directorio autorizado.
- Un mundo inválido no puede aplicarse a la simulación.

## Atajos

`Ctrl+N`, `Ctrl+O`, `Ctrl+S`, `Ctrl+Mayús+S`, `Ctrl+D`, `Supr`, `R` y `Escape`
realizan respectivamente nuevo, abrir, guardar, guardar como, duplicar,
eliminar, rotar y cancelar la selección. En Tkinter los diálogos de archivos
son nativos de Windows; en Web se usa el selector del navegador.

## Diferencias visuales aceptadas

Tkinter usa separadores ajustables para sus paneles. Web permite ocultar
Biblioteca e Inspector en anchos de portátil. Esta diferencia responde al
control nativo de cada plataforma; no cambia assets, datos, validación ni el
resultado del mundo guardado.

## Referencias

- Contrato: `simulador_ev3/application/world_editor_session.py`.
- Catálogo: `simulador_ev3/shared/asset_catalog.py`.
- Evidencia: `Documentos/REPORTE_UNIFICACION_EDITOR_MUNDOS_2026-08-24.md`.
