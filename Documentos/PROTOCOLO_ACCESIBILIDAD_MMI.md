# Protocolo de accesibilidad MMI

## Propósito

Completar la verificación manual de la tarea OpenSpec 3.3 para Web y Tkinter.
Las comprobaciones automatizadas de contraste, tema, foco y teclado acompañan
este protocolo, pero no sustituyen la escucha real de un lector de pantalla.

## Entorno

- Windows 10/11, Narrador (`Win` + `Ctrl` + `Enter`) o NVDA actualizado.
- Navegador Chrome o Edge para la Web.
- Aplicación Tkinter iniciada desde el entorno virtual o paquete distribuido.
- Temas claro y oscuro; tamaños Web 1920×1080, 1280×800, 1024×768 y 390×844;
  tamaños Tkinter 1920×1080, 1280×800 y 1024×768.

## Recorrido obligatorio por plataforma

| ID | Acción | Resultado esperado | Web | Tkinter |
|---|---|---|---|---|
| ACC-01 | Alternar claro → oscuro → claro tres veces. | Fondos, texto, bordes, foco, telemetría y diálogos conservan contraste. | PASS manual 2026-08-23 | PASS manual 2026-08-23 |
| ACC-02 | Recorrer con Tab y Shift+Tab los menús, controles de simulación, editor, telemetría y ayuda. | Foco visible, orden lógico y ningún control inaccesible. | PASS manual 2026-08-23 | PASS manual 2026-08-23 |
| ACC-03 | Abrir/cerrar menú y diálogo con Enter/Escape. | El foco vuelve al disparador y no queda modal bloqueado. | PASS manual 2026-08-23 | PASS manual 2026-08-23 |
| ACC-04 | Activar Narrador/NVDA y recorrer encabezados, botones, menús, editor, estado y telemetría. | Se anuncian nombre, rol, estado y valor útil; no hay controles sin nombre. | PASS manual 2026-08-23 | PASS manual 2026-08-23 |
| ACC-05 | Ejecutar un programa corto, esperar éxito y detener/reiniciar otro. | El estado terminal, toast Web o diálogo Tkinter se anuncia una sola vez y el foco sigue utilizable. | PASS manual 2026-08-23 | PASS manual 2026-08-23 |

## Evidencia requerida

Para cada caso, registrar fecha, versión/commit, resolución, tema, lector de
pantalla y resultado PASS/FAIL/BLOCKED. Adjuntar captura y, si es posible,
grabación de audio. Un FAIL debe agregarse a
`REGISTRO_DEFECTOS_MMI_YYYY-MM-DD.md` con severidad y caso de regresión.

## Automatización complementaria

- Web: contraste WCAG AA, orden de Tab, Enter/Escape y controles secundarios:
  `tests/e2e/test_web_playwright.py`.
- Tkinter: aplicación de tokens, telemetría dinámica y Escape:
  `tests/ui/test_theme_regression.py` y `tests/ui/test_ui.py`.

### Evidencia técnica adicional — 2026-08-23

La siguiente ejecución operó una ventana Tkinter real mediante Pywinauto:

```powershell
$env:EV3_RUN_DESKTOP_E2E='1'
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_desktop_pywinauto.py -k "controls_cover_execution_debug_and_keyboard or success_dialog_is_shown_once_after_finished" -q
```

Resultado: **2 PASS en 21.25 s**. Se recorrieron controles de ejecución y
depuración, el atajo `Ctrl+N`, teclado y el cierre con `Enter` del diálogo
nativo de finalización. Esta evidencia cubre parte de ACC-02, ACC-03 y ACC-05
en Tkinter, pero no sustituye ACC-04: la comprensión audible de los anuncios
del lector debe ser confirmada por una persona usuaria.

El 2026-08-23 se corrigió una regresión detectada manualmente: Tab no entraba
en los menús de cabecera de Tkinter. Los menús ahora declaran `takefocus=True`
y un anillo de foco temático. La regresión nativa
`test_desktop_tab_moves_between_header_menus` aprobó en **1.89 s** y confirma
el avance de foco de **Archivo** a **Ejemplos**.

La confirmación humana auditiva se realizó el 2026-08-23 con Narrador de
Windows. Las comprobaciones manuales y automatizadas dejan el protocolo
cerrado para ambas interfaces.
