"""
Ejemplo 15 - Esquiva de obstaculos.

Que aprender:
1. Fusion de dos sensores para toma de decision.
2. Patrón reactivo: detener, retroceder, girar.
3. Bucle de control a 50 Hz (wait 20 ms).
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, 55.5, 104)
    touch = TouchSensor(Port.S1)
    us = UltrasonicSensor(Port.S4)

    timer = StopWatch()
    next_report_ms = 0
    run_time_ms = 20000
    obstacle_mm = 120

    ev3.screen.clear()
    ev3.screen.print("15: esquiva")

    while timer.time() < run_time_ms:
        hit = touch.pressed()
        near_wall = us.distance() < obstacle_mm

        if hit or near_wall:
            ev3.screen.print("Evasiva")
            robot.stop()
            robot.straight(-60)
            robot.turn(90)
        else:
            robot.drive(180, 0)
            if timer.time() >= next_report_ms:
                ev3.screen.print("Libre D", us.distance())
                next_report_ms += 1500

        wait(20)

    robot.stop()
    ev3.screen.print("Fin")


if __name__ == "__main__":
    main()
