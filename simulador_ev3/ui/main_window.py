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
import multiprocessing
import re
import sys
import tkinter as tk
from functools import partial
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any, Callable, Optional

from PIL import Image, ImageTk

from simulador_ev3 import __version__
from simulador_ev3.application.desktop_session_adapter import DesktopSessionAdapter
from simulador_ev3.application.snapshot_dto import SnapshotDTO
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.domain.editor.world_editor_model import DEFAULT_WORLD_MM
from simulador_ev3.examples.example_catalog import ExampleCatalog
from simulador_ev3.shared.help_tutorials import (
    HELP_CATEGORIES,
    HELP_GUIDES,
    HELP_REFERENCES,
    PYBRICKS_GLOSSARY,
    HelpGuide,
    guide_by_id,
)
from simulador_ev3.shared.interface_catalog import RUNTIME_LIMIT_OPTIONS, label_for_status
from simulador_ev3.shared.mission_catalog import MissionCatalog
from simulador_ev3.shared.paths import (
    resolve_documentation_path,
    resolve_examples_dir,
    resolve_image_assets_dir,
    resolve_worlds_dir,
)
from simulador_ev3.shared.ui_design_tokens import (
    APP_OUTER_PADDING_PX,
    BRICK_MIN_WIDTH_PX,
    COMPACT_GAP_PX,
    EDITOR_MIN_WIDTH_PX,
    LIGHT_TOKENS,
    PANEL_GAP_PX,
    SIMULATION_MIN_WIDTH_PX,
    STATUS_STRIP_HEIGHT_PX,
    TELEMETRY_MIN_WIDTH_PX,
    WEB_MIN_HEIGHT_PX,
    WEB_MIN_WIDTH_PX,
    WEB_REFERENCE_HEIGHT_PX,
    WEB_REFERENCE_WIDTH_PX,
    ThemeTokens,
    tokens_for_theme,
)
from simulador_ev3.shared.ui_settings import (
    load_desktop_session,
    load_ui_theme,
    save_desktop_session,
    save_ui_theme,
)
from simulador_ev3.shared.world_editor_projection import editor_placements
from simulador_ev3.ui.brick_panel import BrickPanel
from simulador_ev3.ui.editor_panel import EditorPanel
from simulador_ev3.ui.telemetry_panel import TelemetryPanel
from simulador_ev3.ui.world_canvas import WorldCanvas

# Rutas canónicas compartidas (con fallback legacy).
_EXAMPLES_DIR = resolve_examples_dir()
_WORLDS_DIR = resolve_worlds_dir()

_SCENARIOS: list[tuple[str, str, str]] = [
    ("Seguidor de línea", "01_linea_negra_basica.json", "11_siguelineas_basico.py"),
    ("Ultrasonido + obstáculos", "05_obstaculos_baliza_ir.json", "15_esquiva_obstaculos.py"),
    ("Test pantalla/altavoz", "05_obstaculos_baliza_ir.json", "02_intro_pantalla_altavoz.py"),
    ("Radar 360 ultrasonido", "12_radar_ultrasonido_360.json", "23_radar_ultrasonido_5grados.py"),
]

# Periodo del tick en ms (â‰ˆ50 Hz)
_TICK_MS = 20
_INTRO_WIDTH_PX = 800
_INTRO_HEIGHT_PX = 450


