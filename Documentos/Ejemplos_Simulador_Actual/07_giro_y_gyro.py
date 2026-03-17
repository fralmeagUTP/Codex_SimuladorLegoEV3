#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, GyroSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait


def main():
    ev3 = EV3Brick()
    left = Motor(Port.B)
    right = Motor(Port.C)
    gyro = GyroSensor(Port.S4)
    robot = DriveBase(left, right, 55.5, 104)

    ev3.screen.print("Ang inicial:", gyro.angle())
    wait(300)

    robot.turn(90)
    ev3.screen.print("Tras 90:", gyro.angle())
    wait(300)

    robot.turn(-180)
    ev3.screen.print("Tras -180:", gyro.angle())
    wait(300)

    robot.stop()


if __name__ == "__main__":
    main()
