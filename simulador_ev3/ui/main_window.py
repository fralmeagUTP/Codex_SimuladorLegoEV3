"""
main_window.py â€” Ventana principal del Simulador EV3 Pybricks.

DiseÃ±o de la ventana (layout):
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚  MenÃº: Archivo | Ejemplos | Ayuda                      â”‚
  â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
  â”‚  WorldCanvas        â”‚ Panel derecho (PanedWindow):      â”‚
  â”‚  (lienzo 2-D del   â”‚   â”Œâ”€ BrickPanel (estado LED/LCD) â”€â”¤
  â”‚   mundo)            â”‚   â””â”€ TelemetryPanel (motoresâ€¦)   â”‚
  â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
  â”‚  EditorPanel (editor Python + botones Run/Stop)        â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

La ventana llama a `SimulationService` cada 20 ms
(â‰ˆ 50 Hz) mediante `after(20, _tick)`.

Uso:
    from simulador_ev3.ui.main_window import EV3SimulatorApp
    app = EV3SimulatorApp()
    app.mainloop()
"""
from __future__ import annotations

import json
import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter import scrolledtext
from typing import Optional

from simulador_ev3.application.simulation_service import SimulationService
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.domain.editor.world_editor_model import DEFAULT_WORLD_MM
from simulador_ev3.examples.example_catalog import ExampleCatalog
from simulador_ev3.shared.paths import (
    resolve_examples_dir,
    resolve_manual_path,
    resolve_worlds_dir,
)
from simulador_ev3.ui.world_canvas   import WorldCanvas
from simulador_ev3.ui.editor_panel  import EditorPanel
from simulador_ev3.ui.brick_panel   import BrickPanel
from simulador_ev3.ui.telemetry_panel import TelemetryPanel

# Rutas canónicas compartidas (con fallback legacy).
_EXAMPLES_DIR = resolve_examples_dir()
_WORLDS_DIR = resolve_worlds_dir()
_MANUAL_PATH = resolve_manual_path()

_SCENARIOS: list[tuple[str, str, str]] = [
    ("Seguidor de línea", "01_linea_negra_basica.json", "11_siguelineas_basico.py"),
    ("Ultrasonido + obstáculos", "05_obstaculos_baliza_ir.json", "15_esquiva_obstaculos.py"),
    ("Test pantalla/altavoz", "05_obstaculos_baliza_ir.json", "02_intro_pantalla_altavoz.py"),
    ("Radar 360 ultrasonido", "12_radar_ultrasonido_360.json", "23_radar_ultrasonido_5grados.py"),
]

# Periodo del tick en ms (â‰ˆ50 Hz)
_TICK_MS = 20