class EV3SimulatorApp(tk.Tk):
    """
    Ventana principal del simulador EV3.

    Args:
        world_config:  SimEngineConfig con las dimensiones del mundo y
                       posiciÃ³n inicial del robot.  Si None, se usan
                       valores por defecto (mundo 2000 Ã— 2000 mm).
    """

    def __init__(
        self,
        world_config: Optional[SimEngineConfig] = None,
        *,
        restore_session: bool = True,
        persist_session: bool = True,
        start_hidden: bool = False,
    ) -> None:
        super().__init__()
        if start_hidden:
            self.withdraw()
        self.title("BotLab Studio")
        self.geometry(f"{WEB_REFERENCE_WIDTH_PX}x{WEB_REFERENCE_HEIGHT_PX}")
        self.minsize(WEB_MIN_WIDTH_PX, WEB_MIN_HEIGHT_PX)
        self._theme_name = load_ui_theme()
        self.configure(bg=tokens_for_theme(self._theme_name).background)

        # Servicio de simulaciÃ³n (capa de aplicaciÃ³n)
        effective_cfg = world_config or SimEngineConfig(
            world_width_mm=DEFAULT_WORLD_MM,
            world_height_mm=DEFAULT_WORLD_MM,
        )
        self._service = DesktopSessionAdapter(config=effective_cfg)
        self._service.set_snapshot_callback(self._on_snapshot)
        self._service.set_error_callback(self._on_error)
        self._service.set_status_callback(self._on_status)
        self._service.set_debug_callback(self._on_debug_event)
        self._examples = ExampleCatalog(_EXAMPLES_DIR)
        self._missions = MissionCatalog(_EXAMPLES_DIR, _WORLDS_DIR)

        # Pose inicial elegida por el usuario. None = usar config actual.
        self._pending_robot_pose: Optional[tuple[float, float, float]] = None
        self._hover_robot_pos: Optional[tuple[float, float]] = None
        self._world_editor_window: Any | None = None
        self._manual_window: tk.Toplevel | None = None
        self._about_window: tk.Toplevel | None = None
        self._about_images: list[tk.PhotoImage] = []
        self._editor_world_placements: list[dict] = []
        self._active_world_path: str | None = None
        self._active_world_label = "Basico"
        self._debug_active = False
        self._execution_menu_locked = False
        self._next_execution_notification_id = 0
        self._active_execution_notification_id: int | None = None
        self._notified_execution_notification_id: int | None = None
        # Descarta snapshots encolados por la ejecución que se acaba de
        # cancelar. Sin esta barrera, un callback tardío podía volver a dibujar
        # haces/trazas azules justo después de "Detener y reiniciar".
        self._snapshot_epoch = 0
        self._awaiting_worker_reset_snapshot = False
        self._reset_worker_command_id: str | None = None
        self._lockable_menu_buttons: list[tk.Button] = []
        self._persist_session = persist_session

        # Construir la interfaz
        self._build_menu()
        self._build_layout()
        self._apply_theme(self._theme_name)
        if restore_session:
            self._restore_desktop_session()

        # Arrancar el ciclo de ticks
        self._closing = False
        self._tick_id: Optional[str] = None
        self._resize_after_id: Optional[str] = None
        self._layout_idle_id: Optional[str] = None
        self._schedule_tick()

        # Layout responsivo al cambiar tamaÃ±o de ventana
        self.bind("<Configure>", self._on_window_resize)
        self._layout_idle_id = self.after_idle(self._apply_responsive_layout)

        # Al cerrar la ventana, detener la simulaciÃ³n
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # ConstrucciÃ³n de la UI
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        tokens = tokens_for_theme(self._theme_name)
        menu_style: dict[str, Any] = {
            "bg": tokens.surface,
            "fg": tokens.text,
            "activebackground": tokens.primary,
            "activeforeground": "white",
        }
        header = tk.Frame(self, bg=tokens.toolbar, padx=12, pady=8)
        header.pack(fill=tk.X)
        self._menubar = header
        self._header_menu_buttons: list[tk.Button] = []
        self._header_menus: list[tk.Menu] = []
        tk.Label(
            header,
            text="EV3",
            bg=tokens.surface,
            fg=tokens.primary,
            relief=tk.SOLID,
            bd=1,
            font=("Segoe UI", 8, "bold"),
            padx=3,
            pady=3,
        ).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(
            header,
            text="BotLab Studio",
            bg=tokens.toolbar,
            fg=tokens.toolbar_text,
            font=("Segoe UI", 12, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 16))
        navigation = tk.Frame(header, bg=tokens.toolbar)
        navigation.pack(side=tk.LEFT)

        def add_menu_button(label: str, menu: tk.Menu, *, lockable: bool = False) -> None:
            button = tk.Button(
                navigation,
                text=label,
                bg=tokens.toolbar,
                fg=tokens.toolbar_text,
                activebackground=tokens.primary,
                activeforeground=tokens.toolbar_text,
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=3,
                font=("Segoe UI", 9),
                # En Windows, Menubutton no siempre entra en la secuencia de
                # foco si se deja el valor predeterminado. La cabecera debe
                # poder recorrerse igual que la navegación de la Web.
                takefocus=True,
                highlightthickness=2,
                highlightbackground=tokens.toolbar,
                highlightcolor=tokens.focus,
            )
            # No depender de la clase de bindings de Menubutton: con algunos
            # temas/entornos Windows el menú asociado deja de desplegarse.
            # El post explícito conserva el menú nativo y sus comandos.
            button.configure(
                command=lambda item=button, popup=menu: self._post_header_menu(item, popup)
            )
            button.bind(
                "<Return>",
                lambda _event, item=button, popup=menu: self._post_header_menu(item, popup),  # type: ignore[misc]
            )
            button.bind(
                "<space>",
                lambda _event, item=button, popup=menu: self._post_header_menu(item, popup),  # type: ignore[misc]
            )
            button.bind(
                "<FocusIn>",
                lambda _event, item=button: self._set_header_menu_focus(item, True),
            )
            button.bind(
                "<FocusOut>",
                lambda _event, item=button: self._set_header_menu_focus(item, False),
            )
            button.pack(side=tk.LEFT, padx=1)
            self._header_menu_buttons.append(button)
            self._header_menus.append(menu)
            if lockable:
                self._lockable_menu_buttons.append(button)

        # MenÃº Archivo
        file_menu = tk.Menu(header, tearoff=0, **menu_style)
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
        file_menu.add_command(label="Salir", command=self._on_close)
        add_menu_button("Archivo", file_menu, lockable=True)

        self.bind("<Control-n>", self._evt_new_script)
        self.bind("<Control-o>", self._evt_open_script)
        self.bind("<Control-s>", self._evt_save_script)
        self.bind("<F1>", self._evt_help)
        self.bind("<F5>", self._evt_run)
        self.bind("<F6>", self._evt_pause_resume)
        self.bind("<Shift-F5>", self._evt_stop_reset)
        self.bind("<Escape>", self._evt_escape)

        # MenÃº Ejemplos
        examples_menu = tk.Menu(header, tearoff=0, **menu_style)
        self._populate_examples_menu(examples_menu)
        add_menu_button("Ejemplos", examples_menu, lockable=True)

        # MenÃº Mundos
        worlds_menu = tk.Menu(header, tearoff=0, **menu_style)
        worlds_menu.add_command(label="Mundo en blanco (sin mapa)", command=self._cmd_load_blank_world)
        worlds_menu.add_separator()
        worlds_menu.add_command(label="Cargar mundo JSON...", command=self._cmd_load_world)
        worlds_menu.add_command(label="Editor de mundos...", command=self._cmd_open_world_editor)
        worlds_menu.add_separator()
        preset_worlds_menu = tk.Menu(worlds_menu, tearoff=0, **menu_style)
        self._populate_worlds_menu(preset_worlds_menu)
        worlds_menu.add_cascade(label="Mundos preestablecidos", menu=preset_worlds_menu)
        add_menu_button("Mundos", worlds_menu, lockable=True)

        # MenÃº Escenarios (mundo + ejemplo)
        scenario_menu = tk.Menu(header, tearoff=0, **menu_style)
        self._populate_scenarios_menu(scenario_menu)
        add_menu_button("Escenarios", scenario_menu, lockable=True)

        missions_menu = tk.Menu(header, tearoff=0, **menu_style)
        self._populate_missions_menu(missions_menu)
        add_menu_button("Misiones", missions_menu, lockable=True)

        theme_menu = tk.Menu(header, tearoff=0, **menu_style)
        theme_menu.add_command(label="Tema claro", command=lambda: self._set_theme("light"))
        theme_menu.add_command(label="Tema oscuro", command=lambda: self._set_theme("dark"))
        add_menu_button("Tema", theme_menu, lockable=True)

        profile_menu = tk.Menu(header, tearoff=0, **menu_style)
        profile_menu.add_command(label="Ideal", command=lambda: self._set_simulation_profile("ideal"))
        profile_menu.add_command(label="Realista", command=lambda: self._set_simulation_profile("realistic"))
        profile_menu.add_command(label="Calibrado", command=lambda: self._set_simulation_profile("calibrated"))
        add_menu_button("Fidelidad", profile_menu, lockable=True)

        runtime_menu = tk.Menu(header, tearoff=0, **menu_style)
        for seconds in (item for item in RUNTIME_LIMIT_OPTIONS if item > 0):
            runtime_menu.add_command(label=f"{int(seconds)} s", command=partial(self._set_max_runtime, int(seconds)))
        runtime_menu.add_command(label="Sin limite", command=lambda: self._set_max_runtime(0))
        add_menu_button("Tiempo máximo", runtime_menu, lockable=True)

        trace_menu = tk.Menu(header, tearoff=0, **menu_style)
        trace_menu.add_command(label="Iniciar registro", command=self._start_trace)
        trace_menu.add_command(label="Detener registro", command=self._stop_trace)
        trace_menu.add_command(label="Avanzar un tick", command=self._step_tick)
        trace_menu.add_separator()
        trace_menu.add_command(label="Exportar JSON...", command=lambda: self._export_trace("json"))
        trace_menu.add_command(label="Exportar CSV...", command=lambda: self._export_trace("csv"))
        add_menu_button("Trazas", trace_menu, lockable=True)

        # MenÃº Ayuda
        help_menu = tk.Menu(header, tearoff=0, **menu_style)
        help_menu.add_command(label="Centro de ayuda...", command=self._cmd_user_manual)
        help_menu.add_command(label="Diagnóstico de sesión...", command=self._show_session_diagnostics)
        help_menu.add_command(label="Exportar diagnóstico JSON...", command=self._export_session_diagnostics)
        help_menu.add_separator()
        help_menu.add_command(label="Acerca de...", command=self._cmd_about)
        add_menu_button("Ayuda", help_menu)

        self._update_menu_lock_state()

    @staticmethod
    def _post_header_menu(button: tk.Button, menu: tk.Menu) -> str:
        """Despliega un menú de cabecera de forma fiable en Tkinter/Windows."""
        if str(button.cget("state")) == str(tk.DISABLED):
            return "break"
        button.focus_set()
        menu.tk_popup(button.winfo_rootx(), button.winfo_rooty() + button.winfo_height())
        return "break"

    def _set_header_menu_focus(self, button: tk.Button, focused: bool) -> None:
        """Hace inequívoco el foco de teclado en los menús de cabecera."""

        tokens = tokens_for_theme(self._theme_name)
        button.configure(
            bg=tokens.focus if focused else tokens.toolbar,
            fg=tokens.surface if focused else tokens.toolbar_text,
            activebackground=tokens.primary if focused else tokens.primary,
            activeforeground=tokens.surface if focused else tokens.toolbar_text,
            highlightbackground=tokens.focus if focused else tokens.toolbar,
            highlightcolor=tokens.focus,
        )

    def _set_theme(self, theme: str) -> None:
        self._theme_name = save_ui_theme(theme)
        self._apply_theme(self._theme_name)
        editor_window = self._world_editor_window
        try:
            if editor_window is not None and editor_window.winfo_exists():
                editor_window.apply_theme(self._theme_name)
        except Exception:  # noqa: BLE001
            pass

    def _set_simulation_profile(self, profile: str) -> None:
        try:
            self._service.set_simulation_profile(profile)
            self._editor.set_status(f"Perfil de simulacion: {profile}", "#2E7D32")
        except RuntimeError as exc:
            messagebox.showwarning("Perfil de simulacion", str(exc))
        except ValueError as exc:
            messagebox.showerror("Perfil de simulacion", str(exc))

    def _set_max_runtime(self, seconds: int) -> None:
        try:
            self._service.set_max_runtime_s(float(seconds))
            label = "Sin limite" if seconds == 0 else f"{seconds} s"
            self._editor.set_status(f"Tiempo maximo: {label}", "#2E7D32")
        except RuntimeError as exc:
            messagebox.showwarning("Tiempo maximo", str(exc))
        except ValueError as exc:
            messagebox.showerror("Tiempo maximo", str(exc))

    def _start_trace(self) -> None:
        self._service.start_trace()
        self._editor.set_status("Registro de traza iniciado", "#2E7D32")

    def _stop_trace(self) -> None:
        self._service.stop_trace()
        self._editor.set_status("Registro de traza detenido", "#455A64")

    def _step_tick(self) -> None:
        try:
            self._apply_snapshot(self._service.step_tick())
            self._editor.set_status("Se avanzo un tick de simulacion", "#455A64")
        except RuntimeError as exc:
            messagebox.showwarning("Paso de tick", str(exc))

    def _export_trace(self, format: str) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=f".{format}",
            filetypes=[(format.upper(), f"*.{format}")],
        )
        if not path:
            return
        try:
            Path(path).write_text(self._service.export_trace(format), encoding="utf-8")
            self._editor.set_status(f"Traza exportada: {Path(path).name}", "#2E7D32")
        except OSError as exc:
            messagebox.showerror("Exportar traza", str(exc))

    def _show_session_diagnostics(self) -> None:
        """Muestra datos correlacionables de la sesión local sin inspeccionar internals."""

        payload = self._service.observability_snapshot().to_dict()
        messagebox.showinfo(
            "Diagnóstico de sesión",
            json.dumps(payload, ensure_ascii=False, indent=2)
            + "\n\nNo contiene código del programa ni credenciales.",
            parent=self,
        )

    def _export_session_diagnostics(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON", "*.json")]
        )
        if not path:
            return
        try:
            payload = self._service.observability_snapshot().to_dict()
            Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            self._editor.set_status(f"Diagnóstico exportado: {Path(path).name}", "#2E7D32")
        except OSError as exc:
            messagebox.showerror("Exportar diagnóstico", str(exc), parent=self)

    def _restore_desktop_session(self) -> None:
        session = load_desktop_session()
        source = session.get("source")
        if isinstance(source, str):
            self._editor.set_code(source)
        watches = session.get("watches")
        if isinstance(watches, list):
            self._editor.set_watches(watches)
            self._on_watches_changed(self._editor.get_watches())
        breakpoints = session.get("breakpoints")
        if isinstance(breakpoints, list):
            normalized = {int(line) for line in breakpoints if str(line).isdigit()}
            self._editor.set_breakpoints(normalized)
            self._on_breakpoints_changed(normalized)
        world_path = session.get("world_path")
        if isinstance(world_path, str) and Path(world_path).is_file():
            self._load_world(world_path)

    def _apply_theme(self, theme: str) -> None:
        """Aplica el tema de preferencia a widgets Tk sin alterar su funcionalidad."""

        tokens = tokens_for_theme(theme)
        palette = self._theme_palette(tokens)
        palette.update(
            {
            "#ECEFF1": tokens.background,
            "#FFFFFF": tokens.surface,
            "#F8FBFF": tokens.surface_muted,
            "#1D2D44": tokens.text,
            "#385273": tokens.text_muted,
            "#D4DDE8": tokens.border,
            "WHITE": tokens.surface,
            "BLACK": tokens.text,
            "#F0F0F0": tokens.surface,
            "SYSTEMBUTTONFACE": tokens.surface,
            "#F5F8FC": tokens.surface_muted,
            "#172033": tokens.text,
            "#74849A": tokens.text_muted,
            "#1B3557": tokens.primary,
            "#21344D": tokens.text,
            "#213858": tokens.primary_active,
            "#324968": tokens.text_muted,
            "#455A64": tokens.text_muted,
            "#1E2630": tokens.background,
            "#263342": tokens.surface,
            "#F3F7FC": tokens.text,
            "#C6D4E3": tokens.text_muted,
            "#E8F5E9": tokens.surface_muted,
            "#E3F2FD": tokens.surface_muted,
            "#1B5E20": tokens.success,
            "#0D47A1": tokens.focus,
            "#D7E8FA": tokens.surface_muted,
            "#E6ECF3": tokens.surface_muted,
            "#35506F": tokens.text_muted,
            "#102A45": tokens.text,
            "#2D425C": tokens.text_muted,
            "#1F2933": tokens.text,
            "#FAFAFA": tokens.surface,
            "#0B1220": tokens.background,
            "#E6EDF3": tokens.text,
            "#1E3A5F": tokens.primary_active,
            }
        )

        def visit(widget) -> None:
            changes: dict[str, str] = {}
            try:
                background = widget.cget("bg")
                background_key = str(background).upper()
                if background_key in palette:
                    changes["bg"] = palette[background_key]
            except Exception:  # noqa: BLE001
                pass
            for option in (
                "fg",
                "activebackground",
                "activeforeground",
                "disabledforeground",
                "highlightbackground",
                "insertbackground",
                "selectbackground",
                "selectforeground",
                "troughcolor",
            ):
                try:
                    value_key = str(widget.cget(option)).upper()
                    if value_key in palette:
                        changes[option] = palette[value_key]
                except Exception:  # noqa: BLE001
                    continue
            if changes:
                try:
                    widget.configure(**changes)
                except Exception:  # noqa: BLE001
                    pass
            try:
                for child in widget.winfo_children():
                    visit(child)
            except Exception:  # noqa: BLE001
                pass

        self.configure(bg=tokens.background)
        visit(self)
        canvas = getattr(self, "_canvas", None)
        set_canvas_theme = getattr(canvas, "set_theme", None)
        if callable(set_canvas_theme):
            set_canvas_theme(theme)
        telemetry = getattr(self, "_telemetry_panel", None)
        set_telemetry_theme = getattr(telemetry, "set_theme", None)
        if callable(set_telemetry_theme):
            set_telemetry_theme(theme)
        editor = getattr(self, "_editor", None)
        set_editor_theme = getattr(editor, "set_theme", None)
        if callable(set_editor_theme):
            set_editor_theme(theme)
        self._apply_sim_control_palette(tokens)
        self._apply_header_palette(tokens)

    @staticmethod
    def _theme_palette(tokens: ThemeTokens) -> dict[str, str]:
        """Mapea las dos paletas conocidas hacia el tema de destino."""
        palette: dict[str, str] = {}
        # Mapear ambas paletas conocidas hace que oscuro -> claro sea tan
        # completo como claro -> oscuro; antes solo se reconocían colores claros.
        for source in (LIGHT_TOKENS, tokens_for_theme("dark")):
            for name in ThemeTokens.__dataclass_fields__:
                palette[str(getattr(source, name)).upper()] = str(getattr(tokens, name))
        return palette

    def _apply_header_palette(self, tokens: ThemeTokens) -> None:
        """Actualiza la barra superior integrada y sus menús desplegables."""

        header = getattr(self, "_menubar", None)
        if header is not None:
            header.configure(bg=tokens.toolbar)
        for button in getattr(self, "_header_menu_buttons", []):
            try:
                focused = button == self.focus_get()
            except AttributeError:
                # El arnés de UI sin display no implementa ``focus_get``.
                focused = False
            self._set_header_menu_focus(button, focused)
            button.configure(disabledforeground=tokens.text_muted)
        for menu in getattr(self, "_header_menus", []):
            menu.configure(
                bg=tokens.surface,
                fg=tokens.text,
                activebackground=tokens.primary,
                activeforeground=tokens.toolbar_text,
            )

    def _apply_sim_control_palette(self, tokens: ThemeTokens) -> None:
        """Mantiene los controles de ejecucion con la semantica visual de la Web."""

        for key, button in getattr(self, "_sim_control_buttons", {}).items():
            emphasized = key == "run"
            button.configure(
                bg=tokens.primary if emphasized else tokens.surface,
                fg="white" if emphasized else tokens.text,
                activebackground=tokens.primary_active,
                activeforeground="white" if emphasized else tokens.text,
                disabledforeground=tokens.text_muted,
                highlightbackground=tokens.border,
            )

        pose_button = getattr(self, "_pose_control_button", None)
        if pose_button is not None:
            pose_button.configure(
                bg=tokens.surface,
                fg=tokens.text,
                activebackground=tokens.primary_active,
                activeforeground="white",
                disabledforeground=tokens.text_muted,
                highlightbackground=tokens.border,
            )
        theta_label = getattr(self, "_theta_label", None)
        if theta_label is not None:
            theta_label.configure(bg=tokens.surface, fg=tokens.text, highlightbackground=tokens.border)

    def _update_menu_lock_state(self) -> None:
        """Deshabilita menus de trabajo durante una ejecucion activa."""
        state = tk.DISABLED if self._execution_menu_locked else tk.NORMAL
        for button in getattr(self, "_lockable_menu_buttons", []):
            try:
                button.configure(state=state)
            except Exception:  # noqa: BLE001
                continue

    def _set_execution_menu_locked(self, locked: bool) -> None:
        self._execution_menu_locked = bool(locked)
        self._update_menu_lock_state()

    @staticmethod
    def _is_execution_active(status: str) -> bool:
        """Indica si una sesión todavía debe conservar bloqueado el menú."""
        return status in {"started", "running", "paused", "resumed"}

    def _guard_menu_locked(self) -> bool:
        if not self._execution_menu_locked:
            return False
        messagebox.showinfo(
            "Ejecucion en curso",
            "Opciones de menu bloqueadas durante la ejecucion. Usa Detener y reiniciar para habilitarlas.",
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
                command=lambda p=str(example.path): self._load_example(p),  # type: ignore[misc]
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
                command=lambda p=str(path): self._load_world(p),  # type: ignore[misc]
            )

    def _populate_scenarios_menu(self, menu: tk.Menu) -> None:
        if not _SCENARIOS:
            menu.add_command(label="(No hay escenarios)", state=tk.DISABLED)
            return

        for label, world_file, example_file in _SCENARIOS:
            menu.add_command(
                label=label,
                command=lambda w=world_file, e=example_file: self._apply_scenario(w, e),  # type: ignore[misc]
            )

    def _populate_missions_menu(self, menu: tk.Menu) -> None:
        """Carga el mismo catálogo evaluable que expone la interfaz Web."""
        missions = self._missions.list_missions()
        if not missions:
            menu.add_command(label="(No hay misiones disponibles)", state=tk.DISABLED)
            return
        for mission in missions:
            menu.add_command(
                label=mission.title,
                command=lambda item=mission: self._load_mission(item.identifier),  # type: ignore[misc]
            )

    def _build_layout(self) -> None:
        """Construye layout espejo de la web: simulacion izquierda, editor derecha."""
        tokens = tokens_for_theme(self._theme_name)
        self._root_hpane = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=6,
            bg=tokens.border,
            sashrelief=tk.RAISED,
        )
        self._root_hpane.pack(fill=tk.BOTH, expand=True, padx=APP_OUTER_PADDING_PX, pady=(4, 0))

        # Columna izquierda: barra de control + mapa + telemetria/brick
        left_frame = tk.Frame(self._root_hpane, bg=tokens.background)
        self._root_hpane.add(left_frame, minsize=SIMULATION_MIN_WIDTH_PX, stretch="always")

        self._build_sim_control_bar(left_frame)

        map_frame = tk.Frame(left_frame, bg=tokens.background)
        map_frame.pack(fill=tk.BOTH, expand=True)

        map_header = tk.Frame(
            map_frame,
            bg=tokens.surface,
            bd=1,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=tokens.border,
        )
        map_header.pack(fill=tk.X, pady=(0, 1))
        tk.Label(
            map_header,
            text="Entorno de simulacion",
            bg=tokens.surface,
            fg=tokens.text,
            font=("Segoe UI", 10, "bold"),
        ).pack(side=tk.LEFT, padx=10, pady=6)
        self._world_name_var = tk.StringVar(value="Mundo actual: Basico")
        tk.Label(
            map_header,
            textvariable=self._world_name_var,
            bg=tokens.surface,
            fg=tokens.text_muted,
            font=("Consolas", 9),
        ).pack(side=tk.LEFT, padx=(0, 8), pady=6)
        map_tools = tk.Frame(map_header, bg=tokens.surface)
        map_tools.pack(side=tk.RIGHT, padx=(0, 8), pady=4)
        self._sensor_beams_var = tk.BooleanVar(value=True)
        self._sensor_beams_button = tk.Button(
            map_tools,
            text="Haces ON",
            command=self._on_toggle_sensor_beams,
            bg=tokens.surface,
            activebackground=tokens.surface,
            fg=tokens.text,
            font=("Segoe UI", 8),
        )
        self._sensor_beams_button.pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(
            map_tools,
            text="?",
            width=3,
            command=lambda: self._open_contextual_help("use-sensors"),
        ).pack(side=tk.LEFT, padx=2)
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

        engine_cfg = self._service.engine_config
        ww = engine_cfg.world_width_mm
        wh = engine_cfg.world_height_mm

        canvas_frame = tk.Frame(map_frame, bg=tokens.background)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self._placement_bar = tk.Label(
            canvas_frame,
            text="Haz clic en el mapa para colocar el robot antes de ejecutar",
            bg=tokens.surface_muted,
            fg=tokens.focus,
            font=("Segoe UI", 9),
            anchor="w",
            padx=8,
            pady=3,
        )
        self._placement_bar.pack(side=tk.TOP, fill=tk.X)

        canvas_view = tk.Frame(canvas_frame, bg=tokens.background)
        canvas_view.pack(fill=tk.BOTH, expand=True)

        self._canvas = WorldCanvas(canvas_view, world_w_mm=ww, world_h_mm=wh)
        self._canvas.set_sensor_beams_enabled(self._sensor_beams_var.get())
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
            bg=tokens.border,
            sashrelief=tk.RAISED,
        )
        self._bottom_pane.pack(fill=tk.BOTH, padx=2, pady=(PANEL_GAP_PX - 2, 0))

        self._telemetry_panel = TelemetryPanel(self._bottom_pane)
        self._brick_panel = BrickPanel(self._bottom_pane)
        # En pantallas de aula la telemetría se vuelve compacta; estos mínimos
        # impiden que el separador oculte alguno de los dos paneles.
        self._bottom_pane.add(self._telemetry_panel, minsize=TELEMETRY_MIN_WIDTH_PX, stretch="always")
        self._bottom_pane.add(self._brick_panel, minsize=BRICK_MIN_WIDTH_PX, stretch="always")

        # Columna derecha: editor de codigo
        self._editor = EditorPanel(
            self._root_hpane,
            on_run=self._cmd_run,
            on_debug=self._cmd_debug,
            on_debug_step=self._cmd_debug_step,
            on_debug_continue=self._cmd_debug_continue,
            on_breakpoints_changed=self._on_breakpoints_changed,
            on_watches_changed=self._on_watches_changed,
            on_stop=self._cmd_stop,
        )
        self._root_hpane.add(self._editor, minsize=EDITOR_MIN_WIDTH_PX, stretch="always")

        self._status_strip = tk.Frame(self, bg=tokens.surface_muted, height=STATUS_STRIP_HEIGHT_PX)
        self._status_strip.pack(fill=tk.X, padx=APP_OUTER_PADDING_PX, pady=(COMPACT_GAP_PX, 0))
        status_dot = tk.Canvas(
            self._status_strip,
            width=14,
            height=14,
            bg=tokens.surface_muted,
            highlightthickness=0,
        )
        status_dot.create_oval(4, 4, 11, 11, fill=tokens.success, outline=tokens.success)
        status_dot.pack(side=tk.LEFT, padx=(8, 0))
        self._status_text_var = tk.StringVar(value="Estado: ready")
        tk.Label(
            self._status_strip,
            textvariable=self._status_text_var,
            bg=tokens.surface_muted,
            fg=tokens.text_muted,
            font=("Segoe UI", 9),
        ).pack(side=tk.LEFT, padx=8)
        self._learning_text_var = tk.StringVar()
        tk.Label(
            self._status_strip,
            textvariable=self._learning_text_var,
            bg=tokens.surface_muted,
            fg=tokens.primary,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(side=tk.LEFT, padx=18, fill=tk.X, expand=True)
        tk.Label(
            self._status_strip,
            text="Robot: EV3",
            bg=tokens.surface_muted,
            fg=tokens.text_muted,
            font=("Segoe UI", 9),
        ).pack(side=tk.LEFT, padx=18)
        tk.Label(
            self._status_strip,
            text="Python (Pybricks)",
            bg=tokens.surface_muted,
            fg=tokens.text_muted,
            font=("Segoe UI", 9),
        ).pack(side=tk.LEFT, padx=18)
        self._refresh_learning_hint()

    def _refresh_learning_hint(self) -> None:
        """Muestra el mismo objetivo y siguiente paso del puerto compartido."""

        state = self._service.learning_state()
        result = state.result or "pendiente"
        text = (
            f"Actividad: {state.activity_id} · Progreso: "
            f"{state.progress_current}/{state.progress_total} · Resultado: {result}"
        )
        self._learning_text_var.set(text)

    def _build_sim_control_bar(self, parent: tk.Widget) -> None:
        """Barra superior estilo web para controles de simulacion."""
        tokens = tokens_for_theme(self._theme_name)
        bar = tk.Frame(parent, bg=tokens.background, padx=8, pady=6)
        bar.pack(fill=tk.X)

        run_group = tk.Frame(bar, bg=tokens.background)
        run_group.pack(side=tk.LEFT, anchor="w")

        button_base: dict[str, Any] = {"font": ("Segoe UI", 9, "bold"), "padx": 10, "pady": 4, "bd": 0}
        self._sim_control_buttons: dict[str, tk.Button] = {}
        for key, label, command, color in (
            ("run", "Ejecutar", self._cmd_run_from_editor, tokens.primary),
            ("pause", "Pausar", self._cmd_pause, tokens.surface),
            ("resume", "Reanudar", self._cmd_resume, tokens.surface),
            ("stop", "Detener y reiniciar", self._cmd_stop_and_reset, tokens.danger),
        ):
            foreground = "white" if key in {"run", "stop"} else tokens.text
            button = tk.Button(run_group, text=label, command=command, bg=color, fg=foreground, **button_base)
            button.pack(side=tk.LEFT, padx=2)
            self._sim_control_buttons[key] = button
        tk.Button(
            run_group,
            text="? Ejecución",
            command=lambda: self._open_contextual_help("run-simulation"),
        ).pack(side=tk.LEFT, padx=(8, 2))
        tk.Button(
            run_group,
            text="? Errores",
            command=lambda: self._open_contextual_help("recover-script-error"),
        ).pack(side=tk.LEFT, padx=2)
        self._sync_sim_control_states("ready")

        pose_group = tk.Frame(bar, bg=tokens.background)
        pose_group.pack(side=tk.RIGHT, anchor="e")
        self._pose_control_button = tk.Button(
            pose_group,
            text="Ubicar robot",
            command=self._activate_placement_mode,
        )
        self._pose_control_button.pack(side=tk.LEFT, padx=(8, 4))
        tk.Label(pose_group, text="Theta", bg=tokens.background, fg=tokens.text).pack(side=tk.LEFT)
        self._theta_var = tk.StringVar(value="0")
        self._theta_label = tk.Label(
            pose_group,
            textvariable=self._theta_var,
            width=5,
            bg=tokens.surface,
            fg=tokens.text,
            relief="solid",
            bd=1,
            anchor="e",
        )
        self._theta_label.pack(side=tk.LEFT, padx=(4, 0))
        self._robot_start_readout = tk.Label(
            pose_group,
            text="Pose inicial no fijada",
            bg=tokens.surface_muted,
            fg=tokens.text_muted,
            font=("Segoe UI", 8),
            padx=6,
            pady=3,
        )
        self._robot_start_readout.pack(side=tk.LEFT, padx=(8, 0))
        self._apply_sim_control_palette(tokens)

    def _on_window_resize(self, _event) -> None:
        """Aplica layout responsivo con debounce en cada resize de la ventana."""
        if self._closing:
            return
        if self._resize_after_id:
            try:
                self.after_cancel(self._resize_after_id)
            except tk.TclError:
                pass
        self._resize_after_id = self.after(60, self._apply_responsive_layout)

    # ------------------------------------------------------------------
    # Modo de colocaciÃ³n del robot
    # ------------------------------------------------------------------

    def _activate_placement_mode(self) -> None:
        """Habilita el clic en el canvas para fijar la posiciÃ³n inicial."""
        # El robot visible procede siempre del snapshot de simulacion. El asset
        # del editor se oculta para no crear una segunda imagen al ubicarlo.
        self._canvas.set_editor_robot_visible(False)
        self._canvas.enable_placement_mode(
            callback=self._on_canvas_placement,
            hover_callback=self._on_canvas_hover,
        )
        cfg = self._service.engine_config
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
        tokens = tokens_for_theme(self._theme_name)
        self._placement_bar.config(
            text="Simulacion en curso",
            bg=tokens.surface_muted,
            fg=tokens.success,
        )

    def _preserve_final_robot_visual(self, status: str) -> None:
        """Conserva solo el robot del último snapshot al cerrar una ejecución.

        El sprite del editor y el marcador naranja pertenecen al modo de
        colocación. Reactivarlos al finalizar una misión superponía una segunda
        representación sobre el robot que ya estaba en la pose final calculada.
        """
        self._canvas.set_editor_robot_visible(False)
        self._canvas.disable_placement_mode()
        self._hover_robot_pos = None
        tokens = tokens_for_theme(self._theme_name)
        message = {
            "finished": "Misión finalizada. El robot permanece en su posición final.",
            "timed_out": "Tiempo agotado. El robot permanece en su última posición.",
            "stopped": "Simulación detenida. El robot permanece en su última posición.",
            "error": "Ejecución con error. El robot permanece en su última posición.",
        }.get(status, "Ejecución finalizada.")
        self._placement_bar.config(text=message, bg=tokens.surface_muted, fg=tokens.text_muted)

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

        tokens = tokens_for_theme(self._theme_name)
        if pose is None:
            self._robot_start_readout.configure(text="Pose inicial no fijada")
            self._placement_bar.config(
                text=(f"Haz clic para fijar la posicion inicial. Arrastra o usa la rueda para orientar.{cursor_text}"),
                bg=tokens.surface_muted,
                fg=tokens.focus,
            )
            return

        x_mm, y_mm, theta_deg = pose
        self._robot_start_readout.configure(
            text=f"Pose: {x_mm / 10.0:.1f}, {y_mm / 10.0:.1f} cm; {theta_deg:.0f}°"
        )
        self._placement_bar.config(
            text=(
                f"Robot inicial: ({x_mm / 10.0:.1f} cm, {y_mm / 10.0:.1f} cm), "
                f"theta {theta_deg:.0f} °. "
                "Clic para mover, arrastra o rueda para orientar, Ejecutar para iniciar."
                f"{cursor_text}"
            ),
            bg=tokens.surface_muted,
            fg=tokens.success,
        )

    def _apply_responsive_layout(self) -> None:
        """Ajusta posiciones de sashes para distribuir espacios proporcionalmente."""
        if self._closing:
            return
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1:
            return

        # Proporciones base en espejo web: simulacion izquierda + editor derecha
        editor_w = max(420, int(width * 0.38))
        editor_x = max(640, width - editor_w)
        # La telemetría es una tabla de cuatro columnas: necesita prioridad de
        # anchura frente al brick para no comprimir sus celdas.
        bottom_available = max(1, editor_x - 20)
        telemetry_w = min(
            max(300, int(bottom_available * 0.68)),
            max(300, bottom_available - 250),
        )
        # El tablero incluye cuatro sensores y cuatro motores; con menos de
        # esta altura termina desplazándose y deja de conservar la tabla.
        # Reservar una mitad útil de la columna para que el tablero compacto
        # muestre las tarjetas de motores y sensores sin depender del scroll.
        bottom_height = max(380, int(height * 0.50))

        try:
            self._root_hpane.sash_place(0, editor_x, 0)
        except Exception:  # noqa: BLE001
            pass
        try:
            self._bottom_pane.sash_place(0, telemetry_w, 0)
        except Exception:  # noqa: BLE001
            pass
        try:
            self._bottom_pane.configure(height=bottom_height)
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
        self._schedule_tick()  # reprogramar ANTES de cualquier excepciÃ³n
        for event in self._service.drain_worker_events():
            event_type = event.get("type")
            payload = event.get("payload")
            if event_type == "snapshot" and isinstance(payload, dict):
                self._apply_worker_snapshot_event(event, payload)
            elif event_type == "status" and isinstance(payload, dict):
                worker_status = str(payload.get("status", ""))
                self._on_status({"running": "started"}.get(worker_status, worker_status))
            elif event_type == "debug" and isinstance(payload, dict):
                self._on_debug_event(payload)
            elif event_type == "error" and isinstance(payload, dict):
                normalized_error = dict(payload)
                normalized_error.setdefault(
                    "error", normalized_error.get("message", normalized_error.get("code", "Error de worker"))
                )
                self._on_error(normalized_error)
                # El worker puede terminar tras emitir solo el evento de error.
                # La UI debe abandonar RUNNING aunque no llegue después un evento
                # ``status`` separado; de otro modo quedan bloqueados menús y una
                # nueva ejecución hasta que el usuario fuerce un reinicio.
                self._on_status("error")

    # ------------------------------------------------------------------
    # Callbacks del SimulationService
    # ------------------------------------------------------------------

    def _on_snapshot(self, dto) -> None:
        """Recibe el SnapshotDTO desde el EngineThread â€” DEBE serializar a Tkinter."""
        if self._service.worker_enabled:
            return
        # after_idle garantiza que la actualizaciÃ³n de widgets ocurre
        # en el hilo de Tkinter (MainThread)
        snapshot_epoch = self._snapshot_epoch
        self.after_idle(self._apply_snapshot_if_current, dto, snapshot_epoch)

    def _apply_worker_snapshot_event(self, event: dict, payload: dict) -> None:
        """Aplica snapshots IPC, descartando los anteriores al reinicio.

        El worker puede tener snapshots de la ejecución previa aún en su cola
        cuando se pulsa "Detener y reiniciar". Solo el snapshot emitido por el
        comando ``reset`` puede volver a pintar el canvas en ese intervalo.
        """
        if self._awaiting_worker_reset_snapshot:
            if event.get("command_id") != self._reset_worker_command_id:
                return
            self._awaiting_worker_reset_snapshot = False
            self._reset_worker_command_id = None
        self._apply_snapshot(SnapshotDTO(payload))

    def _apply_snapshot_if_current(self, dto, snapshot_epoch: int) -> None:
        """Aplica solo snapshots pertenecientes a la ejecución vigente."""
        if snapshot_epoch != self._snapshot_epoch:
            return
        self._apply_snapshot(dto)

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
        msg = label_for_status(status)
        color = {
            "started": "#1565C0", "resumed": "#1565C0", "finished": "#2E7D32",
            "paused": "#F57F17", "timed_out": "#B71C1C", "error": "#B71C1C",
            "world_loaded": "#2E7D32",
        }.get(status, "#212121")
        self.after_idle(self._editor.set_status, msg, color)
        self.after_idle(self._status_text_var.set, f"Estado: {msg}")
        self.after_idle(self._telemetry_panel.set_execution_status, status)
        self.after_idle(self._sync_sim_control_states, status)
        self.after_idle(self._refresh_learning_hint)

        self.after_idle(self._set_execution_menu_locked, self._is_execution_active(status))

        # Re-habilitar modo de colocaciÃ³n al terminar la simulaciÃ³n
        if status in ("stopped", "finished", "timed_out", "error", "reset"):
            self._debug_active = False
            if status == "reset":
                self.after_idle(self._activate_placement_mode)
            else:
                self.after_idle(self._preserve_final_robot_visual, status)
            self.after_idle(self._editor.clear_debug_line)

        outcome_by_status = {
            "finished": "finished",
            "stopped": "cancelled",
            "timed_out": "timed_out",
            "error": "error",
        }
        if status in outcome_by_status:
            mission_result = self._service.complete_active_mission(outcome_by_status[status])
            if mission_result is not None:
                self.after_idle(self._show_mission_result, mission_result)
        if status == "finished":
            self.after_idle(self._show_execution_success_notification, self._active_execution_notification_id)
        elif status in {"stopped", "timed_out", "error", "reset"}:
            self._active_execution_notification_id = None

    def _begin_execution_notification_cycle(self) -> None:
        """Asocia el posible aviso de éxito con una única ejecución de la UI."""

        self._next_execution_notification_id += 1
        self._active_execution_notification_id = self._next_execution_notification_id

    def _show_execution_success_notification(self, execution_id: int | None) -> None:
        """Muestra una sola confirmación tras aplicar el snapshot terminal."""

        if (
            self._closing
            or execution_id is None
            or execution_id != self._active_execution_notification_id
            or execution_id == self._notified_execution_notification_id
        ):
            return
        # El diálogo modal siguiente entra en su propio bucle de eventos.  La
        # transición terminal ya es definitiva, por lo que la cabecera debe
        # quedar habilitada antes de abrirlo y no depender de otro callback
        # ``after_idle`` pendiente.
        self._set_execution_menu_locked(False)
        self._notified_execution_notification_id = execution_id
        self._active_execution_notification_id = None
        messagebox.showinfo(
            "Ejecución finalizada",
            "El programa se ejecutó correctamente.",
            parent=self,
        )

    def _show_mission_result(self, payload: dict) -> None:
        """Presenta el resultado de misión usando el DTO compartido."""
        result = payload["result"]
        outcome = str(payload["outcome"])
        state = "COMPLETADA" if result["passed"] and outcome == "finished" else {
            "cancelled": "CANCELADA", "timed_out": "TIEMPO AGOTADO", "error": "ERROR"
        }.get(outcome, "NO SUPERADA")
        criteria = "\n".join(
            f"{'✓' if item['passed'] else '✗'} {item['id']}"
            for item in result.get("criteria", [])
        ) or "Sin criterios evaluables"
        feedback = payload.get("feedback", {})
        summary = str(feedback.get("summary", ""))
        next_step = str(feedback.get("next_step", ""))
        physical_notice = str(feedback.get("physical_validation_notice", ""))
        self._editor.set_status(
            f"Misión {state}: {result['score']:.0f} puntos", "#2E7D32" if result["passed"] else "#B71C1C"
        )
        messagebox.showinfo(
            "Resultado de misión",
            (
                f"{payload['mission']['title']}\n\nEstado: {state}\n"
                f"Puntuación: {result['score']:.0f}\n\nCriterios:\n{criteria}\n\n"
                f"Retroalimentación: {summary}\nSiguiente paso: {next_step}\n\n{physical_notice}"
            ),
            parent=self,
        )

    def _sync_sim_control_states(self, status: str) -> None:
        """Replica la disponibilidad de controles de la Web en Tkinter."""

        buttons = getattr(self, "_sim_control_buttons", {})
        running = status in {"started", "resumed"}
        paused = status == "paused"
        if "run" in buttons:
            buttons["run"].configure(state=tk.DISABLED if (running or paused) else tk.NORMAL)
        if "pause" in buttons:
            buttons["pause"].configure(state=tk.NORMAL if running else tk.DISABLED)
        if "resume" in buttons:
            buttons["resume"].configure(state=tk.NORMAL if paused else tk.DISABLED)
        if "stop" in buttons:
            buttons["stop"].configure(state=tk.NORMAL if (running or paused) else tk.DISABLED)

    def _on_debug_event(self, payload: dict) -> None:
        debug_state = str(payload.get("debug_state", "") or "")
        line_no = payload.get("line")
        if line_no is not None:
            try:
                self.after_idle(self._editor.highlight_debug_line, int(line_no))
            except Exception:  # noqa: BLE001
                pass

        watches = payload.get("watches")
        if isinstance(watches, list):
            self.after_idle(self._editor.show_watch_results, watches)

        if debug_state == "paused_breakpoint" and line_no is not None:
            self.after_idle(self._editor.set_status, f"Pausa en breakpoint (linea {int(line_no)})", "#8E24AA")
            return
        if debug_state == "paused_step" and line_no is not None:
            self.after_idle(self._editor.set_status, f"Pausa paso a paso (linea {int(line_no)})", "#8E24AA")
            return
        if debug_state == "paused_manual":
            self.after_idle(self._editor.set_status, "Pausa manual", "#8E24AA")
        evt_type = str(payload.get("type", "line"))
        if evt_type == "paused" and line_no is not None:
            reason = str(payload.get("reason", "step"))
            if reason == "breakpoint":
                self.after_idle(self._editor.set_status, f"Pausa en breakpoint (linea {int(line_no)})", "#8E24AA")
            else:
                self.after_idle(self._editor.set_status, f"Pausa paso a paso (linea {int(line_no)})", "#8E24AA")

    def _on_breakpoints_changed(self, breakpoints: set[int]) -> None:
        self._service.set_debug_breakpoints(breakpoints)

    def _on_watches_changed(self, watches: list[str]) -> None:
        self._service.set_debug_watches(watches)

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

    def _on_toggle_sensor_beams(self) -> None:
        self._sensor_beams_var.set(not bool(self._sensor_beams_var.get()))
        button = getattr(self, "_sensor_beams_button", None)
        if button is not None:
            button.configure(text="Haces ON" if self._sensor_beams_var.get() else "Haces OFF")
        if hasattr(self, "_canvas") and self._canvas is not None:
            self._canvas.set_sensor_beams_enabled(bool(self._sensor_beams_var.get()))

    def _cmd_reset(self) -> None:
        self._active_execution_notification_id = None
        # Invalida los callbacks de snapshot que el hilo de ejecución hubiera
        # dejado pendientes antes de detenerse.
        self._snapshot_epoch += 1
        is_worker_session = bool(self._service.worker_enabled)
        self._awaiting_worker_reset_snapshot = is_worker_session
        reset_command_id = self._service.reset()
        self._reset_worker_command_id = reset_command_id if is_worker_session else None
        self._set_execution_menu_locked(False)
        self._canvas.reset()
        self._brick_panel.reset()
        self._telemetry_panel.reset()
        self._activate_placement_mode()
        snapshot = self._service.current_snapshot()
        if snapshot is not None and not is_worker_session:
            self._apply_snapshot(snapshot)

    def _cmd_stop_and_reset(self) -> None:
        """Paridad web: detiene la ejecucion actual y reinicia la simulacion."""
        # ``reset()`` emite ``stopped`` y ``reset`` de forma consecutiva.  Si
        # esperamos a que el callback de estado evalúe la misión, el segundo
        # evento puede reconstruir la sesión antes de que se presente el
        # resultado.  Cerramos explícitamente la misión primero: así una
        # interrupción manual queda registrada como CANCELADA y se muestra una
        # sola vez, antes de restaurar el mundo.
        mission_result = self._service.complete_active_mission("cancelled")
        self._cmd_reset()
        self._editor.set_status("Ejecucion finalizada. Simulacion reiniciada.", "#2E7D32")
        if mission_result is not None:
            self.after_idle(self._show_mission_result, mission_result)

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
        self._begin_execution_notification_cycle()
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
        self._begin_execution_notification_cycle()
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
        self._begin_execution_notification_cycle()
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
        self._service.close()

    def _evt_new_script(self, _event=None) -> str:
        self._cmd_new()
        return "break"

    def _evt_open_script(self, _event=None) -> str:
        self._cmd_open_script()
        return "break"

    def _evt_save_script(self, _event=None) -> str:
        self._cmd_save_script()
        return "break"

    def _evt_help(self, _event=None) -> str:
        self._cmd_user_manual()
        return "break"

    def _evt_run(self, _event=None) -> str:
        if not self._service.is_running and not self._service.is_paused:
            self._cmd_run_from_editor()
        return "break"

    def _evt_pause_resume(self, _event=None) -> str:
        if self._service.is_paused:
            self._cmd_resume()
        elif self._service.is_running:
            self._cmd_pause()
        return "break"

    def _evt_stop_reset(self, _event=None) -> str:
        self._cmd_stop_and_reset()
        return "break"

    def _evt_escape(self, _event=None) -> str | None:
        """Cierra el diálogo auxiliar activo, igual que Escape en la Web."""

        for attribute in ("_about_window", "_manual_window"):
            window = getattr(self, attribute, None)
            if window is None:
                continue
            try:
                exists = bool(window.winfo_exists())
            except Exception:  # noqa: BLE001
                exists = False
            if exists:
                window.destroy()
            setattr(self, attribute, None)
            return "break"
        return None

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
            if not messagebox.askyesno("Nuevo script", "La simulación está corriendo. ¿Detener?"):
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
                on_simulate_saved=self._on_editor_world_saved,
                theme=self._theme_name,
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Editor de mundos", str(exc))

    def _on_editor_world_saved(self, path: str) -> None:
        """Recarga en simulaciÃ³n el mundo guardado desde el editor."""
        try:
            self._service.load_world_file(path)
            self._active_world_path = str(Path(path).resolve())
            self._active_world_label = Path(path).stem
            self._load_editor_visual_data(path)
            self._refresh_world_canvas()
            self._activate_placement_mode()
            self._editor.set_status("Mundo aplicado desde editor", "#2E7D32")
            self.deiconify()
            self.lift()
            self.focus_force()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Editor de mundos", str(exc))

    def _load_world(self, path: str) -> None:
        try:
            self._service.load_world_file(path)
            self._active_world_path = str(Path(path).resolve())
            self._active_world_label = Path(path).stem
            self._load_editor_visual_data(path)
            self._refresh_world_canvas()
            self._activate_placement_mode()
            self._refresh_placement_bar()
            self._editor.set_status(f"Mundo cargado: {Path(path).name}", "#2E7D32")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error al cargar mundo", str(exc))

    def _cmd_load_blank_world(self) -> None:
        if self._guard_menu_locked():
            return
        try:
            self._service.load_blank_world()
            self._active_world_path = None
            self._active_world_label = "En blanco"
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
            self._active_world_path = str(world_path.resolve())
            self._active_world_label = Path(world_file).stem
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

    def _load_mission(self, identifier: str) -> None:
        """Carga mundo y script inicial de una misión local compartida."""
        mission = self._missions.get(identifier)
        if mission is None:
            messagebox.showerror("Misiones", "La misión solicitada no está disponible.")
            return
        self._apply_scenario(mission.world_file, mission.starter_script)
        self._service.activate_mission(mission)
        self._refresh_learning_hint()
        self._editor.set_status(f"Misión cargada: {mission.title}", "#2E7D32")

    def _refresh_world_canvas(self) -> None:
        # Fondo, obstáculos y assets se reemplazan a continuación. Limpiamos
        # primero las capas que no pertenecen al mundo (rastro, haces y ghost)
        # para que no queden líneas azules de la sesión previa.
        self._canvas.clear_world_transition_visuals()
        world = self._service.world_visual_data()
        world_name = self._active_world_label or str(world["name"])
        self._world_name_var.set(f"Mundo actual: {world_name}")
        self._canvas.set_world_size_mm(world["width_mm"], world["height_mm"])
        self._canvas.set_surface_cells(world["surface_cells"])
        self._canvas.set_obstacles(world["obstacles"])
        self._canvas.set_editor_placements(self._editor_world_placements)

    def _load_editor_visual_data(self, path: str) -> None:
        self._editor_world_placements = []
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return
        self._editor_world_placements = editor_placements(data.get("editor_spec"))

    def _cmd_about(self) -> None:
        try:
            if self._about_window is not None and self._about_window.winfo_exists():
                self._about_window.lift()
                self._about_window.focus_force()
                return
        except Exception:  # noqa: BLE001
            self._about_window = None

        win = tk.Toplevel(self)
        self._about_window = win
        self._about_images = []
        win.title("Acerca de")
        win.geometry("620x700")
        win.minsize(620, 680)
        win.minsize(580, 500)
        tokens = tokens_for_theme(self._theme_name)
        win.configure(bg=tokens.background)
        win.transient(self)
        win.grab_set()

        header = tk.Frame(win, bg=tokens.surface_muted, bd=1, relief=tk.SOLID, highlightthickness=0)
        header.pack(fill=tk.X, padx=12, pady=(12, 0))
        tk.Label(
            header,
            text="Acerca de",
            bg=tokens.surface_muted,
            fg=tokens.text,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
            padx=10,
            pady=8,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(header, text="X", width=4, command=win.destroy).pack(side=tk.RIGHT, padx=8, pady=6)

        body = tk.Frame(win, bg=tokens.surface_muted, bd=1, relief=tk.SOLID, highlightthickness=0)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        intro = (
            "BotLab Studio\n"
            "Programacion y simulacion robotica con LEGO Mindstorms EV3 y Pybricks\n"
            f"Version {__version__}\n\n"
            "Desarrollado por:\n"
            "  - Francisco Alejandro Medina Aguirre\n"
            "  - Jimy Alexander Cortés Osorio\n"
            "  - Jose Andrés Chaves Osorio\n\n"
            "Aliados academicos:\n"
            "  - Grupo Nyquist\n"
            "  - Robotica Aplicada\n"
            "  - Programa de ingenieria de sistemas y computación\n"
            "  - Programa de ingenieria mecatrónica\n"
            "  - Universidad Tecnologica de Pereira (UTP)\n"
        )
        tk.Label(
            body,
            text=intro,
            justify=tk.LEFT,
            anchor="w",
            bg=tokens.surface_muted,
            fg=tokens.text,
            font=("Segoe UI", 10),
            padx=10,
            pady=10,
        ).pack(fill=tk.X)

        cards = tk.Frame(body, bg=tokens.surface_muted)
        cards.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self._add_about_group_card(
            cards,
            "simulador_ev3/assets/Logo_Nyquist.png",
            "Grupo Nyquist",
            "Lineas UTP: analisis y procesamiento de senales 1D/2D, comunicaciones inalambricas, "
            "procesamiento digital de senales, protocolos y redes de comunicacion, seguridad TIC y educacion.",
        )
        self._add_about_group_card(
            cards,
            "simulador_ev3/assets/Logo_Robotica_Aplicada.png",
            "Robotica Aplicada",
            "Lineas UTP: instrumentacion electronica y transmision de datos, instrumentacion fisica y simulacion "
            "de procesos industriales, reconocimiento de voz, tratamiento de senales y vision artificial.",
        )
        self._add_about_group_card(
            cards,
            "simulador_ev3/assets/utp_logo.png",
            "Universidad Tecnologica de Pereira",
            "Institucion academica de apoyo al proyecto en formacion e investigacion aplicada.",
        )

        footer = tk.Frame(body, bg=tokens.surface_muted)
        footer.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Button(footer, text="Aceptar", width=12, command=win.destroy).pack(side=tk.RIGHT)
        self._center_dialog_over_main_window(win)
        # Las tarjetas pueden ajustar el tamaño solicitado tras el primer
        # layout; repetimos al quedar libre el bucle para centrar la geometría
        # final, no la estimada inicialmente.
        win.after_idle(lambda: self._center_dialog_over_main_window(win))

    def _center_dialog_over_main_window(self, window: tk.Toplevel) -> None:
        """Centra un diálogo respecto a la ventana principal visible."""
        window.update_idletasks()
        width = max(1, window.winfo_width())
        height = max(1, window.winfo_height())
        x = self.winfo_rootx() + max(0, (self.winfo_width() - width) // 2)
        y = self.winfo_rooty() + max(0, (self.winfo_height() - height) // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _add_about_group_card(self, parent: tk.Widget, image_rel_path: str, title: str, desc: str) -> None:
        tokens = tokens_for_theme(self._theme_name)
        card = tk.Frame(parent, bg=tokens.surface, bd=1, relief=tk.SOLID, highlightthickness=0)
        card.pack(fill=tk.X, pady=5)

        icon_box = tk.Frame(card, bg=tokens.surface)
        icon_box.pack(side=tk.LEFT, padx=8, pady=8)

        image_path = Path(image_rel_path)
        logo = self._load_about_logo(image_path, 52, 52)
        if logo is not None:
            self._about_images.append(logo)
            tk.Label(icon_box, image=logo, bg=tokens.surface).pack()
        else:
            tk.Label(
                icon_box,
                text="Logo",
                width=6,
                height=3,
                bg=tokens.surface_muted,
                fg=tokens.text_muted,
                font=("Segoe UI", 9, "bold"),
            ).pack()

        text_box = tk.Frame(card, bg=tokens.surface)
        text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), pady=8)
        tk.Label(
            text_box,
            text=title,
            bg=tokens.surface,
            fg=tokens.text,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            justify=tk.LEFT,
        ).pack(fill=tk.X)
        tk.Label(
            text_box,
            text=desc,
            bg=tokens.surface,
            fg=tokens.text_muted,
            font=("Segoe UI", 9),
            anchor="w",
            justify=tk.LEFT,
            wraplength=470,
        ).pack(fill=tk.X, pady=(2, 0))

    @staticmethod
    def _load_about_logo(path: Path, target_w: int, target_h: int) -> tk.PhotoImage | None:
        try:
            resolved = path if path.is_absolute() else (Path(__file__).resolve().parents[2] / path)
            if not resolved.exists():
                return None
            image = tk.PhotoImage(file=str(resolved))
            w = max(1, image.width())
            h = max(1, image.height())
            scale = max(w / max(1, target_w), h / max(1, target_h), 1)
            factor = int(scale)
            if factor > 1:
                image = image.subsample(factor, factor)
            return image
        except Exception:  # noqa: BLE001
            return None

    def _cmd_user_manual(self) -> None:
        """Abre el manual y los mismos tutoriales orientados a tarea de la Web."""
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
        tokens = tokens_for_theme(self._theme_name)
        win.configure(bg=tokens.background)
        self._build_help_center(win)
        return

    def _tutorials_as_text(self) -> str:
        """Expone el catálogo de ayuda como texto para accesibilidad y compatibilidad.

        El centro de ayuda actual es navegable, pero algunos consumidores (incluidas
        pruebas sin pantalla) necesitan una representación textual estable.  Las
        etiquetas históricas se conservan como alias para no romper enlaces ni
        materiales didácticos existentes.
        """

        legacy_task_labels = {
            "create-world": "Crear tu primer mundo",
            "run-simulation": "Ejecutar un script",
            "debug-script": "Depurar por pasos",
        }
        sections: list[str] = []
        for guide in HELP_GUIDES:
            steps = "\n".join(f"  {index}. {step}" for index, step in enumerate(guide.steps, start=1))
            legacy_label = legacy_task_labels.get(guide.identifier)
            sections.append(
                "\n".join(
                    (
                        guide.title,
                        f"Tarea: {legacy_label}" if legacy_label else "",
                        guide.summary,
                        steps,
                        f"Resultado esperado: {guide.expected_result}",
                        f"Recuperación: {guide.recovery}",
                    )
                )
            )
        return "\n\n".join(sections)

    def _read_manual_text(self) -> str:
        """Devuelve una versión textual del manual rápido para lectores no visuales."""

        references = "\n".join(
            f"{reference.title}: {reference.summary} ({reference.filename})"
            for reference in HELP_REFERENCES
        )
        glossary = "\n".join(
            f"{item.term}: {item.definition}" for item in PYBRICKS_GLOSSARY
        )
        return (
            "CENTRO DE AYUDA - SIMULADOR EV3 PYBRICKS\n\n"
            + self._tutorials_as_text()
            + "\n\nREFERENCIAS COMPARTIDAS\n"
            + references
            + "\n\nGLOSARIO PYBRICKS\n"
            + glossary
        )

    def _open_contextual_help(self, guide_id: str) -> None:
        """Abre la guía asociada a un control crítico de la simulación."""

        self._close_manual_window()
        self._help_initial_query = guide_by_id(guide_id).title
        self._cmd_user_manual()

    def _build_help_center(self, win: tk.Toplevel) -> None:
        """Construye una ayuda navegable a partir del catálogo compartido."""

        tokens = tokens_for_theme(self._theme_name)
        win.title("Centro de ayuda - Simulador EV3 Pybricks")
        win.geometry("1040x720")
        win.minsize(760, 540)
        win.protocol("WM_DELETE_WINDOW", self._close_manual_window)
        win.bind("<Escape>", lambda _event: self._close_manual_window())

        header = tk.Frame(win, bg=tokens.surface_muted, bd=1, relief=tk.SOLID)
        header.pack(fill=tk.X, padx=12, pady=(12, 0))
        tk.Label(
            header,
            text="CENTRO DE APRENDIZAJE",
            bg=tokens.surface_muted,
            fg=tokens.focus,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
            padx=14,
            pady=5,
        ).pack(fill=tk.X)
        tk.Label(
            header,
            text="¿Qué quieres hacer hoy?",
            bg=tokens.surface_muted,
            fg=tokens.text,
            font=("Segoe UI", 17, "bold"),
            anchor="w",
            padx=14,
        ).pack(fill=tk.X)
        tk.Label(
            header,
            text="Guías cortas para crear mundos, programar, simular y resolver problemas.",
            bg=tokens.surface_muted,
            fg=tokens.text_muted,
            font=("Segoe UI", 10),
            anchor="w",
            padx=14,
            pady=2,
        ).pack(fill=tk.X, pady=(0, 10))

        search_bar = tk.Frame(win, bg=tokens.background)
        search_bar.pack(fill=tk.X, padx=12, pady=10)
        tk.Label(
            search_bar,
            text="Buscar una guía, control o error:",
            bg=tokens.background,
            fg=tokens.text,
            font=("Segoe UI", 10, "bold"),
        ).pack(side=tk.LEFT)
        search_var = tk.StringVar(value=getattr(self, "_help_initial_query", ""))
        self._help_initial_query = ""
        search = tk.Entry(search_bar, textvariable=search_var, width=48)
        search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 8))
        status = tk.Label(search_bar, bg=tokens.background, fg=tokens.text_muted, font=("Segoe UI", 9))
        status.pack(side=tk.RIGHT)

        workspace = tk.PanedWindow(win, orient=tk.HORIZONTAL, sashwidth=5, bg=tokens.background, bd=0, relief=tk.FLAT)
        workspace.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        sidebar = tk.Frame(workspace, bg=tokens.surface, bd=1, relief=tk.SOLID)
        content_shell = tk.Frame(workspace, bg=tokens.background)
        workspace.add(sidebar, minsize=185, width=220)
        workspace.add(content_shell, minsize=500)

        tk.Label(
            sidebar,
            text="EXPLORAR POR TAREA",
            bg=tokens.surface,
            fg=tokens.text_muted,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
            padx=12,
            pady=12,
        ).pack(fill=tk.X)
        category_var = tk.StringVar(value="all")
        category_box = tk.Frame(sidebar, bg=tokens.surface)
        category_box.pack(fill=tk.X, padx=8)
        category_labels = (("all", "Todas las guías"), *HELP_CATEGORIES)
        category_buttons: list[tuple[str, tk.Button]] = []

        canvas = tk.Canvas(content_shell, bg=tokens.background, highlightthickness=0)
        scrollbar = tk.Scrollbar(content_shell, orient=tk.VERTICAL, command=canvas.yview)
        cards = tk.Frame(canvas, bg=tokens.background)
        cards_window = canvas.create_window((0, 0), window=cards, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        cards.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(cards_window, width=event.width))

        def refresh_guides(*_args: object) -> None:
            query = " ".join(search_var.get().casefold().split())
            selected_category = category_var.get()
            visible = [
                guide
                for guide in HELP_GUIDES
                if (selected_category == "all" or guide.category == selected_category)
                and (
                    not query
                    or query in " ".join((guide.title, guide.summary, *guide.keywords, *guide.steps)).casefold()
                )
            ]
            for child in cards.winfo_children():
                child.destroy()
            if visible:
                for guide in visible:
                    self._add_help_guide_card(cards, guide)
            else:
                tk.Label(
                    cards,
                    text="No encontramos una guía con esos términos. Prueba con mundo, sensor o error.",
                    bg=tokens.background,
                    fg=tokens.text_muted,
                    font=("Segoe UI", 10),
                    justify=tk.LEFT,
                    padx=18,
                    pady=28,
                ).pack(fill=tk.X)
            plural = "guías disponibles" if len(visible) != 1 else "guía disponible"
            status.configure(text=f"{len(visible)} {plural}")
            for identifier, button in category_buttons:
                active = identifier == selected_category
                button.configure(
                    bg=tokens.surface_muted if active else tokens.surface,
                    fg=tokens.focus if active else tokens.text,
                )
            canvas.yview_moveto(0)

        for identifier, label in category_labels:
            button = tk.Button(
                category_box,
                text=label,
                anchor="w",
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=8,
                command=partial(category_var.set, identifier),
            )
            button.pack(fill=tk.X, pady=1)
            category_buttons.append((identifier, button))

        callout = tk.Frame(sidebar, bg=tokens.surface_muted, bd=1, relief=tk.SOLID)
        callout.pack(fill=tk.X, padx=10, pady=(16, 10))
        tk.Label(
            callout,
            text="¿Necesitas instalar o administrar la aplicación?",
            bg=tokens.surface_muted,
            fg=tokens.text,
            font=("Segoe UI", 9, "bold"),
            wraplength=175,
            justify=tk.LEFT,
            padx=8,
            pady=5,
        ).pack(fill=tk.X, pady=(3, 0))
        tk.Label(
            callout,
            text="Consulta el manual técnico desde el repositorio.",
            bg=tokens.surface_muted,
            fg=tokens.text_muted,
            font=("Segoe UI", 9),
            wraplength=175,
            justify=tk.LEFT,
            padx=8,
            pady=4,
        ).pack(fill=tk.X, pady=(0, 4))
        tk.Button(
            callout,
            text="Abrir referencias y glosario",
            command=self._open_help_references,
        ).pack(anchor="w", padx=8, pady=(0, 8))

        search_var.trace_add("write", refresh_guides)
        category_var.trace_add("write", refresh_guides)
        refresh_guides()
        win.after_idle(search.focus_set)

    def _open_help_references(self) -> None:
        """Presenta los mismos manuales y términos que el Centro de ayuda Web."""

        win = tk.Toplevel(self)
        win.title("Referencias y glosario Pybricks")
        win.geometry("760x620")
        win.minsize(600, 450)
        tokens = tokens_for_theme(self._theme_name)
        win.configure(bg=tokens.background)

        text = tk.Text(
            win,
            wrap=tk.WORD,
            bg=tokens.surface,
            fg=tokens.text,
            insertbackground=tokens.text,
            relief=tk.FLAT,
            padx=18,
            pady=14,
        )
        scrollbar = tk.Scrollbar(win, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.tag_configure("title", font=("Segoe UI", 15, "bold"), foreground=tokens.focus)
        text.tag_configure("heading", font=("Segoe UI", 11, "bold"), foreground=tokens.text)
        text.tag_configure("muted", foreground=tokens.text_muted)
        text.insert(tk.END, "REFERENCIAS COMPARTIDAS\n", "title")
        text.insert(tk.END, "Las mismas referencias están disponibles en la ayuda Web. "
                    "El simulador es educativo y no sustituye validar un programa en un robot físico.\n\n", "muted")
        for reference in HELP_REFERENCES:
            available = (
                "Disponible"
                if resolve_documentation_path(reference.filename).is_file()
                else "No incluido en esta instalación"
            )
            text.insert(tk.END, f"{reference.title}\n", "heading")
            text.insert(tk.END, f"{reference.summary}\nArchivo: {reference.filename} · {available}\n\n")
        text.insert(tk.END, "GLOSARIO PYBRICKS\n", "title")
        for item in PYBRICKS_GLOSSARY:
            text.insert(tk.END, f"{item.term}: ", "heading")
            text.insert(tk.END, f"{item.definition}\n")
        text.configure(state=tk.DISABLED)

    def _add_help_guide_card(self, parent: tk.Widget, guide: HelpGuide) -> None:
        """Renderiza una guía con widgets nativos, no como Markdown plano."""

        tokens = tokens_for_theme(self._theme_name)
        card = tk.Frame(parent, bg=tokens.surface, bd=1, relief=tk.SOLID)
        card.pack(fill=tk.X, padx=2, pady=(0, 12))
        tk.Label(
            card,
            text=f"{guide.category.upper()}  ·  {guide.minutes} MIN",
            bg=tokens.surface_muted,
            fg=tokens.focus,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
            padx=12,
            pady=6,
        ).pack(fill=tk.X)
        tk.Label(
            card, text=guide.title, bg=tokens.surface, fg=tokens.text,
            font=("Segoe UI", 13, "bold"), anchor="w", padx=12, pady=4,
        ).pack(fill=tk.X, pady=(6, 0))
        tk.Label(
            card, text=guide.summary, bg=tokens.surface, fg=tokens.text_muted,
            font=("Segoe UI", 10), anchor="w", justify=tk.LEFT, wraplength=700,
            padx=12, pady=4,
        ).pack(fill=tk.X, pady=(0, 4))
        self._add_help_visual(card, guide, tokens)
        body = tk.Frame(card, bg=tokens.surface)
        body.pack(fill=tk.X, padx=12, pady=(0, 10))
        self._add_help_card_column(
            body, "ANTES DE EMPEZAR", (f"• {item}" for item in guide.prerequisites), tokens, muted=True,
        )
        self._add_help_card_column(
            body, "PASOS", (f"{index}. {step}" for index, step in enumerate(guide.steps, start=1)), tokens,
        )
        tk.Label(
            card, text=f"DEBES VER: {guide.expected_result}", bg=tokens.surface_muted,
            fg=tokens.success, font=("Segoe UI", 9, "bold"), anchor="w", justify=tk.LEFT,
            wraplength=700, padx=12, pady=7,
        ).pack(fill=tk.X, padx=12, pady=(0, 5))
        tk.Label(
            card, text=f"SI ALGO FALLA: {guide.recovery}", bg=tokens.surface_muted,
            fg=tokens.text, font=("Segoe UI", 9), anchor="w", justify=tk.LEFT,
            wraplength=700, padx=12, pady=7,
        ).pack(fill=tk.X, padx=12)
        footer = tk.Frame(card, bg=tokens.surface)
        footer.pack(fill=tk.X, padx=12, pady=10)
        destination = "Editor de mundos" if guide.destination == "worlds" else "Simulación"
        tk.Button(
            footer,
            text=f"Abrir {destination}",
            command=partial(self._manual_open_destination, guide.destination),
        ).pack(side=tk.LEFT)
        tk.Label(
            footer,
            text=f"Para: {', '.join(guide.audience)}",
            bg=tokens.surface,
            fg=tokens.text_muted,
            font=("Segoe UI", 9),
        ).pack(side=tk.RIGHT)

    @staticmethod
    def _add_help_visual(parent: tk.Widget, guide: HelpGuide, tokens: ThemeTokens) -> None:
        """Añade un esquema visual compacto que acompaña el objetivo de la guía."""

        visual = tk.Frame(parent, bg=tokens.surface_muted)
        visual.pack(fill=tk.X, padx=12, pady=(0, 10))
        canvas = tk.Canvas(
            visual, width=108, height=44, bg=tokens.surface_muted,
            highlightthickness=0, takefocus=False,
        )
        canvas.pack(side=tk.LEFT, padx=8, pady=6)
        if guide.category == "mundos":
            for x in range(8, 100, 18):
                canvas.create_line(x, 4, x, 40, fill=tokens.border)
            for y in range(4, 42, 18):
                canvas.create_line(8, y, 98, y, fill=tokens.border)
            canvas.create_rectangle(45, 13, 63, 31, fill=tokens.primary, outline=tokens.primary_active)
        elif guide.category in {"programar", "depurar", "resolver"}:
            canvas.create_text(14, 22, text="<", fill=tokens.focus, font=("Consolas", 20, "bold"))
            canvas.create_line(32, 22, 74, 22, fill=tokens.primary, width=3)
            canvas.create_oval(78, 12, 98, 32, fill=tokens.success, outline=tokens.success)
        else:
            canvas.create_oval(10, 13, 30, 33, fill=tokens.surface, outline=tokens.primary, width=2)
            canvas.create_line(30, 23, 92, 23, fill=tokens.primary, width=3, arrow=tk.LAST)
            canvas.create_arc(46, 5, 84, 41, start=25, extent=280, outline=tokens.focus, width=2)
        tk.Label(
            visual,
            text=guide.image_alt,
            bg=tokens.surface_muted,
            fg=tokens.text_muted,
            font=("Segoe UI", 9, "italic"),
            anchor="w",
            justify=tk.LEFT,
            wraplength=560,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

    @staticmethod
    def _add_help_card_column(
        parent: tk.Widget, title: str, lines: Any, tokens: ThemeTokens, *, muted: bool = False,
    ) -> None:
        column = tk.Frame(
            parent, bg=tokens.surface_muted if muted else tokens.surface, bd=1, relief=tk.SOLID,
        )
        column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5) if muted else (5, 0))
        background = tokens.surface_muted if muted else tokens.surface
        tk.Label(
            column, text=title, bg=background, fg=tokens.focus,
            font=("Segoe UI", 9, "bold"), anchor="w", padx=8, pady=5,
        ).pack(fill=tk.X)
        for line in lines:
            tk.Label(
                column, text=line, bg=background, fg=tokens.text, font=("Segoe UI", 9),
                anchor="w", justify=tk.LEFT, wraplength=350, padx=8, pady=2,
            ).pack(fill=tk.X)

    def _manual_open_destination(self, destination: str) -> None:
        self._close_manual_window()
        if destination == "worlds":
            self._cmd_open_world_editor()
        elif destination == "debug":
            self._manual_open_debug()
        else:
            self._manual_open_simulation()

    def _close_manual_window(self) -> None:
        if self._manual_window is not None:
            try:
                self._manual_window.destroy()
            except tk.TclError:
                pass
        self._manual_window = None

    def _manual_open_worlds(self) -> None:
        self._close_manual_window()
        self._cmd_open_world_editor()

    def _manual_open_simulation(self) -> None:
        self._close_manual_window()
        self.deiconify()
        self.lift()
        self.focus_force()

    def _manual_open_debug(self) -> None:
        self._manual_open_simulation()
        self._editor.focus_editor()

    def _on_close(self) -> None:
        """Cierra la aplicaciÃ³n de forma limpia."""
        if self._closing:
            return
        self._closing = True
        if self._persist_session:
            try:
                save_desktop_session(
                    {
                        "source": self._editor.get_code(),
                        "breakpoints": sorted(self._editor.get_breakpoints()),
                        "watches": self._editor.get_watches(),
                        "world_path": self._active_world_path,
                    }
                )
            except Exception:  # noqa: BLE001
                pass
        for callback_id in (self._tick_id, self._resize_after_id, self._layout_idle_id):
            if callback_id:
                try:
                    self.after_cancel(callback_id)
                except tk.TclError:
                    pass
        self._tick_id = None
        self._resize_after_id = None
        self._layout_idle_id = None
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


