"""
world_model.py
==============
Modelo del mundo completo del simulador EV3.

Agrega:
    - SurfaceModel  → superficie (colores y reflectancia)
    - ObstacleModel → lista de obstáculos con colisión
    - BeaconModel   → lista de balizas IR

Es la fuente de verdad que los sensores consultan en cada tick.
SimulationEngine pasa referencia al WorldModel a cada sensor
durante la construcción del escenario.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from simulador_ev3.domain.world.surface_model  import SurfaceModel, SurfaceColor
from simulador_ev3.domain.world.obstacle_model import ObstacleModel
from simulador_ev3.domain.world.beacon_model   import BeaconModel


@dataclass
class WorldModel:
    """
    Mundo 2D completo del escenario de simulación.

    Args:
        width_mm:  Ancho del escenario en mm (default 2000 = 2 m).
        height_mm: Alto del escenario en mm  (default 2000 = 2 m).
        surface:   Modelo de superficie; si None se crea uno blanco por defecto.
        obstacles: Lista inicial de obstáculos.
        beacons:   Lista inicial de balizas IR.
    """

    width_mm:  float = 2000.0
    height_mm: float = 2000.0

    surface:   SurfaceModel          = field(default_factory=SurfaceModel)
    obstacles: List[ObstacleModel]   = field(default_factory=list)
    beacons:   List[BeaconModel]     = field(default_factory=list)

    # ------------------------------------------------------------------ #
    # Gestión de obstáculos
    # ------------------------------------------------------------------ #

    def add_obstacle(self, obstacle: ObstacleModel) -> None:
        """Agrega un obstáculo al mundo."""
        self.obstacles.append(obstacle)

    def remove_obstacle(self, name: str) -> bool:
        """
        Elimina el primer obstáculo con el nombre dado.
        Retorna True si se encontró y eliminó.
        """
        for i, obs in enumerate(self.obstacles):
            if obs.name == name:
                self.obstacles.pop(i)
                return True
        return False

    # ------------------------------------------------------------------ #
    # Gestión de balizas
    # ------------------------------------------------------------------ #

    def add_beacon(self, beacon: BeaconModel) -> None:
        """Agrega una baliza IR al mundo."""
        self.beacons.append(beacon)

    def get_beacon(self, channel: int) -> Optional[BeaconModel]:
        """Retorna la primera baliza en el canal dado, o None."""
        for b in self.beacons:
            if b.channel == channel:
                return b
        return None

    # ------------------------------------------------------------------ #
    # Consultas de colisión
    # ------------------------------------------------------------------ #

    def is_colliding(self, x_mm: float, y_mm: float, radius_mm: float = 0.0) -> bool:
        """
        True si el punto (x_mm, y_mm) colisiona con algún obstáculo
        o está fuera de los límites del mundo.

        Args:
            radius_mm: Radio del robot para colisión aproximada.
                       Con 0 es colisión puntual exacta.
        """
        # Límites del escenario
        if (x_mm - radius_mm < 0 or x_mm + radius_mm > self.width_mm or
                y_mm - radius_mm < 0 or y_mm + radius_mm > self.height_mm):
            return True

        # Colisión con obstáculos
        for obs in self.obstacles:
            min_x, min_y, max_x, max_y = obs.aabb
            # Verificación rápida de bounding box
            if (x_mm + radius_mm < min_x or x_mm - radius_mm > max_x or
                    y_mm + radius_mm < min_y or y_mm - radius_mm > max_y):
                continue
            if obs.contains_point(x_mm, y_mm):
                return True
            # Si hay radio, verificar puntos del perímetro del robot
            if radius_mm > 0:
                for angle_deg in range(0, 360, 45):
                    import math
                    a = math.radians(angle_deg)
                    px = x_mm + radius_mm * math.cos(a)
                    py = y_mm + radius_mm * math.sin(a)
                    if obs.contains_point(px, py):
                        return True
        return False

    # ------------------------------------------------------------------ #
    # Ray casting para UltrasonicSensor
    # ------------------------------------------------------------------ #

    def ray_cast(
        self,
        ox: float,
        oy: float,
        angle_rad: float,
        max_dist_mm: float = 2500.0,
    ) -> float:
        """
        Lanza un rayo desde (ox, oy) en la dirección `angle_rad` y retorna
        la distancia al obstáculo más cercano (o max_dist_mm si no hay).

        Además considera los bordes del mundo como obstáculos.

        Returns:
            Distancia en mm al primer obstáculo, máximo max_dist_mm.
        """
        import math
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)

        min_dist = max_dist_mm

        # Bordes del mundo como cuatro segmentos
        world_obstacle = ObstacleModel.from_rect(
            0, 0, self.width_mm, self.height_mm, name="_world_border"
        )
        # Para el borde del mundo usamos la distancia al borde más cercano
        # en la dirección del rayo (simple cálculo paramétrico)
        for t_candidate in _ray_vs_world_bounds(
            ox, oy, dx, dy,
            self.width_mm, self.height_mm, max_dist_mm
        ):
            if t_candidate is not None and t_candidate < min_dist:
                min_dist = t_candidate

        # Obstáculos
        for obs in self.obstacles:
            dist = obs.ray_intersection_distance(ox, oy, dx, dy, min_dist)
            if dist is not None and dist < min_dist:
                min_dist = dist

        return min_dist

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"WorldModel({self.width_mm:.0f}×{self.height_mm:.0f}mm, "
            f"obstacles={len(self.obstacles)}, beacons={len(self.beacons)})"
        )


# ------------------------------------------------------------------ #
# Utilidad privada: rayo vs bordes del mundo
# ------------------------------------------------------------------ #

def _ray_vs_world_bounds(
    ox: float, oy: float,
    dx: float, dy: float,
    width: float, height: float,
    max_dist: float,
) -> list[float | None]:
    """
    Calcula distancias del rayo a los cuatro bordes del mundo.
    Retorna lista con hasta 4 valores (puede haber None si no intersecta).
    """
    results: list[float | None] = []

    # Borde izquierdo  x=0        (válido si el rayo apunta a x<0)
    results.append(_ray_vs_vertical(ox, oy, dx, dy, 0.0,    0.0, height))
    # Borde derecho    x=width
    results.append(_ray_vs_vertical(ox, oy, dx, dy, width,  0.0, height))
    # Borde inferior   y=0
    results.append(_ray_vs_horizontal(ox, oy, dx, dy, 0.0,    0.0, width))
    # Borde superior   y=height
    results.append(_ray_vs_horizontal(ox, oy, dx, dy, height, 0.0, width))

    return [r for r in results if r is not None and 1e-3 < r <= max_dist]


def _ray_vs_vertical(
    ox: float, oy: float,
    dx: float, dy: float,
    x_line: float,
    y_min: float, y_max: float,
) -> float | None:
    if abs(dx) < 1e-10:
        return None
    t = (x_line - ox) / dx
    if t <= 0:
        return None
    y_hit = oy + t * dy
    if y_min <= y_hit <= y_max:
        return t
    return None


def _ray_vs_horizontal(
    ox: float, oy: float,
    dx: float, dy: float,
    y_line: float,
    x_min: float, x_max: float,
) -> float | None:
    if abs(dy) < 1e-10:
        return None
    t = (y_line - oy) / dy
    if t <= 0:
        return None
    x_hit = ox + t * dx
    if x_min <= x_hit <= x_max:
        return t
    return None
