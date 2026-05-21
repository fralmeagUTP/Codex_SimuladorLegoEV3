from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait

# Conectar con el EV3
ev3 = EV3Brick()  

# Crear objeto motor en puerto B 
motor_izquierdo = Motor(Port.B)  

# Mover motor a 50% velocidad por 5 segundos
motor_izquierdo.run(50)  
wait(5000)
motor_izquierdo.stop()
