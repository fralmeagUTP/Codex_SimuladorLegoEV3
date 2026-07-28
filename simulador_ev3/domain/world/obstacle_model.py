"""
obstacle_model.py
=================
Modelo de obstáculos del mundo del simulador EV3.

Un obstáculo es un polígono 2D convexo que el robot no puede atravesar.
Se utiliza para:
    - Colisión con TouchSensor (contacto directo)
    - Ray casting de UltrasonicSensor (distancia a obstáculo)
    - Detección de colisión en WorldModel (posición robot vs polígono)

Todos los valores en milímetros (mm) en el sistema de coordenadas del mundo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

Point = Tuple[float, float]  # (x_mm, y_mm)


@dataclass
class ObstacleModel:
    """
    Obstáculo definido como un polígono 2D (lista de vértices en orden).

    Para rectángulos, usar el método de fábrica `from_rect()`.
    Para polígonos arbitrarios, pasar los vértices directamente.

    Attributes:
        vertices:  Lista de puntos (x, y) en mm, en orden (CW o CCW).
        name:      Identificador opcional para debug/UI.
    """

    vertices: List[Point]
    name: str = "obstacle"

    def __post_init__(self) -> None:
        if len(self.vertices) < 3:
            raise ValueError("Un obstáculo necesita al menos 3 vértices.")

    # ------------------------------------------------------------------ #
    # Fábrica de rectángulo
    # ------------------------------------------------------------------ #

    @classmethod
    def from_rect(
        cls,
        x: float,
        y: float,
        width: float,
        height: float,
        name: str = "rect_obstacle",
    ) -> "ObstacleModel":
        """
        Crea un obstáculo rectangular.

        Args:
            x, y:         Esquina inferior-izquierda en mm.
            width, height: Dimensiones en mm.
        """
        verts: List[Point] = [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
        ]
        return cls(vertices=verts, name=name)

    # ------------------------------------------------------------------ #
    # Bounding box (para optimización de detección)
    # ------------------------------------------------------------------ #

    @property
    def aabb(self) -> Tuple[float, float, float, float]:
        """
        Axis-Aligned Bounding Box: (min_x, min_y, max_x, max_y) en mm.
        Útil para descartar obstáculos antes del test de intersección preciso.
        """
        xs = [p[0] for p in self.vertices]
        ys = [p[1] for p in self.vertices]
        return min(xs), min(ys), max(xs), max(ys)

    # ------------------------------------------------------------------ #
    # Contiene un punto — algoritmo ray casting
    # ------------------------------------------------------------------ #

    def contains_point(self, px: float, py: float) -> bool:
        """
        True si el punto (px, py) está dentro del polígono.
        Utiliza el algoritmo de cruce de rayos (ray casting).
        """
        n = len(self.vertices)
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = self.vertices[i]
            xj, yj = self.vertices[j]
            if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi + 1e-12) + xi):
                inside = not inside
            j = i
        return inside

    # ------------------------------------------------------------------ #
    # Intersección de segmento con el polígono — para ray casting sonar
    # ------------------------------------------------------------------ #

    def ray_intersection_distance(
        self,
        ox: float,
        oy: float,
        dx: float,
        dy: float,
        max_dist: float = 2500.0,
    ) -> float | None:
        """
        Calcula la distancia desde el origen (ox, oy) al primer borde del
        polígono en la dirección del rayo (dx, dy), normalizada.

        Returns:
            Distancia en mm, o None si no hay intersección dentro de max_dist.
        """
        min_t: float | None = None
        n = len(self.vertices)
        for i in range(n):
            ax, ay = self.vertices[i]
            bx, by = self.vertices[(i + 1) % n]

            # Segmento del borde: P = A + s*(B-A), s ∈ [0,1]
            # Rayo:               R = O + t*(dx,dy), t ∈ [0, max_dist]
            ex, ey = bx - ax, by - ay
            denom = dx * ey - dy * ex
            if abs(denom) < 1e-10:
                continue  # paralelos

            fx, fy = ax - ox, ay - oy
            t = (fx * ey - fy * ex) / denom
            s = (fx * dy - fy * dx) / denom

            if 0.0 <= s <= 1.0 and 0.0 <= t <= max_dist:
                if min_t is None or t < min_t:
                    min_t = t
        return min_t

    # ------------------------------------------------------------------ #
    # Centro geométrico
    # ------------------------------------------------------------------ #

    @property
    def centroid(self) -> Point:
        """Centro geométrico aproximado del obstáculo."""
        cx = sum(p[0] for p in self.vertices) / len(self.vertices)
        cy = sum(p[1] for p in self.vertices) / len(self.vertices)
        return cx, cy

    def __repr__(self) -> str:  # pragma: no cover
        return f"ObstacleModel(name={self.name!r}, vertices={len(self.vertices)})"
