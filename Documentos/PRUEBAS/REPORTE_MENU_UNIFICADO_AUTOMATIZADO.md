# Evidencia automatizada: menú unificado Web y escritorio

## Alcance

Evidencia técnica de la implementación del menú final:

`Archivo · Aprender · Mundos · Prácticas guiadas · Misiones · Configuración · Diagnóstico · Ayuda`

No sustituye la revisión pedagógica con estudiantes o docentes ni la inspección visual humana de contraste y redimensionamiento. Esas actividades se mantienen en el protocolo manual asociado.

## Resultados verificados

| Área | Evidencia | Resultado |
|---|---|---|
| Catálogo compartido | Prueba contractual de etiquetas, orden y migración de nombres históricos. | Aprobado |
| Carga de contenido Web | Ejemplos, mundos, prácticas y misiones; recuperación de sesión y conservación de cambios no guardados. | Aprobado |
| Configuración Web | Tema, perfil realista y límite de 30 s con estado `aria-pressed`. | Aprobado |
| Accesibilidad Web | Navegación con teclado, foco, escape y bloqueo durante ejecución. | Aprobado |
| Catálogo Tkinter | 23 ejemplos, cuatro prácticas y tres misiones desde menús nativos. | Aprobado |
| Estados Tkinter | Bloqueo durante ejecución y desbloqueo después de detener o finalizar. | Aprobado |
| Interacción Tkinter | Atajos, foco por Tab y aviso único al finalizar en una ventana nativa real. | Aprobado |
| Composición Tkinter | Inspección de tema claro/oscuro a 1280×800 y 1024×720; sin solapamiento, con desplazamiento vertical cuando el alto no basta. | Aprobado |

## Resumen de ejecución

| Conjunto | Resultado |
|---|---:|
| Pruebas unitarias e integración Web/Tkinter | 220 aprobadas |
| Recorrido Web de menús, catálogos, configuración, misiones y bloqueo durante ejecución | 5 aprobadas |
| Interacción nativa de escritorio: catálogo, controles, Tab, aviso de finalización y restauración | 5 aprobadas |

## Comandos ejecutados

```powershell
.\.venv\Scripts\python.exe -m pytest tests\web\test_web_app.py -k "content_loading or content_replacement or missions" -q
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py::test_simulation_menus_load_examples_worlds_and_scenarios tests\e2e\test_web_playwright.py::test_real_catalog_loads_every_example_world_scenario_and_mission -q
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_web_playwright.py::test_settings_menu_updates_theme_profile_and_runtime_with_visible_state tests\e2e\test_web_playwright.py::test_mission_menu_exposes_requirements_and_visible_progress -q
$env:EV3_RUN_DESKTOP_E2E = "1"
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_desktop_pywinauto.py::test_desktop_real_catalog_loads_examples_scenarios_and_missions tests\e2e\test_desktop_pywinauto.py::test_desktop_menus_unlock_after_execution_finishes_or_resets -q
.\.venv\Scripts\python.exe -m pytest tests\e2e\test_desktop_pywinauto.py::test_desktop_controls_cover_execution_debug_and_keyboard tests\e2e\test_desktop_pywinauto.py::test_desktop_tab_reaches_header_menus_from_native_window tests\e2e\test_desktop_pywinauto.py::test_desktop_success_dialog_is_shown_once_after_finished -q
```

## Pendiente manual antes de liberar

1. Aplicar el protocolo `PROTOCOLO_VALIDACION_MENU_UNIFICADO.md` con al menos una persona estudiante o docente.
2. Revisar visualmente el navegador a anchura reducida con una persona usuaria y registrar cualquier ajuste de microcopia.
3. Adjuntar el formulario completado a la evidencia de liberación.

## Capturas generadas durante esta implementación

- `artifacts/e2e-desktop/menu-unified/simulacion_light_1280x800.png`: composición real de escritorio y verificación geométrica de telemetría, Brick y LCD.
- `artifacts/e2e-desktop/menu-unified/simulacion_dark_1280x800.png`: misma composición de escritorio con tema oscuro, para contrastar la legibilidad de la telemetría y la pantalla LCD.
- `artifacts/e2e-desktop/menu-unified/simulacion_light_1024x720.png` y `simulacion_dark_1024x720.png`: inspección del diseño con altura reducida; los paneles conservan su geometría y el contenido vertical queda disponible mediante desplazamiento.
- `artifacts/e2e-web/menu-unified/simulacion_1280x800.png`: composición de la simulación Web.
- `artifacts/e2e-web/menu-unified/mundos_1280x800.png`: composición del Editor de mundos Web.
