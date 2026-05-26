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
import os
import tkinter as tk
from typing import Callable, Optional

from simulador_ev3.application.snapshot_dto import SnapshotDTO
from simulador_ev3.domain.editor.world_editor_model import (
    CELL_SIZE_MM,
    GRID_SIZE_PX,
    get_asset_spec,
    normalize_asset_key,
)
from simulador_ev3.shared.paths import resolve_image_assets_dir
from simulador_ev3.shared.ui_settings import UI_FIT_PADDING_RATIO


# Colores del canvas
_BG           = "#F0F0F0"
_OBSTACLE     = "#37474F"
_OBSTACLE_OUTLINE = "#102027"
_HEADING      = "#1565C0"     # flecha de dirección
_TRAIL        = "#90CAF9"     # rastro opcional
_GRID         = "#CCCCCC"
_SURFACE_BLACK = "#1A1A1A"
_SURFACE_WHITE = "#F5F5F5"
_SURFACE_RED   = "#E53935"
_SURFACE_GREEN = "#43A047"
_SURFACE_BLUE  = "#1E88E5"
_SURFACE_YELLOW = "#FDD835"
_SURFACE_BROWN = "#8D6E63"
_WALL_STYLE = {
    "wall_64x64_a": ("#37474F", "#102027"),
    "wall_64x64_b": ("#455A64", "#263238"),
    "wall_64x64_c": ("#263238", "#11171A"),
}
_PX_PER_MM = GRID_SIZE_PX / CELL_SIZE_MM

_IMAGE_ASSETS_DIR = resolve_image_assets_dir()

_ROBOT_SPRITE_PATH = os.path.join(
    str(_IMAGE_ASSETS_DIR),
    "robot_ev3_32x32.png",
)
_ASSET_IMAGES_DIR = os.path.join(
    str(_IMAGE_ASSETS_DIR),
)
_ASSET_IMAGE_OVERRIDES: dict[str, list[str]] = {
    "line_64x64_cruz": ["line_64X64_Cruz.png"],
    "line_64_64_hor": ["line_64_64_Hor.png"],
    "line_64_64_ver": ["line_64_64_Ver.png"],
    "line_64_64_infder": ["line_64_64_InfDer.png"],
    "line_64_64_infizq": ["line_64_64_InfIzq.png"],
    "line_64_64_supder": ["line_64_64_SupDer.png"],
    "line_64_64_supizq": ["line_64_64_SupIzq.png"],
    "floor_tile_256_c": ["floor_tile_256_c.jpg", "floor_tile_256_b.png"],
}
_ASSET_LAYER_ORDER = {
    "floor": 0,
    "zone": 1,
    "line": 2,
    "wall": 3,
    "robot": 4,
}
_ROBOT_WIDTH_MM = 110.0
_ROBOT_HEIGHT_MM = 70.0
_FRONT_SENSOR_OFFSET_MM = 70.0
_ULTRASONIC_MAX_MM = 2500.0
_IR_MAX_MM = 700.0
_ROBOT_DRAW_W_PX = max(1, int(round(_ROBOT_WIDTH_MM * _PX_PER_MM)))
_ROBOT_DRAW_H_PX = max(1, int(round(_ROBOT_HEIGHT_MM * _PX_PER_MM)))
_ROBOT_ROT_STEP_DEG = 2
_COLOR_SENSOR_OFFSET_MM = 60.0
_COLOR_SENSOR_MARKER_OUTLINE = "#FFB300"

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

# Tamano por defecto del visor cuando no llega un mundo explicito: 4 m x 4 m.
_DEFAULT_WORLD_W = 4000.0
_DEFAULT_WORLD_H = 4000.0

# Tamaño visual del robot: cerebro EV3 a escala real, 11 cm x 7 cm.
_ROBOT_W_MM = _ROBOT_WIDTH_MM
_ROBOT_H_MM = _ROBOT_HEIGHT_MM

_MIN_ZOOM_FACTOR = 0.5
_MAX_ZOOM_FACTOR = 3.0
_ZOOM_STEP = 0.15
_FIT_PADDING_RATIO = UI_FIT_PADDING_RATIO

