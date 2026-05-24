"""
Ejemplo 06A - Siguelineas proporcional (P).

Que aprender:
1. Reflexion de color como variable de control.
2. Error respecto a un objetivo (umbral).
3. Control proporcional: giro = error * Kp.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, 55.5, 104)
    color_sensor = ColorSensor(Port.S3)

    threshold = 50.0
    kp = 1.2
    speed_mm_s = 100
    run_time_ms = 15000
    timer = StopWatch()
    next_report_ms = 0

    ev3.screen.clear()
    ev3.screen.print("06A: P linea")

    while timer.time() < run_time_ms:
        light = color_sensor.reflection()
        error = light - threshold
        turn = error * kp

        robot.drive(speed_mm_s, turn)

        if timer.time() >= next_report_ms:
            ev3.screen.print("L", light, "G", int(turn))
            next_report_ms += 1000

        wait(10)

    robot.stop()
    ev3.screen.print("Fin")


if __name__ == "__main__":
    main()
