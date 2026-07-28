# Propuesta: habilitar eliminación segura de mundos en Tkinter

## Motivo

El editor permite eliminar objetos del lienzo, pero no eliminar un archivo de
mundo guardado. Esto impide completar el ciclo crear/editar/eliminar desde la
interfaz y deja archivos temporales o de práctica sin gestión explícita.

## Cambio

Añadir una acción **Eliminar archivo de mundo** para el archivo abierto en el
Editor de Mundos. Debe pedir confirmación, eliminar solo un mundo personalizado
del directorio de mundos configurado y volver el editor a un mundo nuevo. Los
mundos preestablecidos del proyecto no pueden eliminarse desde la interfaz.

La aplicación Web ofrecerá la misma operación para el último mundo guardado,
con la misma protección de recursos incluidos y validación de sesión.

## Fuera de alcance

- Eliminar objetos individuales (capacidad ya existente).
- Borrado masivo, papelera o recuperación.
- Cambios en el formato de mundo.
