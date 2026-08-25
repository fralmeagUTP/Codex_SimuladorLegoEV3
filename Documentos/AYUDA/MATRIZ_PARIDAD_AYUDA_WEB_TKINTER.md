# Matriz de paridad: Centro de ayuda

| Capacidad | Web | Tkinter | Evidencia |
|---|---|---|---|
| Buscar y filtrar guías | Sí | Sí | Catálogo compartido `HELP_GUIDES` |
| Pasos marcables y reinicio | Sí, persistencia local | Sí, estado local de la ventana | Contrato `GuideProgress` |
| Abrir destino de la guía | Sí | Sí | `destination` compartido |
| Copiar ejemplo seguro | Sí | Sí | `HELP_SAFE_EXAMPLES` |
| Captura real y texto alternativo | Sí, PNG + transcripción | Sí, PNG; fallback textual | Manifiesto de visuales |
| Ruta docente | Sí, persistente | Sí, activable | `TEACHER_ROUTE` |
| Tema claro/oscuro y foco | Sí | Sí | Tokens de tema y widgets nativos |

La persistencia Web se limita al progreso y a la preferencia de modo docente.
No guarda fuente del programa, token de sesión, rutas locales, credenciales ni
datos de un robot físico.
