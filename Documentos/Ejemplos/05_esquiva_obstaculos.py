from pybricks.ev3devices import Motor, TouchSensor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# Equipar el Robot con Motores y ambos sensores
l = Motor(Port.B)
r = Motor(Port.C)
bot = DriveBase(l, r, 55.5, 104)

tacto = TouchSensor(Port.S1)
us = UltrasonicSensor(Port.S4)

print("Aventura: Exploración Infinita Evitando Muros")

while True:
    # 1. Leer Sensores
    chk_choque = tacto.pressed()
    chk_muro = us.distance() < 80 # Muros a menos de 8cm

    # 2. Tomar Decisión
    if chk_choque or chk_muro:
        print("¡Obstáculo! Evadiendo...")
        bot.stop()
        bot.straight(-50) # Hacer espacio hacia atraś
        bot.turn(90)      # Girar a la derecha
    else:
        # 3. Camino despejado, seguir.
        bot.drive(200, 0)
        
    wait(20) # Iteración de Control 50Hz
