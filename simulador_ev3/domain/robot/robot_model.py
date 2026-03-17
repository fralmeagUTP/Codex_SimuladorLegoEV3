"""
robot_model.py
==============
Modelo de dominio del robot EV3 completo.

Responsabilidades:
    - Mantener la pose del robot: (x, y, theta)
    - Integrar DriveBaseModel y PortManager
    - Proveer la actualización de pose basada en cinemática diferencial (SAD §13)
    - Ser la raíz del grafo de dominio

Unidades:
    x, y   → milímetros (origen = posición inicial del escenario)
    theta  → radianes (0 = apunta hacia +X; aumenta en sentido antihorario)

La pose se actualiza en cada tick por SimulationEngine mediante
DriveBaseModel.update() que retorna (delta_distance, delta_angle).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from simulador_ev3.domain.robot.drivebase_model import DriveBaseModel
from simulador_ev3.domain.robot.port_manager import PortManager


@dataclass
class Pose:
    """
    Representa la pose 2D del robot en el plano del mundo.

    Attributes:
        x:     Posición horizontal en mm.
        y:     Posición vertical en mm.
        theta: Orientación en radianes (0 = +X, antihorario positivo).
    """
    x:     float = 0.0
    y:     float = 0.0
    theta: float = 0.0  # radianes

    @property
    def theta_deg(self) -> float:
        """Orientación en grados (lectura conveniente para UI/debug)."""
        return math.degrees(self.theta)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Pose(x={self.x:.2f}mm, y={self.y:.2f}mm, "
            f"θ={self.theta_deg:.2f}°)"
        )


@dataclass
class RobotModel:
    """
    Modelo raíz del robot EV3.

    Agrega la pose, el DriveBase y el PortManager.
    Es el punto de entrada para SimulationEngine al actualizar
    el estado completo del robot cada tick.

    Args:
        drivebase:    Modelo cinemático del DriveBase diferencial.
        port_manager: Registro de puertos y dispositivos.
        initial_pose: Pose inicial en el mundo (por defecto origen).
    """

    drivebase:    DriveBaseModel
    port_manager: PortManager
    initial_pose: Pose = field(default_factory=Pose)

    # Pose actual (mutable durante la simulación)
    _pose: Pose = field(init=False, repr=False)

    def __post_init__(self) -> None:
        # Clona la pose inicial para no mutar el argumento externo
        self._pose = Pose(
            x=self.initial_pose.x,
            y=self.initial_pose.y,
            theta=self.initial_pose.theta,
        )

    # ------------------------------------------------------------------ #
    # Acceso a la pose
    # ------------------------------------------------------------------ #

    @property
    def pose(self) -> Pose:
        """Pose actual del robot (solo lectura desde fuera del engine)."""
        return self._pose

    @property
    def x(self) -> float:
        return self._pose.x

    @property
    def y(self) -> float:
        return self._pose.y

    @property
    def theta(self) -> float:
        """Orientación en radianes."""
        return self._pose.theta

    @property
    def theta_deg(self) -> float:
        """Orientación en grados."""
        return self._pose.theta_deg

    # ------------------------------------------------------------------ #
    # Actualización de pose — llamada por SimulationEngine
    # ------------------------------------------------------------------ #

    def update(self, dt: float) -> bool:
        """
        Avanza el estado del robot un step de `dt` segundos.

        Integra el modelo cinemático diferencial (SAD §13):
            x     += v · cos(θ) · dt
            y     += v · sin(θ) · dt
            θ     += omega · dt

        Returns:
            True si un movimiento acotado (straight/turn) se completó.
        """
        delta_distance_mm, delta_angle_deg, completed = self.drivebase.update(dt)

        # Convertir velocidad angular de grados a radianes para integración
        delta_theta = math.radians(delta_angle_deg)

        # Integración cinemática (SAD §13)
        theta = self._pose.theta
        self._pose.x     += delta_distance_mm * math.cos(theta)
        self._pose.y     += delta_distance_mm * math.sin(theta)
        self._pose.theta  = theta + delta_theta

        # Normalizar theta en [-π, π] para evitar acumulación ilimitada
        self._pose.theta = math.atan2(
            math.sin(self._pose.theta),
            math.cos(self._pose.theta),
        )

        return completed

    # ------------------------------------------------------------------ #
    # Utilidades
    # ------------------------------------------------------------------ #

    def reset_pose(self, pose: Optional[Pose] = None) -> None:
        """
        Reinicia la pose del robot.
        Si no se provee pose, vuelve al origen (0, 0, 0).
        """
        target = pose or Pose()
        self._pose = Pose(x=target.x, y=target.y, theta=target.theta)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RobotModel(pose={self._pose!r}, "
            f"drivebase={self.drivebase.state.name})"
        )
