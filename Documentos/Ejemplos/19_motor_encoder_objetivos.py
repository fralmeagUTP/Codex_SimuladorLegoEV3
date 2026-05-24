#!/usr/bin/env pybricks-micropython
"""
Ejemplo 19 - Encoder de motor y posiciones objetivo.

Que aprender:
1. Resetear y leer el angulo del encoder.
2. Mover el motor a angulos absolutos con run_target().
3. Verificar posicion final con angle().
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait


def report(ev3, motor, label):
    ev3.screen.print(label, "ang", int(motor.angle()))


def main():
    ev3 = EV3Brick()
    arm = Motor(Port.A)

    ev3.screen.clear()
    ev3.screen.print("19: encoder")

    arm.reset_angle(0)
    report(ev3, arm, "inicio")

    arm.run_target(240, 90, then=Stop.HOLD, wait=True)
    report(ev3, arm, "obj 90")
    wait(250)

    arm.run_target(240, -45, then=Stop.HOLD, wait=True)
    report(ev3, arm, "obj -45")
    wait(250)

    arm.run_target(240, 0, then=Stop.BRAKE, wait=True)
    report(ev3, arm, "obj 0")

    arm.stop()
    ev3.screen.print("Fin")


if __name__ == "__main__":
    main()