def _intro_image_path() -> Path:
    """Ruta de la introducción en código fuente y en ejecutables PyInstaller."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root) / "simulador_ev3" / "assets" / "Intro.png"
    return resolve_image_assets_dir() / "Intro.png"


def _load_intro_image() -> Any:
    """Carga la introducción reescalada exactamente a 800×450 px."""

    with Image.open(_intro_image_path()) as source:
        scaled = source.convert("RGBA").resize((_INTRO_WIDTH_PX, _INTRO_HEIGHT_PX), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(scaled)


def _center_splash_window(splash: tk.Tk | tk.Toplevel) -> None:
    """Fija la introducción a 800×450 px y la centra en el escritorio activo."""

    screen_w = max(1, splash.winfo_screenwidth())
    screen_h = max(1, splash.winfo_screenheight())
    width = min(_INTRO_WIDTH_PX, screen_w)
    height = min(_INTRO_HEIGHT_PX, screen_h)
    x = max(0, (screen_w - width) // 2)
    y = max(0, (screen_h - height) // 2)
    splash.geometry(f"{width}x{height}+{x}+{y}")


def _maximize_main_window(app: EV3SimulatorApp) -> None:
    """Abre la aplicación principal maximizada sin depender del gestor de ventanas."""

    try:
        app.state("zoomed")
        return
    except (AttributeError, tk.TclError):
        pass
    try:
        app.attributes("-zoomed", True)
    except (AttributeError, tk.TclError):
        # Fallback para gestores que no exponen el estado "zoomed".
        app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+0+0")


def _show_intro(app: EV3SimulatorApp, duration_ms: int = 3000) -> None:
    """Muestra una introducción no bloqueante antes de revelar la ventana principal."""
    splash = tk.Toplevel(app)
    splash.overrideredirect(True)
    splash.transient(app)
    splash.configure(bg="#ffffff")
    try:
        splash.attributes("-topmost", True)
    except tk.TclError:
        pass
    image: tk.PhotoImage | None = None
    try:
        image = _load_intro_image()
        tk.Label(splash, image=image, bg="#ffffff", bd=0).pack()
        splash._intro_image = image  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        tk.Label(
            splash,
            text="BotLab Studio",
            bg="#ffffff",
            fg="#1f3a5a",
            font=("Segoe UI", 20, "bold"),
            padx=48,
            pady=32,
        ).pack()

    app.update_idletasks()
    _center_splash_window(splash)
    splash.deiconify()
    splash.lift()
    splash.focus_force()
    splash.update_idletasks()

    def reveal() -> None:
        if splash.winfo_exists():
            try:
                splash.attributes("-topmost", False)
            except tk.TclError:
                pass
            splash.destroy()
        app.deiconify()
        app.lift()
        app.focus_force()

    app.after(duration_ms, reveal)


def _launch_after_intro(
    *,
    duration_ms: int = 3000,
    on_intro_ready: Optional[Callable[[tk.Tk], None]] = None,
    on_main_ready: Optional[Callable[[EV3SimulatorApp], None]] = None,
    app_factory: Optional[Callable[[], EV3SimulatorApp]] = None,
) -> None:
    """Usa la raíz inicial exclusivamente como introducción y luego crea la app."""
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.configure(bg="#ffffff")
    try:
        splash.attributes("-topmost", True)
    except tk.TclError:
        pass

    try:
        image = _load_intro_image()
        tk.Label(splash, image=image, bg="#ffffff", bd=0).pack()
        splash._intro_image = image  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        tk.Label(
            splash,
            text="BotLab Studio",
            bg="#ffffff",
            fg="#1f3a5a",
            font=("Segoe UI", 20, "bold"),
            padx=48,
            pady=32,
        ).pack()

    _center_splash_window(splash)
    splash.lift()
    splash.focus_force()
    splash.update_idletasks()
    if on_intro_ready is not None:
        on_intro_ready(splash)

    def launch() -> None:
        splash.destroy()
        app = app_factory() if app_factory is not None else EV3SimulatorApp()
        _maximize_main_window(app)
        if on_main_ready is not None:
            on_main_ready(app)
        app.mainloop()

    splash.after(duration_ms, launch)
    splash.mainloop()


def main() -> None:
    # En un ejecutable PyInstaller, los workers ``spawn`` vuelven a invocar el
    # punto de entrada. Resolverlo antes de crear la intro evita instancias UI
    # recursivas en procesos de worker.
    multiprocessing.freeze_support()
    _launch_after_intro()


if __name__ == "__main__":
    main()
