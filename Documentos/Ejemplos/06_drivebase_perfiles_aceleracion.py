"""
Ejemplo 09 - Perfil de aceleracion en DriveBase.

Que aprender:
1. Parametros de settings para velocidad y aceleracion.
2. Efecto de perfiles lentos vs rapidos.
3. Reutilizar la misma trayectoria con distinta dinamica.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, 55.5, 104)

    ev3.screen.clear()
    ev3.screen.print("09: perfiles")

    # Perfil 1: movimiento suave.
    ev3.screen.print("Perfil suave")
    robot.settings(straight_speed=60, straight_acceleration=25, turn_rate=90, turn_acceleration=45)
    robot.straight(220)

    # Perfil 2: movimiento agresivo.
    ev3.screen.print("Perfil rapido")
    robot.settings(straight_speed=320, straight_acceleration=220, turn_rate=170, turn_acceleration=170)
    robot.straight(-220)

    robot.stop()
    ev3.screen.print("Fin")
    wait(120)


if __name__ == "__main__":
    main()
