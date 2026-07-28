# Propuesta: notificar finalización correcta de programa

## Objetivo

Informar de forma inequívoca que un programa Pybricks terminó correctamente, con el mismo mensaje y semántica en Web y Tkinter.

## Alcance

- Web: toast accesible, no modal, cerrable y con desaparición automática.
- Tkinter: diálogo informativo nativo no duplicado.
- Notificar solo el estado terminal `finished`, después del snapshot terminal coherente.
- Cubrir deduplicación, cancelación, reinicio y estados de error mediante regresión.

## Fuera de alcance

No se modifican reglas del motor, resultados de misión ni la política de límites de tiempo.
