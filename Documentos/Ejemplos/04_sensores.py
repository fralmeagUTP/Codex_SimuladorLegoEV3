from pybricks.ev3devices import Motor, UltrasonicSensor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Color
from pybricks.tools import wait

def main():
    print("Iniciando Prueba de Sensores...")
    
    # Inicializar motores y sensores
    left_motor = Motor(Port.A)
    right_motor = Motor(Port.B)
    
    us = UltrasonicSensor(Port.S1)
    ts = TouchSensor(Port.S2)
    cs = ColorSensor(Port.S3)
    
    # Mover hasta chocar o ver algo cerca
    left_motor.run(150)
    right_motor.run(150)
    
    while True:
        dist = us.distance()
        pressed = ts.pressed()
        col = cs.color()
        
        print(f"Distancia: {dist:.1f} mm, Tocado: {pressed}, Color: {col}")
        
        if dist < 50 or pressed:
            print("¡Obstáculo inminente! Deteniéndose y retrocediendo.")
            break
            
        wait(500) # esperar medio segundo entre lecturas
        
    # Retroceder
    left_motor.run(-150)
    right_motor.run(-150)
    wait(2000)
    left_motor.stop()
    right_motor.stop()
    print("Fin del programa.")

if __name__ == "__main__":
    main()
