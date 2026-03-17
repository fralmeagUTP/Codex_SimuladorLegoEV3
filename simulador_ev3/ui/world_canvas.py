"""
world_canvas.py — Canvas Tkinter que dibuja el mundo 2-D del simulador EV3.

Renderiza (en cada tick):
  • Fondo de la pista / superficie (gris claro).
  • Obstáculos rectangulares (negro).
  • Robot EV3 — cuerpo rectangular + triángulo indicador de heading.
  • Punto de colisión (borde rojo) si colliding=True.

El canvas se escala automáticamente al tamaño del widget para que el
mundo completo (world_width_mm × world_height_mm) siempre sea visible.

No depende directamente de la capa de dominio; sólo consume SnapshotDTO
y la configuración de la pista (WorldConfig, Fase 8).
"""
from __future__ import annotations

import math
import tkinter as tk
from typing import Callable, Optional

from simulador_ev3.application.snapshot_dto import SnapshotDTO


# Colores del canvas
_BG           = "#F0F0F0"
_OBSTACLE     = "#222222"
_HEADING      = "#1565C0"     # flecha de dirección
_TRAIL        = "#90CAF9"     # rastro opcional
_GRID         = "#CCCCCC"
_SURFACE_BLACK = "#1A1A1A"

# Paleta robot tipo EV3 (aproximada)
_ROBOT_BODY      = "#D9DDE3"
_ROBOT_BODY_TOP  = "#C7CDD6"
_ROBOT_OUTLINE   = "#5E6773"
_ROBOT_COLLISION = "#D32F2F"
_ROBOT_WHEEL     = "#1F1F1F"
_ROBOT_SENSOR    = "#2B2B2B"
_ROBOT_SENSOR_EYE = "#8E9AAF"
_ROBOT_BUTTON    = "#E53935"
_ROBOT_SCREEN_FRAME = "#8D939D"
_ROBOT_SCREEN_GLASS = "#C8E6D0"
_ROBOT_DPAD = "#AEB4BD"
_ROBOT_STRIP = "#A7ADB6"
_ROBOT_PORT_RED = "#C62828"

# Tamaño por defecto del mundo (en mm, sincronizado con SimEngineConfig)
_DEFAULT_WORLD_W = 2000.0
_DEFAULT_WORLD_H = 2000.0

# Tamaño visual del robot (en mm del mundo antes de escalar)
_ROBOT_W_MM = 175.0   # largo (eje X local)
_ROBOT_H_MM = 140.0   # ancho (eje Y local)

# Colores del modo de colocación
_PLACEMENT_GHOST  = "#4FC3F7"   # contorno fantasma al mover el ratón
_PLACEMENT_MARKER = "#FF6F00"   # marcador de posición seleccionada


