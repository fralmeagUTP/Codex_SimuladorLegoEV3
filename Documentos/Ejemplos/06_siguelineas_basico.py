from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait

l = Motor(Port.B)
r = Motor(Port.C)
bot = DriveBase(l, r, 55.5, 104)

# Agregar el Sensor de Color mirando hacia el Suelo
color_sens = ColorSensor(Port.S3)

# La pista blanca tiene reflexion ~100%, la negra ~0%
# Target (Umbral): Borde entre el negro y el blanco = 50%
umbral = 50.0

# Constante Proporcional (KP). Afecta qué tan rápido corrige la curva
kp = 1.2 

print("Siguiendo el Borde de una Línea (Control P)...")

while True:
    # Leer el valor actual de luz reflejada (0-100)
    luz = color_sens.reflection()
    
    # Calcular el error (diferencia entre donde estoy y el Target ideal 50)
    error = luz - umbral
    
    # Calcular la tasa de giro requerida multiplicando la fuerza KP
    giro = error * kp
    
    # Conducir hacia delante a 100mm/s y aplicar la tasa de correccion de 'giro'
    bot.drive(100, giro)
    
    wait(10)
