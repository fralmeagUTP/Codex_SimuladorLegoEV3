"""
Ejemplo 10 - Lectura combinada de sensores.

Que aprender:
1. Combinar ultrasonido, tacto y color en una sola logica.
2. Publicar estado resumido en LCD.
3. Reaccionar y cerrar el ciclo con retroceso controlado.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, UltrasonicSensor, TouchSensor, ColorSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

    us = UltrasonicSensor(Port.S4)
    ts = TouchSensor(Port.S1)
    cs = ColorSensor(Port.S3)

    timeout_ms = 18000
    stop_distance_mm = 140
    timer = StopWatch()
    next_report_ms = 0

    ev3.screen.clear()
    ev3.screen.print("10: sensores")
    robot.drive(140, 0)

    while timer.time() < timeout_ms:
        dist = us.distance()
        pressed = ts.pressed()
        color_value = cs.color()

        if timer.time() >= next_report_ms:
            ev3.screen.print("D", dist, "T", pressed)
            ev3.screen.print("C", color_value)
            next_report_ms += 700

        if dist < stop_distance_mm or pressed:
            ev3.screen.print("Obstaculo")
            break

        wait(20)

    robot.stop()
    robot.straight(-100)
    ev3.screen.print("Fin test")


if __name__ == "__main__":
    main()
