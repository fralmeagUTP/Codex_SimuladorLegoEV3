"""
ultrasonic_sensor_model.py
==========================
Modelo del sensor ultrasónico EV3.

Mide la distancia al obstáculo más cercano en la dirección en que apunta
mediante ray casting sobre el WorldModel.

API Pybricks:
    sensor.distance()         → int (mm)
    sensor.presence()         → bool  (otro sensor US activo cerca)

Rango real del sensor: 0-2550 mm (se trunca a 2500 mm en el simulador).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simulador_ev3.domain.world.world_model import WorldModel


MAX_DISTANCE_MM = 2500.0    # rango máximo del sensor EV3


@dataclass
class UltrasonicSensorModel:
    """
    Modelo del sensor ultrasónico EV3.

    Args:
        port_name:     Puerto (p.ej. 'S4').
        offset_x_mm:   Desplazamiento frente-al-robot del sensor (mm).
        offset_y_mm:   Desplazamiento lateral del sensor (mm).
        angle_offset:  Ángulo adicional del sensor respecto al heading (rad).
                       0 = apunta al frente, π/2 = apunta a la izquierda.
    """

    port_name:     str   = "S4"
    offset_x_mm:  float = 70.0   # montado al frente
    offset_y_mm:  float = 0.0
    angle_offset: float = 0.0    # radianes

    # Estado interno
    _distance_mm: float = field(default=MAX_DISTANCE_MM, init=False, repr=False)
    _presence:    bool  = field(default=False,            init=False, repr=False)

    # ------------------------------------------------------------------ #
    # Actualización — llamada por SimulationEngine cada tick
    # ------------------------------------------------------------------ #

    def update(
        self,
        robot_x: float,
        robot_y: float,
        robot_theta: float,
        world: "WorldModel",
    ) -> None:
        """
        Lanza un rayo desde la posición del sensor y actualiza la distancia
        al obstáculo más cercano.
        """
        cos_t = math.cos(robot_theta)
        sin_t = math.sin(robot_theta)

        # Posición del sensor en el mundo
        sx = robot_x + self.offset_x_mm * cos_t - self.offset_y_mm * sin_t
        sy = robot_y + self.offset_x_mm * sin_t + self.offset_y_mm * cos_t

        # Dirección del rayo
        ray_angle = robot_theta + self.angle_offset

        self._distance_mm = world.ray_cast(
            ox=sx, oy=sy,
            angle_rad=ray_angle,
            max_dist_mm=MAX_DISTANCE_MM,
        )

    # ------------------------------------------------------------------ #
    # API de lectura
    # ------------------------------------------------------------------ #

    def distance(self) -> int:
        """
        Distancia al obstáculo más cercano en mm.
        Equivale a UltrasonicSensor.distance() de Pybricks.
        Retorna int (igual que Pybricks).
        """
        return int(self._distance_mm)

    def presence(self) -> bool:
        """
        True si se detecta otro sensor ultrasónico activo.
        En el simulador siempre retorna False (no modelado).
        """
        return self._presence

    def to_dict(self) -> dict:
        return {
            "distance_mm": int(self._distance_mm),
            "presence":    self._presence,
            "port":        self.port_name,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"UltrasonicSensorModel(port={self.port_name!r}, "
            f"distance={int(self._distance_mm)}mm)"
        )
