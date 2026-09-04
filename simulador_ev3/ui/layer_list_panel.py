"""Lista de capas de presentación para seleccionar elementos superpuestos."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from functools import partial
from typing import Any

from simulador_ev3.domain.editor.asset_presentation import presentation_for_asset
from simulador_ev3.shared.ui_design_tokens import LIGHT_TOKENS, tokens_for_theme

_BG = "#ECEFF1"
_SELECTED = "#DCEBFA"


class LayerListPanel(tk.LabelFrame):
    """Expone selección, visibilidad y bloqueo sin alterar el JSON del mundo."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_select: Callable[[str], None],
        on_toggle_visibility: Callable[[str], None],
        on_toggle_lock: Callable[[str], None],
    ) -> None:
        super().__init__(parent, text="Capas", bg=_BG, padx=8, pady=8, font=("Segoe UI", 10, "bold"))
        self._on_select = on_select
        self._on_toggle_visibility = on_toggle_visibility
        self._on_toggle_lock = on_toggle_lock
        self._tokens = LIGHT_TOKENS
        self._content = tk.Frame(self, bg=_BG)
        self._content.pack(fill=tk.BOTH, expand=True)

    def set_layers(
        self,
        placements: list[dict[str, Any]],
        *,
        selected_id: str | None,
        hidden_ids: set[str],
        locked_ids: set[str],
    ) -> None:
        for child in self._content.winfo_children():
            child.destroy()
        if not placements:
            tk.Label(self._content, text="No hay elementos en este mundo.", bg=_BG, fg="#546E7A").pack(fill=tk.X)
            return
        for placement in reversed(placements):
            object_id = str(placement.get("id", ""))
            presentation = presentation_for_asset(str(placement.get("asset_key", "")))
            row = tk.Frame(
                self._content,
                bg=self._tokens.surface_muted if object_id == selected_id else self._tokens.background,
                bd=1,
                relief=tk.SOLID,
            )
            row.pack(fill=tk.X, pady=2)
            tk.Button(
                row,
                text=presentation.name,
                command=partial(self._on_select, object_id),
                bg=self._tokens.surface_muted if object_id == selected_id else self._tokens.surface,
                fg=self._tokens.text,
                activebackground=self._tokens.primary_active,
                activeforeground=self._tokens.text,
                anchor=tk.W,
                relief=tk.FLAT,
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
            tk.Button(
                row,
                text="Mostrar" if object_id in hidden_ids else "Ocultar",
                command=partial(self._on_toggle_visibility, object_id),
                width=8,
            ).pack(side=tk.LEFT, padx=1, pady=2)
            tk.Button(
                row,
                text="Desbloq." if object_id in locked_ids else "Bloquear",
                command=partial(self._on_toggle_lock, object_id),
                width=8,
            ).pack(side=tk.LEFT, padx=1, pady=2)

    def set_theme(self, theme: str) -> None:
        self._tokens = tokens_for_theme(theme)
        self.configure(bg=self._tokens.background, fg=self._tokens.text)
        self._content.configure(bg=self._tokens.background)
