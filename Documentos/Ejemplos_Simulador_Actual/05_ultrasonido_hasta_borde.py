#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait


def main():
    ev3 = EV3Brick()
    left = Motor(Port.B)
    right = Motor(Port.C)
    robot = DriveBase(left, right, 55.5, 104)
    us = UltrasonicSensor(Port.S4)

    for _ in range(5):
        ev3.screen.print("Dist:", us.distance())
        wait(200)

    robot.drive(180, 0)
    while us.distance() > 120:
        ev3.screen.print("Dist:", us.distance())
        wait(50)

    robot.stop()
    ev3.screen.print("Borde cerca")


if __name__ == "__main__":
    main()
