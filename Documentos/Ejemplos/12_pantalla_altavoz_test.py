#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.tools import wait, StopWatch


def main():
    ev3 = EV3Brick()
    sw = StopWatch()

    ev3.screen.print("=== TEST A/V ===")
    ev3.screen.print("Pantalla OK")
    ev3.speaker.beep(440, 200)
    wait(250)

    ev3.screen.print("Beep 2: 660Hz")
    ev3.speaker.beep(660, 200)
    wait(250)

    ev3.screen.print("Beep 3: 880Hz")
    ev3.speaker.beep(880, 250)
    wait(300)

    ev3.screen.print("Cronometro:")
    for _ in range(6):
        ev3.screen.print(sw.time(), "ms")
        ev3.speaker.beep(523, 80)
        wait(180)

    ev3.screen.print("Fin prueba")
    ev3.speaker.beep(330, 150)
    wait(150)
    ev3.speaker.beep(262, 250)


if __name__ == "__main__":
    main()
