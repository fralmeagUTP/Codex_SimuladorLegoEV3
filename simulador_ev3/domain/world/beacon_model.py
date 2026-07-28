"""
beacon_model.py
===============
Modelo de la baliza infrarroja (IR Beacon) del mundo EV3.

La baliza es un dispositivo externo que emite señales IR en un canal (1-4).
El InfraredSensor puede leer:
    - Distancia relativa a la baliza (0-100, sin unidades físicas reales)
    - Heading relativo al robot (-25 a 25, en incrementos de 1)

En el simulador, la distancia y heading se calculan geometricamente
desde la pose del robot a la posición de la baliza.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class BeaconModel:
    """
    Baliza infrarroja posicionada en el mundo.

    Attributes:
        x_mm:    Posición X en el mundo (mm).
        y_mm:    Posición Y en el mundo (mm).
        channel: Canal IR (1-4), debe coincidir con el InfraredSensor.
        name:    Identificador para debug/UI.
    """

    x_mm: float
    y_mm: float
    channel: int = 1
    name: str = "beacon"

    def __post_init__(self) -> None:
        if not (1 <= self.channel <= 4):
            raise ValueError(f"Canal IR debe ser 1-4, recibido: {self.channel}")

    # ------------------------------------------------------------------ #
    # Geometría relativa al robot
    # ------------------------------------------------------------------ #

    def distance_to(self, robot_x: float, robot_y: float) -> float:
        """
        Distancia euclidiana en mm desde el robot a la baliza.
        """
        dx = self.x_mm - robot_x
        dy = self.y_mm - robot_y
        return math.hypot(dx, dy)

    def relative_distance(self, robot_x: float, robot_y: float) -> int:
        """
        Distancia relativa en unidades Pybricks (0-100).
        La escala aproximada es 1 unidad ≈ 30 mm (max 3000 mm → 100).
        """
        d = self.distance_to(robot_x, robot_y)
        return min(100, int(d / 30.0))

    def relative_heading(
        self,
        robot_x: float,
        robot_y: float,
        robot_theta: float,
    ) -> int:
        """
        Heading relativo de la baliza respecto a la orientación del robot.
        Rango: -25 a 25 (unidades arbitrarias Pybricks).
        0 = baliza justo al frente.
        """
        dx = self.x_mm - robot_x
        dy = self.y_mm - robot_y
        # Ángulo absoluto hacia la baliza
        angle_to_beacon = math.atan2(dy, dx)
        # Ángulo relativo al heading del robot
        relative = angle_to_beacon - robot_theta
        # Normalizar a [-π, π]
        relative = math.atan2(math.sin(relative), math.cos(relative))
        # Escalar a [-25, 25]
        heading = int(relative / math.pi * 25.0)
        return max(-25, min(25, heading))

    def __repr__(self) -> str:  # pragma: no cover
        return f"BeaconModel(name={self.name!r}, pos=({self.x_mm:.0f},{self.y_mm:.0f})mm, ch={self.channel})"
