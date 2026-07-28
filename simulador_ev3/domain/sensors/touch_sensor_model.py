"""
touch_sensor_model.py
=====================
Modelo del sensor de tacto EV3.

El sensor de tacto detecta si está siendo presionado físicamente.
En el simulador, se activa cuando el robot colisiona con un obstáculo
en la dirección en que está montado el sensor.

API Pybricks:
    sensor.pressed() → bool
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simulador_ev3.domain.world.world_model import WorldModel


@dataclass
class TouchSensorModel:
    """
    Modelo del sensor de tacto EV3.

    Args:
        offset_x_mm: Desplazamiento X del sensor desde el centro del robot (mm).
        offset_y_mm: Desplazamiento Y del sensor desde el centro del robot (mm).
        robot_radius_mm: Radio aproximado del robot para detección de colisión.
        port_name: Puerto donde está conectado (para identificación).
    """

    port_name: str = "S1"
    offset_x_mm: float = 80.0  # montado al frente del robot
    offset_y_mm: float = 0.0
    robot_radius_mm: float = 5.0

    # Estado interno
    _pressed: bool = field(default=False, init=False, repr=False)

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
        Evalúa si el sensor está presionado según la posición actual del robot.

        Calcula la posición física del sensor en el mundo rotando el offset
        según el heading del robot, luego pregunta al WorldModel si hay colisión.
        """
        cos_t = math.cos(robot_theta)
        sin_t = math.sin(robot_theta)

        # Posición del sensor en coordenadas de mundo
        sx = robot_x + self.offset_x_mm * cos_t - self.offset_y_mm * sin_t
        sy = robot_y + self.offset_x_mm * sin_t + self.offset_y_mm * cos_t

        self._pressed = world.is_colliding(sx, sy, radius_mm=self.robot_radius_mm)

    # ------------------------------------------------------------------ #
    # API de lectura
    # ------------------------------------------------------------------ #

    def pressed(self) -> bool:
        """
        True si el sensor de tacto está siendo presionado.
        Equivale a TouchSensor.pressed() de Pybricks.
        """
        return self._pressed

    def to_dict(self) -> dict:
        return {"pressed": self._pressed, "port": self.port_name}

    def __repr__(self) -> str:  # pragma: no cover
        return f"TouchSensorModel(port={self.port_name!r}, pressed={self._pressed})"
