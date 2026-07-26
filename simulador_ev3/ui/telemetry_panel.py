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
from simulador_ev3.shared.ui_design_tokens import LIGHT_TOKENS, ThemeTokens, tokens_for_theme

_BG = LIGHT_TOKENS.surface
_HDR_BG = LIGHT_TOKENS.surface
_HDR_FG = LIGHT_TOKENS.text
_VAL_FG = LIGHT_TOKENS.text
_COL_FG = LIGHT_TOKENS.danger
_MONO = ("Segoe UI", 9)
_LABEL = ("Segoe UI", 9)
_BOLD = ("Segoe UI", 9, "bold")
_EMPTY = "-"


def _mm_to_cm(value: float) -> float:
    return float(value) / 10.0


_MOTOR_PORTS = ("A", "B", "C", "D")
_SENSOR_PORTS = ("S1", "S2", "S3", "S4")


def _apply_scrollbar_style(sb: tk.Scrollbar, tokens: ThemeTokens = LIGHT_TOKENS) -> None:
    sb.configure(
        bg=tokens.border,
        activebackground=tokens.primary_active,
        troughcolor=tokens.surface_muted,
        relief=tk.RAISED,
        bd=1,
        highlightthickness=1,
        highlightbackground=tokens.border,
    )


class TelemetryPanel(tk.Frame):
    """Panel de telemetria (scroll unico) para robot, motores, sensores y tiempo."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        kwargs.setdefault("bg", _BG)
        kwargs.setdefault("padx", 0)
        kwargs.setdefault("pady", 0)
        super().__init__(parent, **kwargs)

        self._motor_vars: dict[str, dict[str, tk.StringVar]] = {}
        self._sensor_vars: dict[str, dict[str, tk.StringVar]] = {}
        self._motor_frames: dict[str, tk.LabelFrame] = {}
        self._motor_containers: dict[str, tk.Frame] = {}
        self._sensor_frames: dict[str, tk.LabelFrame] = {}
        self._theme = "light"

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
        self._canvas_window = self._scroll_canvas.create_window((0, 0), window=self._content, anchor=tk.NW)

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

    def set_execution_status(self, status: str) -> None:
        labels = {
            "started": "EJECUTANDO", "resumed": "EJECUTANDO", "paused": "PAUSADO",
            "finished": "FINALIZADO", "timed_out": "TIEMPO AGOTADO", "error": "ERROR",
            "stopped": "DETENIDO", "reset": "IDLE", "world_loaded": "IDLE",
        }
        self._summary_status.set(labels.get(status, str(status).upper()))
        tokens = tokens_for_theme(self._theme)
        color = tokens.success if status in {"started", "resumed", "finished", "reset", "world_loaded"} else tokens.text
        if status in {"paused", "timed_out"}:
            color = tokens.warning
        elif status == "error":
            color = tokens.danger
        if self._summary_status_cell is not None:
            self._summary_status_cell.configure(fg=color)

    def reset(self) -> None:
        for motor_vars in self._motor_vars.values():
            for value_var in motor_vars.values():
                value_var.set(_EMPTY)
            motor_vars["state"].set("Sin conectar")

        for sensor_vars in self._sensor_vars.values():
            for value_var in sensor_vars.values():
                value_var.set(_EMPTY)
            sensor_vars["type"].set("Sin conectar")

        self._var_x.set(_EMPTY)
        self._var_y.set(_EMPTY)
        self._var_theta.set(_EMPTY)
        self._var_tick.set(_EMPTY)
        self._var_time.set(_EMPTY)
        self._var_col.set("OK")
        self._lbl_col.configure(fg=_VAL_FG)
        self._set_visible_motor_ports(set())
        self._set_visible_sensor_ports(set())

    def set_theme(self, theme: str) -> None:
        """Actualiza también las etiquetas creadas dinámicamente por telemetría."""
        tokens = tokens_for_theme(theme)
        self._theme = theme
        self.configure(bg=tokens.surface)
        self._scroll_canvas.configure(bg=tokens.surface, highlightbackground=tokens.border)
        self._content.configure(bg=tokens.surface)
        _apply_scrollbar_style(self._scrollbar, tokens)

        def visit(widget: tk.Misc) -> None:
            role = str(getattr(widget, "_telemetry_role", ""))
            changes: dict[str, str] = {}
            if role == "top_header":
                changes = {"bg": tokens.primary, "fg": "white"}
            elif role == "section_header":
                changes = {"bg": tokens.surface_muted, "fg": tokens.primary}
            elif role == "card":
                changes = {"bg": tokens.surface_muted, "fg": tokens.text, "highlightbackground": tokens.border}
            elif role == "label":
                changes = {"bg": tokens.surface_muted, "fg": tokens.text_muted}
            elif role == "value":
                changes = {"bg": tokens.surface_muted, "fg": tokens.text}
            elif isinstance(widget, (tk.Frame, tk.LabelFrame, tk.Label)):
                changes["bg"] = tokens.surface
                if isinstance(widget, (tk.Label, tk.LabelFrame)):
                    changes["fg"] = tokens.text
            if changes:
                try:
                    widget.configure(**changes)
                except tk.TclError:
                    pass
            for child in widget.winfo_children():
                visit(child)

        visit(self._content)
        collision_color = tokens.danger if self._var_col.get() == "COLISION" else tokens.text
        self._lbl_col.configure(fg=collision_color)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        _header(self._content, "TELEMETRÍA DEL ROBOT", primary=True)
        self._summary_status = tk.StringVar(value="LISTO")
        self._summary_time = tk.StringVar(value="--")
        self._summary_tick = tk.StringVar(value="----")
        self._summary_collision = tk.StringVar(value="OK")
        self._summary_status_cell: tk.Label | None = None
        self._summary_collision_cell: tk.Label | None = None
        summary = tk.Frame(self._content, bg=_BG, relief=tk.SOLID, bd=1)
        summary.pack(fill=tk.X, padx=8, pady=(5, 3))
        summary.grid_columnconfigure(1, weight=1)
        summary.grid_columnconfigure(3, weight=1)
        summary.grid_columnconfigure(5, weight=1)
        summary.grid_columnconfigure(7, weight=1)
        summary_pairs = (
            ("Estado:", self._summary_status),
            ("Tiempo:", self._summary_time),
            ("Tick:", self._summary_tick),
            ("Colisión:", self._summary_collision),
        )
        for column, (label, value) in enumerate(summary_pairs):
            tk.Label(summary, text=label, font=_LABEL, anchor="center").grid(
                row=0, column=column * 2, sticky="nsew", padx=8, pady=5
            )
            cell = tk.Label(summary, textvariable=value, font=_BOLD, anchor="center")
            cell.grid(
                row=0, column=column * 2 + 1, sticky="nsew", padx=8, pady=5
            )
            if column == 0:
                self._summary_status_cell = cell
            elif column == 3:
                self._summary_collision_cell = cell
        columns = tk.Frame(self._content, bg=_BG)
        columns.pack(fill=tk.BOTH, expand=True, padx=6, pady=(2, 6))
        columns.grid_columnconfigure(0, weight=18)
        columns.grid_columnconfigure(1, weight=28)
        columns.grid_columnconfigure(2, weight=28)
        columns.grid_columnconfigure(3, weight=26)
        robot_column = tk.Frame(columns, bg=_BG)
        motors_ab_column = tk.Frame(columns, bg=_BG)
        motors_cd_column = tk.Frame(columns, bg=_BG)
        sensors_column = tk.Frame(columns, bg=_BG)
        robot_column.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        motors_ab_column.grid(row=0, column=1, sticky="nsew", padx=4)
        motors_cd_column.grid(row=0, column=2, sticky="nsew", padx=4)
        sensors_column.grid(row=0, column=3, sticky="nsew", padx=(4, 0))

        self._build_robot_section(robot_column)
        self._build_time_section(robot_column)
        self._build_motors_section(motors_ab_column, ("A", "B"), "Motores A-B (28%)")
        self._build_motors_section(motors_cd_column, ("C", "D"), "Motores C-D (28%)")
        self._build_sensors_section(sensors_column)

    def _build_robot_section(self, parent: tk.Widget) -> None:
        grid = _card(parent, "Robot")
        grid.pack(fill=tk.X, padx=4, pady=4)
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        self._var_x = _row(grid, "X (cm):", 0)
        self._var_y = _row(grid, "Y (cm):", 1)
        self._var_theta = _row(grid, "Theta (°):", 2)
        self._var_col = tk.StringVar(value="OK")
        tk.Label(grid, text="Colision:", bg=_BG, font=_LABEL).grid(row=3, column=0, sticky=tk.W)
        self._lbl_col = tk.Label(grid, textvariable=self._var_col, bg=_BG, font=_MONO, fg=_VAL_FG)
        self._lbl_col.grid(row=3, column=1, sticky=tk.W)

    def _build_motors_section(self, parent: tk.Widget, ports: tuple[str, str], title: str) -> None:
        _header(parent, title)
        container = tk.Frame(parent, bg=_BG)
        container.pack(fill=tk.X)
        for port in ports:
            grp = _card(container, f"Motor {port}")
            self._motor_containers[port] = container
            self._motor_frames[port] = grp
            self._motor_vars[port] = {
                "speed": _row(grp, "Vel (°/s):", 0),
                "angle": _row(grp, "Ángulo (0–360°):", 1),
                "angle_norm": tk.StringVar(value=_EMPTY),
                "state": _row(grp, "Estado:", 2),
            }

    def _build_sensors_section(self, parent: tk.Widget) -> None:
        _header(parent, "Sensores")
        self._sensors_container = tk.Frame(parent, bg=_BG)
        self._sensors_container.pack(fill=tk.X)
        self._sensors_empty = tk.Label(
            self._sensors_container,
            text="Sin sensores",
            bg=_BG,
            fg=LIGHT_TOKENS.text_muted,
            font=_LABEL,
        )
        self._sensors_empty.pack(anchor=tk.W, padx=10, pady=3)
        for port in _SENSOR_PORTS:
            grp = _card(self._sensors_container, f"Sensor {port}")
            grp.grid_columnconfigure(0, weight=1)
            grp.grid_columnconfigure(1, weight=2)
            self._sensor_frames[port] = grp
            self._sensor_vars[port] = {
                "type": _sensor_row(grp, "Tipo:", 0),
                "value": _sensor_row(grp, "Valor:", 1, emphasize=True),
            }

    def _build_time_section(self, parent: tk.Widget) -> None:
        grid = _card(parent, "Estado")
        grid.pack(fill=tk.X, padx=4, pady=(0, 4))
        self._var_tick = _row(grid, "Tick:", 0)
        self._var_time = _row(grid, "Tiempo:", 1)

    # ------------------------------------------------------------------
    # Scroll helpers
    # ------------------------------------------------------------------

    def _on_content_configure(self, _event) -> None:
        self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self._scroll_canvas.itemconfigure(self._canvas_window, width=event.width)

    def _bind_mousewheel_recursive(self, widget: tk.Misc) -> None:
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
        self._var_x.set(f"{_mm_to_cm(dto.robot['x_mm']):.1f}")
        self._var_y.set(f"{_mm_to_cm(dto.robot['y_mm']):.1f}")
        self._var_theta.set(f"{dto.robot['theta_deg']:.1f}")
        if dto.colliding:
            self._var_col.set("COLISION")
            self._lbl_col.configure(fg=tokens_for_theme(self._theme).danger)
        else:
            self._var_col.set("OK")
            self._lbl_col.configure(fg=tokens_for_theme(self._theme).text)

    def _update_motors(self, motors: list[dict]) -> None:
        for motor_values in self._motor_vars.values():
            motor_values["speed"].set(_EMPTY)
            motor_values["angle"].set(_EMPTY)
            motor_values["angle_norm"].set(_EMPTY)
            motor_values["state"].set("Sin conectar")

        for motor in motors:
            port = str(motor.get("port", "")).upper()
            vars_by_key: dict[str, tk.StringVar] | None = self._motor_vars.get(port)
            if vars_by_key is None:
                continue

            speed = motor.get("speed")
            angle = motor.get("angle")
            state = motor.get("state")

            if isinstance(speed, (int, float)):
                vars_by_key["speed"].set(f"{speed:.0f}")
            if isinstance(angle, (int, float)):
                normalized = (float(angle) % 360.0 + 360.0) % 360.0
                vars_by_key["angle"].set(f"{normalized:.1f}°")
                vars_by_key["angle_norm"].set(f"{normalized:.1f}°")
            if state is not None:
                vars_by_key["state"].set(str(state))
        self._set_visible_motor_ports(
            {
                str(motor.get("port", "")).upper()
                for motor in motors
                if str(motor.get("port", "")).upper() in _MOTOR_PORTS
            }
        )

    def _set_visible_motor_ports(self, ports: set[str]) -> None:
        del ports
        for frame in self._motor_frames.values():
            frame.pack(fill=tk.X, padx=4, pady=3)

    def _update_sensors(self, sensors: list[dict]) -> None:
        for sensor_values in self._sensor_vars.values():
            sensor_values["type"].set("Sin conectar")
            sensor_values["value"].set(_EMPTY)

        for sensor in sensors:
            port = str(sensor.get("port", "")).upper()
            vars_by_key: dict[str, tk.StringVar] | None = self._sensor_vars.get(port)
            if vars_by_key is None:
                continue

            vars_by_key["type"].set(str(sensor.get("type", _EMPTY)))
            val = sensor.get("value", sensor.get("data", _EMPTY))
            if isinstance(val, dict) and "distance_mm" in val:
                parts: list[str] = []
                dist_mm = val.get("distance_mm")
                if isinstance(dist_mm, (int, float)):
                    parts.append(f"distance_cm={_mm_to_cm(dist_mm):.1f}")
                for key, item in val.items():
                    if key == "distance_mm":
                        continue
                    parts.append(f"{key}={item}")
                vars_by_key["value"].set(", ".join(parts) if parts else _EMPTY)
            else:
                vars_by_key["value"].set(str(val))
        self._set_visible_sensor_ports(
            {
                str(sensor.get("port", "")).upper()
                for sensor in sensors
                if str(sensor.get("port", "")).upper() in _SENSOR_PORTS
            }
        )

    def _set_visible_sensor_ports(self, ports: set[str]) -> None:
        del ports
        forget_empty = getattr(self._sensors_empty, "pack_forget", None)
        if callable(forget_empty):
            forget_empty()
        for frame in self._sensor_frames.values():
            frame.pack(fill=tk.X, padx=4, pady=2)

    def _update_time(self, dto: SnapshotDTO) -> None:
        self._var_tick.set(str(dto.tick))
        self._var_time.set(f"{dto.sim_time_s:.3f} s")
        collision = "COLISIÓN" if dto.colliding else "OK"
        self._summary_time.set(f"{dto.sim_time_s:.3f} s")
        self._summary_tick.set(str(dto.tick))
        self._summary_collision.set(collision)
        if self._summary_collision_cell is not None:
            color = tokens_for_theme(self._theme).danger if dto.colliding else tokens_for_theme(self._theme).success
            self._summary_collision_cell.configure(fg=color)


def _header(parent: tk.Widget, text: str, *, primary: bool = False) -> None:
    frame = tk.Frame(parent, bg=_HDR_BG)
    setattr(frame, "_telemetry_role", "top_header" if primary else "section_header")  # noqa: B010
    frame.pack(fill=tk.X, pady=(0, 0))
    label = tk.Label(
        frame,
        text=text,
        bg=_HDR_BG,
        fg=_HDR_FG,
        font=_BOLD,
        anchor=tk.W,
    )
    setattr(label, "_telemetry_role", "top_header" if primary else "section_header")  # noqa: B010
    label.pack(side=tk.LEFT, padx=10, pady=5 if primary else 4)


def _card(parent: tk.Widget, title: str) -> tk.LabelFrame:
    card = tk.LabelFrame(
        parent, text=title, bg=LIGHT_TOKENS.surface_muted, fg=LIGHT_TOKENS.primary,
        font=_BOLD, padx=3, pady=3, relief=tk.SOLID, bd=1,
        highlightthickness=1, highlightbackground=LIGHT_TOKENS.border,
    )
    setattr(card, "_telemetry_role", "card")  # noqa: B010
    return card


def _separator(parent: tk.Widget) -> None:
    tk.Frame(parent, height=1, bg="#E3E9F1").pack(fill=tk.X, pady=0)


def _row(parent: tk.Widget, label: str, row: int) -> tk.StringVar:
    var = tk.StringVar(value=_EMPTY)
    label_widget = tk.Label(parent, text=label, bg=_BG, font=_LABEL, anchor=tk.W)
    setattr(label_widget, "_telemetry_role", "label")  # noqa: B010
    label_widget.grid(
        row=row,
        column=0,
        sticky=tk.W,
        padx=10,
        pady=1,
    )
    value_widget = tk.Label(
        parent,
        textvariable=var,
        bg=_BG,
        font=_MONO,
        fg=_VAL_FG,
        anchor=tk.W,
    )
    setattr(value_widget, "_telemetry_role", "value")  # noqa: B010
    value_widget.grid(row=row, column=1, sticky=tk.W, padx=(0, 8), pady=1)
    return var


def _sensor_row(parent: tk.Widget, label: str, row: int, *, emphasize: bool = False) -> tk.StringVar:
    """Fila legible para sensores; permite valores extensos sin truncarlos."""
    var = tk.StringVar(value=_EMPTY)
    label_widget = tk.Label(parent, text=label, bg=_BG, font=_LABEL, anchor=tk.NW)
    setattr(label_widget, "_telemetry_role", "label")  # noqa: B010
    label_widget.grid(
        row=row, column=0, sticky=tk.NW, padx=8, pady=2
    )
    value_widget = tk.Label(
        parent,
        textvariable=var,
        bg=_BG,
        font=_BOLD if emphasize else _MONO,
        fg=_VAL_FG,
        anchor=tk.W,
        justify=tk.LEFT,
        wraplength=190,
    )
    setattr(value_widget, "_telemetry_role", "value")  # noqa: B010
    value_widget.grid(row=row, column=1, sticky=tk.W, padx=(0, 8), pady=2)
    _attach_value_tooltip(value_widget, var)
    return var


def _attach_value_tooltip(widget: tk.Label, value: tk.StringVar) -> None:
    """Muestra el valor completo de un sensor cuando la celda se queda corta."""
    tip: tk.Toplevel | None = None

    def show(_event) -> None:
        nonlocal tip
        text = value.get()
        if not text or text == _EMPTY:
            return
        tip = tk.Toplevel(widget)
        tip.wm_overrideredirect(True)
        tip.geometry(f"+{widget.winfo_rootx() + 10}+{widget.winfo_rooty() + widget.winfo_height() + 6}")
        tk.Label(tip, text=text, justify=tk.LEFT, padx=8, pady=5, relief=tk.SOLID, bd=1).pack()

    def hide(_event) -> None:
        nonlocal tip
        if tip is not None:
            tip.destroy()
            tip = None

    widget.bind("<Enter>", show)
    widget.bind("<Leave>", hide)
