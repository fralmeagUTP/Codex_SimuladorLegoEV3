#!/usr/bin/env pybricks-micropython
"""
Ejemplo 22 - Mision por etapas con StopWatch.

Que aprender:
1. Orquestar una mision por tiempo usando StopWatch.
2. Usar pause() y resume() del cronometro.
3. Mantener logica clara con una maquina de estados simple.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, 55.5, 104)
    timer = StopWatch()

    ev3.screen.clear()
    ev3.screen.print("22: etapas")

    stage = 1
    while timer.time() < 9000:
        t = timer.time()

        if stage == 1 and t < 2500:
            robot.drive(160, 0)
            if t < 120:
                ev3.screen.print("E1 avance")
        elif stage == 1:
            robot.stop()
            ev3.screen.print("Pausa cron")
            timer.pause()
            wait(500)
            timer.resume()
            stage = 2

        elif stage == 2 and t < 5000:
            robot.drive(120, 70)
            if t < 2700:
                ev3.screen.print("E2 curva")
        elif stage == 2:
            robot.stop()
            ev3.screen.print("E3 giro")
            robot.turn(-90)
            stage = 3

        else:
            robot.drive(100, 0)
            if t > 8000:
                break

        wait(20)

    robot.stop()
    ev3.screen.print("t", timer.time(), "ms")
    ev3.screen.print("Fin")


if __name__ == "__main__":
    main()

