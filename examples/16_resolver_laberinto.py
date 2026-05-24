"""
Ejemplo 16 - Navegacion reactiva (laberinto simple).

Que aprender:
1. Prioridad de eventos: choque > muro cercano > avance libre.
2. Uso de giros de escape y retrocesos cortos.
3. Control reactivo temporizado.
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
    us = UltrasonicSensor(Port.S4)
    touch = TouchSensor(Port.S1)

    timer = StopWatch()
    run_time_ms = 25000
    near_wall_mm = 150
    next_report_ms = 0

    ev3.screen.clear()
    ev3.screen.print("16: laberinto")

    while timer.time() < run_time_ms:
        dist = us.distance()
        hit = touch.pressed()

        if hit:
            ev3.screen.print("Choque -> izq")
            robot.stop()
            robot.straight(-60)
            robot.turn(-90)
        elif dist < near_wall_mm:
            ev3.screen.print("Muro -> der")
            robot.stop()
            robot.turn(90)
        else:
            robot.drive(180, 0)
            if timer.time() >= next_report_ms:
                ev3.screen.print("Libre D", dist)
                next_report_ms += 1500

        wait(20)

    robot.stop()
    ev3.screen.print("Fin")


if __name__ == "__main__":
    main()
