# Propuesta: unificar el menú principal Web y escritorio

## Motivo

BotLab Studio Web y la aplicación de escritorio exponen controles similares con categorías, orden y nivel de detalle distintos. El menú actual mezcla acciones cotidianas, contenido didáctico, preferencias técnicas y diagnóstico. Además, `Ejemplos`, `Mundos` y `Escenarios` se solapan conceptualmente, mientras que `Fidelidad`, `Tiempo máximo` y `Trazas` son poco comprensibles para estudiantes sin contexto.

## Cambio propuesto

Adoptar en ambos productos una taxonomía común:

**Archivo · Aprender · Mundos · Prácticas guiadas · Configuración · Diagnóstico · Ayuda**

La organización conserva todas las capacidades útiles, reduce duplicidad y explica las opciones técnicas mediante etiquetas, valores actuales y ayuda contextual. No se eliminan funciones sin una alternativa equivalente.

## Alcance

- Reorganizar el menú principal Web y Tkinter con las mismas categorías, orden, etiquetas y atajos cuando sean aplicables.
- Trasladar los ejemplos a **Aprender**, agrupados por nivel y tema.
- Renombrar **Escenarios** como **Prácticas guiadas** e informar objetivo, programa y mundo que se cargarán; integrar allí los retos evaluables para no duplicar rutas didácticas.
- Reunir tema, fidelidad y límite de ejecución en **Configuración de simulación**.
- Reunir trazas, diagnóstico de sesión y exportación en **Diagnóstico**.
- Mantener en Ayuda el centro de ayuda, guía rápida, libro y Acerca de.
- Corregir cargas de ejemplo o mundo que terminen con sesión expirada, errores silenciosos o editor sin actualizar.
- Incorporar pruebas de equivalencia funcional y accesibilidad.

## Fuera de alcance

- Eliminar ejemplos, mundos, retos evaluables, diagnósticos o preferencias existentes.
- Cambiar el motor de simulación, el modelo de sesión o el formato de mundos.
- Añadir autenticación, roles o cuentas de usuario.

## Éxito esperado

Una persona identifica dónde encontrar cada función sin conocer términos técnicos; la misma acción se encuentra en la misma categoría en Web y escritorio, y las cargas de contenido comunican éxito o fallo verificable.
## Anexo: menú final y responsabilidad

| Categoría final | Incluye | Sustituye o reubica |
|---|---|---|
| **Archivo** | Nuevo, abrir, guardar, guardar como y estado de cambios | Punto único para el programa del usuario. |
| **Aprender** | Ejemplos agrupados por nivel y tema | **Ejemplos**. |
| **Mundos** | Editor, mundo en blanco, importar y preestablecidos | **Mundos** actual, con sus acciones diferenciadas. |
| **Prácticas guiadas** | Objetivo, mundo, programa, pasos y sección de retos evaluables | **Escenarios** y la antigua ruta principal de **Misiones**. |
| **Configuración** | Tema, fidelidad/perfil y límite de ejecución | **Tema**, **Fidelidad** y **Tiempo máximo**. |
| **Diagnóstico** | Trazas, salud de sesión y exportación segura | **Trazas** y herramientas diagnósticas dispersas. |
| **Ayuda** | Centro de ayuda, guía rápida, manual, libro y Acerca de | Entradas informativas de **Ayuda**. |

El orden es obligatorio en Web y escritorio. Las adaptaciones por falta de espacio no pueden cambiar la categoría principal de una acción ni crear una segunda ruta principal redundante.

El alcance incorpora un catálogo declarativo compartido para categorías, descripciones accesibles, iconos semánticos y el mapeo de nombres anteriores. También conserva enlaces y automatizaciones heredadas mediante alias interno, redirección o mapeo documentado, sin conservar rótulos ambiguos en la interfaz final.
