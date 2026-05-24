"""
Ejemplo 05A - Colision controlada con tacto.

Que aprender:
1. Diferencia entre mover y detectar impacto.
2. Uso de un tiempo maximo de prueba.
3. Cierre seguro de motores.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)
    touch = TouchSensor(Port.S1)

    timer = StopWatch()
    max_run_ms = 5000

    ev3.screen.clear()
    ev3.screen.print("05A: colision")
    ev3.screen.print("Avance")
    robot.drive(180, 0)

    while timer.time() < max_run_ms and not touch.pressed():
        wait(20)

    robot.stop()

    if touch.pressed():
        ev3.screen.print("Impacto OK")
    else:
        ev3.screen.print("Sin impacto")
        ev3.screen.print("Timeout 5s")

    wait(120)


if __name__ == "__main__":
    main()
