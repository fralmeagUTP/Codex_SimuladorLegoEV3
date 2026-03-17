from pybricks.ev3devices import Motor, TouchSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait

left_motor = Motor(Port.B)
right_motor = Motor(Port.C)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

# Inicializar sensor de Tacto en el Puerto 1
touch_sensor = TouchSensor(Port.S1)

print("Avanzando hasta chocar con algo...")

# Encender motores hacia adelante de forma indefinida a 150 mm/s
robot.drive(150, 0)

# Esperar activamente en un bucle hasta que se presione el sensor
while not touch_sensor.pressed():
    wait(10) # Pequeña pausa para no sobrecargar de iteraciones la CPU

print("¡Choque detectado! Deteniendo el robot...")
robot.stop()

# Reaccionar retrocediendo
print("Echando hacia atrás.")
robot.straight(-100)
print("Robot a salvo.")
