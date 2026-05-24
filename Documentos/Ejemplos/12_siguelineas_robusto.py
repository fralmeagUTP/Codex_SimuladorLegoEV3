"""
Ejemplo 06B - Siguelineas robusto.

Que aprender:
1. Limitar actuacion (saturacion de giro).
2. Detectar perdida de linea (blanco sostenido).
3. Estrategia de recuperacion al perder la pista.
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

    target = 50.0
    kp = 1.2
    speed_mm_s = 60.0
    max_turn_deg_s = 140.0
    lost_white_threshold = 85
    lost_white_limit = 30
    lost_white_ticks = 0
    run_time_ms = 20000

    timer = StopWatch()
    next_report_ms = 0

    ev3.screen.clear()
    ev3.screen.print("06B: robusto")

    while timer.time() < run_time_ms:
        light = color_sensor.reflection()
        error = light - target
        turn = error * kp

        # Saturacion del giro para evitar oscilaciones extremas.
        if turn > max_turn_deg_s:
            turn = max_turn_deg_s
        if turn < -max_turn_deg_s:
            turn = -max_turn_deg_s

        if light >= lost_white_threshold:
            lost_white_ticks += 1
        else:
            lost_white_ticks = 0

        if lost_white_ticks >= lost_white_limit:
            robot.drive(30, max_turn_deg_s)
        else:
            robot.drive(speed_mm_s, turn)

        if timer.time() >= next_report_ms:
            ev3.screen.print("L", light, "T", int(turn))
            next_report_ms += 1200

        wait(10)

    robot.stop()
    ev3.screen.print("Fin")


if __name__ == "__main__":
    main()
