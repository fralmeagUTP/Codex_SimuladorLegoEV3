# Propuesta: corregir altura de telemetría Tkinter

## Motivo

La captura real de Tkinter a 1280x800 muestra una telemetría de solo 334 px de alto.
En estado inicial solo se aprecia Motor A; el resto de motores y sensores queda fuera de la vista inicial.

## Cambio propuesto

Redistribuir el área inferior para presentar Robot/Estado, motores A-D y sensores S1-S4 de forma escaneable a 1280x800.
El scroll será un respaldo para tamaños menores, no el medio normal para descubrir la telemetría.

## Fuera de alcance

- Datos, frecuencia de actualización y reglas de simulación.
- Rediseño funcional de la aplicación Web.
- Sustitución de widgets Tkinter o del motor de canvas.
