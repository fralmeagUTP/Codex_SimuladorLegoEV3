#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.tools import StopWatch, wait


def main():
    ev3 = EV3Brick()
    sw = StopWatch()

    for _ in range(8):
        ev3.screen.print("Tiempo:", sw.time(), "ms")
        wait(250)


if __name__ == "__main__":
    main()
