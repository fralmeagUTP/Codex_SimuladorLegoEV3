"""
gyro_sensor_model.py
====================
Modelo del sensor giroscópico EV3.

El giroscopio mide la velocidad angular y el ángulo acumulado del robot.

API Pybricks:
    sensor.angle()    → int (grados acumulados desde el reset)
    sensor.speed()    → int (velocidad angular en grados/segundo)
    sensor.reset_angle(angle) → void

En el simulador, el ángulo se deriva directamente de robot_theta,
que es la fuente de verdad geométrica.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class GyroSensorModel:
    """
    Modelo del sensor giroscópico EV3.

    El ángulo y la velocidad se inyectan desde el RobotModel en cada tick.
    No necesita WorldModel (no hay geometría de mundo, solo estado del robot).

    Args:
        port_name: Puerto donde está conectado.
    """

    port_name: str = "S2"

    # Estado actualizado cada tick
    _angle_deg:      float = field(default=0.0, init=False, repr=False)
    _speed_deg_s:    float = field(default=0.0, init=False, repr=False)
    _offset_deg:     float = field(default=0.0, init=False, repr=False)   # reset calibrado

    # Theta anterior para calcular velocidad
    _prev_theta_rad: float = field(default=0.0, init=False, repr=False)
    _initialized:    bool  = field(default=False, init=False, repr=False)

    # ------------------------------------------------------------------ #
    # Actualización — llamada por SimulationEngine cada tick
    # ------------------------------------------------------------------ #

    def update(self, robot_theta_rad: float, dt: float) -> None:
        """
        Actualiza el ángulo y velocidad angular a partir del theta del robot.

        Args:
            robot_theta_rad: Orientación actual del robot en radianes.
            dt: Paso de tiempo en segundos.
        """
        if not self._initialized:
            self._prev_theta_rad = robot_theta_rad
            self._initialized    = True

        # Velocidad angular: diferencia de theta / dt
        delta_theta = robot_theta_rad - self._prev_theta_rad
        # Normalizar a [-π, π] para evitar saltos de ±2π
        delta_theta = math.atan2(math.sin(delta_theta), math.cos(delta_theta))

        if dt > 0:
            self._speed_deg_s = math.degrees(delta_theta) / dt
        else:
            self._speed_deg_s = 0.0

        raw_angle        = math.degrees(robot_theta_rad)
        self._angle_deg  = raw_angle - self._offset_deg
        self._prev_theta_rad = robot_theta_rad

    # ------------------------------------------------------------------ #
    # API de lectura
    # ------------------------------------------------------------------ #

    def angle(self) -> int:
        """
        Ángulo acumulado en grados desde el último reset.
        Equivale a GyroSensor.angle() de Pybricks.
        """
        return int(round(self._angle_deg))

    def speed(self) -> int:
        """
        Velocidad angular en grados/segundo.
        Equivale a GyroSensor.speed() de Pybricks.
        """
        return int(round(self._speed_deg_s))

    def reset_angle(self, angle: int = 0) -> None:
        """
        Reinicia el ángulo del giroscopio al valor dado.
        Equivale a GyroSensor.reset_angle() de Pybricks.
        """
        self._offset_deg = math.degrees(self._prev_theta_rad) - angle
        self._angle_deg  = float(angle)

    # ------------------------------------------------------------------ #
    # Serialización
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "angle_deg":   self.angle(),
            "speed_deg_s": self.speed(),
            "port":        self.port_name,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"GyroSensorModel(port={self.port_name!r}, "
            f"angle={self.angle()}°, speed={self.speed()}°/s)"
        )
