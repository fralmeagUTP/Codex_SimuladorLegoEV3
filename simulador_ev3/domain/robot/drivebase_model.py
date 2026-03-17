"""
drivebase_model.py
==================
Modelo de dominio del DriveBase diferencial del robot EV3.

Implementa la cinemática diferencial definida en SAD §13:
    v     = (vr + vl) / 2
    omega = (vr - vl) / L
    x     = x + v·cos(θ)·dt
    y     = y + v·sin(θ)·dt
    θ     = θ + omega·dt

Soporta `settings()` (SAD mejora M3) para controlar aceleración dinámica,
tal como usan los ejemplos 03, 05, 09, 10.

Unidades del sistema:
    Velocidad lineal:   mm/s
    Velocidad angular:  deg/s
    Aceleración lineal: mm/s²
    Ángulo/orientación: radianes (interno), grados (API pública)
    Distancia:          mm
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class DriveState(Enum):
    """Estados operativos del DriveBase."""
    IDLE     = auto()   # parado, sin movimiento activo
    DRIVE    = auto()   # conducción continua (drive)
    STRAIGHT = auto()   # movimiento recto acotado en mm
    TURN     = auto()   # giro acotado en grados


@dataclass
class AccelerationProfile:
    """
    Perfil de aceleración/desaceleración del DriveBase.
    Equivalente a los parámetros de DriveBase.settings().

    Attributes:
        straight_speed:        Velocidad de avance recto (mm/s)
        straight_acceleration: Aceleración lineal (mm/s²)
        turn_rate:             Velocidad angular de giro (deg/s)
        turn_acceleration:     Aceleración angular (deg/s²)
    """
    straight_speed:        float = 200.0
    straight_acceleration: float = 600.0
    turn_rate:             float = 90.0
    turn_acceleration:     float = 360.0

    def __post_init__(self) -> None:
        if self.straight_speed <= 0:
            raise ValueError("straight_speed debe ser > 0")
        if self.straight_acceleration <= 0:
            raise ValueError("straight_acceleration debe ser > 0")
        if self.turn_rate <= 0:
            raise ValueError("turn_rate debe ser > 0")
        if self.turn_acceleration <= 0:
            raise ValueError("turn_acceleration debe ser > 0")


@dataclass
class DriveBaseModel:
    """
    Modelo cinemático del DriveBase diferencial EV3.

    Args:
        wheel_diameter_mm: Diámetro de las ruedas en mm
                           (nominal Lego EV3: 55.5 mm).
        axle_track_mm:     Distancia entre centros de ruedas en mm
                           (nominal EV3: 104 mm).

    Mecánica soportada:
        drive(speed_mm_s, turn_rate_deg_s)  — conducción continua
        stop()                              — detiene inmediatamente
        straight(distance_mm)               — avance acotado (bloqueante)
        turn(angle_deg)                     — giro acotado (bloqueante)
        settings(...)                       — actualiza perfil de aceleración
    """

    wheel_diameter_mm: float
    axle_track_mm:     float

    # Perfil de aceleración configurable (settings())
    profile: AccelerationProfile = field(default_factory=AccelerationProfile)

    # Estado operativo actual
    state: DriveState = field(default=DriveState.IDLE, init=False)

    # Velocidades actuales (lineales en mm/s, angulares en deg/s)
    _current_linear_speed:  float = field(default=0.0, init=False, repr=False)
    _current_angular_speed: float = field(default=0.0, init=False, repr=False)

    # Para comandos acotados (STRAIGHT / TURN): distancia/ángulo restante
    _target_linear_speed:   float = field(default=0.0, init=False, repr=False)
    _target_angular_speed:  float = field(default=0.0, init=False, repr=False)
    _remaining_distance_mm: float = field(default=0.0, init=False, repr=False)
    _remaining_angle_deg:   float = field(default=0.0, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.wheel_diameter_mm <= 0:
            raise ValueError("wheel_diameter_mm debe ser > 0")
        if self.axle_track_mm <= 0:
            raise ValueError("axle_track_mm debe ser > 0")

    # ------------------------------------------------------------------ #
    # Propiedades de lectura
    # ------------------------------------------------------------------ #

    @property
    def linear_speed(self) -> float:
        """Velocidad lineal actual en mm/s."""
        return self._current_linear_speed

    @property
    def angular_speed_deg(self) -> float:
        """Velocidad angular actual en grados/segundo."""
        return self._current_angular_speed

    # ------------------------------------------------------------------ #
    # Velocidades de rueda (para el motor físico)
    # ------------------------------------------------------------------ #

    def wheel_speeds_deg_s(self) -> tuple[float, float]:
        """
        Calcula la velocidad de cada rueda en grados/segundo a partir
        del movimiento diferencial actual.

        Returns:
            Tupla (vel_rueda_izq_deg_s, vel_rueda_der_deg_s)
        """
        v     = self._current_linear_speed          # mm/s
        omega = math.radians(self._current_angular_speed)  # rad/s
        L     = self.axle_track_mm
        r     = self.wheel_diameter_mm / 2.0

        vl = v - omega * L / 2.0  # mm/s rueda izquierda
        vr = v + omega * L / 2.0  # mm/s rueda derecha

        # Convertir mm/s a deg/s en la rueda
        circ        = math.pi * self.wheel_diameter_mm  # mm/vuelta
        deg_per_mm  = 360.0 / circ

        return vl * deg_per_mm, vr * deg_per_mm

    # ------------------------------------------------------------------ #
    # Comandos de movimiento
    # ------------------------------------------------------------------ #

    def cmd_drive(self, speed_mm_s: float, turn_rate_deg_s: float) -> None:
        """
        Conducción continua (no bloqueante).
        Equivale a DriveBase.drive(speed, turn_rate) de Pybricks.
        """
        self._target_linear_speed  = float(speed_mm_s)
        self._target_angular_speed = float(turn_rate_deg_s)
        self._current_linear_speed = float(speed_mm_s)
        self._current_angular_speed = float(turn_rate_deg_s)
        self.state = DriveState.DRIVE

    def cmd_stop(self) -> None:
        """
        Detiene el DriveBase inmediatamente.
        Transición: cualquier estado → IDLE.
        """
        self._current_linear_speed  = 0.0
        self._current_angular_speed = 0.0
        self._target_linear_speed   = 0.0
        self._target_angular_speed  = 0.0
        self._remaining_distance_mm = 0.0
        self._remaining_angle_deg   = 0.0
        self.state = DriveState.IDLE

    def cmd_straight(self, distance_mm: float) -> None:
        """
        Inicia movimiento recto acotado a `distance_mm` mm (bloqueante).
        Negativo → retroceso.
        Transición: cualquier estado → STRAIGHT.
        """
        speed = self.profile.straight_speed * math.copysign(1.0, distance_mm)
        self._target_linear_speed   = speed
        self._target_angular_speed  = 0.0
        self._current_linear_speed  = speed
        self._current_angular_speed = 0.0
        self._remaining_distance_mm = abs(float(distance_mm))
        self._remaining_angle_deg   = 0.0
        self.state = DriveState.STRAIGHT

    def cmd_turn(self, angle_deg: float) -> None:
        """
        Inicia giro acotado de `angle_deg` grados (bloqueante).
        Positivo → giro horario (derecha).
        Transición: cualquier estado → TURN.
        """
        rate = self.profile.turn_rate * math.copysign(1.0, angle_deg)
        self._target_linear_speed   = 0.0
        self._target_angular_speed  = rate
        self._current_linear_speed  = 0.0
        self._current_angular_speed = rate
        self._remaining_distance_mm = 0.0
        self._remaining_angle_deg   = abs(float(angle_deg))
        self.state = DriveState.TURN

    def cmd_settings(
        self,
        straight_speed:        float,
        straight_acceleration: float,
        turn_rate:             float,
        turn_acceleration:     float,
    ) -> None:
        """
        Actualiza el perfil de aceleración del DriveBase.
        Equivale a DriveBase.settings() de Pybricks (ejemplo 09).
        """
        self.profile = AccelerationProfile(
            straight_speed=straight_speed,
            straight_acceleration=straight_acceleration,
            turn_rate=turn_rate,
            turn_acceleration=turn_acceleration,
        )

    # ------------------------------------------------------------------ #
    # Evolución temporal — llamado por SimulationEngine.update()
    # ------------------------------------------------------------------ #

    def update(self, dt: float) -> tuple[float, float, bool]:
        """
        Avanza el DriveBase un paso de `dt` segundos.

        Returns:
            Tupla (delta_distance_mm, delta_angle_deg, completed)
            donde `completed` es True si un movimiento acotado terminó.
        """
        if self.state == DriveState.IDLE:
            return 0.0, 0.0, False

        elif self.state == DriveState.DRIVE:
            dd = self._current_linear_speed  * dt
            da = self._current_angular_speed * dt
            return dd, da, False

        elif self.state == DriveState.STRAIGHT:
            step = abs(self._current_linear_speed) * dt
            advance = min(step, self._remaining_distance_mm)
            dd = math.copysign(advance, self._current_linear_speed)
            self._remaining_distance_mm -= advance

            if self._remaining_distance_mm <= 0.0:
                self.cmd_stop()
                return dd, 0.0, True

            return dd, 0.0, False

        elif self.state == DriveState.TURN:
            step = abs(self._current_angular_speed) * dt
            advance = min(step, self._remaining_angle_deg)
            da = math.copysign(advance, self._current_angular_speed)
            self._remaining_angle_deg -= advance

            if self._remaining_angle_deg <= 0.0:
                self.cmd_stop()
                return 0.0, da, True

            return 0.0, da, False

        return 0.0, 0.0, False  # estado desconocido — seguro por defecto

    # ------------------------------------------------------------------ #
    # Cinemática diferencial (SAD §13)
    # ------------------------------------------------------------------ #

    @staticmethod
    def compute_pose_delta(
        linear_speed_mm_s: float,
        angular_speed_deg_s: float,
        dt: float,
    ) -> tuple[float, float, float]:
        """
        Calcula el delta de pose (dx_mm, dy_mm, dtheta_rad) en `dt` segundos.

        Fórmulas SAD §13:
            x     += v·cos(θ)·dt
            y     += v·sin(θ)·dt
            theta += omega·dt
        
        Nota: este método recibe la velocidad angular en grados/s y retorna
        dtheta en radianes para manipulación interna de la pose.
        """
        v     = linear_speed_mm_s
        omega = math.radians(angular_speed_deg_s)
        # dx e dy dependen de la orientación actual: se calculan en RobotModel
        # donde se conoce theta. Aquí retornamos los componentes de velocidad.
        dv     = v * dt
        dtheta = omega * dt
        return dv, dtheta  # type: ignore[return-value]

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DriveBaseModel(wheel={self.wheel_diameter_mm}mm, "
            f"axle={self.axle_track_mm}mm, state={self.state.name}, "
            f"v={self._current_linear_speed:.1f}mm/s, "
            f"ω={self._current_angular_speed:.1f}°/s)"
        )
