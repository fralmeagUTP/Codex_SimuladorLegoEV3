"""
object_properties_panel.py
==========================
Properties panel for selected placement in the tile-based editor.
"""

from __future__ import annotations

import tkinter as tk
from typing import Any, Optional

_BG = "#ECEFF1"
_LABEL = ("Segoe UI", 9)
_MONO = ("Consolas", 9)


class ObjectPropertiesPanel(tk.LabelFrame):
    """Editable properties for selected placement."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(
            parent,
            text="Propiedades",
            bg=_BG,
            padx=8,
            pady=8,
            font=("Segoe UI", 9, "bold"),
        )
        self._obj: Optional[dict[str, Any]] = None
        self._entries: dict[str, tk.Entry] = {}
        self._build()

    def _build(self) -> None:
        self._title_var = tk.StringVar(value="(Sin seleccion)")
        tk.Label(self, textvariable=self._title_var, bg=_BG, font=("Segoe UI", 9, "bold")).pack(
            anchor=tk.W, pady=(0, 6)
        )

        grid = tk.Frame(self, bg=_BG)
        grid.pack(fill=tk.X, anchor=tk.N)
        for key in ("asset_key", "x_px", "y_px", "rotation"):
            row = tk.Frame(grid, bg=_BG)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=f"{key}:", width=11, anchor=tk.W, bg=_BG, font=_LABEL).pack(side=tk.LEFT)
            entry = tk.Entry(row, font=_MONO)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self._entries[key] = entry

    def set_object(self, obj: Optional[dict[str, Any]]) -> None:
        self._obj = obj
        for entry in self._entries.values():
            entry.delete(0, tk.END)
        if obj is None:
            self._title_var.set("(Sin seleccion)")
            return
        self._title_var.set(f"{obj.get('asset_key', '?')} | {obj.get('id', '?')}")
        self._put("asset_key", obj.get("asset_key"))
        self._put("x_px", obj.get("x_px", obj.get("x")))
        self._put("y_px", obj.get("y_px", obj.get("y")))
        self._put("rotation", obj.get("rotation"))

    def collect_updates(self) -> Optional[dict[str, Any]]:
        if self._obj is None:
            return None
        updates: dict[str, Any] = {}
        asset_key = self._entries["asset_key"].get().strip()
        if asset_key:
            updates["asset_key"] = asset_key

        for key in ("x_px", "y_px", "rotation"):
            raw = self._entries[key].get().strip()
            if not raw:
                continue
            try:
                updates[key] = int(raw)
            except ValueError:
                continue
        return updates

    def _put(self, key: str, value: Any) -> None:
        if value is None:
            return
        self._entries[key].insert(0, str(value))
