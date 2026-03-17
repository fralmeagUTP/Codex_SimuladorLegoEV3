from pybricks.ev3devices import Motor, TouchSensor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# Combinación Maestra: Escaneo de Obstáculos Frontales y Choque
l = Motor(Port.B)
r = Motor(Port.C)
bot = DriveBase(l, r, 55.5, 104)

us = UltrasonicSensor(Port.S4)
touch = TouchSensor(Port.S1)

print("Iniciando Sistema de Auto Exploración Múltiple...")

while True:
    dist = us.distance()
    choque = touch.pressed()
    
    if choque:
        print("¡Colisión Forzosa Analógica Detectada! Rebotando a la izquierda...")
        bot.stop()
        bot.straight(-50) # Hacer 5cm de espacio
        bot.turn(-90)     # Pivot izquierdo seguro
        
    elif dist < 150: # Si hay algo a menos de 15cm
        print("Muro próximo en el radar ultrasónico, calculando evasión a la derecha...")
        bot.stop()
        bot.turn(90)      # Pivot derecho preventivo
        
    else:
        # El camino está Despejado o "Seguro"
        bot.drive(200, 0)
        
    wait(20) # Bucle 50Hz
