#!/usr/bin/env pybricks-micropython
"""
Ejemplo 21 - Curvas con DriveBase y lectura de estado.

Que aprender:
1. Trazar arcos con curve(radius, angle).
2. Consultar state() para distancia/velocidad/giro actuales.
3. Comparar odometria antes y despues de cada tramo.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait


def print_state(ev3, robot, label):
    distance_mm, speed_mm_s, angle_deg, turn_rate = robot.state()
    ev3.screen.print(label, "d", distance_mm, "a", angle_deg)
    ev3.screen.print("v", speed_mm_s, "w", turn_rate)


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, 55.5, 104)

    ev3.screen.clear()
    ev3.screen.print("21: curva/state")

    print_state(ev3, robot, "inicio")
    robot.curve(radius=180, angle=90, wait=True)
    print_state(ev3, robot, "arco izq")
    wait(300)

    robot.curve(radius=-150, angle=-90, wait=True)
    print_state(ev3, robot, "arco der")
    wait(300)

    robot.stop()
    ev3.screen.print("dist", int(robot.distance()))
    ev3.screen.print("ang", int(robot.angle()))
    ev3.screen.print("Fin")


if __name__ == "__main__":
    main()

