"""
motor_model.py
==============
Modelo de dominio de un motor individual del robot EV3.

Estados posibles (SAD §14):
    IDLE       — motor detenido sin fuerza aplicada
    RUN        — gira a velocidad constante indefinidamente
    RUN_TIME   — gira durante un tiempo determinado
    RUN_ANGLE  — gira un ángulo determinado
    HOLD       — mantiene la posición actual aplicando torque
    BRAKE      — frena activamente y luego queda IDLE

Tabla de transiciones:
    Cualquier estado → RUN        al llamar run()
    Cualquier estado → RUN_TIME   al llamar run_time()
    Cualquier estado → RUN_ANGLE  al llamar run_angle()
    Cualquier estado → HOLD       al llamar hold()
    Cualquier estado → BRAKE      al llamar brake()
    Cualquier estado → IDLE       al llamar stop()
    RUN_TIME completado            → IDLE  (o el modo `then`)
    RUN_ANGLE completado           → HOLD  (o el modo `then`)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto


class MotorState(Enum):
    """Estados operativos posibles de un motor EV3."""

    IDLE = auto()  # detenido, sin torque
    RUN = auto()  # velocidad constante indefinida
    RUN_TIME = auto()  # velocidad durante tiempo_ms milisegundos simulados
    RUN_ANGLE = auto()  # gira rotation_angle grados
    HOLD = auto()  # mantiene posición con torque
    BRAKE = auto()  # frena activamente → transiciona a IDLE


# Tabla de modos de detención al completar un comando
class StopMode(Enum):
    """Cómo debe quedar el motor al completar un movimiento con límite."""

    COAST = auto()  # sin torque (→ IDLE)
    BRAKE = auto()  # frena activamente (→ IDLE tras brake)
    HOLD = auto()  # mantiene posición (→ HOLD)


@dataclass
class MotorModel:
    """
    Modelo de un motor servo Lego EV3 (Large o Medium).

    Attributes:
        port_name:   Nombre del puerto (p.ej. 'A', 'B').
        _speed:      Velocidad angular actual en grados/segundo.
        _angle:      Posición acumulada desde el reset, en grados.
        _power:      Nivel de potencia estimado 0-100 %.
        state:       Estado operativo actual (MotorState).
        _target_speed:  Velocidad objetivo del comando activo.
        _remaining_time_ms: Tiempo restante (ms) para RUN_TIME.
        _remaining_angle:   Ángulo restante (°) para RUN_ANGLE.
        _then:       StopMode al finalizar un comando con límite.
    """

    port_name: str

    _speed: float = field(default=0.0, init=False, repr=False)
    _angle: float = field(default=0.0, init=False, repr=False)
    _power: float = field(default=0.0, init=False, repr=False)

    state: MotorState = field(default=MotorState.IDLE, init=False)

    _target_speed: float = field(default=0.0, init=False, repr=False)
    _remaining_time_ms: float = field(default=0.0, init=False, repr=False)
    _remaining_angle: float = field(default=0.0, init=False, repr=False)
    _then: StopMode = field(default=StopMode.COAST, init=False, repr=False)

    # ------------------------------------------------------------------ #
    # Propiedades de lectura (SAD §14)
    # ------------------------------------------------------------------ #

    @property
    def speed(self) -> float:
        """Velocidad angular actual en grados/segundo."""
        return self._speed

    @property
    def angle(self) -> float:
        """Posición acumulada en grados desde el último reset."""
        return self._angle

    @property
    def power(self) -> float:
        """Potencia estimada aplicada al motor (0–100 %)."""
        return self._power

    # ------------------------------------------------------------------ #
    # Comandos (generados por pybricks_api → CommandQueue → motor_model)
    # ------------------------------------------------------------------ #

    def cmd_run(self, speed: float) -> None:
        """
        Inicia giro continuo a `speed` grados/segundo.
        Transición: cualquier estado → RUN.
        """
        self._target_speed = float(speed)
        self._power = min(100.0, abs(speed) / 10.0)
        self.state = MotorState.RUN

    def cmd_stop(self) -> None:
        """
        Detiene el motor sin torque (coast).
        Transición: cualquier estado → IDLE.
        """
        self._target_speed = 0.0
        self._speed = 0.0
        self._power = 0.0
        self.state = MotorState.IDLE

    def cmd_brake(self) -> None:
        """
        Frena activamente y luego queda IDLE.
        Transición: cualquier estado → BRAKE → IDLE (en el próximo tick).
        """
        self._target_speed = 0.0
        self._power = 0.0
        self.state = MotorState.BRAKE

    def cmd_hold(self) -> None:
        """
        Mantiene la posición actual aplicando torque.
        Transición: cualquier estado → HOLD.
        """
        self._target_speed = 0.0
        self._power = 10.0  # potencia mínima de holding
        self.state = MotorState.HOLD

    def cmd_run_time(
        self,
        speed: float,
        time_ms: float,
        then: StopMode = StopMode.COAST,
    ) -> None:
        """
        Gira a `speed` durante `time_ms` milisegundos simulados.
        Transición: cualquier estado → RUN_TIME.
        """
        self._target_speed = float(speed)
        self._remaining_time_ms = float(time_ms)
        self._then = then
        self._power = min(100.0, abs(speed) / 10.0)
        self.state = MotorState.RUN_TIME

    def cmd_run_angle(
        self,
        speed: float,
        rotation_angle: float,
        then: StopMode = StopMode.HOLD,
    ) -> None:
        """
        Gira `rotation_angle` grados a velocidad `speed`.
        El signo del ángulo determina la dirección.
        Transición: cualquier estado → RUN_ANGLE.
        """
        if rotation_angle == 0:
            return
        # Asegura que la velocidad tenga el mismo signo que el ángulo
        effective_speed = abs(speed) * math.copysign(1.0, rotation_angle)
        self._target_speed = effective_speed
        self._remaining_angle = abs(float(rotation_angle))
        self._then = then
        self._power = min(100.0, abs(speed) / 10.0)
        self.state = MotorState.RUN_ANGLE

    # ------------------------------------------------------------------ #
    # Evolución temporal — llamado por SimulationEngine.update()
    # ------------------------------------------------------------------ #

    def update(self, dt: float) -> bool:
        """
        Avanza el estado del motor un paso de `dt` segundos.

        Returns:
            True si el motor completó un movimiento acotado
            (RUN_TIME o RUN_ANGLE) en este tick.
        """
        completed = False

        if self.state == MotorState.IDLE:
            self._speed = 0.0
            self._power = 0.0

        elif self.state == MotorState.RUN:
            self._speed = self._target_speed
            self._angle += self._speed * dt

        elif self.state == MotorState.HOLD:
            # Mantiene ángulo: velocidad efectiva ~0
            self._speed = 0.0

        elif self.state == MotorState.BRAKE:
            # Frena en un tick y pasa a IDLE
            self._speed = 0.0
            self._power = 0.0
            self.state = MotorState.IDLE
            completed = True

        elif self.state == MotorState.RUN_TIME:
            self._speed = self._target_speed
            dt_ms = dt * 1000.0
            advance_ms = min(dt_ms, self._remaining_time_ms)
            self._angle += self._speed * (advance_ms / 1000.0)
            self._remaining_time_ms -= advance_ms

            if self._remaining_time_ms <= 0.0:
                self._apply_stop_mode(self._then)
                completed = True

        elif self.state == MotorState.RUN_ANGLE:
            self._speed = self._target_speed
            step = abs(self._speed) * dt
            advance = min(step, self._remaining_angle)
            self._angle += math.copysign(advance, self._speed)
            self._remaining_angle -= advance

            if self._remaining_angle <= 0.0:
                self._apply_stop_mode(self._then)
                completed = True

        return completed

    # ------------------------------------------------------------------ #
    # Utilidades internas
    # ------------------------------------------------------------------ #

    def _apply_stop_mode(self, mode: StopMode) -> None:
        """Aplica el modo de parada al finalizar un movimiento acotado."""
        self._target_speed = 0.0
        self._remaining_angle = 0.0
        self._remaining_time_ms = 0.0

        if mode == StopMode.HOLD:
            self.cmd_hold()
        elif mode == StopMode.BRAKE:
            self.cmd_brake()
        else:  # COAST
            self.cmd_stop()

    def reset_angle(self) -> None:
        """Reinicia el contador de ángulo a cero (equivale a Pybricks reset_angle)."""
        self._angle = 0.0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"MotorModel(port={self.port_name!r}, state={self.state.name}, "
            f"speed={self._speed:.1f} °/s, angle={self._angle:.1f} °)"
        )
