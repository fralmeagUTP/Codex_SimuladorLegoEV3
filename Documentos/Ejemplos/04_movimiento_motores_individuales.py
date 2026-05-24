"""
Ejemplo 08 - Motores individuales.

Que aprender:
1. run_angle para movimientos exactos por grados.
2. run_time para acciones en paralelo.
3. Diferencia entre control por motor y DriveBase.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)

    ev3.screen.clear()
    ev3.screen.print("08: motores")

    ev3.screen.print("Pivote izq")
    right_motor.run_angle(speed=220, rotation_angle=900, then=Stop.BRAKE, wait=True)
    wait(250)

    ev3.screen.print("Pivote der")
    left_motor.run_angle(speed=220, rotation_angle=900, then=Stop.BRAKE, wait=True)
    wait(250)

    ev3.screen.print("Giro centro")
    left_motor.run_time(speed=280, time=1300, wait=False)
    right_motor.run_time(speed=-280, time=1300, wait=True)

    left_motor.stop()
    right_motor.stop()
    ev3.screen.print("Fin")


if __name__ == "__main__":
    main()
