from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Color
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# En PyBricks el `ColorSensor` puede usar `.color()` para
# obtener una constante como Color.RED, Color.BLACK, Color.WHITE.

l = Motor(Port.B)
r = Motor(Port.C)
bot = DriveBase(l, r, 55.5, 104)

sensor_color = ColorSensor(Port.S3)

print("Avanzando. Me detendré si la superficie debajo de mi es Roja o Negra.")

# Empezar a moverse indefinidamente
bot.drive(100, 0)

while True:
    # Preguntar qué color detecta actualmente
    color_visto = sensor_color.color()
    
    if color_visto == Color.BLACK:
         print("Pise una banda negra! Parando..")
         bot.stop()
         break
    elif color_visto == Color.RED:
         print("Pise una banda roja! Parando..")
         bot.stop()
         break
         
    wait(10) # Reposo de lectura
