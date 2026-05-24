#!/usr/bin/env pybricks-micropython
"""
Ejemplo 01 - Movimiento basico con dos motores.

Que aprender:
1. Crear EV3Brick y motores.
2. Ejecutar un avance controlado por tiempo.
3. Hacer un giro simple con motores en sentidos opuestos.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait


def main():
    # 1) Inicializacion de hardware virtual.
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)

    ev3.screen.clear()
    ev3.screen.print("01: basico")

    # 2) Avanzar durante 1.2 s.
    # run_time con wait=False/True permite iniciar ambos motores casi a la vez.
    ev3.screen.print("Avance")
    left_motor.run_time(450, 1200, then=Stop.BRAKE, wait=False)
    right_motor.run_time(450, 1200, then=Stop.BRAKE, wait=True)

    # 3) Giro corto sobre el centro.
    ev3.screen.print("Giro")
    left_motor.run_time(220, 600, then=Stop.BRAKE, wait=False)
    right_motor.run_time(-220, 600, then=Stop.BRAKE, wait=True)

    # 4) Cierre seguro.
    left_motor.stop()
    right_motor.stop()
    ev3.screen.print("Fin")
    wait(150)


if __name__ == "__main__":
    main()
