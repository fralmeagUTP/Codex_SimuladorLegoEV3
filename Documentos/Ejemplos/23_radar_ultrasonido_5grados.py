#!/usr/bin/env pybricks-micropython
"""
Ejemplo 23 - Radar 360 con ultrasonido (paso de 5 grados).

Que aprender:
1. Hacer un barrido circular tomando una muestra cada 5 grados.
2. Convertir mediciones polares (angulo, distancia) a coordenadas de pantalla EV3.
3. Dibujar en la LCD un radar monocromo usando primitivas graficas.
"""

import math

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.parameters import Port, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait


STEP_DEG = 5
MAX_SENSOR_MM = 2500
MAP_MAX_MM = 2000
SCREEN_W = 178
SCREEN_H = 128
RADAR_CX = SCREEN_W // 2
RADAR_CY = SCREEN_H // 2
RADAR_R = 54


def clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def draw_radar(ev3: EV3Brick, samples: list[tuple[int, int]], nearest_mm: int) -> None:
    """Dibuja radar monocromo en coordenadas de pantalla EV3 (178x128)."""
    ev3.screen.clear()
    ev3.screen.print("Radar 360 (5deg)")
    ev3.screen.print("min", nearest_mm, "mm")


    # Marco y referencias.
    ev3.screen.draw_circle(RADAR_CX, RADAR_CY, RADAR_R, color=1, fill=False)
    ev3.screen.draw_circle(RADAR_CX, RADAR_CY, int(RADAR_R * 0.66), color=1, fill=False)
    ev3.screen.draw_circle(RADAR_CX, RADAR_CY, int(RADAR_R * 0.33), color=1, fill=False)
    ev3.screen.draw_line(RADAR_CX - RADAR_R, RADAR_CY, RADAR_CX + RADAR_R, RADAR_CY, color=1)
    ev3.screen.draw_line(RADAR_CX, RADAR_CY - RADAR_R, RADAR_CX, RADAR_CY + RADAR_R, color=1)

    # Robot (cuadro central).
    ev3.screen.draw_box(RADAR_CX - 1, RADAR_CY - 1, 3, 3, color=1, fill=True)

    for angle_deg, distance_mm in samples:
        has_hit = distance_mm < MAX_SENSOR_MM
        dist = min(distance_mm, MAP_MAX_MM) if has_hit else MAP_MAX_MM
        rr = int((dist / MAP_MAX_MM) * RADAR_R)
        rr = clamp(rr, 0, RADAR_R)

        rad = math.radians(angle_deg)
        x = int(round(RADAR_CX + (rr * math.cos(rad))))
        y = int(round(RADAR_CY - (rr * math.sin(rad))))

        # Rayo fino hasta la lectura.
        ev3.screen.draw_line(RADAR_CX, RADAR_CY, x, y, color=1)

        # Punto de impacto.
        if has_hit:
            ev3.screen.draw_box(x - 1, y - 1, 3, 3, color=1, fill=True)


def main() -> None:
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, 55.5, 104)

    # Si usas otro puerto para ultrasónico, cámbialo aquí.
    us = UltrasonicSensor(Port.S4)

    robot.settings(turn_rate=180)

    ev3.screen.clear()
    ev3.screen.print("23: radar US")
    ev3.screen.print("Barrido 360...")

    samples: list[tuple[int, int]] = []
    nearest_mm = MAX_SENSOR_MM

    # Toma muestra y luego gira 5 grados, hasta cubrir 360 grados.
    for angle in range(0, 360, STEP_DEG):
        distance_mm = us.distance()
        samples.append((angle, distance_mm))
        nearest_mm = min(nearest_mm, distance_mm)

        if angle < 355:
            robot.turn(STEP_DEG, then=Stop.HOLD, wait=True)
            wait(20)

    robot.stop()

    draw_radar(ev3, samples, nearest_mm)

    # Pausa breve para que se vea la pantalla final en la simulacion.
    wait(1500)


if __name__ == "__main__":
    main()
