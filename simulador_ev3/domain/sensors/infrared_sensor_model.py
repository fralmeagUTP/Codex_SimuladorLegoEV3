"""
infrared_sensor_model.py
========================
Modelo del sensor infrarrojo EV3.

Soporta dos modos:
    PROXIMITY: mide proximidad a obstáculos (similar a ultrasonido, 0-100).
    BEACON:    lee distancia y heading de una baliza IR en un canal.

API Pybricks:
    sensor.distance()           → int  (modo PROXIMITY, 0-100)
    sensor.beacon(channel)      → tuple[int, int]  (distancia, heading)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from simulador_ev3.domain.world.world_model import WorldModel


MAX_IR_DISTANCE = 70.0   # distancia real máxima en cm → escalada a 0-100


@dataclass
class InfraredSensorModel:
    """
    Modelo del sensor infrarrojo EV3.

    Args:
        port_name:    Puerto (p.ej. 'S2').
        offset_x_mm:  Desplazamiento frente al robot (mm).
        offset_y_mm:  Desplazamiento lateral (mm).
    """

    port_name:    str   = "S2"
    offset_x_mm: float = 70.0
    offset_y_mm: float = 0.0

    # Estado interno
    _proximity:  int  = field(default=0, init=False, repr=False)

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
        Actualiza la proximidad mediante ray casting (igual que ultrasonido
        pero escalado a 0-100).
        """
        cos_t = math.cos(robot_theta)
        sin_t = math.sin(robot_theta)

        sx = robot_x + self.offset_x_mm * cos_t - self.offset_y_mm * sin_t
        sy = robot_y + self.offset_x_mm * sin_t + self.offset_y_mm * cos_t

        dist_mm = world.ray_cast(
            ox=sx, oy=sy,
            angle_rad=robot_theta,
            max_dist_mm=MAX_IR_DISTANCE * 10,  # 700 mm máx
        )
        # Escalar a 0-100
        self._proximity = min(100, int(dist_mm / (MAX_IR_DISTANCE * 10) * 100))

    # ------------------------------------------------------------------ #
    # API de lectura — MODO PROXIMITY
    # ------------------------------------------------------------------ #

    def distance(self) -> int:
        """
        Proximidad al obstáculo más cercano en unidades 0-100.
        Equivale a InfraredSensor.distance() de Pybricks.
        100 = sin obstáculo en rango.
        """
        return self._proximity

    # ------------------------------------------------------------------ #
    # API de lectura — MODO BEACON
    # ------------------------------------------------------------------ #

    def beacon(self, channel: int, world: "WorldModel",
               robot_x: float, robot_y: float,
               robot_theta: float) -> Tuple[int, int]:
        """
        Retorna (distancia_relativa, heading_relativo) de la baliza en `channel`.
        Equivale a InfraredSensor.beacon(channel) de Pybricks.

        Returns:
            (distancia 0-100, heading -25 a 25)
            Si no hay baliza en ese canal: (0, 0).
        """
        b = world.get_beacon(channel)
        if b is None:
            return 0, 0
        return (
            b.relative_distance(robot_x, robot_y),
            b.relative_heading(robot_x, robot_y, robot_theta),
        )

    # ------------------------------------------------------------------ #
    # Serialización
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {"proximity": self._proximity, "port": self.port_name}

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"InfraredSensorModel(port={self.port_name!r}, "
            f"proximity={self._proximity})"
        )
