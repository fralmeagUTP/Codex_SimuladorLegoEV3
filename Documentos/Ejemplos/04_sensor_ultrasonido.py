from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait

left_motor = Motor(Port.B)
right_motor = Motor(Port.C)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

# Inicializar sensor ultrasónico en el Puerto 4
us_sensor = UltrasonicSensor(Port.S4)

print("Buscando un muro frente a mi...")

while True:
    distancia = us_sensor.distance()
    
    # Si la distancia es mayor a 50 milímetros, sigo avanzando
    if distancia > 50:
        robot.drive(200, 0)
    else:
        # A menos de 5cm me detengo
        robot.stop()
        print(f"Me detuve al detectar obstáculo a {distancia:.1f} mm.")
        break
        
    wait(20) # Loop de muestreo a 50Hz (20ms)
