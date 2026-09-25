# Matriz de paridad actual — Web y Tkinter v1

Fecha de auditoría: `2026-07-24`  
Catálogo evaluado: `interface-parity-v1`  
Alcance: capacidades utilizables por una persona, no similitud visual ni detalles
de transporte (REST, SSE o llamadas locales).

## Criterios

- **Completa**: ambas interfaces permiten el caso de uso con la misma semántica
  de dominio y el mismo estado final esperado.
- **Parcial**: ambas cubren el flujo principal, pero una omite una capacidad que
  el catálogo agrupa dentro del mismo caso de uso.
- **Exclusiva**: solo una interfaz ofrece la capacidad; se convierte en trabajo
  obligatorio de la tarea 2.2 si es aplicable a ambas UI.
- **Planificada**: aún no es una capacidad del producto.

## Casos de uso del catálogo

| ID | Web | Tkinter | Estado actual | Evidencia principal | Acción de cierre |
| --- | --- | --- | --- | --- | --- |
| UC-SESSION-01 | Crea, reinicia, cierra y recupera sesiones con token. | Crea, reinicia y recupera localmente script, mundo y depuración. | Completa | `web/routes/api_simulation.py`, `web/session_manager.py`, `ui/main_window.py`, `shared/ui_settings.py` | Añadir E2E/GUI equivalente. |
| UC-CODE-01 | Editor, ejemplos, abrir/guardar desde navegador. | Editor, abrir/guardar y ejemplos. | Completa | `web/static/js/simulation_app.js`, `ui/editor_panel.py` | Añadir pruebas de contrato equivalentes. |
| UC-RUN-01 | Ejecuta y conserva `finished`. | Ejecuta y presenta `Finalizado`. | Completa | `web/services/simulation_session.py`, `ui/main_window.py` | Añadir E2E/GUI equivalente. |
| UC-RUN-02 | Pausa, reanuda, detiene y reinicia. | Pausa, reanuda, detiene y reinicia. | Completa | `web/routes/api_simulation.py`, `ui/main_window.py` | Añadir pruebas de contrato equivalentes. |
| UC-DEBUG-01 | Breakpoints, watches, step y continue. | Breakpoints, watches, step y continue. | Completa | `web/templates/index.html`, `web/routes/api_simulation.py`, `ui/editor_panel.py` | Añadir E2E/GUI equivalente. |
| UC-ROBOT-01 | Permite definir pose inicial en el mapa. | Permite ubicar y orientar el robot en el canvas. | Completa | `web/static/js/simulation_app.js`, `ui/world_canvas.py` | Verificar tolerancia de coordenadas en prueba compartida. |
| UC-OBSERVE-01 | Mapa, sensores, telemetría y brick mediante snapshot/SSE. | Mapa, sensores, telemetría y brick mediante DTO local. | Completa | `web/static/js/simulation_app.js`, `ui/world_canvas.py`, `ui/telemetry_panel.py`, `ui/brick_panel.py` | Añadir prueba de snapshot renderizado para ambas UI. |
| UC-EXAMPLE-01 | Menús de ejemplos y escenarios. | Menús de ejemplos y escenarios. | Completa | `web/templates/index.html`, `ui/main_window.py` | Cubrir catálogo idéntico en pruebas. |
| UC-WORLD-01 | Crear, abrir, guardar, importar y exportar JSON. | Nuevo, abrir y guardar/guardar como JSON. | Parcial | `web/static/js/world_editor_app.js`, `ui/world_editor_window.py` | Unificar diálogos, estado de cambios y comandos mediante `WorldEditorSession`. |
| UC-WORLD-02 | Coloca, mueve, rota, duplica y elimina assets. | Coloca, mueve, rota, duplica y elimina assets. | Parcial | `web/routes/api_editor.py`, `ui/world_editor_window.py` | Migrar ambos adaptadores al contrato, categorías, ayudas y capas comunes. |
| UC-WORLD-03 | Valida y aplica el mundo a la sesión web. | Valida, guarda y aplica mediante `Simular mundo guardado`. | Completa | `web/routes/api_editor.py`, `ui/world_editor_window.py`, `ui/main_window.py` | Mantener la transición explícita y su prueba de error. |
| UC-HELP-01 | Tutorial web, manual y acerca de. | Manual contextual y acerca de. | Completa | `shared/help_tutorials.py`, `web/templates/help.html`, `ui/main_window.py` | Mantener una única fuente de tutoriales y pruebas de navegación. |
| UC-TRACE-01 | Inicia/detiene registro, avanza un tick y exporta JSON/CSV. | Inicia/detiene registro, avanza un tick y exporta JSON/CSV. | Completa | `trace_controls.js`, `ui/main_window.py`, prueba de contrato compartida | Mantener contrato de exportación versionado. |
| UC-PROFILE-01 | Selecciona perfiles ideal, realista o calibrado. | Selecciona los mismos perfiles desde el menú Fidelidad. | Completa | `profile_controls.js`, `ui/main_window.py`, prueba de contrato compartida | Mantener nombres y calibración equivalentes. |
| UC-ASSESS-01 | No disponible. | No disponible. | Planificada | Catálogo v1 | Fase 5.5. |

## Diferencias fuera de los casos de uso actuales

| Capacidad | Disponible en | Decisión de paridad |
| --- | --- | --- |
| Sesiones múltiples, token de propietario, recuperación y límites de capacidad | Web | Propia del transporte web; la semántica de una simulación local debe permanecer equivalente en Tkinter. |
| Streaming SSE y polling de respaldo | Web | Mecanismo de actualización, no función de usuario que deba duplicarse en Tkinter. |
| Tema claro/oscuro persistente | Web y Tkinter | Web usa `localStorage`; Tkinter guarda la preferencia local en `ui_settings.json`. |
| Seguimiento automático del robot y conmutador de haces de sensores | Web y Tkinter | Ya están presentes: Web centra el panel en cada snapshot y ofrece el conmutador; Tkinter sigue al robot y permite activar los haces. No requiere migración. |

## Brechas de composición del Editor de Mundos (2026-08-24)

| ID | Diferencia observada | Web | Tkinter | Cierre previsto |
| --- | --- | --- | --- | --- |
| WE-01 | Barra de acciones | Barra lineal sin grupos visibles. | Grupos operativos, pero mezcla etiquetas en inglés y español. | Acciones Archivo, Edición y Simulación canónicas. |
| WE-02 | Biblioteca | Búsqueda, categorías y guía inicial claras. | Búsqueda y categorías, con densidad y nombres diferentes. | Presentación proveniente del mismo manifiesto. |
| WE-03 | Inspector y capas | Jerarquía compacta con unidades comprensibles. | Inspector y capas presentes, distribución más técnica. | Contrato de selección, capas y propiedades común. |
| WE-04 | Activos | Reconstruía etiquetas y ayudas en JavaScript. | Catálogo Python de nombres y tooltips. | Metadatos localizados en `editor_asset_manifest`. |
| WE-05 | Estado de edición | Estado de sesión separado del modelo del editor. | Estado local de ventana. | Snapshot `WorldEditorSession` versionado. |

## Resultado y siguiente paso

La auditoría confirma trece casos funcionales principales y dos casos de
autoría en convergencia de experiencia. La paridad de dominio se conserva,
pero la paridad de composición y contrato de UI queda abierta en el cambio
`unificar-editor-mundos-web-tkinter`.
El catálogo y las pruebas de contrato compartidas se ejecutan en CI; un caso no
planificado no puede declararse exclusivo de una interfaz. Esta matriz se verifica
automáticamente contra todos los identificadores del catálogo para evitar que un
caso nuevo quede sin auditar.
