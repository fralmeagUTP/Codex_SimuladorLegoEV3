from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait

l = Motor(Port.B)
r = Motor(Port.C)
bot = DriveBase(l, r, 55.5, 104)

print("1. Avanzando Lentamente (Aceleracion muy paulatina)...")

# Ajustar las limitaciones de Velocidad(mm/s), Aceleración(mm/s^2), Tasa de Giro(deg/s), y aceleracion de Giro
bot.settings(straight_speed=50, straight_acceleration=20, turn_rate=90, turn_acceleration=45) 
bot.straight(200)

print("2. Pisando el Acelerador a Fondo (Alta velocidad/Aceleracion)...")
bot.settings(straight_speed=500, straight_acceleration=300, turn_rate=180, turn_acceleration=180)
# Regresaremos al punto de origen en reversa rápida
bot.straight(-200)

print("Circuito completado.")
