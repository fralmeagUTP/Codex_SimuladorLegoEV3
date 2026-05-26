#!/usr/bin/env pybricks-micropython
"""
Ejemplo 18 - Seguidor de beacon infrarrojo.

Que aprender:
1. Leer (distancia, heading) con InfraredSensor.beacon().
2. Convertir heading en giro para apuntar al beacon.
3. Buscar beacon cuando no hay deteccion y frenar al acercarse o por timeout.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, InfraredSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, 55.5, 104)
    ir = InfraredSensor(Port.S2)

    ev3.screen.clear()
    ev3.screen.print("18: IR beacon")

    timer = StopWatch()
    timeout_ms = 15000
    near_target = 20
    next_report_ms = 0
    seen_beacon = False

    def show_status(mode: str, distance: int, heading: int) -> None:
        # Refresco explicito para que el estado sea siempre visible en LCD.
        ev3.screen.clear()
        ev3.screen.print("18: IR beacon")
        ev3.screen.print("modo", mode)
        ev3.screen.print("d", distance, "h", heading)
        ev3.screen.print("prox", ir.distance())
        ev3.screen.print("t", int(timer.time() / 1000), "s")

    while timer.time() < timeout_ms:
        distance, heading = ir.beacon(1)
        beacon_detected = not (distance == 0 and heading == 0)

        if beacon_detected:
            seen_beacon = True
            turn_rate = heading * 6.0

            # Solo parar por cercania si realmente hay beacon detectado.
            if distance <= near_target:
                ev3.screen.print("beacon cerca")
                break

            # Mayor velocidad si esta lejos.
            speed = 180 if distance > 50 else 110
            robot.drive(speed, turn_rate)
        else:
            # Sin beacon: barrido lento para intentar encontrar heading.
            robot.drive(0, 90)

        if timer.time() >= next_report_ms:
            mode = "trk" if beacon_detected else "scan"
            show_status(mode, distance, heading)
            next_report_ms += 1000

        wait(20)

    robot.stop()
    distance, heading = ir.beacon(1)
    if not seen_beacon:
        show_status("sin beacon", distance, heading)
    else:
        show_status("fin", distance, heading)


if __name__ == "__main__":
    main()

