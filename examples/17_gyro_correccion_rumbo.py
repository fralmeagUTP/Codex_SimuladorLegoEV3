#!/usr/bin/env pybricks-micropython
"""
Ejemplo 17 - Correccion de rumbo con GyroSensor.

Que aprender:
1. Leer angulo del giroscopio en tiempo real.
2. Corregir desviacion con un control proporcional simple.
3. Resetear angulo para iniciar una maniobra nueva.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, GyroSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, 55.5, 104)
    gyro = GyroSensor(Port.S2)

    ev3.screen.clear()
    ev3.screen.print("17: gyro rumbo")

    gyro.reset_angle(0)
    timer = StopWatch()
    kp = 2.0
    next_report_ms = 0

    # Avanza intentando mantener heading 0 deg.
    while timer.time() < 6000:
        error_deg = gyro.angle()
        turn_rate = -kp * error_deg
        robot.drive(140, turn_rate)

        if timer.time() >= next_report_ms:
            ev3.screen.print("ang", gyro.angle(), "spd", gyro.speed())
            next_report_ms += 1200

        wait(20)

    robot.stop()
    ev3.screen.print("Reset y giro")
    gyro.reset_angle(0)
    robot.turn(90)
    ev3.screen.print("gyro", gyro.angle())
    ev3.screen.print("Fin")


if __name__ == "__main__":
    main()

