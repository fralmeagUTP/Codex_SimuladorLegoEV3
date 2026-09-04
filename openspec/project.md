# Simulador EV3 Pybricks

## Propósito

Simulador educativo de programas LEGO EV3 escritos con una API de Python similar a Pybricks. Ofrece un mundo 2D determinista, hardware virtual, ejecución de scripts, edición de mundos e interfaces Tkinter y Flask.

## Alcance actual del producto

- La web es la interfaz principal: simulación (`/`), editor de mundos (`/worlds`) y ayuda (`/help`).
- Tkinter es una interfaz de escritorio activa y mantiene paridad funcional con
  la Web para los casos de uso compartidos; la Web sigue siendo la referencia
  visual adaptable.
- El simulador está dirigido al aprendizaje guiado y al uso local o en aulas controladas.
- La API virtual implementa un subconjunto útil de Pybricks EV3; no es un reemplazo byte a byte ni físicamente equivalente al hardware.

## Contexto técnico

- Python 3.11+; Flask 3.1+ para la web; Tkinter para escritorio.
- La simulación usa un paso fijo nominal de 20 ms (50 Hz).
- Las distancias del mundo y del movimiento se expresan en milímetros; la UI las muestra en centímetros; los ángulos visibles al usuario se expresan en grados.
- JSON es el formato estable de intercambio para mundos físicos.
- Las pruebas usan pytest, Playwright y Pywinauto; GitHub Actions ejecuta matrices
  Python 3.11/3.12 en Windows y Linux, además de E2E, contenedor y empaquetado.

## Principios de diseño

1. El dominio y la simulación DEBERÁN ser independientes de los frameworks UI.
2. Las UI DEBERÁN utilizar la fachada de aplicación en vez de orquestar directamente el motor, runtime y objetos Pybricks virtuales.
3. El backend web DEBERÁ ser la fuente de verdad de una sesión y su mundo.
4. Toda capacidad nueva DEBERÁ incluir propuesta de cambio, diseño, tareas y deltas de especificación en `openspec/changes/`.
5. Las diferencias frente a EV3/Pybricks físico DEBERÁN documentarse y no presentarse silenciosamente como comportamiento exacto.

## Mapa del repositorio

- `simulador_ev3/domain`: modelos de robot, motores, sensores, brick y mundo.
- `simulador_ev3/core`: motor, bus de eventos y cola de comandos.
- `simulador_ev3/runtime`: política de scripts, sandbox y controlador.
- `simulador_ev3/pybricks_api`: módulos Pybricks virtuales por sesión.
- `simulador_ev3/application`: fachadas de simulación y editor de mundos.
- `simulador_ev3/web`: aplicación Flask, sesiones, API, assets y UI.
- `simulador_ev3/ui`: interfaz Tkinter heredada.
- `worlds` y `examples`: recursos educativos compartidos.
- `tests`: verificación unitaria, integración, web, E2E, release y UI.
