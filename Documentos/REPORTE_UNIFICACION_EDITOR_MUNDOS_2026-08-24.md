# Reporte de unificación del Editor de Mundos — 2026-08-24

## Alcance

Se completó el cambio OpenSpec `unificar-editor-mundos-web-tkinter`. Web y
Tkinter comparten el catálogo canónico, nombres en español, modelo de mundo,
reglas de validación, geometría y flujo Archivo → Edición → Simulación.

## Mejoras verificadas

- `WorldEditorSession` versión 1 ofrece un contrato de sesión para operaciones
  de edición sin cambiar el JSON compatible de mundos.
- La Web conserva los placements al redimensionar; si una reducción los deja
  fuera de límites, se rechaza sin perder el modelo editable.
- La Web indica cambios sin guardar y confirma antes de descartar al crear o
  abrir otro mundo.
- Web expone paneles Biblioteca e Inspector ocultables para portátil; Tkinter
  mantiene los paneles redimensionables mediante sus separadores nativos.
- Ambas interfaces incluyen búsqueda/categorías, guía de lienzo vacío,
  propiedades, capas, bloqueo, visibilidad, presets, zoom, atajos y transición
  de un mundo guardado a simulación.

## Evidencia ejecutada

| Comando | Resultado |
|---|---|
| `pytest tests/web/test_qa_world_crud.py -q` | 2 PASS: persistencia aislada y redimensionamiento seguro. |
| `pytest tests/e2e/test_web_playwright.py -k world_editor_preserves_assets -q` | 1 PASS en Chromium: placement, tamaño, indicador pendiente y paneles a 1024×768. |
| `pytest tests/shared/test_interface_execution_parity.py -k "world_editors_place_equivalent_asset or line_world_uses_identical_start_pose" -q` | 2 PASS: placement, assets y pose de inicio equivalentes. |
| `EV3_RUN_DESKTOP_E2E=1 pytest tests/e2e/test_desktop_pywinauto.py -k world_editor_applies_presets -q` | 1 PASS: ventana Tk real, preset Aula y Ctrl+S. |
| `ruff check …`, `node --check …`, `openspec validate unificar-editor-mundos-web-tkinter --strict` | PASS. |

## Diferencias nativas aceptadas

- Tkinter utiliza `filedialog`, `messagebox` y paneles `PanedWindow`; Web usa
  selector de archivos, `confirm` y paneles CSS. La semántica de cada acción y
  los datos persistidos son iguales.
- Los textos internos de algunos widgets Tk owner-drawn no son expuestos por
  Win32. La prueba Pywinauto identifica la instancia por `handle`, acciona el
  control físico y verifica el efecto recibido por la ventana real.

## Compuerta de calidad

El workflow `calidad` ejecuta ahora una compuerta explícita del editor de
mundos: sesión, servicio, catálogo, paridad, CRUD Web y navegación Tkinter.
La automatización Pywinauto continúa disponible para un escritorio Windows
visible mediante `EV3_RUN_DESKTOP_E2E=1`.
