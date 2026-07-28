# Evidencia de verificación

Fecha: 2026-07-28. Entorno: Windows, Python 3.12.5.

- `tests/ui/test_ui.py`: 89 aprobadas.
- E2E nativo de escritorio: 4 omitidas porque el runner de pytest no puede crear una segunda ventana visible; no es una aprobación visual.
- Ruff y Mypy sobre `main_window.py`: aprobados.
- OpenSpec estricto: aprobado.

La regresión unitaria confirma que una pantalla de 1920×1080 centra la introducción en `800x450+560+315`, que Pillow redimensiona la imagen con `LANCZOS` a `(800, 450)` y que el lanzador solicita el estado Tk `zoomed` para la ventana principal.