class EV3SimulatorApp(tk.Tk):
    """
    Ventana principal del simulador EV3.

    Args:
        world_config:  SimEngineConfig con las dimensiones del mundo y
                       posiciÃ³n inicial del robot.  Si None, se usan
                       valores por defecto (mundo 2000 Ã— 2000 mm).
    """

    def __init__(self, world_config: Optional[SimEngineConfig] = None) -> None:
        super().__init__()
        self.title("Simulador EV3 Pybricks")
        self.geometry("1280x800")
        self.minsize(900, 600)
        self.configure(bg="#ECEFF1")

        # Servicio de simulaciÃ³n (capa de aplicaciÃ³n)
        effective_cfg = world_config or SimEngineConfig(
            world_width_mm=DEFAULT_WORLD_MM,
            world_height_mm=DEFAULT_WORLD_MM,
        )
        self._service = SimulationService(config=effective_cfg)
        self._service.set_snapshot_callback(self._on_snapshot)
        self._service.set_error_callback(self._on_error)
        self._service.set_status_callback(self._on_status)
        self._service.set_debug_callback(self._on_debug_event)
        self._examples = ExampleCatalog(_EXAMPLES_DIR)

        # Pose inicial elegida por el usuario. None = usar config actual.
        self._pending_robot_pose: Optional[tuple[float, float, float]] = None
        self._hover_robot_pos: Optional[tuple[float, float]] = None
        self._world_editor_window = None
        self._manual_window = None
        self._editor_world_placements: list[dict] = []
        self._debug_active = False
        self._execution_menu_locked = False
        self._lockable_menu_indices: tuple[int, ...] = ()

        # Construir la interfaz
        self._build_menu()
        self._build_layout()

        # Arrancar el ciclo de ticks
        self._tick_id: Optional[str] = None
        self._resize_after_id: Optional[str] = None
        self._schedule_tick()

        # Layout responsivo al cambiar tamaÃ±o de ventana
        self.bind("<Configure>", self._on_window_resize)
        self.after_idle(self._apply_responsive_layout)

        # Al cerrar la ventana, detener la simulaciÃ³n
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # ConstrucciÃ³n de la UI
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        self._menubar = menubar
        self.configure(menu=menubar)

        # MenÃº Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(
            label="Nuevo script",
            accelerator="Ctrl+N",
            command=self._cmd_new,
        )
        file_menu.add_command(
            label="Abrir script...",
            accelerator="Ctrl+O",
            command=self._cmd_open_script,
        )
        file_menu.add_command(
            label="Guardar script...",
            accelerator="Ctrl+S",
            command=self._cmd_save_script,
        )
        file_menu.add_separator()
        file_menu.add_command(label="Salir",           command=self._on_close)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        self.bind("<Control-n>", self._evt_new_script)
        self.bind("<Control-o>", self._evt_open_script)
        self.bind("<Control-s>", self._evt_save_script)

        # MenÃº Ejemplos
        examples_menu = tk.Menu(menubar, tearoff=0)
        self._populate_examples_menu(examples_menu)
        menubar.add_cascade(label="Ejemplos", menu=examples_menu)

        # MenÃº Mundos
        worlds_menu = tk.Menu(menubar, tearoff=0)
        worlds_menu.add_command(label="Mundo en blanco (sin mapa)", command=self._cmd_load_blank_world)
        worlds_menu.add_separator()
        worlds_menu.add_command(label="Cargar mundo JSON...", command=self._cmd_load_world)
        worlds_menu.add_command(label="Editor de mundos...", command=self._cmd_open_world_editor)
        worlds_menu.add_separator()
        self._populate_worlds_menu(worlds_menu)
        menubar.add_cascade(label="Mundos", menu=worlds_menu)

        # MenÃº Escenarios (mundo + ejemplo)
        scenario_menu = tk.Menu(menubar, tearoff=0)
        self._populate_scenarios_menu(scenario_menu)
        menubar.add_cascade(label="Escenarios", menu=scenario_menu)

        # MenÃº Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Manual de uso...", command=self._cmd_user_manual)
        help_menu.add_separator()
        help_menu.add_command(label="Acerca de...", command=self._cmd_about)
        menubar.add_cascade(label="Ayuda", menu=help_menu)

        self._lockable_menu_indices = (0, 1, 2, 3)
        self._update_menu_lock_state()

    def _update_menu_lock_state(self) -> None:
        """Deshabilita menus de trabajo durante una ejecucion activa."""
        state = tk.DISABLED if self._execution_menu_locked else tk.NORMAL
        menu = getattr(self, "_menubar", None)
        if menu is None:
            return
        entryconfigure = getattr(menu, "entryconfigure", None)
        if not callable(entryconfigure):
            return
        for idx in self._lockable_menu_indices:
            try:
                entryconfigure(idx, state=state)
            except Exception:  # noqa: BLE001
                continue

    def _set_execution_menu_locked(self, locked: bool) -> None:
        self._execution_menu_locked = bool(locked)
        self._update_menu_lock_state()

    def _guard_menu_locked(self) -> bool:
        if not self._execution_menu_locked:
            return False
        messagebox.showinfo(
            "Ejecucion en curso",
            "Opciones de menu bloqueadas durante la ejecucion. Usa Resetear para habilitarlas.",
        )
        return True

    def _populate_examples_menu(self, menu: tk.Menu) -> None:
        """AÃ±ade un Ã­tem por cada *.py en el directorio de ejemplos."""
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
        if not _WORLDS_DIR.is_dir():
            menu.add_command(label="(No hay mundos)", state=tk.DISABLED)
            return
        files = sorted(path.name for path in _WORLDS_DIR.glob("*.json"))
        if not files:
            menu.add_command(label="(No hay mundos)", state=tk.DISABLED)
            return
        for file_name in files:
            path = _WORLDS_DIR / file_name
            menu.add_command(
                label=file_name,
                command=lambda p=str(path): self._load_world(p),
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
        """Construye layout espejo de la web: simulacion izquierda, editor derecha."""
        self._root_hpane = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=6,
            bg="#B0BEC5",
            sashrelief=tk.RAISED,
        )
        self._root_hpane.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 0))

        # Columna izquierda: barra de control + mapa + telemetria/brick
        left_frame = tk.Frame(self._root_hpane, bg="#ECEFF1")
        self._root_hpane.add(left_frame, minsize=700, stretch="always")

        self._build_sim_control_bar(left_frame)

        map_frame = tk.Frame(left_frame, bg="#ECEFF1")
        map_frame.pack(fill=tk.BOTH, expand=True)

        map_header = tk.Frame(
            map_frame,
            bg="#FFFFFF",
            bd=1,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#D4DDE8",
        )
        map_header.pack(fill=tk.X, pady=(0, 1))
        tk.Label(
            map_header,
            text="Entorno de simulacion",
            bg="#FFFFFF",
            fg="#1D2D44",
            font=("Segoe UI", 10, "bold"),
        ).pack(side=tk.LEFT, padx=10, pady=6)
        self._world_name_var = tk.StringVar(value="Mundo actual: Basico")
        tk.Label(
            map_header,
            textvariable=self._world_name_var,
            bg="#FFFFFF",
            fg="#35506F",
            font=("Consolas", 9),
        ).pack(side=tk.LEFT, padx=(0, 8), pady=6)
        map_tools = tk.Frame(map_header, bg="#FFFFFF")
        map_tools.pack(side=tk.RIGHT, padx=(0, 8), pady=4)
        tk.Button(
            map_tools,
            text="+",
            width=3,
            command=self._cmd_map_zoom_in,
        ).pack(side=tk.LEFT, padx=2)
        tk.Button(
            map_tools,
            text="-",
            width=3,
            command=self._cmd_map_zoom_out,
        ).pack(side=tk.LEFT, padx=2)
        tk.Button(
            map_tools,
            text="[]",
            width=3,
            command=self._cmd_map_zoom_reset,
        ).pack(side=tk.LEFT, padx=2)

        engine_cfg = self._service.engine._cfg
        ww = engine_cfg.world_width_mm
        wh = engine_cfg.world_height_mm

        canvas_frame = tk.Frame(map_frame, bg="#ECEFF1")
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self._placement_bar = tk.Label(
            canvas_frame,
            text="Haz clic en el mapa para colocar el robot antes de ejecutar",
            bg="#E3F2FD", fg="#0D47A1",
            font=("Segoe UI", 9), anchor="w", padx=8, pady=3,
        )
        self._placement_bar.pack(side=tk.TOP, fill=tk.X)

        canvas_view = tk.Frame(canvas_frame, bg="#ECEFF1")
        canvas_view.pack(fill=tk.BOTH, expand=True)

        self._canvas = WorldCanvas(canvas_view, world_w_mm=ww, world_h_mm=wh)
        y_scroll = tk.Scrollbar(canvas_view, orient=tk.VERTICAL, command=self._canvas.yview)
        x_scroll = tk.Scrollbar(canvas_view, orient=tk.HORIZONTAL, command=self._canvas.xview)
        self._canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._refresh_world_canvas()
        self._activate_placement_mode()

        # Fila inferior: telemetria y brick como en la web
        self._bottom_pane = tk.PanedWindow(
            left_frame,
            orient=tk.HORIZONTAL,
            sashwidth=4,
            bg="#B0BEC5",
            sashrelief=tk.RAISED,
        )
        self._bottom_pane.pack(fill=tk.BOTH, padx=2, pady=(8, 0))

        self._telemetry_panel = TelemetryPanel(self._bottom_pane)
        self._brick_panel = BrickPanel(self._bottom_pane)
        self._bottom_pane.add(self._telemetry_panel, minsize=360, stretch="always")
        self._bottom_pane.add(self._brick_panel, minsize=320, stretch="always")

        # Columna derecha: editor de codigo
        self._editor = EditorPanel(
            self._root_hpane,
            on_run=self._cmd_run,
            on_debug=self._cmd_debug,
            on_debug_step=self._cmd_debug_step,
            on_debug_continue=self._cmd_debug_continue,
            on_breakpoints_changed=self._on_breakpoints_changed,
            on_stop=self._cmd_stop,
        )
        self._root_hpane.add(self._editor, minsize=420, stretch="always")

        self._status_strip = tk.Frame(self, bg="#F8FBFF", height=30)
        self._status_strip.pack(fill=tk.X, padx=12, pady=(6, 0))
        self._status_text_var = tk.StringVar(value="Estado: Listo")
        tk.Label(
            self._status_strip,
            textvariable=self._status_text_var,
            bg="#F8FBFF",
            fg="#324968",
            font=("Segoe UI", 9),
        ).pack(side=tk.LEFT, padx=8)
        tk.Label(
            self._status_strip,
            text="Robot: EV3",
            bg="#F8FBFF",
            fg="#324968",
            font=("Segoe UI", 9),
        ).pack(side=tk.LEFT, padx=18)
        tk.Label(
            self._status_strip,
            text="Python (Pybricks)",
            bg="#F8FBFF",
            fg="#324968",
            font=("Segoe UI", 9),
        ).pack(side=tk.LEFT, padx=18)

    def _build_sim_control_bar(self, parent: tk.Widget) -> None:
        """Barra superior estilo web para controles de simulacion."""
        bar = tk.Frame(parent, bg="#ECEFF1", padx=4, pady=4)
        bar.pack(fill=tk.X)

        run_group = tk.Frame(bar, bg="#ECEFF1")
        run_group.pack(side=tk.LEFT, anchor="w")

        tk.Button(run_group, text="Ejecutar", command=self._cmd_run_from_editor).pack(side=tk.LEFT, padx=2)
        tk.Button(run_group, text="Pausar", command=self._cmd_pause).pack(side=tk.LEFT, padx=2)
        tk.Button(run_group, text="Reanudar", command=self._cmd_resume).pack(side=tk.LEFT, padx=2)
        tk.Button(run_group, text="Finalizar", command=self._cmd_stop).pack(side=tk.LEFT, padx=2)
        tk.Button(run_group, text="Resetear", command=self._cmd_reset).pack(side=tk.LEFT, padx=2)

        pose_group = tk.Frame(bar, bg="#ECEFF1")
        pose_group.pack(side=tk.RIGHT, anchor="e")
        tk.Button(
            pose_group,
            text="Ubicar robot",
            command=self._activate_placement_mode,
        ).pack(side=tk.LEFT, padx=(8, 4))
        tk.Label(pose_group, text="Theta", bg="#ECEFF1").pack(side=tk.LEFT)
        self._theta_var = tk.StringVar(value="0")
        self._theta_label = tk.Label(
            pose_group,
            textvariable=self._theta_var,
            width=5,
            bg="#FFFFFF",
            relief="solid",
            bd=1,
            anchor="e",
        )
        self._theta_label.pack(side=tk.LEFT, padx=(4, 0))

    def _on_window_resize(self, _event) -> None:
        """Aplica layout responsivo con debounce en cada resize de la ventana."""
        if self._resize_after_id:
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(60, self._apply_responsive_layout)

    # ------------------------------------------------------------------
    # Modo de colocaciÃ³n del robot
    # ------------------------------------------------------------------

    def _activate_placement_mode(self) -> None:
        """Habilita el clic en el canvas para fijar la posiciÃ³n inicial."""
        self._canvas.set_editor_robot_visible(True)
        self._canvas.enable_placement_mode(
            callback=self._on_canvas_placement,
            hover_callback=self._on_canvas_hover,
        )
        cfg = self._service.engine._cfg
        x0, y0 = cfg.robot_x0_mm, cfg.robot_y0_mm
        theta0 = cfg.robot_theta0_deg
        try:
            theta0 = float(self._theta_var.get().strip())
        except (AttributeError, ValueError):
            pass
        self._pending_robot_pose = (x0, y0, theta0)
        self._hover_robot_pos = None
        self._canvas.draw_placement_marker(x0, y0, theta0)
        self._refresh_placement_bar()

    def _deactivate_placement_mode(self) -> None:
        """Deshabilita el modo de colocaciÃ³n durante la simulaciÃ³n."""
        self._canvas.set_editor_robot_visible(False)
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
        self._canvas.set_editor_robot_visible(False)
        self._theta_var.set(f"{theta_deg:.0f}")
        self._refresh_placement_bar()

    def _refresh_placement_bar(self) -> None:
        if self._service.is_running:
            return

        pose = self._pending_robot_pose
        hover = self._hover_robot_pos
        cursor_text = ""
        if hover is not None:
            cursor_text = f" | Cursor: ({hover[0] / 10.0:.1f} cm, {hover[1] / 10.0:.1f} cm)"

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
                f"Robot inicial: ({x_mm / 10.0:.1f} cm, {y_mm / 10.0:.1f} cm), "
                f"theta {theta_deg:.0f} °. "
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

        # Proporciones base en espejo web: simulacion izquierda + editor derecha
        editor_w = max(420, int(width * 0.35))
        editor_x = max(640, width - editor_w)
        telemetry_w = max(360, int((editor_x - 24) * 0.52))

        try:
            self._root_hpane.sash_place(0, editor_x, 0)
        except Exception:  # noqa: BLE001
            pass
        try:
            self._bottom_pane.sash_place(0, telemetry_w, 0)
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    # Tick del engine vÃ­a Tkinter after()
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
        self._schedule_tick()   # reprogramar ANTES de cualquier excepciÃ³n

    # ------------------------------------------------------------------
    # Callbacks del SimulationService
    # ------------------------------------------------------------------

    def _on_snapshot(self, dto) -> None:
        """Recibe el SnapshotDTO desde el EngineThread â€” DEBE serializar a Tkinter."""
        # after_idle garantiza que la actualizaciÃ³n de widgets ocurre
        # en el hilo de Tkinter (MainThread)
        self.after_idle(self._apply_snapshot, dto)

    def _apply_snapshot(self, dto) -> None:
        """Actualiza los widgets con el snapshot (ejecutado en MainThread)."""
        try:
            self._canvas.update_from_dto(dto)
        except Exception:  # noqa: BLE001
            pass
        try:
            self._brick_panel.update_from_dto(dto)
        except Exception:  # noqa: BLE001
            pass
        try:
            self._telemetry_panel.update_from_dto(dto)
        except Exception:  # noqa: BLE001
            pass

    def _on_error(self, payload: dict) -> None:
        """Muestra el error del script en el editor y en un diÃ¡logo."""
        msg = self._format_runtime_error(payload)
        self.after_idle(self._editor.set_status, f"Error: {msg}", "#B71C1C")
        self.after_idle(messagebox.showerror, "Error en script", msg)

    @staticmethod
    def _extract_script_line(payload: dict) -> Optional[int]:
        """Extrae la linea del usuario desde traceback (<script>) si existe."""
        tb = str(payload.get("traceback", "") or "")
        if not tb:
            return None
        match = re.search(r'File "<script>", line (\d+)', tb)
        if not match:
            return None
        try:
            return int(match.group(1))
        except (TypeError, ValueError):
            return None

    def _format_runtime_error(self, payload: dict) -> str:
        """Construye mensaje legible con linea cuando se conoce."""
        base = str(payload.get("error", "Error desconocido"))
        line_no = self._extract_script_line(payload)
        debug_lines = payload.get("debug_last_lines")
        if isinstance(debug_lines, list) and debug_lines:
            last = ", ".join(str(int(n)) for n in debug_lines[-8:])
            base = f"{base}\nUltimas lineas ejecutadas: {last}"
        if line_no is None:
            return base
        return f"Linea {line_no}: {base}"

    def _on_status(self, status: str) -> None:
        status_map = {
            "started":      ("Ejecutando...",      "#1565C0"),
            "paused":       ("Pausado",            "#F57F17"),
            "resumed":      ("Ejecutando...",      "#1565C0"),
            "stopped":      ("Detenido",           "#424242"),
            "error":        ("Error",              "#B71C1C"),
            "reset":        ("Listo",              "#212121"),
            "world_loaded": ("Mundo cargado",      "#2E7D32"),
        }
        msg, color = status_map.get(status, (status, "#212121"))
        self.after_idle(self._editor.set_status, msg, color)
        self.after_idle(self._status_text_var.set, f"Estado: {msg}")

        if status in ("started", "paused", "resumed", "stopped"):
            self.after_idle(self._set_execution_menu_locked, True)
        elif status == "reset":
            self.after_idle(self._set_execution_menu_locked, False)

        # Re-habilitar modo de colocaciÃ³n al terminar la simulaciÃ³n
        if status in ("stopped", "error", "reset"):
            self._debug_active = False
            self.after_idle(self._activate_placement_mode)
            self.after_idle(self._editor.clear_debug_line)

    def _on_debug_event(self, payload: dict) -> None:
        debug_state = str(payload.get("debug_state", "") or "")
        line_no = payload.get("line")
        if line_no is not None:
            try:
                self.after_idle(self._editor.highlight_debug_line, int(line_no))
            except Exception:  # noqa: BLE001
                pass

        if debug_state == "paused_breakpoint" and line_no is not None:
            self.after_idle(self._editor.set_status, f"Pausa en breakpoint (linea {int(line_no)})", "#8E24AA")
            return
        if debug_state == "paused_step" and line_no is not None:
            self.after_idle(self._editor.set_status, f"Pausa paso a paso (linea {int(line_no)})", "#8E24AA")
            return
        if debug_state == "paused_manual":
            self.after_idle(self._editor.set_status, "Pausa manual", "#8E24AA")
            return

        evt_type = str(payload.get("type", "line"))
        if evt_type == "paused" and line_no is not None:
            reason = str(payload.get("reason", "step"))
            if reason == "breakpoint":
                self.after_idle(self._editor.set_status, f"Pausa en breakpoint (linea {int(line_no)})", "#8E24AA")
            else:
                self.after_idle(self._editor.set_status, f"Pausa paso a paso (linea {int(line_no)})", "#8E24AA")

    def _on_breakpoints_changed(self, breakpoints: set[int]) -> None:
        self._service.set_debug_breakpoints(breakpoints)

    def _cmd_run_from_editor(self) -> None:
        self._cmd_run(self._editor.get_code())

    def _cmd_pause(self) -> None:
        self._service.pause()

    def _cmd_resume(self) -> None:
        self._service.resume()

    def _cmd_map_zoom_in(self) -> None:
        self._canvas.zoom_in()

    def _cmd_map_zoom_out(self) -> None:
        self._canvas.zoom_out()

    def _cmd_map_zoom_reset(self) -> None:
        self._canvas.fit_to_view()

    def _cmd_reset(self) -> None:
        self._service.reset()
        self._set_execution_menu_locked(False)
        self._canvas.reset()
        self._brick_panel.reset()
        self._telemetry_panel.reset()
        self._activate_placement_mode()

    # ------------------------------------------------------------------
    # Comandos de la UI
    # ------------------------------------------------------------------

    def _cmd_run(self, source_code: str) -> None:
        """Llamado por EditorPanel cuando el usuario pulsa Ejecutar."""
        # Deshabilitar modo de colocaciÃ³n durante la ejecuciÃ³n
        self._debug_active = False
        self._deactivate_placement_mode()
        self._editor.clear_debug_line()
        self._canvas.reset()
        self._brick_panel.reset()
        self._telemetry_panel.reset()
        self._service.load_script(source_code)
        self._service.start(debug=False, step_mode=False)
        self._set_execution_menu_locked(True)

    def _cmd_debug(self, source_code: str) -> None:
        """Ejecuta el script en modo depuracion (traza de lineas)."""
        self._debug_active = True
        self._deactivate_placement_mode()
        self._editor.clear_debug_line()
        self._canvas.reset()
        self._brick_panel.reset()
        self._telemetry_panel.reset()
        self._service.set_debug_breakpoints(self._editor.get_breakpoints())
        self._service.load_script(source_code)
        self._service.start(debug=True, step_mode=False)
        self._set_execution_menu_locked(True)

    def _cmd_debug_step(self) -> None:
        """Ejecuta un paso de depuracion o inicia depuracion paso a paso."""
        if self._service.is_running:
            self._service.debug_step()
            return
        self._debug_active = True
        source_code = self._editor.get_code()
        self._deactivate_placement_mode()
        self._editor.clear_debug_line()
        self._canvas.reset()
        self._brick_panel.reset()
        self._telemetry_panel.reset()
        self._service.set_debug_breakpoints(self._editor.get_breakpoints())
        self._service.load_script(source_code)
        self._service.start(debug=True, step_mode=True)
        self._set_execution_menu_locked(True)

    def _cmd_debug_continue(self) -> None:
        """Continua ejecucion en modo depuracion hasta el proximo breakpoint."""
        if not self._service.is_running:
            return
        self._service.debug_continue()

    def _cmd_stop(self) -> None:
        """Llamado por EditorPanel cuando el usuario pulsa Detener."""
        self._service.stop()

    def _evt_new_script(self, _event=None) -> str:
        self._cmd_new()
        return "break"

    def _evt_open_script(self, _event=None) -> str:
        self._cmd_open_script()
        return "break"

    def _evt_save_script(self, _event=None) -> str:
        self._cmd_save_script()
        return "break"

    def _cmd_open_script(self) -> None:
        """Abre un script desde disco."""
        if self._guard_menu_locked():
            return
        if self._service.is_running:
            if not messagebox.askyesno(
                "Abrir script",
                "La simulacion esta corriendo. ¿Detener y abrir otro script?",
            ):
                return
            self._service.stop()
        self._editor.open_script_dialog()

    def _cmd_save_script(self) -> None:
        """Guarda el script actual."""
        if self._guard_menu_locked():
            return
        self._editor.save_script_dialog()

    def _cmd_new(self) -> None:
        """Nuevo script en blanco."""
        if self._guard_menu_locked():
            return
        if self._service.is_running:
            if not messagebox.askyesno("Nuevo script",
                                       "La simulación está corriendo. ¿Detener?"):
                return
            self._service.stop()
        self._editor.set_code("# Nuevo script\n")

    def _load_example(self, path: str) -> None:
        """Carga un script de ejemplo en el editor."""
        if self._guard_menu_locked():
            return
        if self._service.is_running:
            self._service.stop()
        try:
            self._editor.load_file(path)
        except OSError as exc:
            messagebox.showerror("Error al cargar ejemplo", str(exc))

    def _cmd_load_world(self) -> None:
        if self._guard_menu_locked():
            return
        path = filedialog.askopenfilename(
            title="Cargar mundo JSON",
            initialdir=str(_WORLDS_DIR),
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
        )
        if path:
            self._load_world(path)

    def _cmd_open_world_editor(self) -> None:
        if self._guard_menu_locked():
            return
        try:
            if self._world_editor_window is not None:
                if self._world_editor_window.winfo_exists():
                    self._world_editor_window.lift()
                    self._world_editor_window.focus_force()
                    return
        except Exception:  # noqa: BLE001
            self._world_editor_window = None

        try:
            from simulador_ev3.ui.world_editor_window import WorldEditorWindow

            self._world_editor_window = WorldEditorWindow(
                self,
                on_world_saved=self._on_editor_world_saved,
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Editor de mundos", str(exc))

    def _on_editor_world_saved(self, path: str) -> None:
        """Recarga en simulaciÃ³n el mundo guardado desde el editor."""
        try:
            self._service.load_world_file(path)
            self._load_editor_visual_data(path)
            self._refresh_world_canvas()
            self._activate_placement_mode()
            self._editor.set_status("Mundo aplicado desde editor", "#2E7D32")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Editor de mundos", str(exc))

    def _load_world(self, path: str) -> None:
        try:
            self._service.load_world_file(path)
            self._load_editor_visual_data(path)
            self._refresh_world_canvas()
            self._activate_placement_mode()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error al cargar mundo", str(exc))

    def _cmd_load_blank_world(self) -> None:
        if self._guard_menu_locked():
            return
        try:
            self._service.load_blank_world()
            self._editor_world_placements = []
            self._refresh_world_canvas()
            self._activate_placement_mode()
            self._editor.set_status("Mundo en blanco cargado", "#2E7D32")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error al cargar mundo", str(exc))

    def _apply_scenario(self, world_file: str, example_file: str) -> None:
        """Carga un mundo preset y un ejemplo asociado en un solo paso."""
        if self._guard_menu_locked():
            return
        world_path = _WORLDS_DIR / world_file
        example_path = _EXAMPLES_DIR / example_file

        if self._service.is_running:
            self._service.stop(reason="scenario_change")

        if not world_path.exists():
            messagebox.showerror("Escenario", f"No existe el mundo: {world_file}")
            return
        if not example_path.exists():
            messagebox.showerror("Escenario", f"No existe el ejemplo: {example_file}")
            return

        try:
            self._service.load_world_file(str(world_path))
            self._load_editor_visual_data(str(world_path))
            self._editor.load_file(str(example_path))
            self._refresh_world_canvas()
            self._activate_placement_mode()
            self._editor.set_status(
                f"Escenario cargado: {Path(example_file).stem}",
                "#2E7D32",
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Escenario", str(exc))

    def _refresh_world_canvas(self) -> None:
        world = self._service.engine.world
        world_name = getattr(world, "name", "Basico")
        self._world_name_var.set(f"Mundo actual: {world_name}")
        self._canvas.set_world_size_mm(world.width_mm, world.height_mm)
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
                "name": getattr(obstacle, "name", "obstacle"),
            })
        self._canvas.set_obstacles(obstacles)
        self._canvas.set_editor_placements(self._editor_world_placements)

    def _load_editor_visual_data(self, path: str) -> None:
        self._editor_world_placements = []
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return
        editor_spec = data.get("editor_spec")
        if not isinstance(editor_spec, dict):
            return
        placements = editor_spec.get("placements")
        if not isinstance(placements, list):
            return

        parsed: list[dict] = []
        for item in placements:
            if not isinstance(item, dict):
                continue
            asset_key = item.get("asset_key")
            if not isinstance(asset_key, str) or not asset_key.strip():
                continue
            parsed.append(
                {
                    "asset_key": asset_key.strip(),
                    "x_px": int(item.get("x_px", item.get("x", 0))),
                    "y_px": int(item.get("y_px", item.get("y", 0))),
                    "rotation": int(item.get("rotation", 0)),
                }
            )
        self._editor_world_placements = parsed

    def _cmd_about(self) -> None:
        messagebox.showinfo(
            "Acerca de",
            "Simulador LEGO Mindstorms EV3 basado en la libreria Pybricks\n"
            "Version 1.3.4\n\n"
            "Desarrollado por:\n"
            "  - Francisco Alejandro Medina Aguirre\n"
            "  - Jimy Alexander Cortés Osorio\n\n"
            "Grupos de investigacion vinculados:\n"
            "  - Nyquist\n"
            "  - Robotica Aplicada\n\n"
            "Institucion de apoyo academico:\n"
            "  - Universidad Tecnologica de Pereira (UTP)\n",
        )

    def _cmd_user_manual(self) -> None:
        """Abre el manual de uso en una ventana con scroll."""
        try:
            if self._manual_window is not None and self._manual_window.winfo_exists():
                self._manual_window.lift()
                self._manual_window.focus_force()
                return
        except Exception:  # noqa: BLE001
            self._manual_window = None

        win = tk.Toplevel(self)
        self._manual_window = win
        win.title("Manual de uso")
        win.geometry("920x680")
        win.minsize(700, 500)
        win.configure(bg="#ECEFF1")

        header = tk.Label(
            win,
            text="Manual de uso - Simulador EV3 Pybricks",
            bg="#ECEFF1",
            fg="#0D47A1",
            anchor="w",
            font=("Segoe UI", 11, "bold"),
            padx=10,
            pady=8,
        )
        header.pack(side=tk.TOP, fill=tk.X)

        txt = scrolledtext.ScrolledText(
            win,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#FAFAFA",
            fg="#1F2933",
            padx=10,
            pady=8,
        )
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        txt.insert("1.0", self._read_manual_text())
        txt.configure(state=tk.DISABLED)

    def _read_manual_text(self) -> str:
        """Lee el manual desde la ruta compartida de documentacion."""
        path = Path(_MANUAL_PATH)
        if not path.exists():
            return (
                "No se encontro el manual de uso.\n\n"
                f"Ruta esperada:\n{path}"
            )
        try:
            return path.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            return (
                "No fue posible leer el manual de uso.\n\n"
                f"Archivo: {path}\n"
                f"Detalle: {exc}"
            )

    def _on_close(self) -> None:
        """Cierra la aplicaciÃ³n de forma limpia."""
        if self._tick_id:
            self.after_cancel(self._tick_id)
        if self._manual_window is not None:
            try:
                self._manual_window.destroy()
            except Exception:  # noqa: BLE001
                pass
        if self._world_editor_window is not None:
            try:
                self._world_editor_window.destroy()
            except Exception:  # noqa: BLE001
                pass
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
