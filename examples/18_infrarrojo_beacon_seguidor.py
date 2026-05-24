#!/usr/bin/env pybricks-micropython
"""
Ejemplo 18 - Seguidor de beacon infrarrojo.

Que aprender:
1. Leer (distancia, heading) con InfraredSensor.beacon().
2. Convertir heading en giro para apuntar al beacon.
3. Frenar al acercarse o por timeout.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, InfraredSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, 55.5, 104)
    ir = InfraredSensor(Port.S2)

    ev3.screen.clear()
    ev3.screen.print("18: IR beacon")

    timer = StopWatch()
    timeout_ms = 15000
    near_target = 20
    next_report_ms = 0

    while timer.time() < timeout_ms:
        distance, heading = ir.beacon(1)
        turn_rate = heading * 6.0

        if distance <= near_target:
            break

        # Mayor velocidad si esta lejos.
        speed = 180 if distance > 50 else 110
        robot.drive(speed, turn_rate)

        if timer.time() >= next_report_ms:
            ev3.screen.print("d", distance, "h", heading)
            next_report_ms += 1000

        wait(20)

    robot.stop()
    distance, heading = ir.beacon(1)
    ev3.screen.print("fin d", distance, "h", heading)


if __name__ == "__main__":
    main()

