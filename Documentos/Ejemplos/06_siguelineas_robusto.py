from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait

l = Motor(Port.B)
r = Motor(Port.C)
bot = DriveBase(l, r, 55.5, 104)

color_sens = ColorSensor(Port.S3)

# Siguelineas robusto:
# 1) velocidad menor para tomar codos cerrados
# 2) control P con giro limitado
# 3) recuperacion cuando se queda en blanco por demasiado tiempo
target = 50.0
kp = 1.2
speed_mm_s = 55.0
max_turn_deg_s = 140.0
lost_white_threshold = 85
lost_white_limit = 30
lost_white_ticks = 0

while True:
    light = color_sens.reflection()
    error = light - target
    turn = error * kp

    if turn > max_turn_deg_s:
        turn = max_turn_deg_s
    if turn < -max_turn_deg_s:
        turn = -max_turn_deg_s

    if light >= lost_white_threshold:
        lost_white_ticks += 1
    else:
        lost_white_ticks = 0

    # Si se perdio la linea (blanco sostenido), gira en busqueda.
    if lost_white_ticks >= lost_white_limit:
        bot.drive(30, max_turn_deg_s)
        wait(10)
        continue

    bot.drive(speed_mm_s, turn)
    wait(10)
