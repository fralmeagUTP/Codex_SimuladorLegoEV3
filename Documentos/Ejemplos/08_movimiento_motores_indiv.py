from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait

# En lugar de usar P.robotics.DriveBase, en ocasiones preferirás 
# inyectar RPM u órdenes (run_time, run_angle) independientes en motores
motor_izquierdo = Motor(Port.B)
motor_derecho = Motor(Port.C)

print("Iniciando Pruebas de Movimiento de Oruga")

# Girar solo la llanta derecha por 1000 grados a velocidad 200 grados/segundo
print("Pivote sobre rueda Izquierda (Llanta Derecha Girando)...")
motor_derecho.run_angle(speed=200, rotation_angle=1000, then=Stop.BRAKE, wait=True)

wait(1000)

print("Pivot sobre Rueda Derecha (Llanta Izquierda Girando)...")
motor_izquierdo.run_angle(speed=400, rotation_angle=1000, then=Stop.BRAKE, wait=True)

wait(1000)

print("Giro sobre el propio centro (Ambas giran opuestas)...")
# Usando wait=False en la inicial hace que se ejecuten en paralelo simultaneamente
motor_izquierdo.run_time(speed=300, time=2000, wait=False)
motor_derecho.run_time(speed=-300, time=2000, wait=True) # Este último retiene la ejecución
