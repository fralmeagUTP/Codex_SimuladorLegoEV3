from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait

def main():
    print("Iniciando Prueba Crítica de Colisión Físca...")
    
    left_motor = Motor(Port.A)
    right_motor = Motor(Port.B)
    
    # Avanzamos sin frenar
    print("Avanzando indefinidamente hacia el muro...")
    left_motor.run(300)
    right_motor.run(300)
    
    # Esperamos bastante tiempo
    # El robot dejará de moverse visualmente en el momento del impacto 
    # aunque los motores sigan girando
    wait(5000)
    
    print("Deteniendo motores.")
    left_motor.stop()
    right_motor.stop()
    print("Fin.")

if __name__ == "__main__":
    main()
