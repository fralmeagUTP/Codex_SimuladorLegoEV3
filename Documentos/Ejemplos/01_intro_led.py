#!/usr/bin/env pybricks-micropython
"""
Ejemplo 11 - LED rojo.

Que aprender:
1. Control del LED del brick.
2. Temporizacion basica con wait.
"""

from pybricks.hubs import EV3Brick
from pybricks.tools import wait
from pybricks.parameters import Color


def main():
    ev3 = EV3Brick()

    ev3.screen.clear()

    ev3.screen.print("LED verde")
    ev3.light.on(Color.GREEN)
    ev3.screen.print("LED ON")
    wait(3000)
    
    ev3.screen.print("LED naranja")
    ev3.light.on(Color.ORANGE)
    ev3.screen.print("LED ON")
    wait(3000)

    ev3.screen.print("LED rojo")
    ev3.light.on(Color.RED)
    ev3.screen.print("LED ON")
    wait(3000)
    

    ev3.light.off()
    ev3.screen.print("LED OFF")
    wait(120)


if __name__ == "__main__":
    main()
