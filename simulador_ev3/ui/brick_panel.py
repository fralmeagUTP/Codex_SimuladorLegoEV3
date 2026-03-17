"""
brick_panel.py — Panel de visualización del estado del EV3 Brick.

Muestra en tiempo real:
  • LED de estado (color según SnapshotDTO.brick["led"]).
  • Pantalla del EV3 (texto de la última llamada a screen.print()).
  • Altavoz — indicador visual de sonido activo.

Actualización: llamar a `update_from_dto(dto)` en cada tick.
"""
from __future__ import annotations

import tkinter as tk
from typing import Optional

from simulador_ev3.application.snapshot_dto import SnapshotDTO

# Paleta de colores LED
_LED_COLORS: dict[str, str] = {
    "RED":    "#F44336",
    "GREEN":  "#4CAF50",
    "ORANGE": "#FF9800",
    "YELLOW": "#FFEB3B",
    None:     "#BDBDBD",      # apagado
}

_SCREEN_BG = "#1B2631"   # fondo oscuro tipo LCD
_SCREEN_FG = "#A9DFBF"   # verde LCD
_BRICK_BG  = "#263238"
_LABEL_FG  = "#ECEFF1"


class BrickPanel(tk.Frame):
    """
    Panel visual del EV3 Brick.

    Args:
        parent:  Widget padre.
        **kwargs: Argumentos para tk.Frame.
    """

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        kwargs.setdefault("bg", _BRICK_BG)
        kwargs.setdefault("padx", 8)
        kwargs.setdefault("pady", 8)
        super().__init__(parent, **kwargs)

        self._build()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def update_from_dto(self, dto: SnapshotDTO) -> None:
        """Actualiza todos los subpaneles con el último snapshot."""
        brick = dto.brick
        self._update_led(brick.get("led"))
        self._update_screen(brick.get("screen"))
        self._update_speaker(brick.get("speaker"))

    def reset(self) -> None:
        """Devuelve el panel a su estado inicial (brick apagado)."""
        self._update_led(None)
        self._update_screen(None)
        self._update_speaker(None)

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------

    def _build(self) -> None:
        tk.Label(self, text="EV3 Brick", bg=_BRICK_BG, fg=_LABEL_FG,
                 font=("Arial", 11, "bold")).pack(pady=(0, 6))
        self._build_led()
        tk.Frame(self, height=1, bg="#455A64").pack(fill=tk.X, pady=6)
        self._build_screen()
        tk.Frame(self, height=1, bg="#455A64").pack(fill=tk.X, pady=6)
        self._build_speaker()

    def _build_led(self) -> None:
        row = tk.Frame(self, bg=_BRICK_BG)
        row.pack(fill=tk.X)
        tk.Label(row, text="LED:", bg=_BRICK_BG, fg=_LABEL_FG,
                 font=("Arial", 10)).pack(side=tk.LEFT)
        self._led_canvas = tk.Canvas(row, width=24, height=24,
                                     bg=_BRICK_BG, highlightthickness=0)
        self._led_canvas.pack(side=tk.LEFT, padx=6)
        self._led_oval = self._led_canvas.create_oval(
            2, 2, 22, 22, fill=_LED_COLORS[None], outline="#FFFFFF"
        )
        self._led_label = tk.Label(row, text="—", bg=_BRICK_BG, fg=_LABEL_FG,
                                   font=("Arial", 10))
        self._led_label.pack(side=tk.LEFT)

    def _build_screen(self) -> None:
        tk.Label(self, text="Pantalla:", bg=_BRICK_BG, fg=_LABEL_FG,
                 font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self._screen_text = tk.Text(
            self, height=5, width=22,
            bg=_SCREEN_BG, fg=_SCREEN_FG,
            font=("Courier New", 9),
            state=tk.DISABLED,
            relief=tk.SUNKEN,
            bd=2,
        )
        self._screen_text.pack(fill=tk.X, padx=2)

    def _build_speaker(self) -> None:
        row = tk.Frame(self, bg=_BRICK_BG)
        row.pack(fill=tk.X)
        tk.Label(row, text="🔔 Altavoz:", bg=_BRICK_BG, fg=_LABEL_FG,
                 font=("Arial", 10)).pack(side=tk.LEFT)
        self._speaker_label = tk.Label(row, text="—", bg=_BRICK_BG, fg=_LABEL_FG,
                                       font=("Arial", 10))
        self._speaker_label.pack(side=tk.LEFT, padx=6)

    # ------------------------------------------------------------------
    # Actualizaciones
    # ------------------------------------------------------------------

    def _update_led(self, color_name: Optional[str]) -> None:
        fill = _LED_COLORS.get(color_name, _LED_COLORS[None])
        self._led_canvas.itemconfigure(self._led_oval, fill=fill)
        self._led_label.configure(text=color_name or "Apagado")

    def _update_screen(self, text: Optional[str]) -> None:
        self._screen_text.configure(state=tk.NORMAL)
        self._screen_text.delete("1.0", tk.END)
        if text:
            self._screen_text.insert("1.0", text)
        self._screen_text.configure(state=tk.DISABLED)

    def _update_speaker(self, speaker_data: Optional[dict]) -> None:
        if speaker_data:
            freq = speaker_data.get("freq", "?")
            dur  = speaker_data.get("duration_ms", "?")
            vol  = speaker_data.get("volume", 50)
            label = f"▶ {freq} Hz | {dur} ms | {vol}%"
        else:
            label = "—"
        self._speaker_label.configure(text=label)
