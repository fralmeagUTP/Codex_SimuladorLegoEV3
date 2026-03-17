"""
command_queue.py — Cola de comandos thread-safe para la simulación EV3.

Los comandos generados por la capa Pybricks se encolan aquí y el
SimulationEngine los consume en cada tick (50 Hz).

Tipos de comando (15 total):
  Motor       : MOTOR_RUN, MOTOR_RUN_TIME, MOTOR_RUN_ANGLE,
                MOTOR_STOP, MOTOR_BRAKE, MOTOR_HOLD
  DriveBase   : DB_DRIVE, DB_STOP, DB_STRAIGHT, DB_TURN, DB_SETTINGS
  LED         : LED_ON, LED_OFF
  Speaker     : PLAY_SOUND
  Screen      : DISPLAY_TEXT, SCREEN_CLEAR

Los comandos 'bloqueantes' (blocking=True) incluyen un threading.Event que
el SimulationEngine dispara al completarse, permitiendo que el hilo del
script de usuario haga wait() sin busy-loop.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import Enum, auto
from queue import Queue
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Tipos de comando
# ---------------------------------------------------------------------------

class CommandType(Enum):
    # Motor individual
    MOTOR_RUN         = auto()   # run(speed)            — no bloqueante
    MOTOR_RUN_TIME    = auto()   # run_time(speed, ms)   — bloqueante
    MOTOR_RUN_ANGLE   = auto()   # run_angle(speed, deg) — bloqueante
    MOTOR_STOP        = auto()   # stop()                — no bloqueante
    MOTOR_BRAKE       = auto()   # brake()               — no bloqueante
    MOTOR_HOLD        = auto()   # hold()                — no bloqueante

    # DriveBase
    DB_DRIVE          = auto()   # drive(speed, turn_rate) — no bloqueante
    DB_STOP           = auto()   # stop()                  — no bloqueante
    DB_STRAIGHT       = auto()   # straight(dist_mm)        — bloqueante
    DB_TURN           = auto()   # turn(angle_deg)          — bloqueante
    DB_SETTINGS       = auto()   # settings(...)            — no bloqueante

    # Ladrillo EV3 — LED
    LED_ON            = auto()   # light.on(LedColor)      — no bloqueante
    LED_OFF           = auto()   # light.off()             — no bloqueante

    # Ladrillo EV3 — Altavoz
    PLAY_SOUND        = auto()   # speaker.beep(...)       — no bloqueante*

    # Ladrillo EV3 — Pantalla
    DISPLAY_TEXT      = auto()   # screen.print(text)      — no bloqueante
    SCREEN_CLEAR      = auto()   # screen.clear()          — no bloqueante


# ---------------------------------------------------------------------------
# Comando
# ---------------------------------------------------------------------------

@dataclass
class SimulationCommand:
    """
    Unidad de trabajo que viaja desde la API Pybricks al SimulationEngine.

    Atributos:
        cmd_type    : Tipo de comando.
        port        : Puerto destino ('A'..'D' para motores, None si no aplica).
        params      : Parámetros libres del comando (velocidad, ángulo, etc.).
        blocking    : Si True, el hilo de usuario debe esperar a que se
                      complete; el Engine señalará `done_event` al terminar.
        done_event  : threading.Event creado automáticamente cuando
                      blocking=True; None en caso contrario.
    """
    cmd_type: CommandType
    port: Optional[str]              = None
    params: dict[str, Any]          = field(default_factory=dict)
    blocking: bool                   = False
    done_event: Optional[threading.Event] = field(default=None, init=False)

    def __post_init__(self) -> None:
        if self.blocking:
            self.done_event = threading.Event()

    # Helpers de fábrica para los comandos más usados -----------------------

    @classmethod
    def motor_run(cls, port: str, speed: float) -> "SimulationCommand":
        return cls(CommandType.MOTOR_RUN, port=port,
                   params={"speed": speed}, blocking=False)

    @classmethod
    def motor_run_time(
        cls, port: str, speed: float, time_ms: float, stop_mode: str = "BRAKE"
    ) -> "SimulationCommand":
        return cls(CommandType.MOTOR_RUN_TIME, port=port,
                   params={"speed": speed, "time_ms": time_ms,
                           "stop_mode": stop_mode},
                   blocking=True)

    @classmethod
    def motor_run_angle(
        cls, port: str, speed: float, angle_deg: float, stop_mode: str = "BRAKE"
    ) -> "SimulationCommand":
        return cls(CommandType.MOTOR_RUN_ANGLE, port=port,
                   params={"speed": speed, "angle_deg": angle_deg,
                           "stop_mode": stop_mode},
                   blocking=True)

    @classmethod
    def motor_stop(cls, port: str) -> "SimulationCommand":
        return cls(CommandType.MOTOR_STOP, port=port, blocking=False)

    @classmethod
    def motor_brake(cls, port: str) -> "SimulationCommand":
        return cls(CommandType.MOTOR_BRAKE, port=port, blocking=False)

    @classmethod
    def motor_hold(cls, port: str) -> "SimulationCommand":
        return cls(CommandType.MOTOR_HOLD, port=port, blocking=False)

    @classmethod
    def db_drive(cls, speed: float, turn_rate: float) -> "SimulationCommand":
        return cls(CommandType.DB_DRIVE,
                   params={"speed": speed, "turn_rate": turn_rate},
                   blocking=False)

    @classmethod
    def db_stop(cls) -> "SimulationCommand":
        return cls(CommandType.DB_STOP, blocking=False)

    @classmethod
    def db_straight(cls, distance_mm: float) -> "SimulationCommand":
        return cls(CommandType.DB_STRAIGHT,
                   params={"distance_mm": distance_mm},
                   blocking=True)

    @classmethod
    def db_turn(cls, angle_deg: float) -> "SimulationCommand":
        return cls(CommandType.DB_TURN,
                   params={"angle_deg": angle_deg},
                   blocking=True)

    @classmethod
    def db_settings(
        cls,
        straight_speed: float,
        straight_acceleration: float,
        turn_rate: float,
        turn_acceleration: float,
    ) -> "SimulationCommand":
        return cls(CommandType.DB_SETTINGS,
                   params={
                       "straight_speed": straight_speed,
                       "straight_acceleration": straight_acceleration,
                       "turn_rate": turn_rate,
                       "turn_acceleration": turn_acceleration,
                   },
                   blocking=False)

    @classmethod
    def led_on(cls, color: str) -> "SimulationCommand":
        return cls(CommandType.LED_ON, params={"color": color}, blocking=False)

    @classmethod
    def led_off(cls) -> "SimulationCommand":
        return cls(CommandType.LED_OFF, blocking=False)

    @classmethod
    def play_sound(cls, frequency: int = 440, duration_ms: int = 100,
                   volume: int = 50) -> "SimulationCommand":
        return cls(CommandType.PLAY_SOUND,
                   params={"frequency": frequency, "duration_ms": duration_ms,
                           "volume": volume},
                   blocking=False)

    @classmethod
    def display_text(cls, text: str, *, newline: bool = True) -> "SimulationCommand":
        return cls(CommandType.DISPLAY_TEXT,
                   params={"text": text, "newline": newline},
                   blocking=False)

    @classmethod
    def screen_clear(cls) -> "SimulationCommand":
        return cls(CommandType.SCREEN_CLEAR, blocking=False)

    def signal_done(self) -> None:
        """El Engine llama a este método cuando el comando bloqueante termina."""
        if self.done_event is not None:
            self.done_event.set()

    def wait(self, timeout: Optional[float] = None) -> bool:
        """
        Bloquea el hilo del script hasta que el Engine señale la finalización.
        Devuelve True si completó, False si expiró el timeout.
        """
        if self.done_event is None:
            return True  # no bloqueante → siempre "completado"
        return self.done_event.wait(timeout=timeout)

    def __repr__(self) -> str:  # pragma: no cover
        blocking_str = " [blocking]" if self.blocking else ""
        port_str = f" port={self.port}" if self.port else ""
        return f"<Command {self.cmd_type.name}{port_str}{blocking_str} {self.params}>"


# ---------------------------------------------------------------------------
# Cola thread-safe
# ---------------------------------------------------------------------------

class CommandQueue:
    """
    Contenedor FIFO thread-safe.

    El hilo del script de usuario produce comandos vía put().
    El SimulationEngine los consume en cada tick vía drain().
    """

    def __init__(self, maxsize: int = 0) -> None:
        self._q: Queue[SimulationCommand] = Queue(maxsize=maxsize)

    def put(self, command: SimulationCommand) -> None:
        """Encola un comando. Nunca bloquea (unbounded por defecto)."""
        self._q.put_nowait(command)

    def drain(self) -> list[SimulationCommand]:
        """
        Extrae todos los comandos pendientes de una vez.
        Devuelve lista vacía si no hay ninguno.

        Nota: el Engine llama a drain() ANTES de actualizar el estado del
        mundo, de modo que los comandos recibidos en el tick n se procesan
        al inicio del tick n+1 (latencia ≤ 20 ms a 50 Hz).
        """
        commands: list[SimulationCommand] = []
        while not self._q.empty():
            try:
                commands.append(self._q.get_nowait())
            except Exception:
                break
        return commands

    def put_and_wait(
        self,
        command: SimulationCommand,
        timeout: Optional[float] = None,
    ) -> bool:
        """
        Encola un comando bloqueante y espera su finalización.
        Devuelve True si completó, False si expiró el timeout.

        Lanza ValueError si el comando no es bloqueante.
        """
        if not command.blocking:
            raise ValueError(
                f"Comando {command.cmd_type.name} no es bloqueante; "
                "usa put() directamente."
            )
        self.put(command)
        return command.wait(timeout=timeout)

    @property
    def size(self) -> int:
        return self._q.qsize()

    def clear(self) -> None:
        """Descarta todos los comandos pendientes (p. ej. al resetear)."""
        while not self._q.empty():
            try:
                self._q.get_nowait()
            except Exception:
                break
