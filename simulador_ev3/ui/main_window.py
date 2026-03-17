"""
main_window.py — Ventana principal del Simulador EV3 Pybricks.

Diseño de la ventana (layout):
  ┌────────────────────────────────────────────────────────┐
  │  Menú: Archivo | Ejemplos | Ayuda                      │
  ├─────────────────────┬──────────────────────────────────┤
  │  WorldCanvas        │ Panel derecho (PanedWindow):      │
  │  (lienzo 2-D del   │   ┌─ BrickPanel (estado LED/LCD) ─┤
  │   mundo)            │   └─ TelemetryPanel (motores…)   │
  ├─────────────────────┴──────────────────────────────────┤
  │  EditorPanel (editor Python + botones Run/Stop)        │
  └────────────────────────────────────────────────────────┘

La ventana llama a `SimulationService` cada 20 ms
(≈ 50 Hz) mediante `after(20, _tick)`.

Uso:
    from simulador_ev3.ui.main_window import EV3SimulatorApp
    app = EV3SimulatorApp()
    app.mainloop()
"""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional

from simulador_ev3.application.simulation_service import SimulationService
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.examples.example_catalog import ExampleCatalog
from simulador_ev3.ui.world_canvas   import WorldCanvas
from simulador_ev3.ui.editor_panel  import EditorPanel
from simulador_ev3.ui.brick_panel   import BrickPanel
from simulador_ev3.ui.telemetry_panel import TelemetryPanel

# Directorio de ejemplos (relativo a la raíz del proyecto)
_EXAMPLES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "Documentos", "Ejemplos"
)
_WORLDS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "Documentos", "Mundos"
)

_SCENARIOS: list[tuple[str, str, str]] = [
    ("Seguidor de línea", "01_linea_negra.json", "06_siguelineas_basico.py"),
    ("Ultrasonido + obstáculos", "02_obstaculos_beacon.json", "05_esquiva_obstaculos.py"),
    ("Test pantalla/altavoz", "02_obstaculos_beacon.json", "12_pantalla_altavoz_test.py"),
]

# Periodo del tick en ms (≈50 Hz)
_TICK_MS = 20


