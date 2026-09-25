# Evidencia de verificación - Centro de ayuda

Fecha: 2026-07-31.

## Alcance comprobado

- Web: la ruta `/help` muestra siete guías, búsqueda con `aria-live`, filtro
  por categoría, rutas de recuperación, tema claro/oscuro y enlaces hacia
  Simulación o el Editor de mundos.
- Web móvil: comprobado en navegador real a `390×844`; no hay desbordamiento
  horizontal y el encabezado, buscador y tarjetas permanecen legibles.
- Tkinter: la apertura del Centro de ayuda, sus menús, el cierre de ventana y
  la navegación nativa fueron ejercitados en una sesión gráfica de Windows.

## Comandos reproducibles

```powershell
.\.venv\Scripts\python.exe -m pytest tests/shared/test_help_tutorials.py tests/web/test_web_app.py -q
.\.venv\Scripts\python.exe -m pytest tests/e2e/test_web_playwright.py -q -k "help_page_is_available_from_browser or help_menu_opens_the_help_center"
$env:EV3_RUN_DESKTOP_E2E = "1"
.\.venv\Scripts\python.exe -m pytest tests/e2e/test_desktop_pywinauto.py -q
```

Resultados de esta ejecución: 90 pruebas de catálogo/Web aprobadas, 2 flujos
E2E Web aprobados y 4 flujos E2E Tkinter aprobados.

## Paridad y limitaciones conocidas

Las dos interfaces usan las mismas siete entradas de ayuda, nombres, pasos,
resultados esperados, recuperación y destinos. La Web incluye selector de tema
explícito; Tkinter aplica el tema global existente. Las diferencias de borde,
foco y scrollbar pertenecen a los controles nativos de Tkinter.
