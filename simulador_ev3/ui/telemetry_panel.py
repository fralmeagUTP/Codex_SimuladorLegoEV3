"""
telemetry_panel.py - Panel de telemetria en tiempo real del simulador EV3.

Muestra en cada tick:
  - Estado del robot (x, y, theta, colision)
  - Estado de motores A/B/C/D
  - Estado de sensores S1/S2/S3/S4
  - Tiempo de simulacion
"""
from __future__ import annotations

import tkinter as tk

from simulador_ev3.application.snapshot_dto import SnapshotDTO

_BG = "#FAFAFA"
_HDR_BG = "#ECEFF1"
_HDR_FG = "#37474F"
_VAL_FG = "#1565C0"
_COL_FG = "#D32F2F"
_MONO = ("Courier New", 10)
_LABEL = ("Arial", 10)
_BOLD = ("Arial", 10, "bold")
_EMPTY = "-"

_MOTOR_PORTS = ("A", "B", "C", "D")
_SENSOR_PORTS = ("S1", "S2", "S3", "S4")


def _apply_scrollbar_style(sb: tk.Scrollbar) -> None:
    sb.configure(
        bg="#B0BEC5",
        activebackground="#78909C",
        troughcolor="#ECEFF1",
        relief=tk.RAISED,
        bd=1,
        highlightthickness=1,
        highlightbackground="#90A4AE",
    )


