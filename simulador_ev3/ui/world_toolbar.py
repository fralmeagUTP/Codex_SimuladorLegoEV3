"""
world_toolbar.py
================
Toolbar for world editor actions and tools.
"""

from __future__ import annotations

import os
import tkinter as tk
from typing import Any, Callable, Literal, Optional

from simulador_ev3.shared.paths import resolve_image_assets_dir

_BAR_BG = "#ECEFF1"
_BTN_BG = "#CFD8DC"
_BTN_ACTIVE = "#90A4AE"
_ICON_SIZE_PX = 32
_IMAGES_DIR = os.path.normpath(str(resolve_image_assets_dir()))
_TOOL_IMAGE_OVERRIDES: dict[str, list[str]] = {
    "line_64x64_cruz": ["line_64X64_Cruz.png"],
    "line_64_64_hor": ["line_64_64_Hor.png"],
    "line_64_64_ver": ["line_64_64_Ver.png"],
    "line_64_64_infder": ["line_64_64_InfDer.png"],
    "line_64_64_infizq": ["line_64_64_InfIzq.png"],
    "line_64_64_supder": ["line_64_64_SupDer.png"],
    "line_64_64_supizq": ["line_64_64_SupIzq.png"],
    "floor_tile_256_c": ["floor_tile_256_c.jpg", "floor_tile_256_b.png"],
}


