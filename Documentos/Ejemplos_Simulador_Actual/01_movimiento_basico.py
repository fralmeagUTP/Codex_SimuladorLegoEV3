#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Color
from pybricks.tools import wait


def main():
    ev3 = EV3Brick()
    left = Motor(Port.A)
    right = Motor(Port.C)

    ev3.light.on(Color.GREEN)
    left.run(500)
    right.run(500)
    wait(1500)
    left.stop()
    right.stop()
    ev3.light.off()


if __name__ == "__main__":
    main()
