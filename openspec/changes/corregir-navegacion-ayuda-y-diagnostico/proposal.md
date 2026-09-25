# Propuesta: aclarar la navegación de ayuda y el diagnóstico

## Motivo

La revisión de las dos interfaces identificó tres inconsistencias en el menú
**Ayuda**:

- En la Web, `Centro de ayuda` y `Guía de actividad` abren la misma página;
  la segunda solo cambia el ancla a `Mi primera simulación`. Aunque el enlace
  funciona, su nombre no comunica el destino y se percibe como redundante.
- En la Web, `Diagnóstico de sesión` reutiliza el diálogo visual de `Acerca de`.
  El contenido es diagnóstico, pero el encabezado visible sigue siendo
  `Acerca de`, por lo que la interfaz contradice el comando elegido.
- Tkinter incluye `Exportar diagnóstico JSON`, mientras que la Web no ofrece
  una acción equivalente. Además, Tkinter no expone desde el menú el acceso
  rápido que la Web llama `Guía de actividad`.

## Cambio propuesto

Unificar el menú Ayuda de Web y Tkinter, con destino y semántica inequívocos:

1. `Centro de ayuda`: abre el catálogo completo de guías.
2. `Guía rápida: primera simulación`: abre directamente la guía compartida
   `first-simulation`.
3. `Diagnóstico de sesión`: abre una superficie de diagnóstico titulada como
   tal, con datos de la sesión activa y del renderizado cuando corresponda.
4. `Exportar diagnóstico JSON`: descarga o guarda el mismo diagnóstico en un
   archivo JSON sin incluir código de usuario ni credenciales.
5. `Libro: Programación en Python para robótica (LEGO EV3)`: abre el registro
   institucional de UTP de la obra de los autores en una nueva pestaña o en el
   navegador predeterminado.
6. `Acerca de`: conserva exclusivamente la información institucional,
   versión, licencias y créditos.

## Fuera de alcance

- Cambiar el contenido didáctico de las guías existentes o la lógica de
  simulación.
- Exponer secretos, código del editor, credenciales o datos de otra sesión en
  el diagnóstico.
- Cambiar la arquitectura de observabilidad del runtime.

## Impacto

- Se ajustan los menús, diálogos y acciones de ayuda de ambas interfaces.
- Se añade exportación de diagnóstico en la Web y se normaliza la guía rápida
  en Tkinter.
- Se amplían las pruebas de destino de enlaces, título de diálogos, exportación
  y paridad de comandos.
