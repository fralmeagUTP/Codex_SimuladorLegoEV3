# Evidencia de verificación — navegación de ayuda y diagnóstico

Fecha: 2026-08-24  
Cambio OpenSpec: `corregir-navegacion-ayuda-y-diagnostico`

## Alcance comprobado

- Las dos interfaces consumen el mismo catálogo y orden de seis comandos de
  Ayuda.
- La guía rápida apunta a `first-simulation`.
- El diagnóstico Web usa título propio, oculta el contenido institucional y se
  cierra con Escape.
- La exportación Web descarga un JSON UTF-8 mediante `Blob`.
- Tkinter muestra y guarda el mismo esquema versionado mediante diálogo y
  selector de archivo nativos.
- `Acerca de` vuelve a mostrar solamente contenido institucional.
- El enlace al libro **Programación en Python para robótica: de la teoría a la
  práctica con LEGO EV3** abre el repositorio institucional de UTP de forma
  segura en ambas interfaces.

## Comandos ejecutados y resultados

```powershell
.\.venv\Scripts\python.exe -m pytest tests/shared/test_session_diagnostics.py tests/shared/test_help_tutorials.py tests/web/test_web_app.py -k "diagnostic or help_menu" -q
```

Resultado: **5 passed**.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ui/test_ui.py::TestMainWindow::test_session_diagnostics_uses_shared_schema_and_safe_native_export tests/e2e/test_web_playwright.py::test_help_diagnostics_has_its_own_title_and_exports_safe_json -q
```

Resultado: **2 passed**. La prueba Web opera una instancia Flask y Chromium:
abre el menú, visualiza el diagnóstico, usa Escape, descarga el JSON y abre
Acerca de sin diálogos superpuestos.

```powershell
.\.venv\Scripts\python.exe -m pytest \
  'tests/e2e/test_web_playwright.py::test_critical_web_text_keeps_wcag_aa_contrast_in_each_theme[#runBtn-dark]' \
  'tests/e2e/test_web_playwright.py::test_critical_web_text_keeps_wcag_aa_contrast_in_each_theme[#sessionStatus-dark]' \
  'tests/e2e/test_web_playwright.py::test_critical_web_text_keeps_wcag_aa_contrast_in_each_theme[#telemetryStatus-dark]' \
  'tests/e2e/test_web_playwright.py::test_critical_web_text_keeps_wcag_aa_contrast_in_each_theme[#telemetryTick-dark]' \
  'tests/e2e/test_web_playwright.py::test_critical_web_text_keeps_wcag_aa_contrast_in_each_theme[#telemetryCollision-dark]' -q
```

Resultado: **5 passed**. La paleta oscura mantiene contraste WCAG AA para los
controles y estados críticos. Los casos claros pertenecen a la misma prueba
parametrizada y se ejecutan en la suite completa de Web.

```powershell
.\.venv\Scripts\python.exe -m ruff check simulador_ev3/shared/session_diagnostics.py simulador_ev3/ui/main_window.py tests/shared/test_session_diagnostics.py tests/ui/test_ui.py tests/web/test_web_app.py tests/e2e/test_web_playwright.py
```

Resultado: **All checks passed**.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/shared/test_help_tutorials.py::test_help_menu_actions_have_a_shared_order_and_specific_quick_guide tests/web/test_web_app.py::test_web_help_menu_offers_diagnostic_view_and_safe_json_export tests/web/test_web_app.py::test_web_help_menu_uses_the_shared_specific_quick_guide_label tests/ui/test_ui.py::TestMainWindow::test_external_book_reference_opens_the_default_browser tests/e2e/test_web_playwright.py::test_help_menu_offers_the_lego_ev3_book_in_a_new_secure_tab -q
```

Resultado: **5 passed**.

## Hallazgo corregido durante la verificación

`about-groups` tenía `display: grid`, que anulaba visualmente el atributo
HTML `hidden` dentro del diagnóstico. Se añadió
`.about-groups[hidden] { display: none; }`, dejando el diagnóstico separado de
la información institucional.
