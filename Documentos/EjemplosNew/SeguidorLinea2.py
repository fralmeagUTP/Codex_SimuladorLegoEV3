#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Color
def main():
    ev3 = EV3Brick() 
    left_motor = Motor(Port.A)
    right_motor = Motor(Port.C)
    color_sensor = ColorSensor(Port.S1)  

    while True:
    color = color_sensor.color()
    
    if color == Color.BLACK: # Izquierda
        left_motor.run(-100)
        right_motor.run(100)
    
    elif color == Color.WHITE: # Derecha      
        left_motor.run(100)
        right_motor.run(-100)
        
    else:
        left_motor.run(500)
        right_motor.run(500)
        
#-----------------------------------------------------------
if __name__ == "__main__":
   main()

