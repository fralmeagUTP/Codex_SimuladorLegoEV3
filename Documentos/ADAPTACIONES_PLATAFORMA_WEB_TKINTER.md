# Adaptaciones legítimas de plataforma: Web y Tkinter

Estas diferencias no son brechas de producto: preservan el mismo resultado de
dominio, contrato de sesión y ruta pedagógica mediante mecanismos adecuados a
cada plataforma.

| Área | Web | Tkinter | Evidencia requerida |
| --- | --- | --- | --- |
| Ventana y tamaño | Navegador responsivo: 1920×1080, 1280×800, 1024×768 y 390×844. | Ventana nativa Windows: 1920×1080, 1280×800 y 1024×768. | Capturas claro/oscuro y recorrido de teclado. |
| Sesión | Token, cookie, REST/SSE y recuperación ante red. | Sesión local y worker aislado. | Mismo `SimulationSessionPort`, snapshots y estados terminales. |
| Archivos | Selector/descarga del navegador, sin rutas locales expuestas. | Diálogo nativo abrir/guardar e instalador. | Mismo JSON/Python validado y mensajes equivalentes. |
| Móvil | Objetivos táctiles y canvas ajustado al contenedor. | No aplica: aplicación de escritorio. | E2E a 390×844 en Web; excepción MMI documentada. |
| Accesibilidad | Semántica HTML, `aria-live`, foco web y Escape. | Foco nativo, atajos y diálogos Tk. | Tab, Shift+Tab, Enter y Escape en ambos entornos. |
| Recursos | `/assets/<filename>` sirve el `AssetCatalog` canónico. | El bundle y el proceso local resuelven el mismo `asset_id`. | Hash/presencia en pruebas de empaquetado. |

No se admite una adaptación que cambie los datos de robot, estado de ejecución,
criterio de misión, ayuda o capacidad didáctica.