class WorldCanvas(tk.Canvas):
    """
    Canvas que renderiza el mundo de simulación en cada tick.

    Args:
        parent:        Widget padre Tkinter.
        world_w_mm:    Ancho del mundo simulado en mm.
        world_h_mm:    Alto del mundo simulado en mm.
        show_trail:    Si True, dibuja el rastro del robot.
        **kwargs:      Argumentos adicionales para tk.Canvas.
    """

    def __init__(
        self,
        parent: tk.Widget,
        world_w_mm: float = _DEFAULT_WORLD_W,
        world_h_mm: float = _DEFAULT_WORLD_H,
        show_trail: bool  = True,
        **kwargs,
    ) -> None:
        kwargs.setdefault("bg", _BG)
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("highlightbackground", "#AAAAAA")
        super().__init__(parent, **kwargs)

        self._world_w  = world_w_mm
        self._world_h  = world_h_mm
        self._show_trail = show_trail

        # Lista de posiciones (x_mm, y_mm) del rastro
        self._trail: list[tuple[float, float]] = []
        self._obstacles: list[dict] = []  # {x, y, w, h} en mm
        self._surface_cells: list[dict] = []  # {x_mm, y_mm, size_mm, color}

        # Handles de items del canvas (para actualizar en lugar de recrear)
        self._robot_items: list[int] = []
        self._obstacle_items: list[int] = []
        self._surface_items: list[int] = []

        # Estado del modo de colocación del robot
        self._placement_mode: bool = False
        self._placement_cb: Optional[Callable[[float, float, float], None]] = None
        self._placement_hover_cb: Optional[Callable[[float, float], None]] = None
        self._placement_pos: Optional[tuple[float, float]] = None
        self._placement_hover_pos: Optional[tuple[float, float]] = None
        self._placement_theta_deg: float = 0.0
        self._placement_dragging: bool = False

        self.bind("<Configure>", self._on_resize)
        self._draw_background()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def update_from_dto(self, dto: SnapshotDTO) -> None:
        """
        Actualiza el canvas con el último SnapshotDTO del engine.
        Debe llamarse en el mainloop de Tkinter (seguro).
        """
        self._clear_robot()

        rx = dto.robot["x_mm"]
        ry = dto.robot["y_mm"]
        th = dto.robot["theta_deg"]

        # Rastro
        if self._show_trail:
            self._trail.append((rx, ry))
            if len(self._trail) > 600:
                self._trail = self._trail[-600:]
            if len(self._trail) > 2:
                self._draw_trail()

        # Dibujar robot
        self._draw_robot(rx, ry, th, dto.colliding)

    def set_obstacles(self, obstacles: list[dict]) -> None:
        """
        Establece la lista de obstáculos a dibujar.
        Cada obstáculo: {"x_mm": float, "y_mm": float,
                         "width_mm": float, "height_mm": float}.
        """
        self._obstacles = obstacles
        self._redraw_obstacles()

    def set_surface_cells(self, surface_cells: list[dict]) -> None:
        """
        Establece celdas de superficie a dibujar.
        Cada celda: {"x_mm": float, "y_mm": float, "size_mm": float, "color": str}.
        """
        self._surface_cells = surface_cells
        self._redraw_surface()

    def clear_trail(self) -> None:
        """Borra el rastro del robot."""
        self._trail.clear()
        self.delete("trail")

    def reset(self) -> None:
        """Limpia el canvas completamente y redibuja el fondo."""
        self.delete("all")
        self._trail.clear()
        self._robot_items.clear()
        self._obstacle_items.clear()
        self._surface_items.clear()
        self._draw_background()
        self._redraw_surface()
        self._redraw_obstacles()

    # ------------------------------------------------------------------
    # Modo de colocación del robot (clic para elegir posición inicial)
    # ------------------------------------------------------------------

    def enable_placement_mode(self, callback=None, hover_callback=None) -> None:
        """
        Activa el modo de colocación: el cursor cambia a cruz y el usuario
        puede hacer clic para elegir la posición inicial del robot.

        Args:
            callback: función ``cb(x_mm, y_mm, theta_deg)`` llamada cuando
                      cambia la pose inicial confirmada.
            hover_callback: función ``cb(x_mm, y_mm)`` llamada al mover
                      el cursor sobre el canvas.
        """
        self._placement_mode = True
        self._placement_cb   = callback
        self._placement_hover_cb = hover_callback
        self._placement_dragging = False
        self.config(cursor="crosshair")
        self.bind("<Motion>",    self._on_placement_hover)
        self.bind("<Leave>",     self._on_placement_leave)
        self.bind("<Button-1>",  self._on_placement_click)
        self.bind("<B1-Motion>", self._on_placement_drag)
        self.bind("<ButtonRelease-1>", self._on_placement_release)
        self.bind("<MouseWheel>", self._on_placement_wheel)

    def disable_placement_mode(self) -> None:
        """Desactiva el modo de colocación y limpia los elementos visuales."""
        self._placement_mode = False
        self._placement_cb   = None
        self._placement_hover_cb = None
        self._placement_hover_pos = None
        self._placement_dragging = False
        self.config(cursor="")
        self.unbind("<Motion>")
        self.unbind("<Leave>")
        self.unbind("<Button-1>")
        self.unbind("<B1-Motion>")
        self.unbind("<ButtonRelease-1>")
        self.unbind("<MouseWheel>")
        self.delete("placement_ghost")

    def draw_placement_marker(
        self,
        x_mm: float,
        y_mm: float,
        theta_deg: float | None = None,
    ) -> None:
        """
        Dibuja el marcador de posición inicial fijada (naranja).
        Puede llamarse externamente para mostrar la posición por defecto.
        """
        self._placement_pos = (x_mm, y_mm)
        if theta_deg is not None:
            self._placement_theta_deg = self._normalize_theta(theta_deg)
        self._redraw_placement_marker()

    # ------------------------------------------------------------------
    # Eventos internos del modo de colocación
    # ------------------------------------------------------------------

    def _on_placement_hover(self, event) -> None:
        """Dibuja el contorno fantasma del robot siguiendo el ratón."""
        x_mm, y_mm = self._event_to_world(event)
        self._placement_hover_pos = (x_mm, y_mm)
        self._draw_placement_ghost(x_mm, y_mm, self._placement_theta_deg)
        if self._placement_hover_cb:
            self._placement_hover_cb(x_mm, y_mm)

    def _on_placement_leave(self, _event) -> None:
        self._placement_hover_pos = None
        self.delete("placement_ghost")

    def _on_placement_click(self, event) -> None:
        """Fija la posición inicial al hacer clic y avisa al callback."""
        x_mm, y_mm = self._event_to_world(event)
        self._placement_pos = (x_mm, y_mm)
        self._placement_dragging = True
        self._redraw_placement_marker()
        self._notify_placement_changed()

    def _on_placement_drag(self, event) -> None:
        """Ajusta el angulo inicial arrastrando desde la posicion fijada."""
        if self._placement_pos is None:
            return
        x_mm, y_mm = self._event_to_world(event)
        theta_deg = self._calculate_theta_deg(self._placement_pos, (x_mm, y_mm))
        if theta_deg is None:
            return
        self._placement_theta_deg = theta_deg
        self._redraw_placement_marker()
        self._notify_placement_changed()

    def _on_placement_release(self, _event) -> None:
        self._placement_dragging = False

    def _on_placement_wheel(self, event) -> None:
        """Permite un ajuste fino del angulo con la rueda del raton."""
        if self._placement_pos is None:
            return

        delta = getattr(event, "delta", 0)
        if delta == 0:
            wheel_num = getattr(event, "num", None)
            if wheel_num == 4:
                delta = 120
            elif wheel_num == 5:
                delta = -120
        if delta == 0:
            return

        step_deg = 5.0 if delta > 0 else -5.0
        self._placement_theta_deg = self._normalize_theta(
            self._placement_theta_deg + step_deg
        )
        self._redraw_placement_marker()
        self._notify_placement_changed()

    def _draw_placement_ghost(
        self,
        x_mm: float,
        y_mm: float,
        theta_deg: float,
    ) -> None:
        """Contorno punteado del robot mientras el ratón se mueve."""
        self.delete("placement_ghost")
        flat, cx, cy, hw, _hh = self._placement_outline(x_mm, y_mm, theta_deg)
        self.create_polygon(
            flat,
            outline=_PLACEMENT_GHOST,
            width=2,
            dash=(6, 4),
            fill="",
            tags="placement_ghost",
        )
        fx, fy = self._rotate_point(cx, cy, hw * 0.65, 0.0, theta_deg)
        self.create_line(
            cx, cy, fx, fy,
            fill=_PLACEMENT_GHOST, width=2, arrow=tk.LAST,
            tags="placement_ghost",
        )

    def _redraw_placement_marker(self) -> None:
        """Redibuja el marcador de posición seleccionada (naranja)."""
        self.delete("placement_marker")
        if self._placement_pos is None:
            return
        x_mm, y_mm = self._placement_pos
        px, py = self._mm_to_px(x_mm, y_mm)
        _, _, _, hw, _ = self._placement_outline(
            x_mm,
            y_mm,
            self._placement_theta_deg,
        )
        r = 9
        self.create_oval(
            px - r, py - r, px + r, py + r,
            fill=_PLACEMENT_MARKER, outline="#BF360C", width=2,
            tags="placement_marker",
        )
        ext = r * 1.7
        self.create_line(px - ext, py, px + ext, py,
                         fill="#BF360C", width=2, tags="placement_marker")
        self.create_line(px, py - ext, px, py + ext,
                         fill="#BF360C", width=2, tags="placement_marker")
        fx, fy = self._rotate_point(px, py, hw * 0.70, 0.0, self._placement_theta_deg)
        self.create_line(
            px, py, fx, fy,
            fill="#BF360C",
            width=3,
            arrow=tk.LAST,
            tags="placement_marker",
        )

    # ------------------------------------------------------------------
    # Dibujo interno
    # ------------------------------------------------------------------

    def _mm_to_px(self, x_mm: float, y_mm: float) -> tuple[float, float]:
        """Convierte coordenadas del mundo (mm) a píxeles del canvas."""
        sx, sy = self._get_transform()
        return x_mm * sx, y_mm * sy

    def _get_transform(self) -> tuple[float, float]:
        """Retorna (sx, sy) para ocupar todo el espacio disponible."""
        cw = self.winfo_width() or 400
        ch = self.winfo_height() or 400
        sx = cw / self._world_w
        sy = ch / self._world_h
        return sx, sy

    def _on_resize(self, _event) -> None:
        """Redibuja todas las capas al cambiar tamaño para evitar deformaciones."""
        self._draw_background()
        self._redraw_surface()
        self._redraw_obstacles()
        if self._show_trail:
            self._draw_trail()
        if self._placement_hover_pos is not None and self._placement_mode:
            self._draw_placement_ghost(
                self._placement_hover_pos[0],
                self._placement_hover_pos[1],
                self._placement_theta_deg,
            )
        self._redraw_placement_marker()

    def _event_to_world(self, event) -> tuple[float, float]:
        sx, sy = self._get_transform()
        x_mm = event.x / sx
        y_mm = event.y / sy
        x_mm = min(max(x_mm, 0.0), self._world_w)
        y_mm = min(max(y_mm, 0.0), self._world_h)
        return x_mm, y_mm

    def _notify_placement_changed(self) -> None:
        if self._placement_cb and self._placement_pos is not None:
            self._placement_cb(
                self._placement_pos[0],
                self._placement_pos[1],
                self._placement_theta_deg,
            )

    def _placement_outline(
        self,
        x_mm: float,
        y_mm: float,
        theta_deg: float,
    ) -> tuple[list[float], float, float, float, float]:
        sx, sy = self._get_transform()
        hw = (_ROBOT_W_MM / 2) * sx
        hh = (_ROBOT_H_MM / 2) * sy
        cx, cy = self._mm_to_px(x_mm, y_mm)
        corners_local = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        corners_world = [
            self._rotate_point(cx, cy, lx, ly, theta_deg)
            for lx, ly in corners_local
        ]
        flat = [coord for point in corners_world for coord in point]
        return flat, cx, cy, hw, hh

    @staticmethod
    def _rotate_point(
        cx: float,
        cy: float,
        lx: float,
        ly: float,
        theta_deg: float,
    ) -> tuple[float, float]:
        th_rad = math.radians(theta_deg)
        cos_t = math.cos(th_rad)
        sin_t = math.sin(th_rad)
        return (
            cx + lx * cos_t - ly * sin_t,
            cy + lx * sin_t + ly * cos_t,
        )

    @staticmethod
    def _calculate_theta_deg(
        origin: tuple[float, float],
        target: tuple[float, float],
    ) -> float | None:
        dx = target[0] - origin[0]
        dy = target[1] - origin[1]
        if abs(dx) < 1e-9 and abs(dy) < 1e-9:
            return None
        return WorldCanvas._normalize_theta(math.degrees(math.atan2(dy, dx)))

    @staticmethod
    def _normalize_theta(theta_deg: float) -> float:
        return ((theta_deg + 180.0) % 360.0) - 180.0

    def _draw_background(self) -> None:
        """Dibuja el fondo y la cuadrícula."""
        self.delete("bg")
        cw = self.winfo_width() or 400
        ch = self.winfo_height() or 400
        self.create_rectangle(0, 0, cw, ch, fill=_BG, outline="", tags="bg")

        # Cuadrícula cada 200 mm ocupando todo el canvas
        step_mm = 200.0
        steps_x = int(self._world_w / step_mm)
        steps_h = int(self._world_h / step_mm)
        for i in range(1, steps_x):
            px, _ = self._mm_to_px(i * step_mm, 0)
            self.create_line(px, 0, px, ch, fill=_GRID, tags="bg")
        for j in range(1, steps_h):
            _, py = self._mm_to_px(0, j * step_mm)
            self.create_line(0, py, cw, py, fill=_GRID, tags="bg")

    def _draw_trail(self) -> None:
        self.delete("trail")
        if len(self._trail) >= 2:
            trail_px = [self._mm_to_px(x_mm, y_mm) for (x_mm, y_mm) in self._trail]
            flat = [c for pt in trail_px for c in pt]
            self.create_line(*flat, fill=_TRAIL, width=2, tags="trail",
                             smooth=True)

    def _clear_robot(self) -> None:
        for item in self._robot_items:
            self.delete(item)
        self._robot_items.clear()

    def _draw_robot(
        self,
        x_mm: float, y_mm: float, theta_deg: float,
        colliding: bool,
    ) -> None:
        """Dibuja un robot estilo EV3 (cuerpo, ruedas, sensor frontal)."""
        sx, sy = self._get_transform()

        hw = (_ROBOT_W_MM / 2) * sx
        hh = (_ROBOT_H_MM / 2) * sy

        # Vértices del rectángulo en coordenadas locales (sin rotar)
        corners_local = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]

        # Rotar y trasladar
        th_rad = math.radians(theta_deg)
        cos_t, sin_t = math.cos(th_rad), math.sin(th_rad)
        cx, cy = self._mm_to_px(x_mm, y_mm)

        def rot(lx, ly):
            return cx + lx * cos_t - ly * sin_t, cy + lx * sin_t + ly * cos_t

        corners_world = [rot(lx, ly) for lx, ly in corners_local]
        flat = [c for pt in corners_world for c in pt]
        outline_color = _ROBOT_COLLISION if colliding else _ROBOT_OUTLINE

        body = self.create_polygon(
            flat,
            fill=_ROBOT_BODY,
            outline=outline_color,
            width=3,
        )

        # Placa superior (interna)
        top_hw = hw * 0.62
        top_hh = hh * 0.58
        top_local = [
            (-top_hw, -top_hh),
            (top_hw, -top_hh),
            (top_hw, top_hh),
            (-top_hw, top_hh),
        ]
        top_world = [rot(lx, ly) for lx, ly in top_local]
        top_flat = [c for pt in top_world for c in pt]
        top_plate = self.create_polygon(
            top_flat,
            fill=_ROBOT_BODY_TOP,
            outline=outline_color,
            width=2,
        )

        # Módulo pantalla (como en EV3 real, lateral frontal)
        screen_mod_w = hw * 0.55
        screen_mod_h = hh * 0.92
        screen_mod_x = -hw * 0.72
        screen_mod_y = 0.0
        screen_mod_local = [
            (screen_mod_x - screen_mod_w / 2, screen_mod_y - screen_mod_h / 2),
            (screen_mod_x + screen_mod_w / 2, screen_mod_y - screen_mod_h / 2),
            (screen_mod_x + screen_mod_w / 2, screen_mod_y + screen_mod_h / 2),
            (screen_mod_x - screen_mod_w / 2, screen_mod_y + screen_mod_h / 2),
        ]
        screen_mod_world = [rot(lx, ly) for lx, ly in screen_mod_local]
        screen_mod = self.create_polygon(
            [c for pt in screen_mod_world for c in pt],
            fill=_ROBOT_SCREEN_FRAME,
            outline=outline_color,
            width=2,
        )

        glass_w = screen_mod_w * 0.72
        glass_h = screen_mod_h * 0.70
        glass_local = [
            (screen_mod_x - glass_w / 2, -glass_h / 2),
            (screen_mod_x + glass_w / 2, -glass_h / 2),
            (screen_mod_x + glass_w / 2, glass_h / 2),
            (screen_mod_x - glass_w / 2, glass_h / 2),
        ]
        glass_world = [rot(lx, ly) for lx, ly in glass_local]
        screen_glass = self.create_polygon(
            [c for pt in glass_world for c in pt],
            fill=_ROBOT_SCREEN_GLASS,
            outline="#3A3F46",
            width=1,
        )

        # Cruceta/botones centrales EV3
        pad_w = hw * 0.50
        pad_h = hh * 0.42
        pad_x = hw * 0.05
        pad_y = 0.0
        hbar = [
            (pad_x - pad_w / 2, pad_y - pad_h / 6),
            (pad_x + pad_w / 2, pad_y - pad_h / 6),
            (pad_x + pad_w / 2, pad_y + pad_h / 6),
            (pad_x - pad_w / 2, pad_y + pad_h / 6),
        ]
        vbar = [
            (pad_x - pad_w / 6, pad_y - pad_h / 2),
            (pad_x + pad_w / 6, pad_y - pad_h / 2),
            (pad_x + pad_w / 6, pad_y + pad_h / 2),
            (pad_x - pad_w / 6, pad_y + pad_h / 2),
        ]
        dpad_h = self.create_polygon(
            [c for pt in [rot(lx, ly) for lx, ly in hbar] for c in pt],
            fill=_ROBOT_DPAD,
            outline=outline_color,
            width=1,
        )
        dpad_v = self.create_polygon(
            [c for pt in [rot(lx, ly) for lx, ly in vbar] for c in pt],
            fill=_ROBOT_DPAD,
            outline=outline_color,
            width=1,
        )

        btn_center = rot(pad_x, pad_y)
        btn_r = max(3.0, min(hw, hh) * 0.10)
        button = self.create_oval(
            btn_center[0] - btn_r,
            btn_center[1] - btn_r,
            btn_center[0] + btn_r,
            btn_center[1] + btn_r,
            fill=_ROBOT_BUTTON,
            outline=outline_color,
            width=1,
        )

        # Franja lateral derecha con puertos rojos
        strip_w = hw * 0.24
        strip_h = hh * 1.05
        strip_x = hw * 0.80
        strip_local = [
            (strip_x - strip_w / 2, -strip_h / 2),
            (strip_x + strip_w / 2, -strip_h / 2),
            (strip_x + strip_w / 2, strip_h / 2),
            (strip_x - strip_w / 2, strip_h / 2),
        ]
        strip_world = [rot(lx, ly) for lx, ly in strip_local]
        side_strip = self.create_polygon(
            [c for pt in strip_world for c in pt],
            fill=_ROBOT_STRIP,
            outline=outline_color,
            width=1,
        )

        port_r = max(2.0, strip_w * 0.23)
        port1_c = rot(strip_x + strip_w * 0.20, -strip_h * 0.18)
        port2_c = rot(strip_x + strip_w * 0.20, strip_h * 0.18)
        port1 = self.create_oval(
            port1_c[0] - port_r,
            port1_c[1] - port_r,
            port1_c[0] + port_r,
            port1_c[1] + port_r,
            fill=_ROBOT_PORT_RED,
            outline="",
        )
        port2 = self.create_oval(
            port2_c[0] - port_r,
            port2_c[1] - port_r,
            port2_c[0] + port_r,
            port2_c[1] + port_r,
            fill=_ROBOT_PORT_RED,
            outline="",
        )

        # Ruedas laterales reales: arriba/abajo respecto al cuerpo (eje Y local)
        wheel_len = hw * 1.05
        wheel_thickness = max(6.0, hh * 0.22)
        wheel_offset_y = hh + (wheel_thickness * 0.48)

        def wheel_polygon(local_y: float) -> list[float]:
            poly_local = [
                (-wheel_len / 2, local_y - wheel_thickness / 2),
                (wheel_len / 2, local_y - wheel_thickness / 2),
                (wheel_len / 2, local_y + wheel_thickness / 2),
                (-wheel_len / 2, local_y + wheel_thickness / 2),
            ]
            poly_world = [rot(lx, ly) for lx, ly in poly_local]
            return [c for pt in poly_world for c in pt]

        left_wheel = self.create_polygon(
            wheel_polygon(-wheel_offset_y),
            fill=_ROBOT_WHEEL,
            outline="#111111",
            width=1,
        )
        right_wheel = self.create_polygon(
            wheel_polygon(wheel_offset_y),
            fill=_ROBOT_WHEEL,
            outline="#111111",
            width=1,
        )

        # Barra de sensor frontal + dos "ojos"
        sensor_w = hw * 0.42
        sensor_h = max(4.0, hh * 0.20)
        sensor_center_x = hw * 0.78
        sensor_local = [
            (sensor_center_x - sensor_w / 2, -sensor_h / 2),
            (sensor_center_x + sensor_w / 2, -sensor_h / 2),
            (sensor_center_x + sensor_w / 2, sensor_h / 2),
            (sensor_center_x - sensor_w / 2, sensor_h / 2),
        ]
        sensor_world = [rot(lx, ly) for lx, ly in sensor_local]
        sensor_flat = [c for pt in sensor_world for c in pt]
        sensor_bar = self.create_polygon(
            sensor_flat,
            fill=_ROBOT_SENSOR,
            outline=outline_color,
            width=1,
        )

        eye_r = max(2.0, sensor_h * 0.22)
        eye1_c = rot(sensor_center_x, -sensor_h * 0.22)
        eye2_c = rot(sensor_center_x, sensor_h * 0.22)
        eye1 = self.create_oval(
            eye1_c[0] - eye_r,
            eye1_c[1] - eye_r,
            eye1_c[0] + eye_r,
            eye1_c[1] + eye_r,
            fill=_ROBOT_SENSOR_EYE,
            outline="",
        )
        eye2 = self.create_oval(
            eye2_c[0] - eye_r,
            eye2_c[1] - eye_r,
            eye2_c[0] + eye_r,
            eye2_c[1] + eye_r,
            fill=_ROBOT_SENSOR_EYE,
            outline="",
        )

        # Flecha de heading (desde centro hacia frente)
        arrow_len = min(hw, hh) * 0.9
        fx, fy = rot(arrow_len, 0)
        arrow = self.create_line(cx, cy, fx, fy, fill=_HEADING, width=2,
                                 arrow=tk.LAST, arrowshape=(10, 12, 4))

        self._robot_items = [
            left_wheel,
            right_wheel,
            body,
            top_plate,
            screen_mod,
            screen_glass,
            dpad_h,
            dpad_v,
            button,
            side_strip,
            port1,
            port2,
            sensor_bar,
            eye1,
            eye2,
            arrow,
        ]

    def _redraw_obstacles(self) -> None:
        for item in self._obstacle_items:
            self.delete(item)
        self._obstacle_items.clear()

        for obs in self._obstacles:
            x1, y1 = self._mm_to_px(obs["x_mm"], obs["y_mm"])
            x2, y2 = self._mm_to_px(
                obs["x_mm"] + obs["width_mm"],
                obs["y_mm"] + obs["height_mm"],
            )
            item = self.create_rectangle(
                x1, y1, x2, y2, fill=_OBSTACLE, outline="#555555"
            )
            self._obstacle_items.append(item)

    def _redraw_surface(self) -> None:
        for item in self._surface_items:
            self.delete(item)
        self._surface_items.clear()

        for cell in self._surface_cells:
            x_mm = cell["x_mm"]
            y_mm = cell["y_mm"]
            size = cell.get("size_mm", 50.0)
            color_name = str(cell.get("color", "BLACK")).upper()

            if color_name == "BLACK":
                fill = _SURFACE_BLACK
            else:
                continue

            x1, y1 = self._mm_to_px(x_mm, y_mm)
            x2, y2 = self._mm_to_px(x_mm + size, y_mm + size)
            item = self.create_rectangle(
                x1, y1, x2, y2,
                fill=fill,
                outline="",
            )
            self._surface_items.append(item)
