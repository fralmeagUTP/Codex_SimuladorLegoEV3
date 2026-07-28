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
from tkinter import filedialog, messagebox, scrolledtext
from typing import Any, Callable, Optional

from simulador_ev3 import __version__
from simulador_ev3.application.desktop_session_adapter import DesktopSessionAdapter
from simulador_ev3.application.snapshot_dto import SnapshotDTO
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.domain.editor.world_editor_model import DEFAULT_WORLD_MM
from simulador_ev3.examples.example_catalog import ExampleCatalog
from simulador_ev3.shared.help_tutorials import HELP_TUTORIALS
from simulador_ev3.shared.mission_catalog import MissionCatalog
from simulador_ev3.shared.paths import (
    resolve_examples_dir,
    resolve_image_assets_dir,
    resolve_manual_path,
    resolve_worlds_dir,
)
from simulador_ev3.shared.ui_design_tokens import (
    LIGHT_TOKENS,
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
_MANUAL_PATH = resolve_manual_path()

_SCENARIOS: list[tuple[str, str, str]] = [
    ("Seguidor de línea", "01_linea_negra_basica.json", "11_siguelineas_basico.py"),
    ("Ultrasonido + obstáculos", "05_obstaculos_baliza_ir.json", "15_esquiva_obstaculos.py"),
    ("Test pantalla/altavoz", "05_obstaculos_baliza_ir.json", "02_intro_pantalla_altavoz.py"),
    ("Radar 360 ultrasonido", "12_radar_ultrasonido_360.json", "23_radar_ultrasonido_5grados.py"),
]

# Periodo del tick en ms (â‰ˆ50 Hz)
_TICK_MS = 20
_INTRO_WIDTH_PX = 800
_INTRO_HEIGHT_PX = 600


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
        self.title("Simulador EV3 Pybricks")
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
        self._lockable_menu_buttons: list[tk.Menubutton] = []
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
        self._header_menu_buttons: list[tk.Menubutton] = []
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
            text="Simulador EV3 Pybricks",
            bg=tokens.toolbar,
            fg=tokens.toolbar_text,
            font=("Segoe UI", 12, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 16))
        navigation = tk.Frame(header, bg=tokens.toolbar)
        navigation.pack(side=tk.LEFT)

        def add_menu_button(label: str, menu: tk.Menu, *, lockable: bool = False) -> None:
            button = tk.Menubutton(
                navigation,
                text=label,
                menu=menu,
                bg=tokens.toolbar,
                fg=tokens.toolbar_text,
                activebackground=tokens.primary,
                activeforeground=tokens.toolbar_text,
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=3,
                font=("Segoe UI", 9),
            )
            # No depender de la clase de bindings de Menubutton: con algunos
            # temas/entornos Windows el menú asociado deja de desplegarse.
            # El post explícito conserva el menú nativo y sus comandos.
            button.bind(
                "<Button-1>",
                lambda _event, item=button, popup=menu: self._post_header_menu(item, popup),  # type: ignore[misc]
            )
            button.bind(
                "<Return>",
                lambda _event, item=button, popup=menu: self._post_header_menu(item, popup),  # type: ignore[misc]
            )
            button.bind(
                "<space>",
                lambda _event, item=button, popup=menu: self._post_header_menu(item, popup),  # type: ignore[misc]
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
        for seconds in (30, 60, 120, 300):
            runtime_menu.add_command(label=f"{seconds} s", command=partial(self._set_max_runtime, seconds))
        runtime_menu.add_command(label="Sin limite", command=lambda: self._set_max_runtime(0))
        add_menu_button("Tiempo maximo", runtime_menu, lockable=True)

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
        help_menu.add_command(label="Manual de uso...", command=self._cmd_user_manual)
        help_menu.add_separator()
        help_menu.add_command(label="Acerca de...", command=self._cmd_about)
        add_menu_button("Ayuda", help_menu)

        self._update_menu_lock_state()

    @staticmethod
    def _post_header_menu(button: tk.Menubutton, menu: tk.Menu) -> str:
        """Despliega un menú de cabecera de forma fiable en Tkinter/Windows."""
        if str(button.cget("state")) == str(tk.DISABLED):
            return "break"
        button.focus_set()
        menu.tk_popup(button.winfo_rootx(), button.winfo_rooty() + button.winfo_height())
        return "break"

    def _set_theme(self, theme: str) -> None:
        self._theme_name = save_ui_theme(theme)
        self._apply_theme(self._theme_name)

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
            button.configure(
                bg=tokens.toolbar,
                fg=tokens.toolbar_text,
                activebackground=tokens.primary,
                activeforeground=tokens.toolbar_text,
                disabledforeground=tokens.text_muted,
            )
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
        self._root_hpane.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 0))

        # Columna izquierda: barra de control + mapa + telemetria/brick
        left_frame = tk.Frame(self._root_hpane, bg=tokens.background)
        self._root_hpane.add(left_frame, minsize=700, stretch="always")

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
        self._bottom_pane.pack(fill=tk.BOTH, padx=2, pady=(8, 0))

        self._telemetry_panel = TelemetryPanel(self._bottom_pane)
        self._brick_panel = BrickPanel(self._bottom_pane)
        # En pantallas de aula la telemetría se vuelve compacta; estos mínimos
        # impiden que el separador oculte alguno de los dos paneles.
        self._bottom_pane.add(self._telemetry_panel, minsize=300, stretch="always")
        self._bottom_pane.add(self._brick_panel, minsize=250, stretch="always")

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
        self._root_hpane.add(self._editor, minsize=420, stretch="always")

        self._status_strip = tk.Frame(self, bg=tokens.surface_muted, height=30)
        self._status_strip.pack(fill=tk.X, padx=12, pady=(6, 0))
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
        editor_w = max(420, int(width * 0.42))
        editor_x = max(640, width - editor_w)
        # La telemetría es una tabla de cuatro columnas: necesita prioridad de
        # anchura frente al brick para no comprimir sus celdas.
        bottom_available = max(1, editor_x - 20)
        telemetry_w = min(
            max(300, int(bottom_available * 0.60)),
            max(300, bottom_available - 250),
        )
        # El tablero incluye cuatro sensores y cuatro motores; con menos de
        # esta altura termina desplazándose y deja de conservar la tabla.
        bottom_height = max(300, int(height * 0.42))

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
                self._apply_snapshot(SnapshotDTO(payload))
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

    # ------------------------------------------------------------------
    # Callbacks del SimulationService
    # ------------------------------------------------------------------

    def _on_snapshot(self, dto) -> None:
        """Recibe el SnapshotDTO desde el EngineThread â€” DEBE serializar a Tkinter."""
        if self._service.worker_enabled:
            return
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
            "started": ("Ejecutando...", "#1565C0"),
            "paused": ("Pausado", "#F57F17"),
            "resumed": ("Ejecutando...", "#1565C0"),
            "stopped": ("Detenido", "#424242"),
            "finished": ("Finalizado", "#424242"),
            "timed_out": ("Tiempo agotado", "#B71C1C"),
            "error": ("Error", "#B71C1C"),
            "reset": ("Listo", "#212121"),
            "world_loaded": ("Mundo cargado", "#2E7D32"),
        }
        msg, color = status_map.get(status, (status, "#212121"))
        self.after_idle(self._editor.set_status, msg, color)
        self.after_idle(self._status_text_var.set, f"Estado: {msg}")
        self.after_idle(self._telemetry_panel.set_execution_status, status)
        self.after_idle(self._sync_sim_control_states, status)

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
        self._editor.set_status(
            f"Misión {state}: {result['score']:.0f} puntos", "#2E7D32" if result["passed"] else "#B71C1C"
        )
        messagebox.showinfo(
            "Resultado de misión",
            (
                f"{payload['mission']['title']}\n\nEstado: {state}\n"
                f"Puntuación: {result['score']:.0f}\n\nCriterios:\n{criteria}"
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
        self._service.reset()
        self._set_execution_menu_locked(False)
        self._canvas.reset()
        self._brick_panel.reset()
        self._telemetry_panel.reset()
        self._activate_placement_mode()
        snapshot = self._service.current_snapshot()
        if snapshot is not None:
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
        self._editor.set_status(f"Misión cargada: {mission.title}", "#2E7D32")

    def _refresh_world_canvas(self) -> None:
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
            "Simulador LEGO Mindstorms EV3 basado en la libreria Pybricks\n"
            f"Version {__version__}\n\n"
            "Desarrollado por:\n"
            "  - Francisco Alejandro Medina Aguirre\n"
            "  - Jimy Alexander Cortés Osorio\n\n"
            "Aliados academicos:\n"
            "  - Grupo Nyquist\n"
            "  - Robotica Aplicada\n"
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

        header = tk.Label(
            win,
            text="Ayuda y manual de uso - Simulador EV3 Pybricks",
            bg=tokens.background,
            fg=tokens.focus,
            anchor="w",
            font=("Segoe UI", 11, "bold"),
            padx=10,
            pady=8,
        )
        header.pack(side=tk.TOP, fill=tk.X)

        navigation = tk.Frame(win, bg=tokens.background, padx=10, pady=8)
        navigation.pack(side=tk.TOP, fill=tk.X)
        tk.Button(navigation, text="Crear mundos", command=self._manual_open_worlds).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(navigation, text="Ir a simulación", command=self._manual_open_simulation).pack(side=tk.LEFT, padx=6)
        tk.Button(navigation, text="Preparar depuración", command=self._manual_open_debug).pack(side=tk.LEFT, padx=6)

        txt = scrolledtext.ScrolledText(
            win,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=tokens.surface,
            fg=tokens.text,
            padx=10,
            pady=8,
        )
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        txt.insert("1.0", self._tutorials_as_text() + "\n\n" + self._read_manual_text())
        txt.configure(state=tk.DISABLED)

    def _tutorials_as_text(self) -> str:
        """Presentación textual de los tutoriales compartidos para Tkinter."""

        sections = ["TUTORIALES GUIADOS"]
        for tutorial in HELP_TUTORIALS:
            steps = "\n".join(f"  {index}. {step}" for index, step in enumerate(tutorial.steps, start=1))
            sections.append(
                f"{tutorial.title}\n{steps}\n"
                f"Resultado esperado: {tutorial.expected_result}\n"
                f"Si falla: {tutorial.recovery}"
            )
        return "\n\n".join(sections)

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

    def _read_manual_text(self) -> str:
        """Lee el manual desde la ruta compartida de documentacion."""
        path = Path(_MANUAL_PATH)
        if not path.exists():
            return f"No se encontro el manual de uso.\n\nRuta esperada:\n{path}"
        try:
            return path.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            return f"No fue posible leer el manual de uso.\n\nArchivo: {path}\nDetalle: {exc}"

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


def _center_splash_window(splash: tk.Tk | tk.Toplevel) -> None:
    """Fija la introducción a 800×600 px y la centra en el escritorio activo."""

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
        source = tk.PhotoImage(file=str(_intro_image_path()))
        screen_w = max(1, splash.winfo_screenwidth())
        screen_h = max(1, splash.winfo_screenheight())
        max_w = max(1, screen_w - 80)
        max_h = max(1, screen_h - 80)
        factor = max(1, -(-source.width() // max_w), -(-source.height() // max_h))
        image = source.subsample(factor, factor) if factor > 1 else source
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
        image = tk.PhotoImage(file=str(_intro_image_path()))
        max_w = max(1, splash.winfo_screenwidth() - 80)
        max_h = max(1, splash.winfo_screenheight() - 80)
        factor = max(1, -(-image.width() // max_w), -(-image.height() // max_h))
        image = image.subsample(factor, factor) if factor > 1 else image
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
