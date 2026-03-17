#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import ColorSensor
from pybricks.parameters import Port
from pybricks.tools import wait


def main():
    ev3 = EV3Brick()
    sensor = ColorSensor(Port.S3)

    for _ in range(10):
        ev3.screen.print("Color:", sensor.color())
        ev3.screen.print("Reflex:", sensor.reflection())
        wait(300)


if __name__ == "__main__":
    main()
