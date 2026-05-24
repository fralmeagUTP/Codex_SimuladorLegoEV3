## Simulador EV3 Pybricks v1.3.2

Release de estabilidad operativa, depuracion web y actualizacion de pruebas/documentacion.

### Novedades principales
- Control de parada simplificado:
  - Se consolida el flujo en el boton `Detener y reiniciar`.
  - Se elimina ambiguedad entre detener y resetear.
- Cierre de ejecucion mas robusto:
  - Al finalizar un script, la simulacion se detiene y reinicia automaticamente.
  - Se reduce la probabilidad de sesiones en estado colgado.
- Depuracion web:
  - Resaltado de linea actual de ejecucion en editor.
  - Mejor consistencia entre breakpoints, paso y estado visible.
- Editor de mundos y ejemplos:
  - Compatibilidad de pruebas E2E con paleta visual de assets.
  - Catalogo de ejemplos educativos reordenado y validado.

### Validacion de calidad
- Suite completa ejecutada localmente:
  - `python -m pytest -q`
  - Resultado: `565 passed`.

### Archivos clave actualizados
- `simulador_ev3/web/static/js/simulation_app.js`
- `simulador_ev3/web/static/js/world_editor_app.js`
- `tests/e2e/test_web_playwright.py`
- `tests/web/test_web_app.py`
- `tests/release/test_full_program_health.py`
- `README.md`
- `Documentos/MANUAL_DE_USO.md`
- `CHANGELOG.md`

