"""
Ejemplo 14 - Navegacion hasta pared.

Que aprender:
1. Integrar DriveBase con sensor ultrasonico.
2. Condicion de parada por distancia.
3. Mensaje final en LCD con medicion.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)
    us = UltrasonicSensor(Port.S4)

    timer = StopWatch()
    timeout_ms = 12000
    stop_distance_mm = 120

    ev3.screen.clear()
    ev3.screen.print("14: pared")
    ev3.screen.print("Busca pared")
    robot.drive(180, 0)

    while timer.time() < timeout_ms and us.distance() > stop_distance_mm:
        wait(20)

    robot.stop()
    ev3.screen.print("Dist", us.distance(), "mm")
    ev3.screen.print("Detenido")


if __name__ == "__main__":
    main()
