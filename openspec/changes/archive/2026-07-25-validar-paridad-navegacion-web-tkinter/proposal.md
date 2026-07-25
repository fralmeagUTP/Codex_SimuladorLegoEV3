# Propuesta: validar paridad de navegación Web–Tkinter

## Why

Formalizar en sintaxis OpenSpec válida la paridad ya implementada entre ayuda,
editor de mundos y simulación. Esta especificación reemplaza como fuente de
validación a la propuesta inicial de navegación, cuyos archivos quedaron
bloqueados por el entorno antes de poder convertir sus deltas al formato actual
de OpenSpec.

## What Changes

- Ayuda contextual compartida para crear mundos, simular y depurar.
- Transición explícita de mundo guardado a simulación en Tkinter.
- Pruebas Web, contratos y prueba nativa Windows activable localmente.

No cambia el motor, el formato JSON ni el contrato de sesión.