class EV3SimulatorApp(tk.Tk):
    """
    Ventana principal del simulador EV3.

    Args:
        world_config:  SimEngineConfig con las dimensiones del mundo y
                       posición inicial del robot.  Si None, se usan
                       valores por defecto (mundo 2000 × 2000 mm).
    """

    def __init__(self, world_config: Optional[SimEngineConfig] = None) -> None:
        super().__init__()
        self.title("Simulador EV3 Pybricks")
        self.geometry("1280x800")
        self.minsize(900, 600)
        self.configure(bg="#ECEFF1")

        # Servicio de simulación (capa de aplicación)
        self._service = SimulationService(config=world_config)
        self._service.set_snapshot_callback(self._on_snapshot)
        self._service.set_error_callback(self._on_error)
        self._service.set_status_callback(self._on_status)
        self._examples = ExampleCatalog(_EXAMPLES_DIR)

        # Pose inicial elegida por el usuario. None = usar config actual.
        self._pending_robot_pose: Optional[tuple[float, float, float]] = None
        self._hover_robot_pos: Optional[tuple[float, float]] = None

        # Construir la interfaz
        self._build_menu()
        self._build_layout()

        # Arrancar el ciclo de ticks
        self._tick_id: Optional[str] = None
        self._resize_after_id: Optional[str] = None
        self._schedule_tick()

        # Layout responsivo al cambiar tamaño de ventana
        self.bind("<Configure>", self._on_window_resize)
        self.after_idle(self._apply_responsive_layout)

        # Al cerrar la ventana, detener la simulación
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Construcción de la UI
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        self.configure(menu=menubar)

        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nuevo script",    command=self._cmd_new)
        file_menu.add_separator()
        file_menu.add_command(label="Salir",           command=self._on_close)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        # Menú Ejemplos
        examples_menu = tk.Menu(menubar, tearoff=0)
        self._populate_examples_menu(examples_menu)
        menubar.add_cascade(label="Ejemplos", menu=examples_menu)

        # Menú Mundos
        worlds_menu = tk.Menu(menubar, tearoff=0)
        worlds_menu.add_command(label="Cargar mundo JSON…", command=self._cmd_load_world)
        worlds_menu.add_separator()
        self._populate_worlds_menu(worlds_menu)
        menubar.add_cascade(label="Mundos", menu=worlds_menu)

        # Menú Escenarios (mundo + ejemplo)
        scenario_menu = tk.Menu(menubar, tearoff=0)
        self._populate_scenarios_menu(scenario_menu)
        menubar.add_cascade(label="Escenarios", menu=scenario_menu)

        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Acerca de…", command=self._cmd_about)
        menubar.add_cascade(label="Ayuda", menu=help_menu)

    def _populate_examples_menu(self, menu: tk.Menu) -> None:
        """Añade un ítem por cada *.py en el directorio de ejemplos."""
        examples = self._examples.list_examples()
        if not examples:
            menu.add_command(label="(No hay ejemplos)", state=tk.DISABLED)
            return
        for example in examples:
            menu.add_command(
                label=example.name,
                command=lambda p=str(example.path): self._load_example(p),
            )

    def _populate_worlds_menu(self, menu: tk.Menu) -> None:
        if not os.path.isdir(_WORLDS_DIR):
            menu.add_command(label="(No hay mundos)", state=tk.DISABLED)
            return
        files = sorted(
            f for f in os.listdir(_WORLDS_DIR)
            if f.lower().endswith(".json")
        )
        if not files:
            menu.add_command(label="(No hay mundos)", state=tk.DISABLED)
            return
        for file_name in files:
            path = os.path.join(_WORLDS_DIR, file_name)
            menu.add_command(
                label=file_name,
                command=lambda p=path: self._load_world(p),
            )

    def _populate_scenarios_menu(self, menu: tk.Menu) -> None:
        if not _SCENARIOS:
            menu.add_command(label="(No hay escenarios)", state=tk.DISABLED)
            return

        for label, world_file, example_file in _SCENARIOS:
            menu.add_command(
                label=label,
                command=lambda w=world_file, e=example_file: self._apply_scenario(w, e),
            )

    def _build_layout(self) -> None:
        """Construye el layout principal (PanedWindow horizontal + editor abajo)."""
        # PanedWindow vertical: mundo+telemetría arriba, editor abajo
        self._vpane = tk.PanedWindow(self, orient=tk.VERTICAL, sashwidth=6,
                                     bg="#B0BEC5", sashrelief=tk.RAISED)
        self._vpane.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # ── Parte superior: lienzo + panel derecho ──
        top_frame = tk.Frame(self._vpane, bg="#ECEFF1")
        self._vpane.add(top_frame, minsize=350, stretch="always")

        self._hpane = tk.PanedWindow(top_frame, orient=tk.HORIZONTAL, sashwidth=6,
                                     bg="#B0BEC5", sashrelief=tk.RAISED)
        self._hpane.pack(fill=tk.BOTH, expand=True)

        # WorldCanvas (izquierda) — envuelta en un frame con barra de ayuda
        engine_cfg = self._service.engine._cfg
        ww = engine_cfg.world_width_mm
        wh = engine_cfg.world_height_mm

        canvas_frame = tk.Frame(self._hpane, bg="#ECEFF1")
        self._hpane.add(canvas_frame, minsize=300, stretch="always")

        # Barra informativa de colocación del robot
        self._placement_bar = tk.Label(
            canvas_frame,
            text="Haz clic en el mapa para colocar el robot antes de ejecutar",
            bg="#E3F2FD", fg="#0D47A1",
            font=("Segoe UI", 9), anchor="w", padx=8, pady=3,
        )
        self._placement_bar.pack(side=tk.TOP, fill=tk.X)

        self._canvas = WorldCanvas(canvas_frame, world_w_mm=ww, world_h_mm=wh)
        self._canvas.pack(fill=tk.BOTH, expand=True)

        self._refresh_world_canvas()

        # Activar modo de colocación (antes de correr código)
        self._activate_placement_mode()

        # Panel derecho: BrickPanel + TelemetryPanel
        self._right_pane = tk.PanedWindow(self._hpane, orient=tk.VERTICAL, sashwidth=4,
                                          bg="#B0BEC5", sashrelief=tk.RAISED)
        self._hpane.add(self._right_pane, minsize=240, stretch="always")

        self._brick_panel     = BrickPanel(self._right_pane)
        self._telemetry_panel = TelemetryPanel(self._right_pane)
        self._right_pane.add(self._brick_panel,     minsize=160, stretch="always")
        self._right_pane.add(self._telemetry_panel, minsize=200, stretch="always")

        # ── Parte inferior: Editor ──
        self._editor = EditorPanel(
            self._vpane,
            on_run=self._cmd_run,
            on_stop=self._cmd_stop,
        )
        self._vpane.add(self._editor, minsize=180, stretch="always")

    def _on_window_resize(self, _event) -> None:
        """Aplica layout responsivo con debounce en cada resize de la ventana."""
        if self._resize_after_id:
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(60, self._apply_responsive_layout)

    # ------------------------------------------------------------------
    # Modo de colocación del robot
    # ------------------------------------------------------------------

    def _activate_placement_mode(self) -> None:
        """Habilita el clic en el canvas para fijar la posición inicial."""
        self._canvas.enable_placement_mode(
            callback=self._on_canvas_placement,
            hover_callback=self._on_canvas_hover,
        )
        cfg = self._service.engine._cfg
        x0, y0, theta0 = cfg.robot_x0_mm, cfg.robot_y0_mm, cfg.robot_theta0_deg
        self._pending_robot_pose = (x0, y0, theta0)
        self._hover_robot_pos = None
        self._canvas.draw_placement_marker(x0, y0, theta0)
        self._refresh_placement_bar()

    def _deactivate_placement_mode(self) -> None:
        """Deshabilita el modo de colocación durante la simulación."""
        self._canvas.disable_placement_mode()
        self._hover_robot_pos = None
        self._placement_bar.config(
            text="Simulacion en curso",
            bg="#E8F5E9", fg="#1B5E20",
        )

    def _on_canvas_hover(self, x_mm: float, y_mm: float) -> None:
        """Actualiza la ayuda con coordenadas en tiempo real."""
        self._hover_robot_pos = (x_mm, y_mm)
        self._refresh_placement_bar()

    def _on_canvas_placement(self, x_mm: float, y_mm: float, theta_deg: float) -> None:
        """Callback: el usuario ajusto la pose inicial del robot."""
        self._pending_robot_pose = (x_mm, y_mm, theta_deg)
        self._service.set_robot_start(x_mm, y_mm, theta_deg)
        self._refresh_placement_bar()

    def _refresh_placement_bar(self) -> None:
        if self._service.is_running:
            return

        pose = self._pending_robot_pose
        hover = self._hover_robot_pos
        cursor_text = ""
        if hover is not None:
            cursor_text = f" | Cursor: ({hover[0]:.0f} mm, {hover[1]:.0f} mm)"

        if pose is None:
            self._placement_bar.config(
                text=(
                    "Haz clic para fijar la posicion inicial. "
                    "Arrastra o usa la rueda para orientar."
                    f"{cursor_text}"
                ),
                bg="#E3F2FD",
                fg="#0D47A1",
            )
            return

        x_mm, y_mm, theta_deg = pose
        self._placement_bar.config(
            text=(
                f"Robot inicial: ({x_mm:.0f} mm, {y_mm:.0f} mm), "
                f"theta {theta_deg:.0f} deg. "
                "Clic para mover, arrastra o rueda para orientar, Ejecutar para iniciar."
                f"{cursor_text}"
            ),
            bg="#E8F5E9",
            fg="#1B5E20",
        )

    def _apply_responsive_layout(self) -> None:
        """Ajusta posiciones de sashes para distribuir espacios proporcionalmente."""
        self._resize_after_id = None
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1:
            return

        # Proporciones base
        top_h = max(320, int(height * 0.62))
        right_w = max(320, int(width * 0.30))
        right_x = max(280, width - right_w)
        brick_h = max(140, int(top_h * 0.34))

        try:
            self._vpane.sash_place(0, 0, top_h)
        except Exception:  # noqa: BLE001
            pass
        try:
            self._hpane.sash_place(0, right_x, 0)
        except Exception:  # noqa: BLE001
            pass
        try:
            self._right_pane.sash_place(0, 0, brick_h)
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    # Tick del engine vía Tkinter after()
    # ------------------------------------------------------------------

    def _schedule_tick(self) -> None:
        self._tick_id = self.after(_TICK_MS, self._tick)

    def _tick(self) -> None:
        """
        Llamado por Tkinter cada _TICK_MS ms.
        Delega al service.tick() (que llama al engine manualmente si
        el EngineThread no gestiona el loop, o simplemente es un hook
        para la UI cuando el loop corre en background).
        """
        self._schedule_tick()   # reprogramar ANTES de cualquier excepción

    # ------------------------------------------------------------------
    # Callbacks del SimulationService
    # ------------------------------------------------------------------

    def _on_snapshot(self, dto) -> None:
        """Recibe el SnapshotDTO desde el EngineThread — DEBE serializar a Tkinter."""
        # after_idle garantiza que la actualización de widgets ocurre
        # en el hilo de Tkinter (MainThread)
        self.after_idle(self._apply_snapshot, dto)

    def _apply_snapshot(self, dto) -> None:
        """Actualiza los widgets con el snapshot (ejecutado en MainThread)."""
        try:
            self._canvas.update_from_dto(dto)
            self._brick_panel.update_from_dto(dto)
            self._telemetry_panel.update_from_dto(dto)
        except Exception:  # noqa: BLE001
            pass

    def _on_error(self, payload: dict) -> None:
        """Muestra el error del script en el editor y en un diálogo."""
        msg = payload.get("error", "Error desconocido")
        self.after_idle(self._editor.set_status, f"Error: {msg}", "#B71C1C")
        self.after_idle(messagebox.showerror, "Error en script", msg)

    def _on_status(self, status: str) -> None:
        status_map = {
            "started":      ("Ejecutando…",      "#1565C0"),
            "paused":       ("Pausado",            "#F57F17"),
            "resumed":      ("Ejecutando…",      "#1565C0"),
            "stopped":      ("Detenido",           "#424242"),
            "error":        ("Error",              "#B71C1C"),
            "reset":        ("Listo",              "#212121"),
            "world_loaded": ("Mundo cargado",      "#2E7D32"),
        }
        msg, color = status_map.get(status, (status, "#212121"))
        self.after_idle(self._editor.set_status, msg, color)

        # Re-habilitar modo de colocación al terminar la simulación
        if status in ("stopped", "error", "reset"):
            self.after_idle(self._activate_placement_mode)

    # ------------------------------------------------------------------
    # Comandos de la UI
    # ------------------------------------------------------------------

    def _cmd_run(self, source_code: str) -> None:
        """Llamado por EditorPanel cuando el usuario pulsa Ejecutar."""
        # Deshabilitar modo de colocación durante la ejecución
        self._deactivate_placement_mode()
        self._canvas.reset()
        self._brick_panel.reset()
        self._telemetry_panel.reset()
        self._service.load_script(source_code)
        self._service.start()

    def _cmd_stop(self) -> None:
        """Llamado por EditorPanel cuando el usuario pulsa Detener."""
        self._service.stop()

    def _cmd_new(self) -> None:
        """Nuevo script en blanco."""
        if self._service.is_running:
            if not messagebox.askyesno("Nuevo script",
                                       "La simulación está corriendo. ¿Detener?"):
                return
            self._service.stop()
        self._editor.set_code("# Nuevo script\n")

    def _load_example(self, path: str) -> None:
        """Carga un script de ejemplo en el editor."""
        if self._service.is_running:
            self._service.stop()
        try:
            self._editor.load_file(path)
        except OSError as exc:
            messagebox.showerror("Error al cargar ejemplo", str(exc))

    def _cmd_load_world(self) -> None:
        path = filedialog.askopenfilename(
            title="Cargar mundo JSON",
            initialdir=_WORLDS_DIR,
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
        )
        if path:
            self._load_world(path)

    def _load_world(self, path: str) -> None:
        try:
            self._service.load_world_file(path)
            self._refresh_world_canvas()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error al cargar mundo", str(exc))

    def _apply_scenario(self, world_file: str, example_file: str) -> None:
        """Carga un mundo preset y un ejemplo asociado en un solo paso."""
        world_path = os.path.join(_WORLDS_DIR, world_file)
        example_path = os.path.join(_EXAMPLES_DIR, example_file)

        if self._service.is_running:
            self._service.stop(reason="scenario_change")

        if not os.path.exists(world_path):
            messagebox.showerror("Escenario", f"No existe el mundo: {world_file}")
            return
        if not os.path.exists(example_path):
            messagebox.showerror("Escenario", f"No existe el ejemplo: {example_file}")
            return

        try:
            self._service.load_world_file(world_path)
            self._editor.load_file(example_path)
            self._refresh_world_canvas()
            self._editor.set_status(
                f"Escenario cargado: {os.path.splitext(example_file)[0]}",
                "#2E7D32",
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Escenario", str(exc))

    def _refresh_world_canvas(self) -> None:
        world = self._service.engine.world
        surface_cells = []
        cell_size = world.surface.cell_size_mm
        for (col, row), cell in world.surface._grid.items():
            surface_cells.append({
                "x_mm": col * cell_size,
                "y_mm": row * cell_size,
                "size_mm": cell_size,
                "color": cell.color.name,
            })
        self._canvas.set_surface_cells(surface_cells)

        obstacles = []
        for obstacle in world.obstacles:
            min_x, min_y, max_x, max_y = obstacle.aabb
            obstacles.append({
                "x_mm": min_x,
                "y_mm": min_y,
                "width_mm": max_x - min_x,
                "height_mm": max_y - min_y,
            })
        self._canvas.set_obstacles(obstacles)

    def _cmd_about(self) -> None:
        messagebox.showinfo(
            "Acerca de",
            "Simulador EV3 Pybricks\n"
            "Versión 1.0\n\n"
            "Simulador de robots LEGO EV3 con API compatible Pybricks.\n"
            "Desarrollado con Python + Tkinter.",
        )

    def _on_close(self) -> None:
        """Cierra la aplicación de forma limpia."""
        if self._tick_id:
            self.after_cancel(self._tick_id)
        self._service.stop()
        self.destroy()


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main() -> None:
    app = EV3SimulatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
