# Propuesta: exponer resultados de misión en las interfaces

## Motivo

El catálogo y el evaluador de misiones existen, pero Tkinter carga una misión
como mundo y script inicial sin evaluar ni presentar un resultado al finalizar.
Esto impide validar éxito, fallo y cancelación desde la interfaz y deja una
diferencia funcional respecto al servicio Web disponible.

## Cambio propuesto

Evaluar la misión activa a partir de la traza al finalizar, fallar o cancelar;
presentar estado, criterios y puntuación en Tkinter y Web con el mismo contrato
de sesión; y añadir pruebas de los tres desenlaces.

## Fuera de alcance

- Cambiar criterios o rúbricas ya definidos en el catálogo.
- Cambiar la física, scripts iniciales o mundos de misión.
