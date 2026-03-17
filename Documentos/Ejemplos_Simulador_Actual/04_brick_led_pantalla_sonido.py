#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.parameters import Color
from pybricks.tools import wait


def main():
    ev3 = EV3Brick()

    ev3.light.on(Color.RED)
    ev3.screen.print("Hola")
    ev3.screen.print("Simulador EV3")
    ev3.speaker.beep(440, 200)
    wait(400)

    ev3.light.on(Color.GREEN)
    ev3.screen.print("LED verde")
    ev3.speaker.beep(660, 200)
    wait(600)

    ev3.light.off()


if __name__ == "__main__":
    main()
