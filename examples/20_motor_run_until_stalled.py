#!/usr/bin/env pybricks-micropython
"""
Ejemplo 20 - run_until_stalled y estado de motor.

Que aprender:
1. Usar run_until_stalled() para finalizar una accion por condicion.
2. Consultar done(), stalled() y load() del motor.
3. Reportar resultados de la maniobra en LCD.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait


def main():
    ev3 = EV3Brick()
    motor = Motor(Port.A)

    ev3.screen.clear()
    ev3.screen.print("20: stalled")

    motor.reset_angle(0)
    ev3.screen.print("run_until...")
    advanced = motor.run_until_stalled(300, then=Stop.BRAKE)

    ev3.screen.print("avance", int(advanced), "deg")
    ev3.screen.print("done", motor.done())
    ev3.screen.print("stall", motor.stalled())
    ev3.screen.print("load", int(motor.load()))

    wait(300)
    motor.stop()
    ev3.screen.print("Fin")


if __name__ == "__main__":
    main()

