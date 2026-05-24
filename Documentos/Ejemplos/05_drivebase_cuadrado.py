#!/usr/bin/env pybricks-micropython
"""
Ejemplo 02 - Dibujar un cuadrado con DriveBase.

Que aprender:
1. Usar DriveBase en lugar de controlar motores por separado.
2. Combinar tramos rectos y giros de 90 grados.
3. Repeticion con for para trayectorias geometricas.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

    lado_mm = 220
    ev3.screen.clear()
    ev3.screen.print("02: cuadrado")

    # Recorre 4 lados: avanzar + girar 90.
    for lado in range(4):
        ev3.screen.print("Lado", lado + 1, "/4")
        robot.straight(lado_mm)
        robot.turn(90)

    robot.stop()
    ev3.screen.print("Listo")
    wait(200)


if __name__ == "__main__":
    main()
