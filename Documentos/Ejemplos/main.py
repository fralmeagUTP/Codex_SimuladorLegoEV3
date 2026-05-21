# Inicia tu programa aquí
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait

ev3 = EV3Brick()
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)
robot = DriveBase(left_motor, right_motor, 55.5, 104)
us = UltrasonicSensor(Port.S4)

# Avanza hasta encontrar la pared (borde del simulador)
robot.drive(200, 0)
while us.distance() > 30:
    wait(10)

robot = DriveBase(left_motor, right_motor, -55.5, 104)
robot.stop()
ev3.screen.print("Pared detectada a", us.distance(), "mm")
wait(10)


