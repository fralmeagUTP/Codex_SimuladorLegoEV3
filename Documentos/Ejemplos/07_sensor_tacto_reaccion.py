"""
Ejemplo 03 - Reaccion al sensor de tacto.

Que aprender:
1. Bucle de sondeo con pausa corta (wait).
2. Uso de timeout para evitar espera infinita.
3. Maniobra de seguridad al detectar choque.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)
    touch_sensor = TouchSensor(Port.S1)

    timer = StopWatch()
    next_report_ms = 0
    timeout_ms = 15000

    ev3.screen.clear()
    ev3.screen.print("03: tacto")
    ev3.screen.print("Avanzando")
    robot.drive(150, 0)

    # Espera hasta detectar tacto o llegar a timeout.
    while (not touch_sensor.pressed()) and timer.time() < timeout_ms:
        if timer.time() >= next_report_ms:
            ev3.screen.print("Esperando toque")
            next_report_ms += 2000
        wait(20)

    robot.stop()

    if touch_sensor.pressed():
        ev3.screen.print("Choque detectado")
        ev3.screen.print("Retroceso")
        robot.straight(-100)
        ev3.screen.print("A salvo")
    else:
        ev3.screen.print("Sin choque")
        ev3.screen.print("Timeout 15s")


if __name__ == "__main__":
    main()
