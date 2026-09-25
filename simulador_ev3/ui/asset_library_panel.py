"""Biblioteca lateral de elementos del Editor de Mundos EV3."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from functools import partial

from simulador_ev3.domain.editor.asset_presentation import (
    ASSET_PRESENTATIONS,
    CATEGORY_ORDER,
    presentation_for_asset,
)
from simulador_ev3.shared.asset_catalog import asset_path
from simulador_ev3.shared.ui_design_tokens import LIGHT_TOKENS, tokens_for_theme

_BG = "#ECEFF1"
_CARD_BG = "#FFFFFF"
_ACTIVE_BG = "#DCEBFA"


class AssetLibraryPanel(tk.LabelFrame):
    """Permite buscar y elegir assets sin depender de identificadores técnicos."""

    def __init__(self, parent: tk.Widget, on_select: Callable[[str], None]) -> None:
        super().__init__(parent, text="Biblioteca", bg=_BG, padx=8, pady=8, font=("Segoe UI", 10, "bold"))
        self._on_select = on_select
        self._selected_asset: str | None = None
        self._selected_category = "Todos"
        self._tokens = LIGHT_TOKENS
        self._search_var = tk.StringVar(value="")
        self._asset_buttons: dict[str, tk.Button] = {}
        self._asset_icons: dict[str, tk.PhotoImage] = {}
        self._category_buttons: list[tk.Button] = []
        self._static_labels: list[tk.Label] = []
        self._content: tk.Frame | None = None
        self._build()

    def _build(self) -> None:
        search_label = tk.Label(self, text="Buscar elemento", bg=_BG, anchor=tk.W)
        search_label.pack(fill=tk.X)
        self._static_labels.append(search_label)
        search = tk.Entry(self, textvariable=self._search_var)
        search.pack(fill=tk.X, pady=(2, 8))
        search.bind("<KeyRelease>", self._on_search_changed)

        self._help_var = tk.StringVar(value="Selecciona un elemento para colocarlo en el lienzo.")
        help_label = tk.Label(self, textvariable=self._help_var, bg=_BG, fg="#455A64", justify=tk.LEFT, wraplength=180)
        help_label.pack(
            fill=tk.X, pady=(0, 6)
        )
        self._static_labels.append(help_label)

        categories = tk.Frame(self, bg=_BG)
        categories.pack(fill=tk.X, pady=(0, 6))
        for category in ("Todos", *CATEGORY_ORDER):
            category_button = tk.Button(
                categories,
                text=category,
                command=partial(self._set_category, category),
                bg=_BG,
                relief=tk.FLAT,
                anchor=tk.W,
            )
            category_button.pack(fill=tk.X)
            self._category_buttons.append(category_button)

        self._content = tk.Frame(self, bg=_BG)
        self._content.pack(fill=tk.BOTH, expand=True)
        self._refresh_assets()

    def _set_category(self, category: str) -> None:
        self._selected_category = category
        self._refresh_assets()

    def _on_search_changed(self, _event: tk.Event[tk.Misc]) -> None:
        self._refresh_assets()

    def _make_tooltip_handler(self, text: str) -> Callable[[tk.Event[tk.Misc]], None]:
        def show_tooltip(_event: tk.Event[tk.Misc]) -> None:
            self._help_var.set(text)

        return show_tooltip

    def _clear_tooltip(self, _event: tk.Event[tk.Misc]) -> None:
        self._help_var.set("Selecciona un elemento para colocarlo en el lienzo.")

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
                bg=self._tokens.background,
                fg=self._tokens.primary,
                font=("Segoe UI", 9, "bold"),
                anchor=tk.W,
            ).pack(fill=tk.X, pady=(6, 2))
            for key in keys:
                presentation = presentation_for_asset(key)
                button = tk.Button(
                    self._content,
                    text=presentation.name,
                    command=partial(self._select_asset, key),
                    bg=self._tokens.surface_muted if key == self._selected_asset else self._tokens.surface,
                    fg=self._tokens.text,
                    activebackground=self._tokens.surface_muted,
                    activeforeground=self._tokens.text,
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
                button.bind("<Enter>", self._make_tooltip_handler(presentation.tooltip))
                button.bind("<Leave>", self._clear_tooltip)
                button.pack(fill=tk.X, pady=1)
                self._asset_buttons[key] = button

    def _select_asset(self, asset_key: str) -> None:
        self._selected_asset = asset_key
        self._refresh_assets()
        self._on_select(asset_key)

    def set_selected_asset(self, asset_key: str | None) -> None:
        self._selected_asset = asset_key
        self._refresh_assets()

    def set_theme(self, theme: str) -> None:
        """Conserva contraste al reconstruir las tarjetas de la biblioteca."""

        self._tokens = tokens_for_theme(theme)
        self.configure(bg=self._tokens.background, fg=self._tokens.text)
        for index, label in enumerate(self._static_labels):
            label.configure(
                bg=self._tokens.background,
                fg=self._tokens.text_muted if index else self._tokens.text,
            )
        for button in self._category_buttons:
            button.configure(
                bg=self._tokens.background,
                fg=self._tokens.text,
                activebackground=self._tokens.surface_muted,
                activeforeground=self._tokens.text,
            )
        self._refresh_assets()

    def _get_icon(self, asset_key: str) -> tk.PhotoImage | None:
        cached = self._asset_icons.get(asset_key)
        if cached is not None:
            return cached
        try:
            source = tk.PhotoImage(file=str(asset_path(asset_key)))
            icon = self._resize_icon(source)
        except (KeyError, tk.TclError):
            return None
        self._asset_icons[asset_key] = icon
        return icon

    @staticmethod
    def _resize_icon(source: tk.PhotoImage) -> tk.PhotoImage:
        width = max(1, int(source.width()))
        height = max(1, int(source.height()))
        try:
            return source.zoom(24, 24).subsample(width, height)
        except Exception:  # noqa: BLE001
            return source
