"""
world_canvas_editor.py
======================
Tile-based canvas widget for interactive world editing.
"""

from __future__ import annotations

import math
import os
import tkinter as tk
from typing import Any, Callable, Optional

from simulador_ev3.application.world_validation_engine import rotated_connectors
from simulador_ev3.domain.editor.world_editor_model import CELL_SIZE_MM, GRID_SIZE_PX, get_asset_spec

_BG = "#F4F6F8"
_GRID = "#D0D7DE"
_BORDER = "#B0BEC5"
_LINE_TRACK_WIDTH_MM = 25.0
_SIM_SURFACE_CELL_MM = 12.5
_IMAGES_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "images"))
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


class WorldCanvasEditor(tk.Canvas):
    """Interactive tile-based canvas for editing world placements."""

    def __init__(
        self,
        parent: tk.Widget,
        on_place_asset: Callable[[str, int, int], None],
        on_select: Callable[[Optional[str]], None],
        on_move: Callable[[str, int, int], None],
        on_delete: Callable[[str], None],
        on_status: Callable[[str], None],
    ) -> None:
        super().__init__(
            parent,
            bg=_BG,
            highlightthickness=1,
            highlightbackground=_BORDER,
        )
        self._on_place_asset = on_place_asset
        self._on_select = on_select
        self._on_move = on_move
        self._on_delete = on_delete
        self._on_status = on_status

        self._world_w_mm = 2000.0
        self._world_h_mm = 2000.0
        self._tool = "select"
        self._placements: list[dict[str, Any]] = []
        self._selected_id: Optional[str] = None
        self._item_to_obj_id: dict[int, str] = {}
        self._placement_index: dict[str, dict[str, Any]] = {}
        self._image_lookup = self._build_image_lookup()
        self._asset_base_images: dict[str, tk.PhotoImage] = {}
        self._asset_image_cache: dict[tuple[str, int, int, int], tk.PhotoImage] = {}

        self._dragging = False
        self._drag_offset_px = (0, 0)
        self._hover_cell_px: Optional[tuple[int, int]] = None
        self._px_per_mm = GRID_SIZE_PX / CELL_SIZE_MM

        self.bind("<Configure>", self._on_resize)
        self.bind("<Button-1>", self._on_left_down)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_left_up)
        self.bind("<Motion>", self._on_motion)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_world_size(self, width_mm: float, height_mm: float) -> None:
        self._world_w_mm = max(CELL_SIZE_MM, float(width_mm))
        self._world_h_mm = max(CELL_SIZE_MM, float(height_mm))
        self._update_scrollregion()
        self._redraw()

    def set_tool(self, tool_id: str) -> None:
        self._tool = tool_id
        self._dragging = False
        if tool_id in {"select", "delete"}:
            self._hover_cell_px = None
            self.delete("preview")
        self._redraw()

    def set_placements(self, placements: list[dict[str, Any]]) -> None:
        self._placements = list(placements)
        self._placement_index = {str(p.get("id", "")): p for p in self._placements}
        self._redraw()

    def set_selected_id(self, object_id: Optional[str]) -> None:
        self._selected_id = object_id
        self._redraw()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _on_resize(self, _event) -> None:
        self._update_scrollregion()
        self._redraw()

    def _on_motion(self, event) -> None:
        canvas_x = self.canvasx(event.x)
        canvas_y = self.canvasy(event.y)
        x_mm, y_mm = self._px_to_mm(canvas_x, canvas_y)
        sx_px, sy_px = self._mm_to_editor_px(x_mm, y_mm)
        sx_px = _snap_editor_px(sx_px)
        sy_px = _snap_editor_px(sy_px)
        self._hover_cell_px = (sx_px, sy_px)
        self._draw_preview()
        self._on_status(
            f"Cursor: ({x_mm:.0f} mm, {y_mm:.0f} mm) | Snap: ({sx_px}px, {sy_px}px) | Tool: {self._tool}"
        )

    def _on_left_down(self, event) -> None:
        canvas_x = self.canvasx(event.x)
        canvas_y = self.canvasy(event.y)
        obj_id = self._pick_object_id(canvas_x, canvas_y)
        if self._tool == "delete":
            if obj_id:
                self._on_delete(obj_id)
            return

        if self._tool == "select":
            self._selected_id = obj_id
            self._on_select(obj_id)
            if obj_id:
                placement = self._placement_index.get(obj_id)
                if placement is not None:
                    cursor_x_px, cursor_y_px = self._cursor_to_editor_px(canvas_x, canvas_y)
                    self._drag_offset_px = (
                        _placement_x_px(placement) - cursor_x_px,
                        _placement_y_px(placement) - cursor_y_px,
                    )
                    self._dragging = True
            self._redraw()
            return

        if get_asset_spec(self._tool) is None:
            return
        x_px, y_px = self._cursor_to_editor_px(canvas_x, canvas_y)
        place_x_px, place_y_px = self._placement_origin_for_tool(x_px, y_px)
        self._on_place_asset(self._tool, place_x_px, place_y_px)

    def _on_drag(self, event) -> None:
        if self._tool != "select" or not self._dragging or not self._selected_id:
            return
        canvas_x = self.canvasx(event.x)
        canvas_y = self.canvasy(event.y)
        cursor_x_px, cursor_y_px = self._cursor_to_editor_px(canvas_x, canvas_y)
        target_x = _snap_editor_px(cursor_x_px + self._drag_offset_px[0])
        target_y = _snap_editor_px(cursor_y_px + self._drag_offset_px[1])
        self._on_move(self._selected_id, target_x, target_y)

    def _on_left_up(self, _event) -> None:
        self._dragging = False
        if self._tool not in {"select", "delete"}:
            self._draw_preview()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _redraw(self) -> None:
        self.delete("all")
        self._item_to_obj_id.clear()
        self._draw_background()
        for placement in self._placements:
            self._draw_placement(placement)
        self._draw_preview()

    def _draw_background(self) -> None:
        world_w_px, world_h_px = self._world_px_size()
        self.create_rectangle(0, 0, world_w_px, world_h_px, fill=_BG, outline="", tags="bg")
        self.create_rectangle(0, 0, world_w_px, world_h_px, fill="", outline="#B0BEC5", tags="bg")

        for x in range(GRID_SIZE_PX, world_w_px, GRID_SIZE_PX):
            self.create_line(x, 0, x, world_h_px, fill=_GRID, tags="bg")
        for y in range(GRID_SIZE_PX, world_h_px, GRID_SIZE_PX):
            self.create_line(0, y, world_w_px, y, fill=_GRID, tags="bg")

    def _draw_placement(self, placement: dict[str, Any]) -> None:
        placement_id = str(placement.get("id", ""))
        asset_key = str(placement.get("asset_key", ""))
        spec = get_asset_spec(asset_key)
        if spec is None:
            return

        rotation = int(placement.get("rotation", 0))
        width_cells = spec.width_cells
        height_cells = spec.height_cells
        if rotation % 180 == 90:
            width_cells, height_cells = height_cells, width_cells

        x_px = _placement_x_px(placement)
        y_px = _placement_y_px(placement)
        x_mm = _editor_px_to_mm(x_px)
        y_mm = _editor_px_to_mm(y_px)
        w_mm = width_cells * CELL_SIZE_MM
        h_mm = height_cells * CELL_SIZE_MM
        px0, py0 = self._mm_to_px(x_mm, y_mm)
        px1, py1 = self._mm_to_px(x_mm + w_mm, y_mm + h_mm)
        selected = placement_id == self._selected_id

        item_ids: list[int] = []
        draw_w_px = max(1, int(round(px1 - px0)))
        draw_h_px = max(1, int(round(py1 - py0)))
        asset_image = self._get_asset_image(asset_key, rotation, draw_w_px, draw_h_px)
        if asset_image is not None:
            cx = (px0 + px1) / 2.0
            cy = (py0 + py1) / 2.0
            item_ids.append(self.create_image(cx, cy, image=asset_image))
        elif spec.asset_type == "floor":
            item_ids.append(
                self.create_rectangle(px0, py0, px1, py1, fill="#D7CCC8", outline="#BCAAA4", width=1)
            )
        elif spec.asset_type == "zone":
            fill = "#ECEFF1"
            outline = "#B0BEC5"
            if "red" in asset_key:
                fill, outline = "#EF5350", "#C62828"
            elif "green" in asset_key:
                fill, outline = "#66BB6A", "#2E7D32"
            item_ids.append(self.create_rectangle(px0, py0, px1, py1, fill=fill, outline=outline, width=2))
        elif spec.asset_type == "wall":
            item_ids.append(self.create_rectangle(px0, py0, px1, py1, fill="#37474F", outline="#102027", width=2))
        elif spec.asset_type == "robot":
            item_ids.append(self.create_rectangle(px0, py0, px1, py1, fill="#D9DDE3", outline="#263238", width=2))
            cx = (px0 + px1) / 2.0
            cy = (py0 + py1) / 2.0
            item_ids.append(self.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill="#E53935", outline=""))
        elif spec.asset_type == "line":
            item_ids.extend(self._draw_line_tile(spec.connectors, rotation, x_mm, y_mm, w_mm, h_mm))

        if selected:
            item_ids.append(
                self.create_rectangle(px0, py0, px1, py1, outline="#FFC107", width=2, dash=(4, 3))
            )
        for item_id in item_ids:
            self._item_to_obj_id[item_id] = placement_id

    def _draw_preview(self) -> None:
        self.delete("preview")
        if self._tool in {"select", "delete"}:
            return
        spec = get_asset_spec(self._tool)
        if spec is None or self._hover_cell_px is None:
            return
        x_px, y_px = self._placement_origin_for_tool(*self._hover_cell_px)
        w_mm = spec.width_cells * CELL_SIZE_MM
        h_mm = spec.height_cells * CELL_SIZE_MM
        x_mm = _editor_px_to_mm(x_px)
        y_mm = _editor_px_to_mm(y_px)
        px0, py0 = self._mm_to_px(x_mm, y_mm)
        px1, py1 = self._mm_to_px(x_mm + w_mm, y_mm + h_mm)
        self.create_rectangle(
            px0,
            py0,
            px1,
            py1,
            outline="#1565C0",
            width=2,
            dash=(4, 3),
            tags="preview",
        )

    def _draw_line_tile(
        self,
        connectors: frozenset[str],
        rotation: int,
        x_mm: float,
        y_mm: float,
        w_mm: float,
        h_mm: float,
    ) -> list[int]:
        item_ids: list[int] = []
        cx_mm = x_mm + w_mm / 2.0
        cy_mm = y_mm + h_mm / 2.0
        oriented = rotated_connectors(set(connectors), int(rotation))
        cells: set[tuple[int, int]] = set()
        for direction in oriented:
            ex_mm, ey_mm = _line_endpoint(direction, x_mm, y_mm, w_mm, h_mm)
            cells |= _raster_segment_cells(
                cx_mm,
                cy_mm,
                ex_mm,
                ey_mm,
                width_mm=_LINE_TRACK_WIDTH_MM,
                cell_size_mm=_SIM_SURFACE_CELL_MM,
            )
        for col, row in sorted(cells):
            x0_mm = col * _SIM_SURFACE_CELL_MM
            y0_mm = row * _SIM_SURFACE_CELL_MM
            x1_mm = x0_mm + _SIM_SURFACE_CELL_MM
            y1_mm = y0_mm + _SIM_SURFACE_CELL_MM
            p0x, p0y = self._mm_to_px(x0_mm, y0_mm)
            p1x, p1y = self._mm_to_px(x1_mm, y1_mm)
            item_ids.append(self.create_rectangle(p0x, p0y, p1x, p1y, fill="#111111", outline=""))
        return item_ids

    def _build_image_lookup(self) -> dict[str, str]:
        lookup: dict[str, str] = {}
        if not os.path.isdir(_IMAGES_DIR):
            return lookup
        for name in os.listdir(_IMAGES_DIR):
            full_path = os.path.join(_IMAGES_DIR, name)
            lookup[name.lower()] = full_path
        return lookup

    def _resolve_asset_image_paths(self, asset_key: str) -> list[str]:
        key = str(asset_key).strip().lower()
        candidates = list(_ASSET_IMAGE_OVERRIDES.get(key, []))
        candidates.extend([f"{key}.png", f"{key}.jpg", f"{key}.jpeg"])
        resolved: list[str] = []
        for candidate in candidates:
            hit = self._image_lookup.get(candidate.lower())
            if hit:
                resolved.append(hit)
        return resolved

    def _load_asset_base_image(self, asset_key: str) -> tk.PhotoImage | None:
        key = str(asset_key).strip().lower()
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
        target_w_px: int,
        target_h_px: int,
    ) -> tk.PhotoImage | None:
        key = str(asset_key).strip().lower()
        rot = int(round(int(rotation_deg) / 90.0) * 90) % 360
        cache_key = (key, rot, int(target_w_px), int(target_h_px))
        cached = self._asset_image_cache.get(cache_key)
        if cached is not None:
            return cached

        base_image = self._load_asset_base_image(key)
        if base_image is None:
            return None
        out = self._resize_photoimage(
            base_image,
            target_w=max(1, int(target_w_px)),
            target_h=max(1, int(target_h_px)),
        )
        if rot % 360:
            out = self._rotate_photoimage(out, rot)
        self._asset_image_cache[cache_key] = out
        return out

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

    def _rotate_photoimage(self, src: tk.PhotoImage, angle_deg: int) -> tk.PhotoImage:
        if angle_deg % 360 == 0:
            return src

        src_get = getattr(src, "get", None)
        if not callable(src_get):
            return src

        src_w_fn = getattr(src, "width", None)
        src_h_fn = getattr(src, "height", None)
        src_w = int(src_w_fn()) if callable(src_w_fn) else 1
        src_h = int(src_h_fn()) if callable(src_h_fn) else 1
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

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def _scale(self) -> float:
        return self._px_per_mm

    def _origin(self) -> tuple[float, float]:
        return 0.0, 0.0

    def _mm_to_px(self, x_mm: float, y_mm: float) -> tuple[float, float]:
        s = self._scale()
        ox, oy = self._origin()
        return ox + x_mm * s, oy + y_mm * s

    def _px_to_mm(self, x_px: float, y_px: float) -> tuple[float, float]:
        s = self._scale()
        ox, oy = self._origin()
        x_mm = (x_px - ox) / s
        y_mm = (y_px - oy) / s
        x_mm = min(max(0.0, x_mm), self._world_w_mm)
        y_mm = min(max(0.0, y_mm), self._world_h_mm)
        return x_mm, y_mm

    def _mm_to_editor_px(self, x_mm: float, y_mm: float) -> tuple[int, int]:
        return _mm_to_editor_px(x_mm), _mm_to_editor_px(y_mm)

    def _cursor_to_editor_px(self, x_canvas_px: float, y_canvas_px: float) -> tuple[int, int]:
        x_mm, y_mm = self._px_to_mm(x_canvas_px, y_canvas_px)
        x_px, y_px = self._mm_to_editor_px(x_mm, y_mm)
        return _snap_editor_px(x_px), _snap_editor_px(y_px)

    def _placement_origin_for_tool(self, snap_x_px: int, snap_y_px: int) -> tuple[int, int]:
        spec = get_asset_spec(self._tool)
        if spec is None:
            return snap_x_px, snap_y_px
        width_px = spec.width_cells * GRID_SIZE_PX
        height_px = spec.height_cells * GRID_SIZE_PX
        origin_x = snap_x_px - (spec.width_cells // 2) * GRID_SIZE_PX
        origin_y = snap_y_px - (spec.height_cells // 2) * GRID_SIZE_PX
        max_x = max(0, self._world_px_size()[0] - width_px)
        max_y = max(0, self._world_px_size()[1] - height_px)
        origin_x = min(max(0, _snap_editor_px(origin_x)), max_x)
        origin_y = min(max(0, _snap_editor_px(origin_y)), max_y)
        return origin_x, origin_y

    def _world_px_size(self) -> tuple[int, int]:
        world_w_px = int(round(self._world_w_mm / CELL_SIZE_MM * GRID_SIZE_PX))
        world_h_px = int(round(self._world_h_mm / CELL_SIZE_MM * GRID_SIZE_PX))
        return world_w_px, world_h_px

    def _update_scrollregion(self) -> None:
        world_w_px, world_h_px = self._world_px_size()
        self.configure(scrollregion=(0, 0, world_w_px, world_h_px))

    def _pick_object_id(self, x_px: float, y_px: float) -> Optional[str]:
        items = self.find_overlapping(x_px - 2, y_px - 2, x_px + 2, y_px + 2)
        for item in reversed(items):
            obj_id = self._item_to_obj_id.get(item)
            if obj_id:
                return obj_id
        return None


def _mm_to_editor_px(mm_value: float) -> int:
    return int(round(float(mm_value) / CELL_SIZE_MM * GRID_SIZE_PX))


def _editor_px_to_mm(editor_px: int | float) -> float:
    return float(editor_px) / GRID_SIZE_PX * CELL_SIZE_MM


def _snap_editor_px(editor_px: int) -> int:
    return int(round(editor_px / GRID_SIZE_PX) * GRID_SIZE_PX)


def _placement_x_px(placement: dict[str, Any]) -> int:
    if "x_px" in placement:
        return int(placement.get("x_px", 0))
    return int(placement.get("x", 0))


def _placement_y_px(placement: dict[str, Any]) -> int:
    if "y_px" in placement:
        return int(placement.get("y_px", 0))
    return int(placement.get("y", 0))


def _line_endpoint(direction: str, x_mm: float, y_mm: float, w_mm: float, h_mm: float) -> tuple[float, float]:
    cx = x_mm + w_mm / 2.0
    cy = y_mm + h_mm / 2.0
    if direction == "N":
        return cx, y_mm
    if direction == "S":
        return cx, y_mm + h_mm
    if direction == "E":
        return x_mm + w_mm, cy
    return x_mm, cy


def _raster_segment_cells(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    width_mm: float,
    cell_size_mm: float,
) -> set[tuple[int, int]]:
    half = width_mm / 2.0
    min_x = min(x1, x2) - half
    max_x = max(x1, x2) + half
    min_y = min(y1, y2) - half
    max_y = max(y1, y2) + half
    col_min = int(math.floor(min_x / cell_size_mm))
    col_max = int(math.floor(max_x / cell_size_mm))
    row_min = int(math.floor(min_y / cell_size_mm))
    row_max = int(math.floor(max_y / cell_size_mm))

    cells: set[tuple[int, int]] = set()
    for col in range(col_min, col_max + 1):
        for row in range(row_min, row_max + 1):
            cell_x0 = col * cell_size_mm
            cell_y0 = row * cell_size_mm
            cell_x1 = cell_x0 + cell_size_mm
            cell_y1 = cell_y0 + cell_size_mm
            if _segment_intersects_expanded_aabb(
                x1,
                y1,
                x2,
                y2,
                cell_x0 - half,
                cell_y0 - half,
                cell_x1 + half,
                cell_y1 + half,
            ):
                cells.add((col, row))
    return cells


def _segment_intersects_expanded_aabb(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    min_x: float,
    min_y: float,
    max_x: float,
    max_y: float,
) -> bool:
    if min_x <= x1 <= max_x and min_y <= y1 <= max_y:
        return True
    if min_x <= x2 <= max_x and min_y <= y2 <= max_y:
        return True

    dx = x2 - x1
    dy = y2 - y1
    p = (-dx, dx, -dy, dy)
    q = (x1 - min_x, max_x - x1, y1 - min_y, max_y - y1)

    u1 = 0.0
    u2 = 1.0
    for pi, qi in zip(p, q):
        if abs(pi) < 1e-12:
            if qi < 0:
                return False
            continue
        t = qi / pi
        if pi < 0:
            u1 = max(u1, t)
        else:
            u2 = min(u2, t)
        if u1 > u2:
            return False
    return True
