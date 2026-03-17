#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait


def main():
    left = Motor(Port.B)
    right = Motor(Port.C)
    robot = DriveBase(left, right, 55.5, 104)

    for _ in range(4):
        robot.straight(250)
        wait(150)
        robot.turn(90)
        wait(150)

    robot.stop()


if __name__ == "__main__":
    main()
