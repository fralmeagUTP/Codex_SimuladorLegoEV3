"""
brick_panel.py - Panel de visualizacion del estado del EV3 Brick.

Muestra en tiempo real:
  - LED de estado (color segun SnapshotDTO.brick["led"]).
  - Pantalla EV3 simulada en formato 178x128 monocromo horizontal.
  - Altavoz - indicador visual de sonido activo.

Actualizacion: llamar a update_from_dto(dto) en cada tick.
"""

from __future__ import annotations

import tkinter as tk
from typing import Optional

from simulador_ev3.application.snapshot_dto import SnapshotDTO
from simulador_ev3.shared.ui_design_tokens import LIGHT_TOKENS

# Paleta de colores LED
_LED_COLORS: dict[str | None, str] = {
    "RED": "#F44336",
    "GREEN": "#4CAF50",
    "ORANGE": "#FF9800",
    "YELLOW": "#FFEB3B",
    None: "#C9CED6",  # apagado
}

# Paleta general del panel
_BRICK_BG = LIGHT_TOKENS.surface
_LABEL_FG = LIGHT_TOKENS.text
_DIVIDER = LIGHT_TOKENS.border

# Paleta de LCD EV3 simulado (monocromo)
_LCD_FRAME = "#4F585F"
_LCD_BG = "#E6ECD6"
_LCD_FG = "#111111"
_LCD_SCANLINE = "#D7DFCA"
_LCD_LED_ON = "#F8F8EF"
_LCD_LED_OFF = "#A4AA95"
_LCD_CANVAS_W = 507
# Debe dejar espacio visible para la tabla Robot/Estado bajo la LCD en la
# franja inferior de la ventana, incluso sin redimensionar el panel.
_LCD_CANVAS_H = 169


