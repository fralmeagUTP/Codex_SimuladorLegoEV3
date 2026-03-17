#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait


def main():
    ev3 = EV3Brick()
    left = Motor(Port.B)
    right = Motor(Port.C)
    touch = TouchSensor(Port.S1)
    robot = DriveBase(left, right, 55.5, 104)

    robot.drive(200, 0)
    while not touch.pressed():
        ev3.screen.print("Touch:", touch.pressed())
        wait(50)

    robot.stop()
    ev3.screen.print("Colision detectada")


if __name__ == "__main__":
    main()
