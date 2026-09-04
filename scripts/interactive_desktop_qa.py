"""Acciones reproducibles de QA sobre una ventana Tkinter visible.

El arnés usa eventos Windows reales. No sustituye las pruebas de dominio: su
objetivo es conservar evidencia de que editor y controles reciben interacción
de ratón y teclado en una sesión gráfica.
"""

from __future__ import annotations

import argparse
import ctypes
import time
from pathlib import Path

import pyautogui
import pyperclip
import win32gui


def _focus_window(title: str) -> None:
    handles: list[int] = []

    def collect(hwnd: int, _unused: object) -> None:
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == title:
            handles.append(hwnd)

    win32gui.EnumWindows(collect, None)
    if not handles:
        raise RuntimeError(f"No hay una ventana visible con título {title!r}")

    user32 = ctypes.windll.user32
    target = handles[0]
    foreground = user32.GetForegroundWindow()
    source_thread = user32.GetWindowThreadProcessId(foreground, None)
    target_thread = user32.GetWindowThreadProcessId(target, None)
    user32.AttachThreadInput(source_thread, target_thread, True)
    try:
        user32.SetForegroundWindow(target)
        user32.BringWindowToTop(target)
    finally:
        user32.AttachThreadInput(source_thread, target_thread, False)
    time.sleep(0.4)


def close_transient_dialogs() -> None:
    """Cancela diálogos nativos que puedan haber quedado de otro caso.

    La campaña no confirma ningún caso mientras un selector de archivos o un
    cuadro modal tenga el foco: esos elementos consumen el teclado y hacen que
    la siguiente interacción parezca una prueba válida cuando no lo es.
    """

    pyautogui.PAUSE = 0.2
    for _ in range(3):
        pyautogui.press("escape")
        time.sleep(0.25)


def reset_simulation() -> None:
    """Restablece la sesión antes de un caso independiente."""

    _focus_window("Simulador EV3 Pybricks")
    pyautogui.click(304, 91)
    time.sleep(1.0)


def run_motor_a_smoke(output: Path) -> None:
    """Ejecuta Motor A real desde el editor y captura el estado terminal."""

    close_transient_dialogs()
    _focus_window("Simulador EV3 Pybricks")
    reset_simulation()
    source = "\n".join(
        (
            "from pybricks.ev3devices import Motor",
            "from pybricks.parameters import Port",
            "from pybricks.tools import wait",
            "motor = Motor(Port.A)",
            "motor.run_time(360, 500)",
            "wait(100)",
            "",
        )
    )
    pyperclip.copy(source)
    pyautogui.PAUSE = 0.2
    pyautogui.click(1500, 260)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "v")
    pyautogui.click(58, 91)
    time.sleep(2)
    output.parent.mkdir(parents=True, exist_ok=True)
    pyautogui.screenshot().save(output)


def run_all_motors_smoke(output: Path) -> None:
    """Ejercita los puertos A, B, C y D desde el intérprete visible."""

    close_transient_dialogs()
    _focus_window("Simulador EV3 Pybricks")
    reset_simulation()
    source = "\n".join(
        (
            "from pybricks.ev3devices import Motor",
            "from pybricks.parameters import Port",
            "from pybricks.tools import wait",
            "for port in (Port.A, Port.B, Port.C, Port.D):",
            "    Motor(port).run_time(240, 250)",
            "wait(100)",
            "",
        )
    )
    pyperclip.copy(source)
    pyautogui.PAUSE = 0.2
    pyautogui.click(1500, 260)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "v")
    pyautogui.click(58, 91)
    time.sleep(2.6)
    output.parent.mkdir(parents=True, exist_ok=True)
    pyautogui.screenshot().save(output)


def run_sensors_smoke(output: Path) -> None:
    """Lee S1 y S4 en el mundo básico desde un programa visible."""

    close_transient_dialogs()
    _focus_window("Simulador EV3 Pybricks")
    reset_simulation()
    source = "\n".join(
        (
            "from pybricks.hubs import EV3Brick",
            "from pybricks.ev3devices import TouchSensor, UltrasonicSensor",
            "from pybricks.parameters import Port",
            "from pybricks.tools import wait",
            "ev3 = EV3Brick()",
            "touch = TouchSensor(Port.S1)",
            "ultrasonic = UltrasonicSensor(Port.S4)",
            "ev3.screen.print('S1=' + str(touch.pressed()))",
            "ev3.screen.print('S4=' + str(ultrasonic.distance()))",
            "wait(100)",
            "",
        )
    )
    pyperclip.copy(source)
    pyautogui.PAUSE = 0.2
    pyautogui.click(1500, 260)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "v")
    pyautogui.click(58, 91)
    time.sleep(2.2)
    output.parent.mkdir(parents=True, exist_ok=True)
    pyautogui.screenshot().save(output)


def run_drivebase_smoke(output: Path) -> None:
    """Ejercita desplazamiento y giro con DriveBase en la UI real."""

    close_transient_dialogs()
    _focus_window("Simulador EV3 Pybricks")
    reset_simulation()
    source = "\n".join(
        (
            "from pybricks.ev3devices import Motor",
            "from pybricks.parameters import Port",
            "from pybricks.robotics import DriveBase",
            "from pybricks.tools import wait",
            "robot = DriveBase(Motor(Port.B), Motor(Port.C), 56, 112)",
            "robot.straight(100)",
            "robot.turn(90)",
            "wait(100)",
            "",
        )
    )
    pyperclip.copy(source)
    pyautogui.PAUSE = 0.2
    pyautogui.click(1500, 260)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "v")
    pyautogui.click(58, 91)
    time.sleep(2.5)
    output.parent.mkdir(parents=True, exist_ok=True)
    pyautogui.screenshot().save(output)