class TelemetryPanel(tk.Frame):
    """Panel de telemetria (scroll unico) para robot, motores, sensores y tiempo."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        kwargs.setdefault("bg", _BG)
        kwargs.setdefault("padx", 8)
        kwargs.setdefault("pady", 8)
        super().__init__(parent, **kwargs)

        self._motor_vars: dict[str, dict[str, tk.StringVar]] = {}
        self._sensor_vars: dict[str, dict[str, tk.StringVar]] = {}

        self._scroll_canvas = tk.Canvas(self, bg=_BG, highlightthickness=0)
        self._scrollbar = tk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self._scroll_canvas.yview,
        )
        self._scroll_canvas.configure(yscrollcommand=self._scrollbar.set)
        _apply_scrollbar_style(self._scrollbar)

        self._scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._content = tk.Frame(self._scroll_canvas, bg=_BG)
        self._canvas_window = self._scroll_canvas.create_window(
            (0, 0), window=self._content, anchor=tk.NW
        )

        self._content.bind("<Configure>", self._on_content_configure)
        self._scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        self._scroll_canvas.bind("<MouseWheel>", self._on_panel_mousewheel)
        self._content.bind("<MouseWheel>", self._on_panel_mousewheel)
        self._scroll_canvas.bind("<Button-4>", self._on_panel_mousewheel)
        self._content.bind("<Button-4>", self._on_panel_mousewheel)
        self._scroll_canvas.bind("<Button-5>", self._on_panel_mousewheel)
        self._content.bind("<Button-5>", self._on_panel_mousewheel)

        self._build()
        self._bind_mousewheel_recursive(self._content)
        self.reset()

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    def update_from_dto(self, dto: SnapshotDTO) -> None:
        self._update_robot(dto)
        self._update_motors(dto.motors)
        self._update_sensors(dto.sensors)
        self._update_time(dto)

    def reset(self) -> None:
        for motor_vars in self._motor_vars.values():
            for value_var in motor_vars.values():
                value_var.set(_EMPTY)

        for sensor_vars in self._sensor_vars.values():
            for value_var in sensor_vars.values():
                value_var.set(_EMPTY)

        self._var_x.set(_EMPTY)
        self._var_y.set(_EMPTY)
        self._var_theta.set(_EMPTY)
        self._var_tick.set(_EMPTY)
        self._var_time.set(_EMPTY)
        self._var_col.set("OK")
        self._lbl_col.configure(fg=_VAL_FG)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        self._build_robot_section()
        _separator(self._content)
        self._build_motors_section()
        _separator(self._content)
        self._build_sensors_section()
        _separator(self._content)
        self._build_time_section()

    def _build_robot_section(self) -> None:
        _header(self._content, "Robot")
        grid = tk.Frame(self._content, bg=_BG)
        grid.pack(fill=tk.X)
        self._var_x = _row(grid, "X (mm):", 0)
        self._var_y = _row(grid, "Y (mm):", 1)
        self._var_theta = _row(grid, "Theta (deg):", 2)
        self._var_col = tk.StringVar(value="OK")
        tk.Label(grid, text="Colision:", bg=_BG, font=_LABEL).grid(
            row=3, column=0, sticky=tk.W
        )
        self._lbl_col = tk.Label(
            grid, textvariable=self._var_col, bg=_BG, font=_MONO, fg=_VAL_FG
        )
        self._lbl_col.grid(row=3, column=1, sticky=tk.W)

    def _build_motors_section(self) -> None:
        _header(self._content, "Motores")
        for port in _MOTOR_PORTS:
            grp = tk.LabelFrame(self._content, text=port, bg=_BG, font=_LABEL, pady=2)
            grp.pack(fill=tk.X, padx=4, pady=2)
            self._motor_vars[port] = {
                "speed": _row(grp, "Vel (deg/s):", 0),
                "angle": _row(grp, "Ang (deg):", 1),
                "state": _row(grp, "Estado:", 2),
            }

    def _build_sensors_section(self) -> None:
        _header(self._content, "Sensores")
        for port in _SENSOR_PORTS:
            grp = tk.LabelFrame(self._content, text=port, bg=_BG, font=_LABEL, pady=2)
            grp.pack(fill=tk.X, padx=4, pady=2)
            self._sensor_vars[port] = {
                "type": _row(grp, "Tipo:", 0),
                "value": _row(grp, "Valor:", 1),
            }

    def _build_time_section(self) -> None:
        _header(self._content, "Tiempo")
        grid = tk.Frame(self._content, bg=_BG)
        grid.pack(fill=tk.X)
        self._var_tick = _row(grid, "Tick:", 0)
        self._var_time = _row(grid, "Tiempo:", 1)

    # ------------------------------------------------------------------
    # Scroll helpers
    # ------------------------------------------------------------------

    def _on_content_configure(self, _event) -> None:
        self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self._scroll_canvas.itemconfigure(self._canvas_window, width=event.width)

    def _bind_mousewheel_recursive(self, widget: tk.Widget) -> None:
        widget.bind("<MouseWheel>", self._on_panel_mousewheel)
        widget.bind("<Button-4>", self._on_panel_mousewheel)
        widget.bind("<Button-5>", self._on_panel_mousewheel)
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child)

    def _on_panel_mousewheel(self, event) -> str:
        if hasattr(event, "delta") and event.delta:
            step = -1 if event.delta > 0 else 1
        elif getattr(event, "num", None) == 4:
            step = -1
        elif getattr(event, "num", None) == 5:
            step = 1
        else:
            step = 0
        if step != 0:
            self._scroll_canvas.yview_scroll(step, "units")
        return "break"

    # ------------------------------------------------------------------
    # Update helpers
    # ------------------------------------------------------------------

    def _update_robot(self, dto: SnapshotDTO) -> None:
        self._var_x.set(f"{dto.robot['x_mm']:.1f}")
        self._var_y.set(f"{dto.robot['y_mm']:.1f}")
        self._var_theta.set(f"{dto.robot['theta_deg']:.1f}")
        if dto.colliding:
            self._var_col.set("COLISION")
            self._lbl_col.configure(fg=_COL_FG)
        else:
            self._var_col.set("OK")
            self._lbl_col.configure(fg=_VAL_FG)

    def _update_motors(self, motors: list[dict]) -> None:
        for vars_by_key in self._motor_vars.values():
            vars_by_key["speed"].set(_EMPTY)
            vars_by_key["angle"].set(_EMPTY)
            vars_by_key["state"].set(_EMPTY)

        for motor in motors:
            port = str(motor.get("port", "")).upper()
            vars_by_key = self._motor_vars.get(port)
            if vars_by_key is None:
                continue

            speed = motor.get("speed")
            angle = motor.get("angle")
            state = motor.get("state")

            if isinstance(speed, (int, float)):
                vars_by_key["speed"].set(f"{speed:.0f}")
            if isinstance(angle, (int, float)):
                vars_by_key["angle"].set(f"{angle:.1f}deg")
            if state is not None:
                vars_by_key["state"].set(str(state))

    def _update_sensors(self, sensors: list[dict]) -> None:
        for vars_by_key in self._sensor_vars.values():
            vars_by_key["type"].set(_EMPTY)
            vars_by_key["value"].set(_EMPTY)

        for sensor in sensors:
            port = str(sensor.get("port", "")).upper()
            vars_by_key = self._sensor_vars.get(port)
            if vars_by_key is None:
                continue

            vars_by_key["type"].set(str(sensor.get("type", _EMPTY)))
            val = sensor.get("value", sensor.get("data", _EMPTY))
            vars_by_key["value"].set(str(val)[:40])

    def _update_time(self, dto: SnapshotDTO) -> None:
        self._var_tick.set(str(dto.tick))
        self._var_time.set(f"{dto.sim_time_s:.3f} s")


def _header(parent: tk.Widget, text: str) -> None:
    frame = tk.Frame(parent, bg=_HDR_BG)
    frame.pack(fill=tk.X, pady=(6, 2))
    tk.Label(
        frame,
        text=text,
        bg=_HDR_BG,
        fg=_HDR_FG,
        font=_BOLD,
        anchor=tk.W,
    ).pack(side=tk.LEFT, padx=4, pady=1)


def _separator(parent: tk.Widget) -> None:
    tk.Frame(parent, height=1, bg="#BDBDBD").pack(fill=tk.X, pady=2)


def _row(parent: tk.Widget, label: str, row: int) -> tk.StringVar:
    var = tk.StringVar(value=_EMPTY)
    tk.Label(parent, text=label, bg=_BG, font=_LABEL, anchor=tk.W).grid(
        row=row,
        column=0,
        sticky=tk.W,
        padx=4,
    )
    tk.Label(
        parent,
        textvariable=var,
        bg=_BG,
        font=_MONO,
        fg=_VAL_FG,
        anchor=tk.W,
    ).grid(row=row, column=1, sticky=tk.W)
    return var
