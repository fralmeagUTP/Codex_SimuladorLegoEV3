"""
Ejemplo 04A - Frenado por distancia con ultrasonido.

Que aprender:
1. Leer distancia en milimetros.
2. Decidir avance/parada con umbral.
3. Informar telemetria en LCD sin saturarla.
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
    us_sensor = UltrasonicSensor(Port.S4)

    timeout_ms = 15000
    stop_distance_mm = 120
    timer = StopWatch()
    next_report_ms = 0

    ev3.screen.clear()
    ev3.screen.print("04A: ultrasonido")

    while timer.time() < timeout_ms:
        distance = us_sensor.distance()

        if timer.time() >= next_report_ms:
            ev3.screen.print("Dist", distance, "mm")
            next_report_ms += 500

        if distance <= stop_distance_mm:
            break

        robot.drive(180, 0)
        wait(20)

    robot.stop()

    if us_sensor.distance() <= stop_distance_mm:
        ev3.screen.print("Obstaculo")
    else:
        ev3.screen.print("Timeout")

    wait(120)


if __name__ == "__main__":
    main()
