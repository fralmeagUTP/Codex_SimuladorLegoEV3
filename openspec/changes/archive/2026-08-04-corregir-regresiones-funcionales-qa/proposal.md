# Propuesta: corregir regresiones funcionales QA

## Motivo

La validación interactiva de Tkinter confirmó cuatro regresiones: pausar no
conserva el tiempo pendiente de `wait()`, las trazas del worker se exportan
vacías, el encabezado no identifica el mundo activo y el diálogo Acerca de no
se centra sobre la ventana principal.

## Cambio propuesto

Hacer cooperativa la pausa de las esperas Pybricks, registrar snapshots que
llegan del worker aislado, conservar un nombre de mundo visible en la UI y
centrar los diálogos secundarios. Las correcciones se harán en contratos y
adaptadores compartidos cuando aplique, sin modificar las reglas de simulación.

## Fuera de alcance

- Crear una nueva evaluación visual de resultados de misión.
- Cambiar formatos de mundos o trazas ya publicados.
- Rediseñar la interfaz Web.
