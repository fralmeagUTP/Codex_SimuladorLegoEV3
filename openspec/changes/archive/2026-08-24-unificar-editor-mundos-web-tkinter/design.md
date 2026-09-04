# Diseño: Editor de Mundos común Web/Tkinter

## Referencia de experiencia

La composición de referencia se mantiene estable en ambas plataformas:

```text
Menú / título
┌ Archivo ───────┬ Edición ────────────┬ Simulación ───────┐
├ Tamaño · presets · robot inicial · zoom · validación ────┤
├ Biblioteca ┬────────────── Lienzo ─────────────┬ Inspector┤
│ búsqueda   │ guía de primeros pasos / objetos   │ Capas    │
│ categorías │ selección, arrastre, rejilla       │ propiedades
└────────────┴────────────────────────────────────┴──────────┘
 Estado: nombre · cambios pendientes · cursor · snap · validación
```

La Web aporta búsqueda, tarjetas de biblioteca y guía vacía. Tkinter aporta
grupos de acciones claros, atajos y acciones directas de simulación. Ambos
beneficios se implementarán en los dos adaptadores.

## Arquitectura

`WorldEditorSession` será la fachada común, respaldada por el modelo y los
puertos existentes. Sus comandos son: `new`, `open`, `save`, `save_as`,
`import`, `export`, `select`, `place`, `move`, `rotate`, `duplicate`,
`delete`, `resize`, `set_robot_pose`, `validate`, `apply_to_simulation` y
`set_layer_visibility_or_lock`.

Cada respuesta contendrá modelo de mundo, selección, lista de capas,
validaciones, estado de persistencia y acciones habilitadas. Web y Tkinter no
leerán atributos internos del modelo para resolver su presentación.

## Catálogo visual y texto

El catálogo compartido será fuente de verdad de `asset_id`, imagen, categoría,
nombre localizado, descripción, tooltip, tamaño lógico, rotación permitida y
reglas de colocación. Se usarán los assets más actuales de escritorio como
origen de consolidación, empaquetados para Web y Tkinter con hash verificable.

Categorías canónicas: Robot, Obstáculos, Suelos, Zonas y metas, Líneas y
Sensores. Las acciones se mostrarán en español: Seleccionar, Eliminar, Rotar
90°, Duplicar, Aplicar propiedades y Probar mundo guardado.

## Adaptación responsiva

En escritorio, las tres columnas mantienen Biblioteca 20 %, Lienzo flexible e
Inspector 20 %, con mínimo documentado. Al reducirse el ancho, los paneles
laterales pasan a paneles colapsables/dockables antes de recortar controles.
El lienzo conserva escala física; sólo su viewport se desplaza o cambia zoom.

## Accesibilidad y seguridad

Todos los comandos tendrán nombre accesible, tooltip y atajo cuando aplique.
Tab seguirá el orden Archivo → Edición → Simulación → Tamaño → Biblioteca →
Lienzo → Inspector → Capas. Las confirmaciones sólo aparecerán en operaciones
destructivas o reducción de mundo con elementos fuera de límites. Los errores
mantendrán el estado editable previo y ofrecerán recuperación.

## Verificación

La matriz de paridad asociará cada comando a prueba de contrato, Playwright y
Pywinauto. Las capturas de referencia cubrirán lienzo vacío, selección,
propiedades, mundo con activos, tema claro/oscuro y 1920×1080, 1280×800 y
1024×768. Se tolerarán exclusivamente diferencias de antialiasing y widget
nativo previamente documentadas.
