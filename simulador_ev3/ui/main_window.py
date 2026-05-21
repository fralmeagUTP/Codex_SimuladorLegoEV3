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
import os
import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter import scrolledtext
from typing import Optional

from simulador_ev3.application.simulation_service import SimulationService
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.domain.editor.world_editor_model import MAX_WORLD_MM
from simulador_ev3.examples.example_catalog import ExampleCatalog
from simulador_ev3.ui.world_canvas   import WorldCanvas
from simulador_ev3.ui.editor_panel  import EditorPanel
from simulador_ev3.ui.brick_panel   import BrickPanel
from simulador_ev3.ui.telemetry_panel import TelemetryPanel

# Directorio de ejemplos (relativo a la raÃ­z del proyecto)
_EXAMPLES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "Documentos", "Ejemplos"
)
_WORLDS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "Documentos", "Mundos"
)
_MANUAL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "Documentos", "MANUAL_DE_USO.md"
)

_SCENARIOS: list[tuple[str, str, str]] = [
    ("Seguidor de línea", "01_linea_negra.json", "06_siguelineas_basico.py"),
    ("Ultrasonido + obstáculos", "02_obstaculos_beacon.json", "05_esquiva_obstaculos.py"),
    ("Test pantalla/altavoz", "02_obstaculos_beacon.json", "12_pantalla_altavoz_test.py"),
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
            world_width_mm=MAX_WORLD_MM,
            world_height_mm=MAX_WORLD_MM,
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
        """Construye el layout principal: trabajo a la izquierda, estado a la derecha."""
        self._root_hpane = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=6,
            bg="#B0BEC5",
            sashrelief=tk.RAISED,
        )
        self._root_hpane.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Columna izquierda: mundo arriba + editor abajo
        left_frame = tk.Frame(self._root_hpane, bg="#ECEFF1")
        self._root_hpane.add(left_frame, minsize=560, stretch="always")

        self._vpane = tk.PanedWindow(
            left_frame,
            orient=tk.VERTICAL,
            sashwidth=6,
            bg="#B0BEC5",
            sashrelief=tk.RAISED,
        )
        self._vpane.pack(fill=tk.BOTH, expand=True)

        top_frame = tk.Frame(self._vpane, bg="#ECEFF1")
        self._vpane.add(top_frame, minsize=350, stretch="always")

        engine_cfg = self._service.engine._cfg
        ww = engine_cfg.world_width_mm
        wh = engine_cfg.world_height_mm

        canvas_frame = tk.Frame(top_frame, bg="#ECEFF1")
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

        self._editor = EditorPanel(
            self._vpane,
            on_run=self._cmd_run,
            on_debug=self._cmd_debug,
            on_debug_step=self._cmd_debug_step,
            on_debug_continue=self._cmd_debug_continue,
            on_breakpoints_changed=self._on_breakpoints_changed,
            on_stop=self._cmd_stop,
        )
        self._vpane.add(self._editor, minsize=180, stretch="always")

        # Columna derecha: telemetria arriba + pantalla del robot abajo
        self._right_pane = tk.PanedWindow(
            self._root_hpane,
            orient=tk.VERTICAL,
            sashwidth=4,
            bg="#B0BEC5",
            sashrelief=tk.RAISED,
        )
        self._root_hpane.add(self._right_pane, minsize=300, stretch="never")

        self._telemetry_panel = TelemetryPanel(self._right_pane)
        self._brick_panel = BrickPanel(self._right_pane)
        self._right_pane.add(self._telemetry_panel, minsize=260, stretch="always")
        self._right_pane.add(self._brick_panel, minsize=180, stretch="always")

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
        x0, y0, theta0 = cfg.robot_x0_mm, cfg.robot_y0_mm, cfg.robot_theta0_deg
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
        right_w = max(360, int(width * 0.34))  # reduce ancho util del editor
        right_x = max(520, width - right_w)
        telemetry_h = max(280, int(height * 0.62))

        try:
            self._root_hpane.sash_place(0, right_x, 0)
        except Exception:  # noqa: BLE001
            pass
        try:
            self._vpane.sash_place(0, 0, top_h)
        except Exception:  # noqa: BLE001
            pass
        try:
            self._right_pane.sash_place(0, 0, telemetry_h)
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

        # Re-habilitar modo de colocaciÃ³n al terminar la simulaciÃ³n
        if status in ("stopped", "error", "reset"):
            self._debug_active = False
            self.after_idle(self._activate_placement_mode)
            self.after_idle(self._editor.clear_debug_line)

    def _on_debug_event(self, payload: dict) -> None:
        evt_type = str(payload.get("type", "line"))
        line_no = payload.get("line")
        if line_no is None:
            return
        try:
            self.after_idle(self._editor.highlight_debug_line, int(line_no))
        except Exception:  # noqa: BLE001
            pass
        if evt_type == "paused":
            reason = str(payload.get("reason", "step"))
            if reason == "breakpoint":
                msg = f"Pausa en breakpoint (linea {int(line_no)})"
            else:
                msg = f"Pausa paso a paso (linea {int(line_no)})"
            self.after_idle(self._editor.set_status, msg, "#8E24AA")

    def _on_breakpoints_changed(self, breakpoints: set[int]) -> None:
        self._service.set_debug_breakpoints(breakpoints)

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
        self._editor.save_script_dialog()

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

    def _cmd_open_world_editor(self) -> None:
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
            self._load_editor_visual_data(world_path)
            self._editor.load_file(example_path)
            self._refresh_world_canvas()
            self._activate_placement_mode()
            self._editor.set_status(
                f"Escenario cargado: {os.path.splitext(example_file)[0]}",
                "#2E7D32",
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Escenario", str(exc))

    def _refresh_world_canvas(self) -> None:
        world = self._service.engine.world
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
            "Simulador Lego mindstorms EV3 basado en la librería Pybricks\n"
            "Versión 1.0\n\n"
            "Desarrollado por: \n "
            "\t\tFrancisco Alejandro Medina\n"
            "\t\tJimmy Alexander Cortez\n",
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
        """Lee el manual desde Documentos."""
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
