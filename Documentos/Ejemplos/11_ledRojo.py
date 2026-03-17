#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.tools import wait
from pybricks.parameters import Color

''' 
    Este programa controla la luz del ladrillo EV3 
    para mostrar una luz roja durante un segundo.
'''
def main():
    # Inicializar el EV3
    ev3 = EV3Brick()

    # Encender una luz roja
    ev3.light.on(Color.RED)

    # Esperar un 5 segundos
    wait(5000)

    # Apagar la luz
    ev3.light.off()

#-----------------------------------------------------------
if __name__ == "__main__":
   main()
