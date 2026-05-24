#!/usr/bin/env pybricks-micropython
"""
Ejemplo 12 - Prueba de pantalla y altavoz.

Que aprender:
1. Mostrar mensajes en LCD.
2. Emitir tonos con distintas frecuencias.
3. Medir tiempo con StopWatch.
"""

from pybricks.hubs import EV3Brick
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    sw = StopWatch()

    ev3.screen.clear()
    ev3.screen.print("12: A/V test")
    ev3.screen.print("LCD OK")

    # Secuencia de tonos de referencia.
    ev3.speaker.beep(440, 180)
    wait(220)
    ev3.screen.print("Beep 660")

    ev3.speaker.beep(660, 180)
    wait(220)
    ev3.screen.print("Beep 880")

    ev3.speaker.beep(880, 220)
    wait(260)

    # Muestra tiempo acumulado mientras emite un tono corto.
    ev3.screen.print("Cronometro")
    for _ in range(6):
        ev3.screen.print(sw.time(), "ms")
        ev3.speaker.beep(523, 70)
        wait(170)

    ev3.screen.print("Fin")
    ev3.speaker.beep(330, 120)
    wait(120)
    ev3.speaker.beep(262, 220)


if __name__ == "__main__":
    main()
