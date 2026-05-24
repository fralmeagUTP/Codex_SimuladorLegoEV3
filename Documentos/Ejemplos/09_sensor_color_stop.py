"""
Ejemplo 09 - Detenerse por color.

Que aprender:
1. Lectura discreta de color (BLACK/RED).
2. Condiciones de parada por eventos.
3. Timeout como proteccion del flujo.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Color
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, 55.5, 104)
    color_sensor = ColorSensor(Port.S3)

    timer = StopWatch()
    timeout_ms = 15000
    next_report_ms = 0

    ev3.screen.clear()
    ev3.screen.print("09: color stop")
    robot.drive(100, 0)

    while timer.time() < timeout_ms:
        color_seen = color_sensor.color()

        if color_seen == Color.BLACK:
            ev3.screen.print("Negro")
            break
        if color_seen == Color.RED:
            ev3.screen.print("Rojo")
            break

        if timer.time() >= next_report_ms:
            ev3.screen.print("Color", color_seen)
            next_report_ms += 1200

        wait(20)

    robot.stop()

    if timer.time() >= timeout_ms:
        ev3.screen.print("Timeout")
    else:
        ev3.screen.print("Detenido")


if __name__ == "__main__":
    main()
