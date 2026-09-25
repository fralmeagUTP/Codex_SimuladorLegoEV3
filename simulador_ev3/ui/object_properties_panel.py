"""Inspector comprensible para elementos seleccionados del editor de mundos."""

from __future__ import annotations

import tkinter as tk
from typing import Any, Optional

from simulador_ev3.domain.editor.asset_presentation import (
    cells_to_pixels,
    pixels_to_cells,
    pixels_to_mm,
    presentation_for_asset,
)

_BG = "#ECEFF1"
_LABEL = ("Segoe UI", 9)
_VALUE = ("Segoe UI", 9, "bold")


class ObjectPropertiesPanel(tk.LabelFrame):
    """Edita unidades de dominio y oculta claves internas del JSON."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(
            parent,
            text="Inspector",
            bg=_BG,
            padx=10,
            pady=10,
            font=("Segoe UI", 10, "bold"),
        )
        self._obj: Optional[dict[str, Any]] = None
        self._entries: dict[str, tk.Entry] = {}
        self._build()

    def _build(self) -> None:
        self._title_var = tk.StringVar(value="Sin selección")
        self._hint_var = tk.StringVar(value="Selecciona un elemento del lienzo para editar sus propiedades.")
        tk.Label(self, textvariable=self._title_var, bg=_BG, font=("Segoe UI", 10, "bold"), anchor=tk.W).pack(
            fill=tk.X
        )
        tk.Label(self, textvariable=self._hint_var, bg=_BG, fg="#546E7A", justify=tk.LEFT, wraplength=260).pack(
            fill=tk.X, pady=(2, 10)
        )

        self._details = tk.Frame(self, bg=_BG)
        self._details.pack(fill=tk.X, anchor=tk.N)
        self._add_readonly("Tipo")
        self._add_entry("x_cells", "Posición X (celdas)")
        self._add_entry("y_cells", "Posición Y (celdas)")
        self._add_entry("rotation", "Rotación (°)")
        self._units_var = tk.StringVar(value="")
        tk.Label(
            self._details, textvariable=self._units_var, bg=_BG, fg="#455A64", justify=tk.LEFT, wraplength=260
        ).pack(
            fill=tk.X, pady=(8, 0)
        )

    def _add_readonly(self, label: str) -> None:
        row = tk.Frame(self._details, bg=_BG)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=f"{label}:", width=18, anchor=tk.W, bg=_BG, font=_LABEL).pack(side=tk.LEFT)
        self._type_var = tk.StringVar(value="—")
        tk.Label(row, textvariable=self._type_var, anchor=tk.W, bg=_BG, font=_VALUE).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

    def _add_entry(self, key: str, label: str) -> None:
        row = tk.Frame(self._details, bg=_BG)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=f"{label}:", width=18, anchor=tk.W, bg=_BG, font=_LABEL).pack(side=tk.LEFT)
        entry = tk.Entry(row, font=_VALUE, justify=tk.RIGHT)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._entries[key] = entry

    def set_object(self, obj: Optional[dict[str, Any]]) -> None:
        self._obj = obj
        for entry in self._entries.values():
            entry.delete(0, tk.END)
        if obj is None:
            self._title_var.set("Sin selección")
            self._hint_var.set("Selecciona un elemento del lienzo para editar sus propiedades.")
            self._type_var.set("—")
            self._units_var.set("")
            return

        asset_key = str(obj.get("asset_key", ""))
        presentation = presentation_for_asset(asset_key)
        x_px = obj.get("x_px", obj.get("x", 0))
        y_px = obj.get("y_px", obj.get("y", 0))
        rotation = obj.get("rotation", 0)
        self._title_var.set(presentation.name)
        self._hint_var.set(presentation.tooltip)
        self._type_var.set(presentation.category)
        self._put("x_cells", _format_number(pixels_to_cells(x_px)))
        self._put("y_cells", _format_number(pixels_to_cells(y_px)))
        self._put("rotation", str(rotation))
        self._units_var.set(
            f"Equivalencia: X {pixels_to_mm(x_px) / 10:.1f} cm · Y {pixels_to_mm(y_px) / 10:.1f} cm"
        )

    def collect_updates(self) -> Optional[dict[str, Any]]:
        if self._obj is None:
            return None
        try:
            x_cells = float(self._entries["x_cells"].get().strip())
            y_cells = float(self._entries["y_cells"].get().strip())
            rotation = int(self._entries["rotation"].get().strip())
        except ValueError:
            return None
        return {
            "x_px": cells_to_pixels(x_cells),
            "y_px": cells_to_pixels(y_cells),
            "rotation": rotation,
        }

    def _put(self, key: str, value: str) -> None:
        self._entries[key].insert(0, value)


def _format_number(value: float) -> str:
    return str(int(value)) if value.is_integer() else f"{value:.2f}".rstrip("0").rstrip(".")
