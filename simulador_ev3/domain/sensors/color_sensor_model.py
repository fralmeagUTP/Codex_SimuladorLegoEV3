"""
color_sensor_model.py
=====================
Modelo del sensor de color EV3 (corrige M2 del SAD).

Soporta DOS MODOS de operación (ambos necesarios para los ejemplos):

    Modo COLOR:       sensor.color()      → SurfaceColor (mapeada a Color Pybricks)
    Modo REFLECTION:  sensor.reflection() → int 0-100 %

El modo activo no cambia la lectura; ambas propiedades están siempre
disponibles. La distinción de modo solo afecta la configuración LEGO
real, pero en el simulador se computa todo en cada tick.

Montado mirando hacia abajo (hacia la superficie).
API Pybricks:
    sensor.color()       → Color.*
    sensor.reflection()  → int (0-100)
    sensor.ambient()     → int (0-100, luz ambiente — siempre 0 en simulador)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from simulador_ev3.domain.world.surface_model import SurfaceColor

if TYPE_CHECKING:
    from simulador_ev3.domain.world.world_model import WorldModel


@dataclass
class ColorSensorModel:
    """
    Modelo del sensor de color EV3.

    Args:
        port_name:    Puerto (p.ej. 'S3').
        offset_x_mm:  Desplazamiento del sensor desde el centro del robot (mm).
                      Negativo = hacia atrás.
        offset_y_mm:  Desplazamiento lateral.
    """

    port_name:    str   = "S3"
    offset_x_mm: float = 60.0   # ligeramente al frente
    offset_y_mm: float = 0.0

    # Estado interno actualizado cada tick
    _color:       SurfaceColor = field(default=SurfaceColor.WHITE, init=False, repr=False)
    _reflectance: float        = field(default=95.0,               init=False, repr=False)

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
        Calcula la posición del sensor en el mundo y consulta la superficie.
        """
        cos_t = math.cos(robot_theta)
        sin_t = math.sin(robot_theta)

        # Posición del sensor proyectada en el mundo
        sx = robot_x + self.offset_x_mm * cos_t - self.offset_y_mm * sin_t
        sy = robot_y + self.offset_x_mm * sin_t + self.offset_y_mm * cos_t

        self._color, self._reflectance = world.surface.query(sx, sy)

    # ------------------------------------------------------------------ #
    # API de lectura — MODO COLOR
    # ------------------------------------------------------------------ #

    def color(self) -> SurfaceColor:
        """
        Retorna el color detectado en la superficie.
        Equivale a ColorSensor.color() de Pybricks → Color.*

        Retorna SurfaceColor que la capa pybricks_api convierte a Color.*.
        """
        return self._color

    # ------------------------------------------------------------------ #
    # API de lectura — MODO REFLECTION
    # ------------------------------------------------------------------ #

    def reflection(self) -> int:
        """
        Retorna la reflectancia de la superficie en 0-100 %.
        Equivale a ColorSensor.reflection() de Pybricks.

        Usado en algoritmos de sigue-líneas (ejemplo 06):
            error = reflection() - umbral
            giro  = error * kp
        """
        return int(round(self._reflectance))

    # ------------------------------------------------------------------ #
    # API de lectura — LUZ AMBIENTE (stub)
    # ------------------------------------------------------------------ #

    def ambient(self) -> int:
        """
        Retorna la luz ambiente (0-100).
        En el simulador siempre es 0 (no modelado).
        """
        return 0

    # ------------------------------------------------------------------ #
    # Serialización
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "color":       self._color.name,
            "reflectance": int(round(self._reflectance)),
            "port":        self.port_name,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ColorSensorModel(port={self.port_name!r}, "
            f"color={self._color.name}, ref={int(self._reflectance)}%)"
        )
