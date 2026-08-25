"""
world_toolbar.py
================
Toolbar for world editor actions and tools.
"""

from __future__ import annotations

import os
import tkinter as tk
from typing import Any, Callable, Literal, Optional

from simulador_ev3.shared.asset_catalog import asset_candidate_paths
from simulador_ev3.shared.paths import resolve_image_assets_dir

_BAR_BG = "#ECEFF1"
_BTN_BG = "#CFD8DC"
_BTN_ACTIVE = "#90A4AE"
_ICON_SIZE_PX = 32
_IMAGES_DIR = os.path.normpath(str(resolve_image_assets_dir()))


class WorldToolbar(tk.Frame):
    """Cabecera agrupada de acciones y elementos rápidos del editor."""

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
        super().__init__(parent, bg=_BAR_BG, padx=8, pady=6)
        self._on_tool_change = on_tool_change
        self._active_tool = "select"
        self._tool_buttons: dict[str, tk.Button] = {}
        self._tool_icons: dict[str, tk.PhotoImage] = {}
        self._image_lookup = self._build_image_lookup()
        self._selection_buttons: list[tk.Button] = []

        action_row = tk.Frame(self, bg=_BAR_BG)
        action_row.pack(fill=tk.X, anchor=tk.W)
        file_group = self._add_group(action_row, "Archivo")
        edit_group = self._add_group(action_row, "Edición")
        simulation_group = self._add_group(action_row, "Simulación")

        self._add_action_button("Nuevo", on_new, parent=file_group)
        self._add_action_button("Abrir", on_open, parent=file_group)
        self._add_action_button("Guardar", on_save, parent=file_group, primary=True)
        self._add_action_button("Guardar como", on_save_as, parent=file_group)
        self._delete_world_file_button = self._add_action_button(
            "Eliminar archivo",
            on_delete_world_file or (lambda: None),
            parent=file_group,
            state=tk.DISABLED,
            danger=True,
        )

        self._simulate_saved_button = self._add_action_button(
            "Probar mundo guardado",
            on_simulate_saved or (lambda: None),
            parent=simulation_group,
            state=tk.DISABLED,
            primary=True,
        )

        self._add_tool_button("select", "Seleccionar", parent=edit_group)
        self._selection_buttons.extend(
            [
                self._add_action_button("Eliminar", on_delete, parent=edit_group, state=tk.DISABLED, danger=True),
                self._add_action_button("Duplicar", on_duplicate, parent=edit_group, state=tk.DISABLED),
                self._add_action_button("Rotar 90°", on_rotate, parent=edit_group, state=tk.DISABLED),
                self._add_action_button("Aplicar propiedades", on_apply_props, parent=edit_group, state=tk.DISABLED),
            ]
        )

        self._refresh_tool_styles()

    @staticmethod
    def _add_group(
        parent: tk.Widget,
        title: str,
        *,
        fill: Literal["none", "x", "y", "both"] | None = None,
    ) -> tk.LabelFrame:
        group = tk.LabelFrame(parent, text=title, bg=_BAR_BG, padx=4, pady=3, font=("Segoe UI", 8, "bold"))
        group.pack(side=tk.LEFT, padx=(0, 8), fill=fill or "none", anchor=tk.W)
        return group

    def _add_action_button(
        self,
        label: str,
        command: Callable[[], None],
        *,
        parent: tk.Widget,
        state: Literal["normal", "active", "disabled"] = "normal",
        primary: bool = False,
        danger: bool = False,
    ) -> tk.Button:
        bg = "#1565C0" if primary else "#C62828" if danger else _BTN_BG
        fg = "white" if primary or danger else "#102027"
        btn = tk.Button(
            parent,
            text=label,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=_BTN_ACTIVE,
            # Los controles primario y de peligro conservan contraste también
            # mientras se pulsan o cuando su acción todavía no está disponible.
            activeforeground=fg,
            disabledforeground=fg if primary or danger else "#455A64",
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

        self._simulate_saved_button.configure(state="normal" if enabled else "disabled")

    def set_delete_world_file_enabled(self, enabled: bool) -> None:
        """Habilita borrar solo cuando existe un archivo de mundo editable."""

        self._delete_world_file_button.configure(state="normal" if enabled else "disabled")

    def set_selection_actions_enabled(self, enabled: bool) -> None:
        """Sin selección no se ofrecen acciones que no podrían completarse."""

        state: Literal["normal", "disabled"] = "normal" if enabled else "disabled"
        for button in self._selection_buttons:
            button.configure(state=state)

    def set_active_tool(self, tool_id: str) -> None:
        """Sincroniza la selección de herramienta desde la biblioteca lateral."""

        self._active_tool = tool_id
        self._refresh_tool_styles()

    def _add_tool_button(self, tool_id: str, label: str, *, parent: tk.Widget) -> None:
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
            parent,
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
        try:
            candidates = [str(path) for path in asset_candidate_paths(tool_id)]
        except KeyError:
            candidates = []
        candidates.extend([f"{tool_id}.png", f"{tool_id}.jpg", f"{tool_id}.jpeg"])
        resolved: list[str] = []
        for candidate in candidates:
            if os.path.isabs(candidate) and os.path.isfile(candidate):
                resolved.append(candidate)
                continue
            hit = self._image_lookup.get(candidate.lower())
            if hit:
                resolved.append(hit)
        return list(dict.fromkeys(resolved))

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
