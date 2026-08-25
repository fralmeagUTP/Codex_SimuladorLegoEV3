# Inventario de ayuda previo a la implementación

| Comando | Web actual | Tkinter actual | Decisión |
|---|---|---|---|
| Centro de ayuda | `/help`, catálogo completo | Ventana Centro de ayuda | Conservar. |
| Guía de actividad | `/help#guide-first-simulation` | No disponible desde menú | Renombrar como `Guía rápida: primera simulación` y exponer en ambas. |
| Diagnóstico de sesión | Reutiliza el diálogo de Acerca de | `messagebox` con título correcto | Separar diálogo Web en fase 3. |
| Exportar diagnóstico JSON | No disponible | Selector de archivo nativo | Añadir en Web en fase 3. |
| Acerca de | Diálogo institucional | Ventana institucional | Conservar solo para información institucional. |

## Esquema de diagnóstico acordado

La exportación usará UTF-8 y un objeto con `schema_version`, `generated_at`,
`session`, `runtime`, `render` y `worker` cuando aplique. No incluirá fuente
del editor, credenciales, cookies, tokens ni datos de otras sesiones.