class BrickPanel(tk.Frame):
    """
    Panel visual del EV3 Brick.

    Args:
        parent: Widget padre.
        **kwargs: Argumentos para tk.Frame.
    """

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        kwargs.setdefault("bg", _BRICK_BG)
        kwargs.setdefault("padx", 0)
        kwargs.setdefault("pady", 0)
        super().__init__(parent, **kwargs)

        self._screen_state = self._default_screen_state()
        self._scroll_canvas = tk.Canvas(self, bg=_BRICK_BG, highlightthickness=0)
        self._scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self._scroll_canvas.yview)
        self._scroll_canvas.configure(yscrollcommand=self._scrollbar.set)
        self._scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._content = tk.Frame(self._scroll_canvas, bg=_BRICK_BG)
        self._content_window = self._scroll_canvas.create_window((0, 0), window=self._content, anchor=tk.NW)
        self._content.bind("<Configure>", self._on_content_configure)
        self._scroll_canvas.bind("<Configure>", self._on_panel_configure)
        self._build()

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    def update_from_dto(self, dto: SnapshotDTO) -> None:
        """Actualiza todos los subpaneles con el ultimo snapshot."""
        brick = dto.brick
        self._update_led(brick.get("led"))
        self._update_screen(brick.get("screen"))
        self._update_speaker(brick.get("speaker"))
        self._update_robot_state(dto)

    def reset(self) -> None:
        """Devuelve el panel a su estado inicial (brick apagado)."""
        self._update_led(None)
        self._update_screen(None)
        self._update_speaker(None)
        for variable in self._robot_vars.values():
            variable.set("-")

    # ------------------------------------------------------------------
    # Construccion
    # ------------------------------------------------------------------

    def _build(self) -> None:
        tk.Label(self._content, text="EV3 Brick", bg=_BRICK_BG, fg=_LABEL_FG, font=("Segoe UI", 14, "bold"),
                 anchor="center", relief=tk.SOLID, bd=1).pack(fill=tk.X, padx=8, pady=(8, 0), ipady=12)
        status_row = tk.Frame(self._content, bg=_BRICK_BG, relief=tk.SOLID, bd=1)
        status_row.pack(fill=tk.X, padx=8)
        status_row.grid_columnconfigure(0, weight=1)
        status_row.grid_columnconfigure(1, weight=1)
        self._build_led(status_row)
        self._build_speaker(status_row)
        self._build_screen()
        self._build_robot_state()

    def _build_led(self, row: tk.Widget) -> None:
        cell = tk.Frame(row, bg=_BRICK_BG, relief=tk.SOLID, bd=0)
        cell.grid(row=0, column=0, sticky="nsew")
        tk.Label(cell, text="LED:", bg=_BRICK_BG, fg=_LABEL_FG, font=("Segoe UI", 11)).pack(
            side=tk.LEFT, padx=(16, 6), pady=12
        )
        self._led_canvas = tk.Canvas(
            cell,
            width=24,
            height=24,
            bg=_BRICK_BG,
            highlightthickness=0,
        )
        self._led_canvas.pack(side=tk.LEFT, padx=6)
        self._led_oval = self._led_canvas.create_oval(
            2,
            2,
            22,
            22,
            fill=_LED_COLORS[None],
            outline="#778",
        )
        self._led_label = tk.Label(cell, text="Apagado", bg=_BRICK_BG, fg=_LABEL_FG, font=("Segoe UI", 9))
        self._led_label.pack(side=tk.LEFT)

    def _build_screen(self) -> None:
        tk.Label(
            self._content,
            text="Pantalla LCD EV3 (178x128):",
            bg=_BRICK_BG,
            fg=_LABEL_FG,
            font=("Segoe UI", 11), anchor="center",
        ).pack(fill=tk.X, padx=16, pady=(10, 4))

        self._screen_canvas = tk.Canvas(
            self._content,
            width=_LCD_CANVAS_W,
            height=_LCD_CANVAS_H,
            bg=_BRICK_BG, highlightthickness=0, bd=1, relief=tk.SOLID,
        )
        self._screen_canvas.pack(fill=tk.X, padx=16)
        self._screen_canvas.bind("<Configure>", self._on_screen_resize)
        self._render_screen()

    def _build_speaker(self, row: tk.Widget) -> None:
        cell = tk.Frame(row, bg=_BRICK_BG, relief=tk.SOLID, bd=0)
        cell.grid(row=0, column=1, sticky="nsew")
        tk.Label(cell, text="Altavoz:", bg=_BRICK_BG, fg=_LABEL_FG, font=("Segoe UI", 11)).pack(
            side=tk.LEFT, padx=(18, 8), pady=12
        )
        self._speaker_label = tk.Label(
            cell,
            text="Inactivo",
            bg=_BRICK_BG,
            fg=_LABEL_FG,
            font=("Segoe UI", 9),
        )
        self._speaker_label.pack(side=tk.LEFT, padx=6)

    def _build_robot_state(self) -> None:
        """Muestra el estado del robot junto al brick, debajo de la LCD."""
        section = tk.Frame(self._content, bg=_BRICK_BG, relief=tk.SOLID, bd=1)
        self._robot_state_section = section
        section.pack(fill=tk.X, padx=16, pady=(8, 8))
        tk.Label(
            section,
            text="ROBOT / ESTADO",
            bg=_BRICK_BG,
            fg=_LABEL_FG,
            font=("Segoe UI", 11, "bold"),
            anchor="center",
        ).grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(4, 2))
        self._robot_vars = {key: tk.StringVar(value="-") for key in ("x", "y", "theta")}
        labels = (("X:", "x", ""), ("Y:", "y", ""), ("Theta:", "theta", ""))
        for row, (label, key, unit) in enumerate(labels, start=1):
            tk.Label(section, text=label, bg=_BRICK_BG, fg=_LABEL_FG, font=("Segoe UI", 10), anchor=tk.W).grid(
                row=row, column=0, sticky="nsew", padx=(10, 4), pady=1
            )
            value = tk.Label(section, textvariable=self._robot_vars[key], bg=_BRICK_BG, fg=_LABEL_FG,
                             font=("Segoe UI", 10), anchor="center")
            value.grid(row=row, column=1, sticky="nsew", padx=(4, 10), pady=1)
            if unit:
                tk.Label(section, text=unit, bg=_BRICK_BG, fg=_LABEL_FG, font=("Segoe UI", 9), anchor=tk.W).grid(
                    row=row, column=2, sticky=tk.W, padx=(0, 10), pady=1
                )
        section.grid_columnconfigure(0, weight=1)
        section.grid_columnconfigure(1, weight=1)

    def _on_content_configure(self, _event) -> None:
        self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all"))

    def _on_panel_configure(self, event) -> None:
        self._scroll_canvas.itemconfigure(self._content_window, width=event.width)

    # ------------------------------------------------------------------
    # Actualizaciones
    # ------------------------------------------------------------------

    def _update_led(self, color_name: Optional[str]) -> None:
        fill = _LED_COLORS.get(color_name, _LED_COLORS[None])
        self._led_canvas.itemconfigure(self._led_oval, fill=fill)
        self._led_label.configure(text=color_name or "Apagado")

    def _update_screen(self, screen_data: Optional[dict | str]) -> None:
        state = self._default_screen_state()
        if isinstance(screen_data, dict):
            state["lines"] = [str(ln) for ln in screen_data.get("lines", [])]
            state["draw_ops"] = [dict(op) for op in screen_data.get("draw_ops", []) if isinstance(op, dict)]
            state["width_px"] = int(screen_data.get("width_px", state["width_px"]))
            state["height_px"] = int(screen_data.get("height_px", state["height_px"]))
            state["backlight_leds"] = int(screen_data.get("backlight_leds", state["backlight_leds"]))
        elif isinstance(screen_data, str):
            state["lines"] = screen_data.splitlines() or [screen_data]
        elif screen_data:
            text = str(screen_data)
            state["lines"] = text.splitlines() or [text]

        self._screen_state = state
        self._render_screen()

    def _update_speaker(self, speaker_data: Optional[dict]) -> None:
        if speaker_data:
            freq = speaker_data.get("freq", "?")
            dur = speaker_data.get("duration_ms", "?")
            vol = speaker_data.get("volume", 50)
            label = f"ON {freq} Hz | {dur} ms | {vol}%"
        else:
            label = "-"
        self._speaker_label.configure(text=label)

    def _update_robot_state(self, dto: SnapshotDTO) -> None:
        robot = dto.robot
        self._robot_vars["x"].set(f"{float(robot.get('x_mm', 0)) / 10.0:.1f}")
        self._robot_vars["y"].set(f"{float(robot.get('y_mm', 0)) / 10.0:.1f}")
        self._robot_vars["theta"].set(f"{float(robot.get('theta_deg', 0)):.1f}")

    # ------------------------------------------------------------------
    # Render LCD
    # ------------------------------------------------------------------

    def _on_screen_resize(self, _event) -> None:
        self._render_screen()

    def _render_screen(self) -> None:
        canvas = self._screen_canvas
        canvas.delete("all")

        cw = canvas.winfo_width() or _LCD_CANVAS_W
        ch = canvas.winfo_height() or _LCD_CANVAS_H
        if cw <= 4 or ch <= 4:
            return

        logical_w = max(1, int(self._screen_state["width_px"]))
        logical_h = max(1, int(self._screen_state["height_px"]))
        margin = 4.0
        scale = min((cw - 2 * margin) / logical_w, (ch - 2 * margin) / logical_h)
        if scale <= 0:
            return

        disp_w = logical_w * scale
        disp_h = logical_h * scale
        x0 = (cw - disp_w) / 2
        y0 = (ch - disp_h) / 2
        x1 = x0 + disp_w
        y1 = y0 + disp_h

        # Marco fisico del LCD
        canvas.create_rectangle(x0 - 4, y0 - 4, x1 + 4, y1 + 4, fill=_LCD_FRAME, outline="")
        canvas.create_rectangle(x0, y0, x1, y1, fill=_LCD_BG, outline="#A6AE98", width=1)

        # Scanlines para dar sensacion de matriz monocromo
        scan_step = max(2, int(round(scale * 2.5)))
        y: float = float(int(y0))
        while y <= int(y1):
            canvas.create_line(x0, y, x1, y, fill=_LCD_SCANLINE)
            y += scan_step

        # Simula 4 LEDs blancos de retroiluminacion
        leds = max(1, min(4, int(self._screen_state["backlight_leds"])))
        led_r = max(2.0, scale * 1.2)
        for i in range(leds):
            cx = x0 + ((i + 1) * disp_w / (leds + 1))
            cy = y0 + max(4.0, scale * 2.0)
            canvas.create_oval(
                cx - led_r,
                cy - led_r,
                cx + led_r,
                cy + led_r,
                fill=_LCD_LED_ON,
                outline=_LCD_LED_OFF,
            )

        def px_to_canvas_x(px: float) -> float:
            p = max(0.0, min(float(logical_w - 1), float(px)))
            return x0 + (p * scale)

        def px_to_canvas_y(py: float) -> float:
            p = max(0.0, min(float(logical_h - 1), float(py)))
            return y0 + (p * scale)

        for op in self._screen_state.get("draw_ops", []):
            kind = str(op.get("op", "")).lower()
            color = _LCD_FG if int(op.get("color", 1)) else _LCD_BG
            if kind == "pixel":
                x = px_to_canvas_x(op.get("x", 0))
                y = px_to_canvas_y(op.get("y", 0))
                r = max(1.0, scale * 0.6)
                canvas.create_rectangle(x - r, y - r, x + r, y + r, fill=color, outline="")
            elif kind == "line":
                canvas.create_line(
                    px_to_canvas_x(op.get("x1", 0)),
                    px_to_canvas_y(op.get("y1", 0)),
                    px_to_canvas_x(op.get("x2", 0)),
                    px_to_canvas_y(op.get("y2", 0)),
                    fill=color,
                    width=max(1, int(round(scale * 0.9))),
                )
            elif kind == "circle":
                cx = px_to_canvas_x(op.get("x", 0))
                cy = px_to_canvas_y(op.get("y", 0))
                radius = max(0.0, float(op.get("r", 0)) * scale)
                fill = color if bool(op.get("fill", False)) else ""
                canvas.create_oval(
                    cx - radius,
                    cy - radius,
                    cx + radius,
                    cy + radius,
                    outline=color,
                    fill=fill,
                    width=max(1, int(round(scale * 0.8))),
                )
            elif kind == "box":
                x = px_to_canvas_x(op.get("x", 0))
                y = px_to_canvas_y(op.get("y", 0))
                w = max(0.0, float(op.get("w", 0)) * scale)
                h = max(0.0, float(op.get("h", 0)) * scale)
                fill = color if bool(op.get("fill", False)) else ""
                canvas.create_rectangle(
                    x,
                    y,
                    x + w,
                    y + h,
                    outline=color,
                    fill=fill,
                    width=max(1, int(round(scale * 0.8))),
                )

        # Texto de la pantalla (hasta 8 lineas visibles), escalado al tamano real.
        # Al derivar desde disp_h evitamos texto diminuto cuando el canvas crece.
        line_step = max(10.0, disp_h / 8.3)
        font_size = max(6, int(round(line_step * 0.41)))  # ~30% menor que 0.58
        tx = x0 + max(6.0, scale * 4.0)
        ty = y0 + max(10.0, line_step * 0.52)
        for row_idx, line in enumerate(self._screen_state["lines"][:8]):
            y_line = ty + row_idx * line_step
            if y_line > y1 - 4:
                break
            canvas.create_text(
                tx,
                y_line,
                anchor=tk.NW,
                text=str(line),
                fill=_LCD_FG,
                font=("Courier New", font_size),
            )

    @staticmethod
    def _default_screen_state() -> dict:
        return {
            "lines": [],
            "draw_ops": [],
            "width_px": 178,
            "height_px": 128,
            "backlight_leds": 4,
        }
