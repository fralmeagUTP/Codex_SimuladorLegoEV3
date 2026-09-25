# Inventario de assets y línea base visual Web–Tkinter

Fecha de revisión: 2026-08-23
Cambio OpenSpec: `unificar-renderizado-y-composicion-visual-web-tkinter`

## Fuente canónica

Los recursos visuales aprobados residen en `simulador_ev3/assets/`. Tanto
Tkinter como la Web deben resolverlos desde `AssetCatalog`:

- Tkinter los obtiene por `asset_path()` y `asset_candidate_paths()`.
- La Web recibe los nombres desde `editor_asset_manifest()` y los sirve por
  `/assets/<nombre>`; no debe mantener copias en `web/static`.
- PyInstaller incluye recursivamente `simulador_ev3/assets`.

La versión 2 del manifiesto declara por asset: `asset_id`, archivo, SHA-256,
dimensiones de origen, tipo, capa, dimensiones lógicas, conectores y anclas.
La variante aprobada de robot y de líneas es la que se encuentra hoy en este
directorio canónico, procedente de la línea de recursos usada por escritorio.

## Recursos del editor

| Grupo | IDs canónicos | Origen | Tamaño | Geometría lógica |
|---|---|---:|---:|---:|
| Robot | `robot_ev3_32x32` | PNG | 32×32 px | 1×1 celda / 100×100 mm |
| Líneas | `line_64_64_hor`, `line_64_64_ver`, `line_64x64_cruz`, cuatro curvas | PNG | 64×64 px | 2×2 celdas / 200×200 mm |
| Muros | `wall_64x64_a`, `wall_64x64_b`, `wall_64x64_c` | PNG | 64×64 px | 2×2 celdas |
| Zonas | `zone_green_128`, `zone_red_128`, `zone_white_128` | PNG | 128×128 px | 4×4 celdas |
| Pisos | `floor_tile_256_a`, `floor_tile_256_b`, `floor_tile_256_c` | PNG/JPG | 256×256 px | 8×8 celdas |

Los recursos de marca e inicio también pertenecen al catálogo, pero no forman
parte de la geometría de los mundos.

## Hallazgos de la línea base

1. Los mundos `01_linea_negra_basica` a `04_linea_negra_v3` contienen dos
   representaciones relacionadas: celdas físicas negras en `world.surface`
   para los sensores y placements `line_*` en `editor_spec` para la vista.
2. Si una interfaz prioriza celdas y otra placements, la misma pista puede
   parecer un obstáculo grueso en una UI y una línea conectable en la otra.
   La fase 3 debe fijar el orden de capas y una política única de visibilidad.
3. El robot se guarda como placement desde esquina superior izquierda, pero el
   snapshot físico expresa su pose desde el centro. El manifiesto explicita
   ambas anclas para impedir compensaciones distintas por interfaz.
4. Web ya dispone de carga asíncrona del asset canónico; el renderizador aún
   conserva símbolos de fallback. La fase 3 deberá comprobar que dichos
   fallbacks no sustituyen recursos aprobados en mundos normales.

## Evidencia automatizada disponible

- `tests/shared/test_asset_catalog.py` valida existencia, SHA-256,
  dimensiones de origen y todos los placements de los mundos incluidos.
- `tests/web/test_web_units.py` valida que la API Web publica el manifiesto
  versionado con la geometría necesaria para el cliente.
- `tests/release/test_asset_distribution.py` valida que PyInstaller y el ZIP,
  cuando están construidos, contienen las mismas versiones de los assets.

## Pendiente de la fase 1

Generar y almacenar capturas controladas de Web y Tkinter en 1920×1080,
1280×800 y 1024×768, claro y oscuro. Esas capturas serán la referencia de
comparación regional de la fase 5; este inventario no las sustituye.
