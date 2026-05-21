#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait
def main():
    # Inicializa el brick
    ev3 = EV3Brick()

    # Inicializa los motores
    left_motor = Motor(Port.A) 
    right_motor = Motor(Port.C)

    for i in range(10):
        for j in range(4):
            # Mueve el motor los motores A y C 
            # a una velocidad rotacinal 500 grados por segundo
            left_motor.run(450)
            right_motor.run(450)  
            # Espera 1000 milisegundos
            wait(2000)
            # Detiene los motores A
            left_motor.hold()
            # Mueve el motor C a una velocidad rotacional 
            # de -500 grados por segundo
            right_motor.run(-475)
            # Espera 1000 milisegundos
            wait(760)
    # Detiene los motores A y C
    left_motor.stop()
    right_motor.stop()
#----------------------------------

if __name__ == "__main__":
   main()