# Colores del modo de colocación
_PLACEMENT_GHOST  = "#4FC3F7"   # contorno fantasma al mover el ratón
_PLACEMENT_MARKER = "#FF6F00"   # marcador de posición seleccionada
_FOLLOW_EDGE_MARGIN_RATIO = 0.45


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
        self._zoom_factor = 1.0
        self._px_per_mm = _PX_PER_MM
        self._follow_robot = True
        self._show_editor_robot_asset = True
        self._show_sensor_beams = True
        self._follow_pad_x_px = 0.0
        self._follow_pad_y_px = 0.0

        # Lista de posiciones (x_mm, y_mm) del rastro
        self._trail: list[tuple[float, float]] = []
        self._obstacles: list[dict] = []  # {x, y, w, h} en mm
        self._surface_cells: list[dict] = []  # {x_mm, y_mm, size_mm, color}
        self._editor_placements: list[dict] = []

        # Handles de items del canvas (para actualizar en lugar de recrear)
        self._robot_items: list[int] = []
        self._obstacle_items: list[int] = []
        self._surface_items: list[int] = []
        self._asset_items: list[int] = []
        self._robot_sprite_base: Optional[tk.PhotoImage] = None
        self._robot_sprite: Optional[tk.PhotoImage] = None
        self._robot_sprite_rot_cache: dict[int, tk.PhotoImage] = {}
        self._asset_image_lookup = self._build_asset_image_lookup()
        self._asset_base_images: dict[str, tk.PhotoImage] = {}
        self._asset_image_cache: dict[tuple[str, int, int, int], tk.PhotoImage] = {}

        # Estado del modo de colocación del robot
        self._placement_mode: bool = False
        self._placement_cb: Optional[Callable[[float, float, float], None]] = None
        self._placement_hover_cb: Optional[Callable[[float, float], None]] = None
        self._placement_pos: Optional[tuple[float, float]] = None
        self._placement_hover_pos: Optional[tuple[float, float]] = None
        self._placement_theta_deg: float = 0.0
        self._placement_dragging: bool = False

        self.bind("<Configure>", self._on_resize)
        self._update_scrollregion()
        self._load_robot_sprite()
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
        color_sensor_reflection = self._extract_color_sensor_reflection(dto)

        # Rastro
        if self._show_trail:
            self._trail.append((rx, ry))
            if len(self._trail) > 600:
                self._trail = self._trail[-600:]
            if len(self._trail) > 2:
                self._draw_trail()

        if self._show_sensor_beams:
            self._draw_sensor_beams(dto, rx, ry, th)

        # Dibujar robot
        self._draw_robot(rx, ry, th, dto.colliding, color_sensor_reflection)
        if self._follow_robot:
            self._center_view_on_mm(rx, ry)

    def set_obstacles(self, obstacles: list[dict]) -> None:
        """
        Establece la lista de obstáculos a dibujar.
        Cada obstáculo: {"x_mm": float, "y_mm": float,
                         "width_mm": float, "height_mm": float}.
        """
        self._obstacles = obstacles
        self._redraw_obstacles()

    def set_world_size_mm(self, width_mm: float, height_mm: float) -> None:
        self._world_w = max(100.0, float(width_mm))
        self._world_h = max(100.0, float(height_mm))
        self._update_scrollregion()
        self._draw_background()
        self._redraw_surface()
        self._redraw_obstacles()
        if self._show_trail:
            self._draw_trail()
        self._redraw_placement_marker()

    def set_robot_follow_enabled(self, enabled: bool) -> None:
        self._follow_robot = bool(enabled)

    def set_sensor_beams_enabled(self, enabled: bool) -> None:
        self._show_sensor_beams = bool(enabled)

    def zoom_in(self) -> float:
        return self._set_zoom_factor(self._zoom_factor + _ZOOM_STEP)

    def zoom_out(self) -> float:
        return self._set_zoom_factor(self._zoom_factor - _ZOOM_STEP)

    def reset_zoom(self) -> float:
        return self._set_zoom_factor(1.0)

    def fit_to_view(self) -> float:
        view_w_px = max(1.0, float(self.winfo_width() or 1))
        view_h_px = max(1.0, float(self.winfo_height() or 1))
        if view_w_px <= 1.0 or view_h_px <= 1.0:
            return self._zoom_factor

        world_w_mm = max(1.0, float(self._world_w))
        world_h_mm = max(1.0, float(self._world_h))
        usable_w_px = max(1.0, view_w_px * (1.0 - 2.0 * _FIT_PADDING_RATIO))
        usable_h_px = max(1.0, view_h_px * (1.0 - 2.0 * _FIT_PADDING_RATIO))
        zoom_x = usable_w_px / (world_w_mm * _PX_PER_MM)
        zoom_y = usable_h_px / (world_h_mm * _PX_PER_MM)
        applied = self._set_zoom_factor(min(zoom_x, zoom_y))
        self._center_view_on_mm(world_w_mm / 2.0, world_h_mm / 2.0)
        return applied

    def get_zoom_factor(self) -> float:
        return self._zoom_factor

    def set_surface_cells(self, surface_cells: list[dict]) -> None:
        """
        Establece celdas de superficie a dibujar.
        Cada celda: {"x_mm": float, "y_mm": float, "size_mm": float, "color": str}.
        """
        self._surface_cells = surface_cells
        self._redraw_surface()

    def set_editor_placements(self, placements: list[dict]) -> None:
        """
        Establece placements del editor para render visual fiel con sprites.
        Si la lista esta vacia, vuelve al render clasico por superficie/obstaculos.
        """
        self._editor_placements = list(placements)
        self._redraw_surface()
        self._redraw_obstacles()
        self._redraw_editor_assets()

    def set_editor_robot_visible(self, visible: bool) -> None:
        """Muestra/oculta el sprite de robot proveniente del editor."""
        new_value = bool(visible)
        if self._show_editor_robot_asset == new_value:
            return
        self._show_editor_robot_asset = new_value
        self._redraw_editor_assets()

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
        self._update_scrollregion()
        self._draw_background()
        self._redraw_surface()
        self._redraw_obstacles()
        self._redraw_editor_assets()

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
        fx, fy = self._rotate_point(px, py, hw * 1.68, 0.0, self._placement_theta_deg)
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
        return self._px_per_mm, self._px_per_mm

    def _get_origin(self) -> tuple[float, float]:
        return 0.0, 0.0

    def _on_resize(self, _event) -> None:
        """Redibuja todas las capas al cambiar tamaño para evitar deformaciones."""
        self._update_scrollregion()
        self._draw_background()
        self._redraw_surface()
        self._redraw_obstacles()
        self._redraw_editor_assets()
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
        x_px = self.canvasx(event.x)
        y_px = self.canvasy(event.y)
        x_mm = x_px / sx
        y_mm = y_px / sy
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
        world_w_px = self._world_w * self._px_per_mm
        world_h_px = self._world_h * self._px_per_mm
        self.create_rectangle(0, 0, world_w_px, world_h_px, fill=_BG, outline="", tags="bg")
        x0, y0 = self._mm_to_px(0.0, 0.0)
        x1, y1 = self._mm_to_px(self._world_w, self._world_h)
        self.create_rectangle(x0, y0, x1, y1, fill="", outline="#B0BEC5", tags="bg")

        step_mm = CELL_SIZE_MM
        steps_x = int(self._world_w / step_mm)
        steps_h = int(self._world_h / step_mm)
        for i in range(1, steps_x):
            px, _ = self._mm_to_px(i * step_mm, 0)
            self.create_line(px, y0, px, y1, fill=_GRID, tags="bg")
        for j in range(1, steps_h):
            _, py = self._mm_to_px(0, j * step_mm)
            self.create_line(x0, py, x1, py, fill=_GRID, tags="bg")

    def _draw_trail(self) -> None:
        self.delete("trail")
        if len(self._trail) >= 2:
            trail_px = [self._mm_to_px(x_mm, y_mm) for (x_mm, y_mm) in self._trail]
            flat = [c for pt in trail_px for c in pt]
            self.create_line(*flat, fill=_TRAIL, width=2, tags="trail",
                             smooth=True)

    def _load_robot_sprite(self) -> None:
        """Carga el sprite del robot y lo ajusta a 32x23 px."""
        try:
            img = tk.PhotoImage(file=_ROBOT_SPRITE_PATH)
        except Exception:  # noqa: BLE001
            self._robot_sprite_base = None
            self._robot_sprite = None
            return
        self._robot_sprite_base = img
        target_w, target_h = self._robot_draw_size_px()
        self._robot_sprite = self._resize_photoimage(
            img,
            target_w=target_w,
            target_h=target_h,
        )
        self._robot_sprite_rot_cache = {0: self._robot_sprite}

    def _robot_draw_size_px(self) -> tuple[int, int]:
        return (
            max(1, int(round(_ROBOT_WIDTH_MM * self._px_per_mm))),
            max(1, int(round(_ROBOT_HEIGHT_MM * self._px_per_mm))),
        )

    def _resize_photoimage(
        self,
        img: tk.PhotoImage,
        target_w: int,
        target_h: int,
    ) -> tk.PhotoImage:
        src_w_fn = getattr(img, "width", None)
        src_h_fn = getattr(img, "height", None)
        src_w = int(src_w_fn()) if callable(src_w_fn) else target_w
        src_h = int(src_h_fn()) if callable(src_h_fn) else target_h
        src_w = max(1, src_w)
        src_h = max(1, src_h)
        zoom_w = max(1, int(target_w))
        zoom_h = max(1, int(target_h))
        try:
            return img.zoom(zoom_w, zoom_h).subsample(src_w, src_h)
        except Exception:  # noqa: BLE001
            return img

    def _get_rotated_robot_sprite(self, theta_deg: float) -> Optional[tk.PhotoImage]:
        if self._robot_sprite is None:
            return None
        bucket = int(round(float(theta_deg) / _ROBOT_ROT_STEP_DEG) * _ROBOT_ROT_STEP_DEG) % 360
        cached = self._robot_sprite_rot_cache.get(bucket)
        if cached is not None:
            return cached
        rotated = self._rotate_photoimage(self._robot_sprite, bucket)
        self._robot_sprite_rot_cache[bucket] = rotated
        return rotated

    def _rotate_photoimage(self, src: tk.PhotoImage, angle_deg: int) -> tk.PhotoImage:
        """Rota una PhotoImage con nearest-neighbor (fallback sin dependencias)."""
        if angle_deg % 360 == 0:
            return src

        src_get = getattr(src, "get", None)
        if not callable(src_get):
            return src

        src_w_fn = getattr(src, "width", None)
        src_h_fn = getattr(src, "height", None)
        src_w = int(src_w_fn()) if callable(src_w_fn) else _ROBOT_DRAW_W_PX
        src_h = int(src_h_fn()) if callable(src_h_fn) else _ROBOT_DRAW_H_PX
        src_w = max(1, src_w)
        src_h = max(1, src_h)

        theta = math.radians(angle_deg)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        out_w = max(1, int(math.ceil(abs(src_w * cos_t) + abs(src_h * sin_t))))
        out_h = max(1, int(math.ceil(abs(src_w * sin_t) + abs(src_h * cos_t))))

        try:
            dst = tk.PhotoImage(width=out_w, height=out_h)
        except Exception:  # noqa: BLE001
            return src

        dst_put = getattr(dst, "put", None)
        if not callable(dst_put):
            return src

        src_transparency_get = getattr(src, "transparency_get", None)
        src_cx = (src_w - 1) / 2.0
        src_cy = (src_h - 1) / 2.0
        dst_cx = (out_w - 1) / 2.0
        dst_cy = (out_h - 1) / 2.0

        for y in range(out_h):
            for x in range(out_w):
                dx = x - dst_cx
                dy = y - dst_cy
                sx = dx * cos_t + dy * sin_t + src_cx
                sy = -dx * sin_t + dy * cos_t + src_cy
                ix = int(round(sx))
                iy = int(round(sy))
                if ix < 0 or iy < 0 or ix >= src_w or iy >= src_h:
                    continue
                if callable(src_transparency_get):
                    try:
                        if bool(src_transparency_get(ix, iy)):
                            continue
                    except Exception:  # noqa: BLE001
                        pass
                try:
                    color = src_get(ix, iy)
                    if isinstance(color, tuple) and len(color) >= 3:
                        color = f"#{int(color[0]):02x}{int(color[1]):02x}{int(color[2]):02x}"
                    dst_put(color, (x, y))
                except Exception:  # noqa: BLE001
                    continue
        return dst

    def _clear_robot(self) -> None:
        for item in self._robot_items:
            self.delete(item)
        self._robot_items.clear()

    def _draw_robot(
        self,
        x_mm: float, y_mm: float, theta_deg: float,
        colliding: bool,
        color_sensor_reflection: Optional[float] = None,
    ) -> None:
        if self._robot_sprite is not None:
            self._draw_robot_sprite(
                x_mm,
                y_mm,
                theta_deg,
                colliding,
                color_sensor_reflection=color_sensor_reflection,
            )
            return

        # Fallback vectorial si el sprite no se pudo cargar.
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
        sensor_marker = self._draw_color_sensor_marker(
            x_mm,
            y_mm,
            theta_deg,
            color_sensor_reflection,
        )

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
        if sensor_marker is not None:
            self._robot_items.append(sensor_marker)

    def _draw_robot_sprite(
        self,
        x_mm: float,
        y_mm: float,
        theta_deg: float,
        colliding: bool,
        color_sensor_reflection: Optional[float] = None,
    ) -> None:
        cx, cy = self._mm_to_px(x_mm, y_mm)
        sprite_image = self._get_rotated_robot_sprite(theta_deg) or self._robot_sprite
        draw_w_px, draw_h_px = self._robot_draw_size_px()
        sprite = self.create_image(cx, cy, image=sprite_image)

        th_rad = math.radians(theta_deg)
        arrow_len = max(draw_w_px, draw_h_px) * 0.95
        fx = cx + math.cos(th_rad) * arrow_len
        fy = cy + math.sin(th_rad) * arrow_len
        heading = self.create_line(
            cx,
            cy,
            fx,
            fy,
            fill=_ROBOT_COLLISION if colliding else _HEADING,
            width=2,
            arrow=tk.LAST,
            arrowshape=(9, 10, 4),
        )

        items = [sprite, heading]
        sensor_marker = self._draw_color_sensor_marker(
            x_mm,
            y_mm,
            theta_deg,
            color_sensor_reflection,
        )
        if sensor_marker is not None:
            items.append(sensor_marker)
        if colliding:
            border = self.create_rectangle(
                cx - draw_w_px / 2.0,
                cy - draw_h_px / 2.0,
                cx + draw_w_px / 2.0,
                cy + draw_h_px / 2.0,
                outline=_ROBOT_COLLISION,
                width=2,
            )
            items.append(border)
        self._robot_items = items

    def _draw_color_sensor_marker(
        self,
        robot_x_mm: float,
        robot_y_mm: float,
        theta_deg: float,
        reflection: Optional[float],
    ) -> Optional[int]:
        if reflection is None:
            return None
        theta_rad = math.radians(theta_deg)
        sx_mm = robot_x_mm + _COLOR_SENSOR_OFFSET_MM * math.cos(theta_rad)
        sy_mm = robot_y_mm + _COLOR_SENSOR_OFFSET_MM * math.sin(theta_rad)
        sx_px, sy_px = self._mm_to_px(sx_mm, sy_mm)
        color_fill = "#111111" if reflection < 50.0 else "#FAFAFA"
        return self.create_oval(
            sx_px - 4.0,
            sy_px - 4.0,
            sx_px + 4.0,
            sy_px + 4.0,
            fill=color_fill,
            outline=_COLOR_SENSOR_MARKER_OUTLINE,
            width=1,
        )

    def _draw_sensor_beams(self, dto: SnapshotDTO, rx: float, ry: float, theta_deg: float) -> None:
        sensors = getattr(dto, "sensors", []) or []
        if not isinstance(sensors, list):
            return

        theta_rad = math.radians(theta_deg)
        sx_mm = rx + math.cos(theta_rad) * _FRONT_SENSOR_OFFSET_MM
        sy_mm = ry + math.sin(theta_rad) * _FRONT_SENSOR_OFFSET_MM
        sx_px, sy_px = self._mm_to_px(sx_mm, sy_mm)

        for sensor in sensors:
            if not isinstance(sensor, dict):
                continue
            sensor_type = str(sensor.get("type", "")).lower()
            data = sensor.get("data")
            if not isinstance(data, dict):
                data = {}

            if "ultrasonic" in sensor_type:
                distance_mm = float(data.get("distance_mm", _ULTRASONIC_MAX_MM) or _ULTRASONIC_MAX_MM)
                distance_mm = max(0.0, min(_ULTRASONIC_MAX_MM, distance_mm))
                self._draw_sensor_cone(
                    sx_px,
                    sy_px,
                    theta_rad,
                    distance_mm if distance_mm > 0 else _ULTRASONIC_MAX_MM,
                    half_angle_deg=12.0,
                    fill="#B2EBF2",
                    outline="#00ACC1",
                )
            elif "infrared" in sensor_type:
                proximity = float(data.get("proximity", 100) or 100)
                proximity = max(0.0, min(100.0, proximity))
                distance_mm = (proximity / 100.0) * _IR_MAX_MM
                self._draw_sensor_cone(
                    sx_px,
                    sy_px,
                    theta_rad,
                    distance_mm if distance_mm > 0 else _IR_MAX_MM,
                    half_angle_deg=8.0,
                    fill="#FFE0B2",
                    outline="#FB8C00",
                )

    def _draw_sensor_cone(
        self,
        sx_px: float,
        sy_px: float,
        theta_rad: float,
        distance_mm: float,
        *,
        half_angle_deg: float,
        fill: str,
        outline: str,
    ) -> None:
        scale_x, scale_y = self._get_transform()
        distance_px = distance_mm * ((scale_x + scale_y) / 2.0)
        half = math.radians(half_angle_deg)

        left_x = sx_px + math.cos(theta_rad - half) * distance_px
        left_y = sy_px + math.sin(theta_rad - half) * distance_px
        right_x = sx_px + math.cos(theta_rad + half) * distance_px
        right_y = sy_px + math.sin(theta_rad + half) * distance_px
        front_x = sx_px + math.cos(theta_rad) * distance_px
        front_y = sy_px + math.sin(theta_rad) * distance_px

        cone = self.create_polygon(
            sx_px,
            sy_px,
            left_x,
            left_y,
            right_x,
            right_y,
            fill=fill,
            outline=outline,
            width=1,
        )
        ray = self.create_line(
            sx_px,
            sy_px,
            front_x,
            front_y,
            fill=outline,
            width=2,
        )
        self._robot_items.extend([cone, ray])

    @staticmethod
    def _extract_color_sensor_reflection(dto: SnapshotDTO) -> Optional[float]:
        sensors = getattr(dto, "sensors", [])
        for sensor in sensors:
            if not isinstance(sensor, dict):
                continue
            sensor_type = str(sensor.get("type", "")).lower()
            if "colorsensor" not in sensor_type and "color_sensor" not in sensor_type:
                continue
            data = sensor.get("data")
            if isinstance(data, dict):
                reflection = data.get("reflectance")
                if isinstance(reflection, (int, float)):
                    return float(reflection)
            value = sensor.get("value")
            if isinstance(value, dict):
                reflection = value.get("reflectance")
                if isinstance(reflection, (int, float)):
                    return float(reflection)
        return None

    def _redraw_obstacles(self) -> None:
        for item in self._obstacle_items:
            self.delete(item)
        self._obstacle_items.clear()
        if self._editor_placements:
            return

        for obs in self._obstacles:
            x1, y1 = self._mm_to_px(obs["x_mm"], obs["y_mm"])
            x2, y2 = self._mm_to_px(
                obs["x_mm"] + obs["width_mm"],
                obs["y_mm"] + obs["height_mm"],
            )
            fill, outline = _obstacle_style_from_name(str(obs.get("name", "")))
            item = self.create_rectangle(
                x1, y1, x2, y2, fill=fill, outline=outline
            )
            self._obstacle_items.append(item)

    def _redraw_surface(self) -> None:
        for item in self._surface_items:
            self.delete(item)
        self._surface_items.clear()
        if self._editor_placements:
            return

        surface_fill = {
            "BLACK": _SURFACE_BLACK,
            "WHITE": _SURFACE_WHITE,
            "RED": _SURFACE_RED,
            "GREEN": _SURFACE_GREEN,
            "BLUE": _SURFACE_BLUE,
            "YELLOW": _SURFACE_YELLOW,
            "BROWN": _SURFACE_BROWN,
        }

        for cell in self._surface_cells:
            x_mm = cell["x_mm"]
            y_mm = cell["y_mm"]
            size = cell.get("size_mm", 50.0)
            color_name = str(cell.get("color", "BLACK")).upper()

            fill = surface_fill.get(color_name)
            if fill is None:
                continue

            x1, y1 = self._mm_to_px(x_mm, y_mm)
            x2, y2 = self._mm_to_px(x_mm + size, y_mm + size)
            outline = ""
            if color_name == "WHITE":
                outline = "#E0E0E0"
            item = self.create_rectangle(
                x1, y1, x2, y2,
                fill=fill,
                outline=outline,
            )
            self._surface_items.append(item)

    def _redraw_editor_assets(self) -> None:
        for item in self._asset_items:
            self.delete(item)
        self._asset_items.clear()
        if not self._editor_placements:
            return

        sorted_placements = sorted(
            self._editor_placements,
            key=self._editor_asset_sort_key,
        )
        for placement in sorted_placements:
            asset_key = normalize_asset_key(str(placement.get("asset_key", "")))
            spec = get_asset_spec(asset_key)
            if spec is None:
                continue
            if spec.asset_type == "robot" and not self._show_editor_robot_asset:
                continue

            rotation = int(placement.get("rotation", 0))
            width_cells = spec.width_cells
            height_cells = spec.height_cells
            if rotation % 180 == 90:
                width_cells, height_cells = height_cells, width_cells

            x_px = int(placement.get("x_px", placement.get("x", 0)))
            y_px = int(placement.get("y_px", placement.get("y", 0)))
            x_mm = x_px / GRID_SIZE_PX * CELL_SIZE_MM
            y_mm = y_px / GRID_SIZE_PX * CELL_SIZE_MM
            w_mm = width_cells * CELL_SIZE_MM
            h_mm = height_cells * CELL_SIZE_MM
            px0, py0 = self._mm_to_px(x_mm, y_mm)
            px1, py1 = self._mm_to_px(x_mm + w_mm, y_mm + h_mm)

            draw_w = max(1, int(round(px1 - px0)))
            draw_h = max(1, int(round(py1 - py0)))
            image = self._get_asset_image(asset_key, rotation, draw_w, draw_h)
            if image is not None:
                cx = (px0 + px1) / 2.0
                cy = (py0 + py1) / 2.0
                self._asset_items.append(self.create_image(cx, cy, image=image))
                continue

            if spec.asset_type == "floor":
                self._asset_items.append(
                    self.create_rectangle(px0, py0, px1, py1, fill="#D7CCC8", outline="#BCAAA4", width=1)
                )
            elif spec.asset_type == "zone":
                fill = "#ECEFF1"
                outline = "#B0BEC5"
                if "red" in asset_key:
                    fill, outline = "#EF5350", "#C62828"
                elif "green" in asset_key:
                    fill, outline = "#66BB6A", "#2E7D32"
                self._asset_items.append(
                    self.create_rectangle(px0, py0, px1, py1, fill=fill, outline=outline, width=2)
                )
            elif spec.asset_type in {"line", "wall"}:
                fill, outline = ("#111111", "") if spec.asset_type == "line" else ("#37474F", "#102027")
                self._asset_items.append(
                    self.create_rectangle(px0, py0, px1, py1, fill=fill, outline=outline, width=1)
                )

    def _editor_asset_sort_key(self, placement: dict) -> tuple[int, int, int]:
        asset_key = normalize_asset_key(str(placement.get("asset_key", "")))
        spec = get_asset_spec(asset_key)
        layer = spec.layer if spec is not None else "robot"
        y_px = int(placement.get("y_px", placement.get("y", 0)))
        x_px = int(placement.get("x_px", placement.get("x", 0)))
        return (_ASSET_LAYER_ORDER.get(layer, 4), y_px, x_px)

    def _build_asset_image_lookup(self) -> dict[str, str]:
        lookup: dict[str, str] = {}
        if not os.path.isdir(_ASSET_IMAGES_DIR):
            return lookup
        for name in os.listdir(_ASSET_IMAGES_DIR):
            full_path = os.path.join(_ASSET_IMAGES_DIR, name)
            lookup[name.lower()] = full_path
        return lookup

    def _resolve_asset_image_paths(self, asset_key: str) -> list[str]:
        key = normalize_asset_key(asset_key)
        candidates = list(_ASSET_IMAGE_OVERRIDES.get(key, []))
        candidates.extend([f"{key}.png", f"{key}.jpg", f"{key}.jpeg"])
        resolved: list[str] = []
        for candidate in candidates:
            hit = self._asset_image_lookup.get(candidate.lower())
            if hit:
                resolved.append(hit)
        return resolved

    def _load_asset_base_image(self, asset_key: str) -> Optional[tk.PhotoImage]:
        key = normalize_asset_key(asset_key)
        cached = self._asset_base_images.get(key)
        if cached is not None:
            return cached
        for path in self._resolve_asset_image_paths(key):
            try:
                image = tk.PhotoImage(file=path)
            except Exception:  # noqa: BLE001
                continue
            self._asset_base_images[key] = image
            return image
        return None

    def _get_asset_image(
        self,
        asset_key: str,
        rotation_deg: int,
        target_w: int,
        target_h: int,
    ) -> Optional[tk.PhotoImage]:
        key = normalize_asset_key(asset_key)
        rot = int(round(int(rotation_deg) / 90.0) * 90) % 360
        cache_key = (key, rot, int(target_w), int(target_h))
        cached = self._asset_image_cache.get(cache_key)
        if cached is not None:
            return cached

        base = self._load_asset_base_image(key)
        if base is None:
            return None

        out = self._resize_photoimage(base, target_w=max(1, target_w), target_h=max(1, target_h))
        if rot % 360:
            out = self._rotate_photoimage(out, rot)
        self._asset_image_cache[cache_key] = out
        return out

    def _update_scrollregion(self) -> None:
        world_w_px = int(round(self._world_w * self._px_per_mm))
        world_h_px = int(round(self._world_h * self._px_per_mm))
        view_w_px = max(1.0, float(self.winfo_width() or 1))
        view_h_px = max(1.0, float(self.winfo_height() or 1))
        self._follow_pad_x_px = (
            view_w_px * _FOLLOW_EDGE_MARGIN_RATIO if world_w_px > view_w_px else 0.0
        )
        self._follow_pad_y_px = (
            view_h_px * _FOLLOW_EDGE_MARGIN_RATIO if world_h_px > view_h_px else 0.0
        )
        self.configure(
            scrollregion=(
                -self._follow_pad_x_px,
                -self._follow_pad_y_px,
                world_w_px + self._follow_pad_x_px,
                world_h_px + self._follow_pad_y_px,
            )
        )

    def _set_zoom_factor(self, zoom_factor: float) -> float:
        clamped = min(max(float(zoom_factor), _MIN_ZOOM_FACTOR), _MAX_ZOOM_FACTOR)
        if abs(clamped - self._zoom_factor) < 1e-9:
            return self._zoom_factor

        center_world = self._viewport_center_mm()
        self._zoom_factor = clamped
        self._px_per_mm = _PX_PER_MM * self._zoom_factor
        self._asset_image_cache.clear()
        self._load_robot_sprite()
        self._update_scrollregion()
        self._draw_background()
        self._redraw_surface()
        self._redraw_obstacles()
        self._redraw_editor_assets()
        if self._show_trail:
            self._draw_trail()
        self._redraw_placement_marker()
        if center_world is not None:
            self._center_view_on_mm(center_world[0], center_world[1])
        return self._zoom_factor

    def _viewport_center_mm(self) -> Optional[tuple[float, float]]:
        sx, sy = self._get_transform()
        if sx <= 0 or sy <= 0:
            return None

        view_w_px = max(1.0, float(self.winfo_width() or 1))
        view_h_px = max(1.0, float(self.winfo_height() or 1))
        center_x_px = self.canvasx(view_w_px / 2.0)
        center_y_px = self.canvasy(view_h_px / 2.0)
        x_mm = min(max(center_x_px / sx, 0.0), self._world_w)
        y_mm = min(max(center_y_px / sy, 0.0), self._world_h)
        return x_mm, y_mm

    def _center_view_on_mm(self, x_mm: float, y_mm: float) -> None:
        world_w_px = max(1.0, self._world_w * self._px_per_mm)
        world_h_px = max(1.0, self._world_h * self._px_per_mm)
        total_w_px = world_w_px + 2.0 * self._follow_pad_x_px
        total_h_px = world_h_px + 2.0 * self._follow_pad_y_px
        view_w_px = max(1.0, float(self.winfo_width() or 1))
        view_h_px = max(1.0, float(self.winfo_height() or 1))

        center_x_px = x_mm * self._px_per_mm + self._follow_pad_x_px
        center_y_px = y_mm * self._px_per_mm + self._follow_pad_y_px

        max_left = max(0.0, total_w_px - view_w_px)
        max_top = max(0.0, total_h_px - view_h_px)
        left_px = min(max(0.0, center_x_px - view_w_px / 2.0), max_left)
        top_px = min(max(0.0, center_y_px - view_h_px / 2.0), max_top)

        x_fraction = 0.0 if total_w_px <= 0 else left_px / total_w_px
        y_fraction = 0.0 if total_h_px <= 0 else top_px / total_h_px
        x_fraction = min(max(0.0, x_fraction), 1.0)
        y_fraction = min(max(0.0, y_fraction), 1.0)

        x_move = getattr(self, "xview_moveto", None)
        y_move = getattr(self, "yview_moveto", None)
        if callable(x_move):
            x_move(x_fraction)
        if callable(y_move):
            y_move(y_fraction)


def _obstacle_style_from_name(name: str) -> tuple[str, str]:
    if name.startswith("wall:"):
        parts = name.split(":")
        if len(parts) >= 2:
            key = parts[1].strip().lower()
            style = _WALL_STYLE.get(key)
            if style:
                return style
    return _OBSTACLE, _OBSTACLE_OUTLINE
