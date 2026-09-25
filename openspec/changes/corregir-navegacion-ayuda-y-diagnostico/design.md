# Diseño: navegación inequívoca de ayuda y diagnóstico

## Contrato de menú compartido

Ambas interfaces presentarán las mismas seis opciones, en el mismo orden:

| Orden | Etiqueta | Destino |
|---|---|---|
| 1 | Centro de ayuda | Catálogo completo de ayuda |
| 2 | Guía rápida: primera simulación | Guía compartida `first-simulation` |
| 3 | Diagnóstico de sesión | Vista de diagnóstico de la sesión actual |
| 4 | Exportar diagnóstico JSON | Archivo JSON descargable/guardable |
| 5 | Libro: Programación en Python para robótica (LEGO EV3) | Ficha editorial oficial en navegador externo |
| 6 | Acerca de | Información institucional y versión |

La guía rápida puede compartir la página o ventana del Centro de ayuda, pero
debe posicionarse y enfocarse en la guía solicitada. No se etiquetará como
`Guía de actividad`, porque esa expresión no identifica su contenido ni su
alcance.

El enlace al repositorio institucional de la Universidad Tecnológica de
Pereira se abre con `target="_blank"` y `rel="noopener noreferrer"` en Web,
y con el navegador predeterminado en Tkinter. No se incrusta contenido externo
en la aplicación ni se recolectan datos del usuario.

## Diagnóstico

Se define un modelo de presentación separado del diálogo institucional:

- título visible: `Diagnóstico de sesión`;
- contenido: identificador de sesión, estado, tiempos, worker cuando exista,
  estadísticas de renderizado y errores operativos seguros;
- acciones: `Copiar`, `Exportar JSON` y `Cerrar` en Web; `Guardar JSON` y
  `Cerrar` en Tkinter cuando corresponda;
- el contenido se obtiene desde los adaptadores de observabilidad existentes y
  se serializa con formato JSON estable.

La Web debe usar un diálogo dedicado o un diálogo genérico cuyo título se
actualice explícitamente. No puede mostrar datos de diagnóstico bajo un
encabezado `Acerca de`.

## Exportación

La exportación genera un documento UTF-8 con extensión `.json`, nombre
sugerido que incluya fecha/hora y contenido equivalente en ambas plataformas.
La Web usará `Blob` y descarga del navegador; Tkinter mantendrá el selector de
archivo nativo. Ante cancelación no se mostrará error. Ante fallo se mostrará
un mensaje accionable sin perder la pantalla de diagnóstico.

## Accesibilidad y seguridad

- Todos los comandos se recorren con Tab y se activan con Enter/Espacio.
- Los diálogos se cierran con Escape y devuelven el foco al comando de origen.
- El diagnóstico no contiene fuente del programa, tokens, credenciales ni
  identificadores de otras sesiones.
- Los estados y errores se anuncian mediante regiones accesibles en la Web.

## Validación

Las pruebas deben verificar enlaces y anclas, títulos visibles de diálogos,
paridad de menú, contenido seguro, exportación JSON y cierre por Escape. Una
prueba E2E Web comprobará que el menú Ayuda no deja modales superpuestos.
