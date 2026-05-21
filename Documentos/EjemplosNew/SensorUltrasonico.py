#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import UltrasonicSensor
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.hubs import EV3Brick
from pybricks.tools import wait


def main():
    # Inicializar el EV3
    ev3 = EV3Brick()
            
    # Inicializar el sensor de Ultrasonico por el puerto 2
    sensor_ultrasonido = UltrasonicSensor(Port.S2) 
    # Inicializar los motores en el puerto A y C
    motor_A = Motor(Port.A)
    motor_C = Motor(Port.C)
    while True:
        d= sensor_ultrasonido.distance()
        if (d<150):
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

if __name__ == "__main__":
   main()
