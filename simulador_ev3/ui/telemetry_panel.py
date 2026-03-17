"""
telemetry_panel.py — Panel de telemetría en tiempo real del simulador EV3.

Muestra en cada tick (actualización vía `update_from_dto`):
  • Posición del robot (x, y, θ).
  • Estado de los 4 motores: puerto · velocidad · ángulo · estado.
  • Lecturas de sensores adjuntos: puerto · tipo · valor.
  • Tiempo de simulación y tick número.
  • Indicador visual de colisión.
"""
from __future__ import annotations

import tkinter as tk

from simulador_ev3.application.snapshot_dto import SnapshotDTO

_BG       = "#FAFAFA"
_HDR_BG   = "#ECEFF1"
_HDR_FG   = "#37474F"
_VAL_FG   = "#1565C0"
_COL_FG   = "#D32F2F"
_MONO     = ("Courier New", 10)
_LABEL    = ("Arial", 10)
_BOLD     = ("Arial", 10, "bold")


def _apply_scrollbar_style(sb: tk.Scrollbar) -> None:
    """Aplica estilo visible y consistente para barras de scroll en Tk."""
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
    """
    Panel de telemetría que muestra el estado del robot en tiempo real.

    Args:
        parent:  Widget padre.
        **kwargs: Argumentos para tk.Frame.
    """

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        kwargs.setdefault("bg", _BG)
        kwargs.setdefault("padx", 8)
        kwargs.setdefault("pady", 8)
        super().__init__(parent, **kwargs)

        self._motor_vars:  list[dict[str, tk.StringVar]] = []
        self._sensor_vars: list[dict[str, tk.StringVar]] = []

        self._scroll_canvas = tk.Canvas(self, bg=_BG, highlightthickness=0)
        self._scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL,
                                       command=self._scroll_canvas.yview)
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

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def update_from_dto(self, dto: SnapshotDTO) -> None:
        """Refresca todos los indicadores con el último Snapshot."""
        self._update_robot(dto)
        self._update_motors(dto.motors)
        self._update_sensors(dto.sensors)
        self._update_time(dto)

    def reset(self) -> None:
        """Pone a cero todos los valores."""
        for mv in self._motor_vars:
            for v in mv.values():
                v.set("—")
        for sv in self._sensor_vars:
            for v in sv.values():
                v.set("—")
        self._var_x.set("—")
        self._var_y.set("—")
        self._var_theta.set("—")
        self._var_tick.set("—")
        self._var_time.set("—")
        self._var_col.set("OK")
        self._lbl_col.configure(fg=_VAL_FG)

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------

    def _build(self) -> None:
        self._build_robot_section()
        _separator(self._content)
        self._build_motors_section()
        _separator(self._content)
        self._build_sensors_section()
        _separator(self._content)
        self._build_time_section()

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

    def _build_robot_section(self) -> None:
        _header(self._content, "🤖 Robot")
        grid = tk.Frame(self._content, bg=_BG)
        grid.pack(fill=tk.X)
        self._var_x     = _row(grid, "X (mm):", 0)
        self._var_y     = _row(grid, "Y (mm):", 1)
        self._var_theta = _row(grid, "θ (deg):", 2)
        self._var_col   = tk.StringVar(value="OK")
        tk.Label(grid, text="Colisión:", bg=_BG, font=_LABEL).grid(
            row=3, column=0, sticky=tk.W)
        self._lbl_col = tk.Label(grid, textvariable=self._var_col,
                                 bg=_BG, font=_MONO, fg=_VAL_FG)
        self._lbl_col.grid(row=3, column=1, sticky=tk.W)

    def _build_motors_section(self) -> None:
        _header(self._content, "⚙ Motores")
        ports = ("A", "B", "C", "D")
        for port in ports:
            grp = tk.LabelFrame(self._content, text=port, bg=_BG, font=_LABEL, pady=2)
            grp.pack(fill=tk.X, padx=4, pady=2)
            mv = {
                "speed": _row(grp, "Vel (°/s):", 0),
                "angle": _row(grp, "Ang (°):",  1),
                "state": _row(grp, "Estado:",   2),
            }
            self._motor_vars.append(mv)

    def _build_sensors_section(self) -> None:
        _header(self._content, "📡 Sensores")
        ports = ("S1", "S2", "S3", "S4")
        for port in ports:
            grp = tk.LabelFrame(self._content, text=port, bg=_BG, font=_LABEL, pady=2)
            grp.pack(fill=tk.X, padx=4, pady=2)
            sv = {
                "type":  _row(grp, "Tipo:",  0),
                "value": _row(grp, "Valor:", 1),
            }
            self._sensor_vars.append(sv)

    def _build_time_section(self) -> None:
        _header(self._content, "⏱ Tiempo")
        grid = tk.Frame(self._content, bg=_BG)
        grid.pack(fill=tk.X)
        self._var_tick = _row(grid, "Tick:",   0)
        self._var_time = _row(grid, "Tiempo:", 1)

    # ------------------------------------------------------------------
    # Actualizaciones
    # ------------------------------------------------------------------

    def _update_robot(self, dto: SnapshotDTO) -> None:
        self._var_x.set(f"{dto.robot['x_mm']:.1f}")
        self._var_y.set(f"{dto.robot['y_mm']:.1f}")
        self._var_theta.set(f"{dto.robot['theta_deg']:.1f}")
        if dto.colliding:
            self._var_col.set("⚠ COLISIÓN")
            self._lbl_col.configure(fg=_COL_FG)
        else:
            self._var_col.set("OK")
            self._lbl_col.configure(fg=_VAL_FG)

    def _update_motors(self, motors: list[dict]) -> None:
        for idx, m in enumerate(motors):
            if idx >= len(self._motor_vars):
                break
            mv = self._motor_vars[idx]
            mv["speed"].set(f"{m['speed']:.0f}")
            mv["angle"].set(f"{m['angle']:.1f}°")
            mv["state"].set(m["state"])

    def _update_sensors(self, sensors: list[dict]) -> None:
        for idx, s in enumerate(sensors):
            if idx >= len(self._sensor_vars):
                break
            sv = self._sensor_vars[idx]
            sv["type"].set(s.get("type", "—"))
            val = s.get("value", s.get("data", "—"))
            sv["value"].set(str(val)[:30])   # truncar si es muy largo

    def _update_time(self, dto: SnapshotDTO) -> None:
        self._var_tick.set(str(dto.tick))
        self._var_time.set(f"{dto.sim_time_s:.3f} s")


# ---------------------------------------------------------------------------
# Helpers de construcción
# ---------------------------------------------------------------------------

def _header(parent: tk.Widget, text: str) -> None:
    frm = tk.Frame(parent, bg=_HDR_BG)
    frm.pack(fill=tk.X, pady=(6, 2))
    tk.Label(frm, text=text, bg=_HDR_BG, fg=_HDR_FG, font=_BOLD,
             anchor=tk.W).pack(side=tk.LEFT, padx=4, pady=1)


def _separator(parent: tk.Widget) -> None:
    tk.Frame(parent, height=1, bg="#BDBDBD").pack(fill=tk.X, pady=2)


def _row(parent: tk.Widget, label: str, row: int) -> tk.StringVar:
    """Crea una fila etiqueta+valor y devuelve la StringVar del valor."""
    var = tk.StringVar(value="—")
    tk.Label(parent, text=label, bg=_BG, font=_LABEL, anchor=tk.W).grid(
        row=row, column=0, sticky=tk.W, padx=4)
    tk.Label(parent, textvariable=var, bg=_BG, font=_MONO, fg=_VAL_FG,
             anchor=tk.W).grid(row=row, column=1, sticky=tk.W)
    return var
