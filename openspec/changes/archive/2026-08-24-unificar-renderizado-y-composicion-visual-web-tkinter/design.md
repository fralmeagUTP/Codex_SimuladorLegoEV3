# Diseño: renderizado y composición visual común

## Línea base

Los assets actualmente usados por Tkinter serán inventariados y evaluados como
referencia inicial, en particular `robot_ev3_*` y las piezas `line_*`.
La referencia no se define por su carpeta actual sino por el resultado de la
auditoría: cada recurso aprobado tendrá un `asset_id`, versión, hash SHA-256,
dimensiones lógicas, punto de anclaje, rotación permitida y licencia/origen.

```text
AssetCatalog canónico
  ├─ definición: asset_id, geometría, hash, variante, capa
  ├─ recurso de escritorio / bundle
  ├─ recurso Web estático generado o sincronizado
  └─ validación de empaquetado y manifiesto

World editor/spec ── asset_id + x/y/rotación ──> adaptador Web / Tkinter
                                                   └─ misma geometría física
```

## Contrato geométrico

- El mundo conserva `CELL_SIZE_MM = 100` y `GRID_SIZE_PX = 32` como contrato
  de conversión cuando el `editor_spec` use esa cuadrícula.
- Las posiciones del placement se interpretan desde el mismo origen y ancla
  de asset; no se aplicarán compensaciones específicas de una UI.
- Robot y assets de línea se dibujan por capas explícitas: suelo, línea/meta,
  obstáculos, robot, sensores/haces, trazas y marcadores de edición.
- La figura del robot debe ocupar el mismo tamaño lógico y girar alrededor de
  su centro físico en ambas interfaces.
- Las pistas de seguimiento se representan como assets de línea conectables;
  no deben degradarse a rectángulos de obstáculo ni adquirir fondos ajenos al
  mundo salvo que el `asset_id` lo especifique.

## Composición objetivo

La estructura de información será equivalente, no idéntica en píxeles:

```text
Controles y estado global
├─ Canvas / entorno de simulación                 Editor de código
└─ Telemetría de motores y sensores │ EV3 Brick
                                      ├─ LCD
                                      └─ Robot / Estado
```

- Canvas y editor reciben prioridad de ancho; la telemetría usa una grilla
  estable, no tarjetas comprimidas.
- Brick agrupa LED, altavoz, LCD y Robot/Estado para que la pose no quede
  separada de la representación del brick.
- Web adapta la composición con CSS Grid y puntos de ruptura; Tkinter usa
  paneles redimensionables y scroll interno cuando sea imprescindible.
- La actividad pedagógica no será un panel fijo que desplace el canvas. Se
  accede mediante Ayuda/guía contextual y conserva su contrato compartido.

## Estados y editor

`SessionStatus` mantiene el valor técnico interno; el catálogo compartido
define su etiqueta visible localizada y color semántico. Ambas UI renderizan
la misma etiqueta y no exponen alternadamente `running` y `EJECUTANDO`.

El resaltado de código usa el mismo mapa semántico (comentarios, palabras
clave, cadenas, números y errores), con adaptadores para Canvas/HTML y Tk.

## Verificación

1. Pruebas de manifiesto verifican hash, dimensiones, destino Web y bundle.
2. Pruebas de contrato cargan un mundo de línea y comparan pose, asset ids,
   capa y límites renderizables para ambas UI.
3. Playwright y Pywinauto generan capturas en 1920×1080, 1280×800 y
   1024×768; la comparación se realiza por regiones y tolerancias nativas.
4. Pruebas manuales verifican tema claro/oscuro, zoom, paneo, cambio de mundo
   y misión sin assets o trazas residuales.

## Riesgos

- Un asset existente puede tener diferente tamaño de píxel aunque corresponda
  al mismo nombre. El manifiesto bloquea su uso hasta declarar su geometría.
- La transparencia o antialiasing nativo puede variar. Se compara forma,
  escala, ubicación y contraste, no píxeles exactos.
- Un mundo antiguo puede depender de una variante retirada. Se agrega una
  migración/alias explícito y prueba de compatibilidad por mundo.
