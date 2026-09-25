# Manifiesto de Madurez Integral (MMI) v1

Versión de manifiesto: `1`
Objetivo de liberación: `100/100` en funcionalidad y calidad; mínimo `95/100`
en las restantes dimensiones aplicables.

## Dimensiones, peso y responsable

| ID | Dimensión | Peso | Umbral | Responsable |
| --- | --- | ---: | ---: | --- |
| architecture | Arquitectura y contratos | 18 | 95 | Arquitectura |
| experience | Diseño, accesibilidad y navegación | 16 | 95 | UX/UI |
| functionality | Funcionalidad y sesión | 22 | 100 | Desarrollo |
| learning | Experiencia didáctica, ayuda y pedagogía | 14 | 95 | Producto educativo |
| quality | Calidad, pruebas y liberación | 18 | 100 | QA |
| observability | Observabilidad y soporte | 12 | 95 | Operación |

La puntuación ponderada total es 100. Una dimensión bajo su umbral o una fila
aplicable sin evidencia en **Web y Tkinter** bloquea el cierre del cambio.

## Regla de evidencia

Cada `UC-*` del catálogo `interface-parity-v1` exige una prueba automatizada y
una evidencia manual reproducible por interfaz. La matriz operativa está en
[`Documentos/MATRIZ_MADUREZ_WEB_TKINTER.md`](../../Documentos/MATRIZ_MADUREZ_WEB_TKINTER.md).
La verificación `tests/shared/test_maturity_manifest.py` impide declarar una
fila como cerrada sin ambas evidencias.

## Adaptaciones legítimas

| Adaptación | Evidencia equivalente |
| --- | --- |
| Web móvil | Capturas y flujo táctil a 390×844; Tkinter no aplica. |
| Instalador Tkinter | Arranque de ejecutable/instalador Windows; Web no aplica. |
| Persistencia Web | Sesión/red del navegador; Tkinter valida almacenamiento local equivalente. |

Ninguna adaptación elimina el caso de uso ni cambia su resultado de dominio.
