#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait


def main():
    left = Motor(Port.A)
    right = Motor(Port.C)

    left.run(400)
    right.run(400)
    wait(1200)

    left.hold()
    right.run(-350)
    wait(800)

    left.run(-350)
    right.hold()
    wait(800)

    left.stop()
    right.stop()


if __name__ == "__main__":
    main()
