"""Biblioteca lateral de elementos del Editor de Mundos EV3."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from pathlib import Path

from simulador_ev3.domain.editor.asset_presentation import (
    ASSET_PRESENTATIONS,
    CATEGORY_ORDER,
    presentation_for_asset,
)
from simulador_ev3.shared.paths import resolve_image_assets_dir

_BG = "#ECEFF1"
_CARD_BG = "#FFFFFF"
_ACTIVE_BG = "#DCEBFA"
_IMAGE_OVERRIDES = {
    "line_64x64_cruz": ["line_64X64_Cruz.png"],
    "floor_tile_256_c": ["floor_tile_256_c.jpg", "floor_tile_256_b.png"],
}


class AssetLibraryPanel(tk.LabelFrame):
    """Permite buscar y elegir assets sin depender de identificadores técnicos."""

    def __init__(self, parent: tk.Widget, on_select: Callable[[str], None]) -> None:
        super().__init__(parent, text="Biblioteca", bg=_BG, padx=8, pady=8, font=("Segoe UI", 10, "bold"))
        self._on_select = on_select
        self._selected_asset: str | None = None
        self._selected_category = "Todos"
        self._search_var = tk.StringVar(value="")
        self._asset_buttons: dict[str, tk.Button] = {}
        self._asset_icons: dict[str, tk.PhotoImage] = {}
        self._content: tk.Frame | None = None
        self._build()

    def _build(self) -> None:
        tk.Label(self, text="Buscar elemento", bg=_BG, anchor=tk.W).pack(fill=tk.X)
        search = tk.Entry(self, textvariable=self._search_var)
        search.pack(fill=tk.X, pady=(2, 8))
        search.bind("<KeyRelease>", lambda _event: self._refresh_assets())

        self._help_var = tk.StringVar(value="Selecciona un elemento para colocarlo en el lienzo.")
        tk.Label(self, textvariable=self._help_var, bg=_BG, fg="#455A64", justify=tk.LEFT, wraplength=180).pack(
            fill=tk.X, pady=(0, 6)
        )

        categories = tk.Frame(self, bg=_BG)
        categories.pack(fill=tk.X, pady=(0, 6))
        for category in ("Todos", *CATEGORY_ORDER):
            tk.Button(
                categories,
                text=category,
                command=lambda value=category: self._set_category(value),
                bg=_BG,
                relief=tk.FLAT,
                anchor=tk.W,
            ).pack(fill=tk.X)

        self._content = tk.Frame(self, bg=_BG)
        self._content.pack(fill=tk.BOTH, expand=True)
        self._refresh_assets()

    def _set_category(self, category: str) -> None:
        self._selected_category = category
        self._refresh_assets()

    def _refresh_assets(self) -> None:
        if self._content is None:
            return
        for child in self._content.winfo_children():
            child.destroy()
        self._asset_buttons.clear()
        query = self._search_var.get().strip().casefold()
        visible = [
            key
            for key, metadata in ASSET_PRESENTATIONS.items()
            if self._selected_category in {"Todos", metadata.category}
            and (not query or query in metadata.name.casefold() or query in metadata.category.casefold())
        ]
        if not visible:
            tk.Label(self._content, text="No hay elementos coincidentes.", bg=_BG, anchor=tk.W).pack(fill=tk.X)
            return
        for category in CATEGORY_ORDER:
            keys = [key for key in visible if presentation_for_asset(key).category == category]
            if not keys:
                continue
            tk.Label(
                self._content,
                text=category,
                bg=_BG,
                fg="#1565C0",
                font=("Segoe UI", 9, "bold"),
                anchor=tk.W,
            ).pack(fill=tk.X, pady=(6, 2))
            for key in keys:
                presentation = presentation_for_asset(key)
                button = tk.Button(
                    self._content,
                    text=presentation.name,
                    command=lambda asset_key=key: self._select_asset(asset_key),
                    bg=_ACTIVE_BG if key == self._selected_asset else _CARD_BG,
                    activebackground=_ACTIVE_BG,
                    anchor=tk.W,
                    relief=tk.SOLID,
                    bd=1,
                    padx=7,
                    pady=4,
                    takefocus=True,
                )
                icon = self._get_icon(key)
                if icon is not None:
                    button.configure(image=icon, compound=tk.LEFT)
                button.bind("<Enter>", lambda _event, text=presentation.tooltip: self._help_var.set(text))
                button.bind(
                    "<Leave>",
                    lambda _event: self._help_var.set("Selecciona un elemento para colocarlo en el lienzo."),
                )
                button.pack(fill=tk.X, pady=1)
                self._asset_buttons[key] = button

    def _select_asset(self, asset_key: str) -> None:
        self._selected_asset = asset_key
        self._refresh_assets()
        self._on_select(asset_key)

    def set_selected_asset(self, asset_key: str | None) -> None:
        self._selected_asset = asset_key
        self._refresh_assets()

    def _get_icon(self, asset_key: str) -> tk.PhotoImage | None:
        cached = self._asset_icons.get(asset_key)
        if cached is not None:
            return cached
        assets_dir = Path(resolve_image_assets_dir())
        candidates = [*_IMAGE_OVERRIDES.get(asset_key, []), f"{asset_key}.png", f"{asset_key}.jpg"]
        for candidate in candidates:
            path = assets_dir / candidate
            if not path.exists():
                continue
            try:
                source = tk.PhotoImage(file=str(path))
                icon = self._resize_icon(source)
            except Exception:  # noqa: BLE001 - un asset inválido no bloquea la biblioteca.
                continue
            self._asset_icons[asset_key] = icon
            return icon
        return None

    @staticmethod
    def _resize_icon(source: tk.PhotoImage) -> tk.PhotoImage:
        width = max(1, int(source.width()))
        height = max(1, int(source.height()))
        try:
            return source.zoom(24, 24).subsample(width, height)
        except Exception:  # noqa: BLE001
            return source
