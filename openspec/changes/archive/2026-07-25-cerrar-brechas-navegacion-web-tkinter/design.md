# Diseño: navegación equivalente entre interfaces

## Mapa de destinos

| Capacidad | Web | Tkinter | Resultado esperado |
| --- | --- | --- | --- |
| Simulación | `/` | Ventana principal | Ejecutar y observar una sesión. |
| Crear mundos | `/worlds` | `Mundos > Editor de mundos…` | Editar, validar y guardar JSON. |
| Simular mundo guardado | Enlace de la página de mundos | Acción visible tras guardar en el editor | El mundo queda cargado en la ventana principal. |
| Ayuda didáctica | `/help` | `Ayuda > Manual de uso…` | Mismos tutoriales, pasos, resultado y recuperación. |
| Acerca de | Diálogo de la Web | `Ayuda > Acerca de…` | Versión y alcance del producto. |

## Ayuda

La fuente de contenido se separará de su presentación. Un recurso estructurado
en español contendrá los tres tutoriales: crear mundo, ejecutar simulación y
depurar. La plantilla Web y la ventana Tkinter lo renderizarán con sus controles
nativos. Cada tutorial expondrá pasos, resultado esperado y acción de
recuperación; Tkinter incluirá botones o enlaces internos hacia el editor de
mundos y la ventana principal cuando corresponda.

## Retorno desde el editor de mundos

Después de validar y guardar correctamente, el editor Tkinter mostrará una
acción inequívoca **Simular mundo guardado**. La acción cerrará o relegará el
editor, activará la ventana principal y aplicará el mismo archivo JSON mediante
la fachada pública de sesión. Los errores de validación o carga no cambiarán la
sesión actual y se comunicarán con el mismo significado que en Web.

## Verificación

La prueba de contrato seguirá comprobando resultados de dominio. Se añadirá:

- Playwright para el mapa de enlaces Web y tutoriales.
- Automatización real de Tkinter en Windows (ratón/teclado) para menús,
  ventana de ayuda, editor, guardado y retorno a simulación.
- Una prueba de catálogo que falle si un destino obligatorio no tiene evidencia
  Web y Tkinter o si el contenido de tutorial diverge.

La automatización de escritorio se aislará y podrá omitirse solo en entornos
sin escritorio interactivo, informándolo claramente en CI.
