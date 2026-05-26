"""
Ejemplo 16 - Resolver laberinto (regla de mano derecha mejorada).

Que aprender:
1. Decidir en cruces: derecha > frente > izquierda.
2. Evitar oscilaciones con memoria corta de decisiones.
3. Recuperacion de atascos y choques.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    robot = DriveBase(left_motor, right_motor, 55.5, 104)
    us = UltrasonicSensor(Port.S4)
    touch = TouchSensor(Port.S1)

    timer = StopWatch()
    run_time_ms = 70000
    next_report_ms = 0

    # Ajustes para este mundo: pasillos relativamente amplios.
    front_block_mm = 135   # Distancia de bloqueo frontal (ajustar segun mundo).
    side_open_mm = 170     # Distancia para considerar un lateral abierto en el sondeo (ajustar segun mundo).
    advance_mm = 120    # Avance en cada movimiento (ajustar segun mundo y precision de giro).
    probe_turn_deg = 88   # Grados para sondear laterales (ajustar segun mundo).
    turn_deg = 90         # Grados para giro (ajustar segun mundo).

    # Memoria corta para evitar "derecha-izquierda-derecha-izquierda".
    last_actions = []

    def push_action(tag):
        last_actions.append(tag)
        if len(last_actions) > 8:
            last_actions.pop(0)

    def count_recent(tag):
        c = 0
        for item in last_actions[-4:]:
            if item == tag:
                c += 1
        return c

    def sample_distance():
        # Mediana de 3 para reducir lecturas espurias.
        a = us.distance()
        wait(8)
        b = us.distance()
        wait(8)
        c = us.distance()
        vals = [a, b, c]
        vals.sort()
        return vals[1]

    def peek_side(turn_angle_deg):
        # Sondeo rapido lateral.
        robot.turn(turn_angle_deg)
        wait(10)
        d = sample_distance()
        robot.turn(-turn_angle_deg)
        wait(10)
        return d

    def escape_collision():
        robot.stop()
        robot.straight(-80)
        robot.turn(-turn_deg)
        push_action("escape")

    def go_forward():
        robot.straight(advance_mm)
        push_action("F")

    def turn_right_and_go():
        robot.turn(turn_deg)
        robot.straight(advance_mm)
        push_action("R")

    def turn_left_and_go():
        robot.turn(-turn_deg)
        robot.straight(advance_mm)
        push_action("L")

    ev3.screen.clear()
    ev3.screen.print("16: laberinto+")

    while timer.time() < run_time_ms:
        dist_front = sample_distance()
        hit = touch.pressed()

        if hit:
            ev3.screen.print("Choque")
            escape_collision()
            wait(15)
            continue

        # Solo sondeamos laterales cerca de cruces/obstaculos.
        near_intersection = dist_front < 260
        dist_right = peek_side(probe_turn_deg) if near_intersection else 0

        # Regla base de mano derecha con anti-oscilacion.
        if near_intersection and dist_right > side_open_mm and count_recent("R") < 3:
            ev3.screen.print("Cruce: derecha", int(dist_right))
            turn_right_and_go()
        elif dist_front > front_block_mm:
            if timer.time() >= next_report_ms:
                ev3.screen.print("Frente", int(dist_front))
                next_report_ms += 1400
            go_forward()
        else:
            # Frente bloqueado: primero izquierda; si no, media vuelta.
            dist_left = peek_side(-probe_turn_deg)
            if dist_left > side_open_mm and count_recent("L") < 3:
                ev3.screen.print("Bloqueo: izq", int(dist_left))
                turn_left_and_go()
            else:
                ev3.screen.print("Callejon")
                robot.turn(180)
                robot.straight(90)
                push_action("U")

        wait(12)

    robot.stop()
    ev3.screen.print("Fin")


if __name__ == "__main__":
    main()