def run_menu_during_execution_smoke(output: Path) -> None:
    """Comprueba visualmente el bloqueo de menús mientras existe una misión."""

    close_transient_dialogs()
    _focus_window("Simulador EV3 Pybricks")
    reset_simulation()
    pyperclip.copy("from pybricks.tools import wait\nwait(5000)\n")
    pyautogui.PAUSE = 0.2
    pyautogui.click(1500, 260)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "v")
    pyautogui.click(58, 91)
    time.sleep(0.6)
    # Mundos: si está deshabilitado, no debe desplegar un menú ni alterar mundo.
    pyautogui.click(404, 44)
    time.sleep(0.4)
    output.parent.mkdir(parents=True, exist_ok=True)
    pyautogui.screenshot().save(output)
    reset_simulation()


def run_syntax_error_smoke(output: Path) -> None:
    """Provoca un error sintáctico real y preserva el cuadro de error."""

    close_transient_dialogs()
    _focus_window("Simulador EV3 Pybricks")
    reset_simulation()
    pyperclip.copy("if True print('error de QA')\n")
    pyautogui.PAUSE = 0.2
    pyautogui.click(1500, 260)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "v")
    pyautogui.click(58, 91)
    time.sleep(1.2)
    output.parent.mkdir(parents=True, exist_ok=True)
    pyautogui.screenshot().save(output)


def run_screen_text_smoke(output: Path) -> None:
    """Verifica el texto LCD que el simulador declara como soportado."""

    close_transient_dialogs()
    _focus_window("Simulador EV3 Pybricks")
    reset_simulation()
    source = "\n".join(
        (
            "from pybricks.hubs import EV3Brick",
            "ev3 = EV3Brick()",
            "ev3.screen.print('QA OK')",
            "",
        )
    )
    pyperclip.copy(source)
    pyautogui.PAUSE = 0.2
    pyautogui.click(1500, 260)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "v")
    pyautogui.click(58, 91)
    time.sleep(1.2)
    output.parent.mkdir(parents=True, exist_ok=True)
    pyautogui.screenshot().save(output)


def run_pause_resume_reset_smoke(output: Path) -> None:
    """Ejercita pausa, reanudación y reinicio con un script todavía activo."""

    close_transient_dialogs()
    _focus_window("Simulador EV3 Pybricks")
    reset_simulation()
    pyperclip.copy("from pybricks.tools import wait\nwait(5000)\n")
    pyautogui.PAUSE = 0.2
    pyautogui.click(1500, 260)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "v")
    pyautogui.click(58, 91)
    time.sleep(0.6)
    pyautogui.click(128, 91)
    time.sleep(0.4)
    paused_output = output.with_name("pausa_real.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    pyautogui.screenshot().save(paused_output)
    pyautogui.click(196, 91)
    time.sleep(0.4)
    pyautogui.click(304, 91)
    time.sleep(0.8)
    pyautogui.screenshot().save(output)


def run_keyboard_navigation_smoke(output: Path) -> None:
    """Recorre menú y controles con F10, Tab, Shift+Tab, Enter y Escape."""

    close_transient_dialogs()
    _focus_window("Simulador EV3 Pybricks")
    pyautogui.PAUSE = 0.2
    # F10 desplaza el foco a la barra de menús clásica de Tk. La primera
    # opción es un nuevo documento en la instancia aislada de QA, por lo que
    # Enter permite comprobar la activación sin modificar datos de usuario.
    pyautogui.press("f10")
    pyautogui.press("down")
    pyautogui.press("enter")
    time.sleep(0.4)
    pyautogui.press("tab", presses=4, interval=0.1)
    pyautogui.hotkey("shift", "tab")
    pyautogui.press("f10")
    pyautogui.press("escape")
    _focus_window("Simulador EV3 Pybricks")
    output.parent.mkdir(parents=True, exist_ok=True)
    pyautogui.screenshot().save(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "case",
        choices=(
            "motor-a",
            "motors-all",
            "sensors",
            "drivebase",
            "menu-running",
            "syntax-error",
            "screen-text",
            "pause-resume-reset",
            "keyboard-navigation",
        ),
    )
    args = parser.parse_args()
    evidence = Path("Documentos/EVIDENCIA_TESTEO_INTEGRAL_TKINTER_2026-07-28")
    cases = {
        "motor-a": (run_motor_a_smoke, evidence / "motor_a_real.png"),
        "motors-all": (run_all_motors_smoke, evidence / "motores_abcd_real.png"),
        "sensors": (run_sensors_smoke, evidence / "sensores_s1_s4_real.png"),
        "drivebase": (run_drivebase_smoke, evidence / "drivebase_real.png"),
        "menu-running": (run_menu_during_execution_smoke, evidence / "menu_durante_ejecucion_real.png"),
        "syntax-error": (run_syntax_error_smoke, evidence / "error_sintaxis_real.png"),
        "screen-text": (run_screen_text_smoke, evidence / "screen_draw_text_real.png"),
        "pause-resume-reset": (run_pause_resume_reset_smoke, evidence / "reinicio_real.png"),
        "keyboard-navigation": (run_keyboard_navigation_smoke, evidence / "teclado_foco_escape_real.png"),
    }
    action, target = cases[args.case]
    action(target)
    print(target)
