#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import TouchSensor
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.hubs import EV3Brick
from pybricks.tools import wait


def main():
    # Inicializar el EV3
    ev3 = EV3Brick()
            
    # Inicializar el sensor de tacto por el puerto 4
    sensor_tactil = TouchSensor(Port.S4) 

    # Inicializar los motores en el puerto A y C
    motor_A = Motor(Port.A)
    motor_C = Motor(Port.C)
    while True:
        if sensor_tactil.pressed():
            # Retroceder y girar al chocar
            motor_A.run(-250)
            motor_C.run(-250)
            wait(2500)
            motor_C.stop()
            motor_A.run(-100)
            wait(3000)
        else:
            # Avanzar normalmente
            motor_A.run(250)
            motor_C.run(250)
#-----------------------------------------------------------    

if__name__ == "__main__":
    main()