class WorldToolbar(tk.Frame):
    """Simple toolbar with world-editor tools."""

    def __init__(
        self,
        parent: Any,
        on_tool_change: Callable[[str], None],
        on_new: Callable[[], None],
        on_open: Callable[[], None],
        on_save: Callable[[], None],
        on_save_as: Callable[[], None],
        on_delete: Callable[[], None],
        on_duplicate: Callable[[], None],
        on_rotate: Callable[[], None],
        on_apply_props: Callable[[], None],
        on_delete_world_file: Optional[Callable[[], None]] = None,
        on_simulate_saved: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(parent, bg=_BAR_BG, padx=6, pady=4)
        self._on_tool_change = on_tool_change
        self._active_tool = "select"
        self._tool_buttons: dict[str, tk.Button] = {}
        self._tool_icons: dict[str, tk.PhotoImage] = {}
        self._image_lookup = self._build_image_lookup()

        self._add_action_button("Nuevo", on_new)
        self._add_action_button("Abrir", on_open)
        self._add_action_button("Guardar", on_save)
        self._add_action_button("Guardar como", on_save_as)
        self._delete_world_file_button = self._add_action_button(
            "Eliminar archivo",
            on_delete_world_file or (lambda: None),
            state=tk.DISABLED,
        )
        self._simulate_saved_button = self._add_action_button(
            "Simular mundo guardado",
            on_simulate_saved or (lambda: None),
            state=tk.DISABLED,
        )
        self._add_separator()

        self._add_tool_button("select", "Select")
        self._add_tool_button("delete", "Delete")
        self._add_separator()

        self._add_tool_button("robot_ev3_32x32", "Robot")
        self._add_tool_button("wall_64x64_a", "Wall A")
        self._add_tool_button("wall_64x64_b", "Wall B")
        self._add_tool_button("wall_64x64_c", "Wall C")
        self._add_tool_button("floor_tile_256_a", "Fondo A")
        self._add_tool_button("floor_tile_256_b", "Fondo B")
        self._add_tool_button("floor_tile_256_c", "Fondo C")
        self._add_tool_button("zone_white_128", "Zone White")
        self._add_tool_button("zone_red_128", "Zone Red")
        self._add_tool_button("zone_green_128", "Zone Green")
        self._add_tool_button("line_64_64_hor", "Line Hor")
        self._add_tool_button("line_64_64_ver", "Line Ver")
        self._add_tool_button("line_64x64_cruz", "Line Cross")
        self._add_tool_button("line_64_64_infder", "Curve InfDer")
        self._add_tool_button("line_64_64_infizq", "Curve InfIzq")
        self._add_tool_button("line_64_64_supder", "Curve SupDer")
        self._add_tool_button("line_64_64_supizq", "Curve SupIzq")
        self._add_separator()

        self._add_action_button("Eliminar", on_delete)
        self._add_action_button("Duplicate", on_duplicate)
        self._add_action_button("Rotar 90", on_rotate)
        self._add_action_button("Aplicar propiedades", on_apply_props)

        self._refresh_tool_styles()

    def _add_action_button(
        self,
        label: str,
        command: Callable[[], None],
        *,
        state: Literal["normal", "active", "disabled"] = "normal",
    ) -> tk.Button:
        btn = tk.Button(
            self,
            text=label,
            command=command,
            bg=_BTN_BG,
            activebackground=_BTN_ACTIVE,
            relief=tk.RAISED,
            bd=1,
            padx=6,
            pady=2,
            state=state,
        )
        btn.pack(side=tk.LEFT, padx=2)
        return btn

    def set_simulate_saved_enabled(self, enabled: bool) -> None:
        """Habilita el retorno explícito a simulación tras un guardado válido."""

        self._simulate_saved_button.configure(state=tk.NORMAL if enabled else tk.DISABLED)

    def set_delete_world_file_enabled(self, enabled: bool) -> None:
        """Habilita borrar solo cuando existe un archivo de mundo editable."""

        self._delete_world_file_button.configure(state=tk.NORMAL if enabled else tk.DISABLED)

    def _add_tool_button(self, tool_id: str, label: str) -> None:
        icon = self._get_tool_icon(tool_id)
        kwargs: dict[str, Any] = {
            "command": lambda t=tool_id: self._set_tool(t),
            "bg": _BTN_BG,
            "activebackground": _BTN_ACTIVE,
            "relief": tk.RAISED,
            "bd": 1,
            "padx": 6,
            "pady": 2,
        }
        if icon is not None:
            kwargs.update(
                {
                    "image": icon,
                    "width": _ICON_SIZE_PX + 4,
                    "height": _ICON_SIZE_PX + 4,
                    "padx": 1,
                    "pady": 1,
                    "text": "",
                }
            )
        else:
            kwargs["text"] = label
        btn = tk.Button(
            self,
            **kwargs,
        )
        btn.pack(side=tk.LEFT, padx=2)
        self._tool_buttons[tool_id] = btn

    def _add_separator(self) -> None:
        tk.Frame(self, width=1, height=24, bg="#90A4AE").pack(side=tk.LEFT, padx=6)

    def _set_tool(self, tool_id: str) -> None:
        self._active_tool = tool_id
        self._refresh_tool_styles()
        self._on_tool_change(tool_id)

    def _refresh_tool_styles(self) -> None:
        for tool_id, btn in self._tool_buttons.items():
            is_active = tool_id == self._active_tool
            btn.configure(
                relief=tk.SUNKEN if is_active else tk.RAISED,
                bg="#B0BEC5" if is_active else _BTN_BG,
            )

    def _build_image_lookup(self) -> dict[str, str]:
        lookup: dict[str, str] = {}
        if not os.path.isdir(_IMAGES_DIR):
            return lookup
        for name in os.listdir(_IMAGES_DIR):
            full_path = os.path.join(_IMAGES_DIR, name)
            lookup[name.lower()] = full_path
        return lookup

    def _resolve_tool_image_paths(self, tool_id: str) -> list[str]:
        candidates = list(_TOOL_IMAGE_OVERRIDES.get(tool_id, []))
        candidates.extend([f"{tool_id}.png", f"{tool_id}.jpg", f"{tool_id}.jpeg"])
        resolved: list[str] = []
        for candidate in candidates:
            hit = self._image_lookup.get(candidate.lower())
            if hit:
                resolved.append(hit)
        return resolved

    def _get_tool_icon(self, tool_id: str) -> tk.PhotoImage | None:
        cached = self._tool_icons.get(tool_id)
        if cached is not None:
            return cached
        image_paths = self._resolve_tool_image_paths(tool_id)
        if not image_paths:
            return None
        for image_path in image_paths:
            try:
                image = tk.PhotoImage(file=image_path)
                icon = self._resize_photoimage(image, _ICON_SIZE_PX, _ICON_SIZE_PX)
            except Exception:  # noqa: BLE001
                continue
            self._tool_icons[tool_id] = icon
            return icon
        return None

    @staticmethod
    def _resize_photoimage(img: tk.PhotoImage, target_w: int, target_h: int) -> tk.PhotoImage:
        src_w = max(1, int(img.width()))
        src_h = max(1, int(img.height()))
        zx = max(1, int(target_w))
        zy = max(1, int(target_h))
        try:
            return img.zoom(zx, zy).subsample(src_w, src_h)
        except Exception:  # noqa: BLE001
            return img
