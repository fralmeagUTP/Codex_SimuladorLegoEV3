"""
editor_panel.py — Panel editor de código Python para el simulador EV3.

Proporciona:
  • Editor de texto con resaltado de sintaxis básico (coloreado por palabras).
  • Botones: Ejecutar / Detener / Cargar archivo / Guardar archivo.
  • Numeración de líneas.
  • Callback `on_run(source_code: str)` que la ventana principal conecta
    con SimulationService.load_script + start().
"""

from __future__ import annotations

import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any, Callable, Optional

from simulador_ev3.shared.debug_configuration import normalize_watches
from simulador_ev3.shared.ui_design_tokens import LIGHT_TOKENS

# Palabras clave a resaltar (coloreado muy básico, sin librería externa)
_KEYWORDS = {
    "kw": (
        "from",
        "import",
        "def",
        "class",
        "return",
        "if",
        "else",
        "elif",
        "for",
        "while",
        "in",
        "not",
        "and",
        "or",
        "True",
        "False",
        "None",
        "try",
        "except",
        "finally",
        "raise",
        "with",
        "as",
        "pass",
        "break",
        "continue",
        "lambda",
    ),
    "builtin": ("print", "len", "range", "str", "int", "float", "list", "dict", "set", "tuple", "type"),
    "comment": ("#",),
}

_COLORS = {
    "kw": "#79C0FF",
    "builtin": "#D2A8FF",
    "comment": "#7EE787",
    "string": "#FFA657",
    "number": "#A5D6FF",
}

_PLACEHOLDER = """\
# Escribe tu script EV3 aquí
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Color
from pybricks.tools import wait

ev3 = EV3Brick()
left  = Motor(Port.A)
right = Motor(Port.C)

left.run(500)
right.run(500)
wait(2000)
left.stop()
right.stop()
"""

_PYBRICKS_HINTS = (
    "EV3Brick",
    "Motor",
    "ColorSensor",
    "UltrasonicSensor",
    "TouchSensor",
    "GyroSensor",
    "DriveBase",
    "Port",
    "Color",
    "Direction",
    "Stop",
    "Button",
    "wait",
    "run",
    "run_time",
    "run_angle",
    "dc",
    "stop",
    "angle",
    "speed",
    "drive",
    "turn",
    "straight",
    "distance",
    "state",
    "reflection",
    "rgb",
    "pressed",
    "beep",
    "screen",
    "clear",
    "print",
)

_AUTOCOMPLETE_WORDS = tuple(sorted(set(_KEYWORDS["kw"]) | set(_KEYWORDS["builtin"]) | set(_PYBRICKS_HINTS)))

_CONTEXT_HINTS = {
    "EV3Brick": ("screen", "speaker", "light", "buttons"),
    "Port": ("A", "B", "C", "D", "S1", "S2", "S3", "S4"),
    "Color": (
        "BLACK",
        "BLUE",
        "BROWN",
        "CYAN",
        "GREEN",
        "ORANGE",
        "PURPLE",
        "RED",
        "WHITE",
        "YELLOW",
    ),
    "Stop": ("BRAKE", "COAST", "HOLD"),
    "Direction": ("CLOCKWISE", "COUNTERCLOCKWISE"),
    "Button": ("LEFT", "RIGHT", "UP", "DOWN", "CENTER"),
    "Motor": ("run", "run_time", "run_angle", "dc", "hold", "brake", "stop", "angle", "speed"),
    "DriveBase": ("drive", "stop", "straight", "turn", "distance", "state"),
    "ColorSensor": ("reflection", "rgb", "color"),
    "UltrasonicSensor": ("distance", "presence"),
    "TouchSensor": ("pressed",),
    "Screen": ("clear", "print"),
    "Speaker": ("beep",),
    "Light": ("on", "off"),
}

_ATTR_TYPE_HINTS = {
    ("EV3Brick", "screen"): "Screen",
    ("EV3Brick", "speaker"): "Speaker",
    ("EV3Brick", "light"): "Light",
}


class EditorPanel(tk.Frame):
    """
    Panel editor de código para el simulador EV3.

    Args:
        parent:   Widget padre.
        on_run:   Callback(source_code) llamado al pulsar "Ejecutar".
        on_stop:  Callback() llamado al pulsar "Detener".
        **kwargs: Argumentos para tk.Frame.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_run: Optional[Callable[[str], None]] = None,
        on_debug: Optional[Callable[[str], None]] = None,
        on_debug_step: Optional[Callable[[], None]] = None,
        on_debug_continue: Optional[Callable[[], None]] = None,
        on_breakpoints_changed: Optional[Callable[[set[int]], None]] = None,
        on_watches_changed: Optional[Callable[[list[str]], None]] = None,
        on_stop: Optional[Callable[[], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_run = on_run
        self._on_debug = on_debug
        self._on_debug_step = on_debug_step
        self._on_debug_continue = on_debug_continue
        self._on_breakpoints_changed = on_breakpoints_changed
        self._on_watches_changed = on_watches_changed
        self._on_stop = on_stop
        self._debug_line: Optional[int] = None
        self._breakpoints: set[int] = set()
        self._watches: list[str] = []
        self._ac_popup: Optional[tk.Toplevel] = None
        self._ac_listbox: Optional[tk.Listbox] = None
        self._ac_items: list[str] = []
        self._pair_map = {
            "(": ")",
            "[": "]",
            "{": "}",
            '"': '"',
            "'": "'",
        }
        self._closing_chars = set(")]}\"'")

        self._build_toolbar()
        self._build_editor()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def get_code(self) -> str:
        """Devuelve el contenido del editor."""
        return self._text.get("1.0", tk.END)

    def set_code(self, code: str) -> None:
        """Reemplaza el contenido del editor."""
        self._text.delete("1.0", tk.END)
        self._text.insert("1.0", code)
        try:
            self._text.mark_set("insert", "1.0")
            self._text.see("1.0")
            self._text.yview_moveto(0.0)
        except Exception:  # noqa: BLE001
            pass
        self.clear_debug_line()
        self._highlight()
        self._update_linenos()

    def highlight_debug_line(self, line_no: int) -> None:
        """Resalta la linea actual de depuracion."""
        self.clear_debug_line()
        if line_no <= 0:
            return
        self._debug_line = int(line_no)
        start = f"{self._debug_line}.0"
        end = f"{self._debug_line}.end"
        try:
            self._text.tag_add("debug_line", start, end)
            self._text.see(start)
        except Exception:  # noqa: BLE001
            pass
        self._update_linenos()

    def clear_debug_line(self) -> None:
        self._debug_line = None
        try:
            self._text.tag_remove("debug_line", "1.0", tk.END)
        except Exception:  # noqa: BLE001
            pass
        self._update_linenos()

    def get_breakpoints(self) -> set[int]:
        return set(self._breakpoints)

    def set_breakpoints(self, breakpoints: set[int]) -> None:
        self._breakpoints = {int(line) for line in breakpoints if int(line) > 0}
        breakpoints_var = getattr(self, "_breakpoints_var", None)
        if breakpoints_var is not None:
            breakpoints_var.set(", ".join(str(line) for line in sorted(self._breakpoints)))
        self._update_linenos()

    def get_watches(self) -> list[str]:
        """Devuelve las expresiones watch configuradas para la depuración."""
        return list(self._watches)

    def set_watches(self, watches: list[str]) -> None:
        """Actualiza watches usando el mismo límite de la interfaz web."""
        self._watches = normalize_watches(watches)
        self._watches_var.set(", ".join(self._watches))

    def show_watch_results(self, watches: list[dict]) -> None:
        """Muestra el resultado de los watches evaluados en la pausa actual."""
        if not watches:
            self._watch_results_var.set("Watches: sin datos (pausa para evaluar)")
            return
        values: list[str] = []
        for item in watches:
            expression = str(item.get("expr", ""))
            error = item.get("error")
            result = f"error: {error}" if error else repr(item.get("value"))
            values.append(f"{expression} = {result}")
        self._watch_results_var.set("Watches: " + " | ".join(values))

    def set_status(self, msg: str, color: str = "black") -> None:
        """Actualiza la barra de estado del editor."""
        self._status_var.set(msg)
        self._status_lbl.configure(fg=color)

    def load_file(self, path: str) -> None:
        """Carga el código desde un fichero externo."""
        with open(path, encoding="utf-8") as f:
            self.set_code(f.read())

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------

    def _build_toolbar(self) -> None:
        tokens = LIGHT_TOKENS
        bar = tk.Frame(self, bg=tokens.surface, padx=6, pady=4)
        bar.pack(side=tk.TOP, fill=tk.X)
        bar.configure(highlightthickness=1, highlightbackground=tokens.border)

        title = tk.Label(
            bar,
            text="Editor de codigo",
            bg=tokens.surface,
            fg=tokens.text,
            font=("Segoe UI", 10, "bold"),
        )
        title.pack(side=tk.LEFT, padx=(2, 8))
        tk.Label(
            bar,
            text="Python (Pybricks)",
            bg=tokens.surface,
            fg=tokens.text,
            relief=tk.SOLID,
            bd=1,
            padx=6,
            pady=2,
            font=("Segoe UI", 9),
        ).pack(side=tk.RIGHT, padx=(8, 2))

        btn_style: dict[str, Any] = {
            "relief": tk.FLAT,
            "padx": 10,
            "pady": 3,
            "cursor": "hand2",
            "font": ("Segoe UI", 9),
            "bd": 1,
            "highlightthickness": 0,
        }

        debug_bar = tk.Frame(self, bg=tokens.surface_muted, padx=6, pady=3)
        debug_bar.pack(side=tk.TOP, fill=tk.X)
        debug_bar.configure(highlightthickness=1, highlightbackground=tokens.border)

        btn_debug = tk.Button(
            debug_bar,
            text="Depurar",
            bg=tokens.surface,
            fg=tokens.primary_active,
            command=self._cmd_debug,
            **btn_style,
        )
        btn_debug.pack(side=tk.LEFT, padx=2)

        btn_step = tk.Button(
            debug_bar,
            text="Paso",
            bg=tokens.surface,
            fg=tokens.primary_active,
            command=self._cmd_debug_step,
            **btn_style,
        )
        btn_step.pack(side=tk.LEFT, padx=2)

        btn_continue = tk.Button(
            debug_bar,
            text="Continuar",
            bg=tokens.surface,
            fg=tokens.primary_active,
            command=self._cmd_debug_continue,
            **btn_style,
        )
        btn_continue.pack(side=tk.LEFT, padx=2)

        self._breakpoints_var = tk.StringVar()
        tk.Label(debug_bar, text="Breakpoints", bg=tokens.surface_muted, fg=tokens.primary_active).pack(
            side=tk.LEFT, padx=(10, 2)
        )
        breakpoints_entry = tk.Entry(debug_bar, textvariable=self._breakpoints_var, width=10)
        breakpoints_entry.pack(side=tk.LEFT, padx=2)
        breakpoints_entry.bind("<FocusOut>", self._on_breakpoints_changed_event)
        breakpoints_entry.bind("<Return>", self._on_breakpoints_changed_event)

        watches_bar = tk.Frame(self, bg=tokens.surface_muted, padx=6, pady=2)
        watches_bar.pack(side=tk.TOP, fill=tk.X)
        self._watches_var = tk.StringVar()
        tk.Label(watches_bar, text="Watches", bg=tokens.surface_muted, fg=tokens.primary_active).pack(
            side=tk.LEFT, padx=(2, 6)
        )
        watches_entry = tk.Entry(watches_bar, textvariable=self._watches_var)
        watches_entry.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        watches_entry.bind("<FocusOut>", self._on_watches_changed_event)
        watches_entry.bind("<Return>", self._on_watches_changed_event)

        self._status_var = tk.StringVar(value="sin eventos")
        self._status_lbl = tk.Label(
            watches_bar,
            textvariable=self._status_var,
            bg=tokens.surface_muted,
            fg=tokens.text_muted,
            anchor=tk.W,
            font=("Consolas", 9),
        )
        self._status_lbl.pack(side=tk.RIGHT, padx=8)

        self._watch_results_var = tk.StringVar(value="Watches: sin configurar")
        tk.Label(
            self,
            textvariable=self._watch_results_var,
            bg="#F5F8FC",
            fg="#385273",
            anchor=tk.W,
            font=("Consolas", 8),
            padx=8,
            pady=2,
        ).pack(side=tk.TOP, fill=tk.X)

    def _on_watches_changed_event(self, _event=None):
        parsed = [part.strip() for part in self._watches_var.get().replace("\n", ",").split(",")]
        self.set_watches(parsed)
        if self._on_watches_changed:
            self._on_watches_changed(self.get_watches())
        return "break" if _event is not None else None

    def _on_breakpoints_changed_event(self, _event=None):
        parsed = {
            int(part.strip())
            for part in self._breakpoints_var.get().replace("\n", ",").split(",")
            if part.strip().isdigit() and int(part.strip()) > 0
        }
        self.set_breakpoints(parsed)
        if self._on_breakpoints_changed:
            self._on_breakpoints_changed(self.get_breakpoints())
        return "break" if _event is not None else None

    def _build_editor(self) -> None:
        frame = tk.Frame(self, bg="#FFFFFF")
        frame.pack(fill=tk.BOTH, expand=True)

        # Numeración de líneas
        self._linenos = tk.Text(
            frame,
            width=6,
            padx=4,
            takefocus=0,
            border=0,
            state=tk.DISABLED,
            bg="#F8FAFC",
            fg="#74849A",
            font=("Consolas", 10),
        )
        self._linenos.pack(side=tk.LEFT, fill=tk.Y)

        # Scrollbar compartida
        self._scroll = tk.Scrollbar(frame)
        self._scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Editor principal
        self._text = tk.Text(
            frame,
            undo=True,
            wrap=tk.NONE,
            font=("Consolas", 10),
            bg="#FFFFFF",
            fg="#172033",
            insertbackground="#1B3557",
            selectbackground="#D7E8FA",
            yscrollcommand=self._on_text_vertical_scroll,
        )
        self._text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scroll.configure(command=self._on_vertical_scroll)

        # Tags de sintaxis
        self._text.tag_configure("kw", foreground=_COLORS["kw"])
        self._text.tag_configure("builtin", foreground=_COLORS["builtin"])
        self._text.tag_configure("comment", foreground=_COLORS["comment"])
        self._text.tag_configure("string", foreground=_COLORS["string"])
        self._text.tag_configure("number", foreground=_COLORS["number"])
        self._text.tag_configure("debug_line", background="#3A2E00")
        self._linenos.tag_configure("breakpoint_dot", foreground="#FF3B30")
        self._linenos.tag_configure(
            "breakpoint_line",
            foreground="#FF8A80",
            font=("Courier New", 11, "bold"),
        )
        self._linenos.tag_configure("debug_current_line", background="#3A2E00")

        # Contenido inicial
        self._text.insert("1.0", _PLACEHOLDER)
        self._highlight()
        self._update_linenos()

        # Eventos
        self._text.bind("<KeyRelease>", self._on_key_release)
        self._text.bind("<KeyPress>", self._on_key_press)
        self._text.bind("<Control-space>", self._on_ctrl_space)
        self._text.bind("<Tab>", self._on_tab_pressed)
        self._text.bind("<Return>", self._on_return_pressed)
        self._text.bind("<Escape>", self._on_escape_pressed)
        self._text.bind("<Up>", self._on_up_pressed)
        self._text.bind("<Down>", self._on_down_pressed)
        self._text.bind("<Button-1>", lambda _e: self._hide_autocomplete())
        self._text.bind("<FocusOut>", lambda _e: self._hide_autocomplete())
        self._linenos.bind("<MouseWheel>", self._on_linenos_mousewheel)
        self._linenos.bind("<Button-4>", self._on_linenos_mousewheel_linux_up)
        self._linenos.bind("<Button-5>", self._on_linenos_mousewheel_linux_down)
        self._linenos.bind("<Button-1>", self._on_linenos_click)

    # ------------------------------------------------------------------
    # IntelliSense básico (MVP)
    # ------------------------------------------------------------------

    @staticmethod
    def _autocomplete_candidates(
        prefix: str,
        context_name: Optional[str] = None,
        limit: int = 25,
    ) -> list[str]:
        if context_name and context_name in _CONTEXT_HINTS:
            words = _CONTEXT_HINTS[context_name]
            pref = prefix.strip().lower()
            if not pref:
                return list(words[:limit])
            return [w for w in words if w.lower().startswith(pref)][:limit]

        pref = prefix.strip()
        if not pref:
            return list(_AUTOCOMPLETE_WORDS[:limit])
        pref_l = pref.lower()
        items = [w for w in _AUTOCOMPLETE_WORDS if w.lower().startswith(pref_l)]
        return items[:limit]

    def _infer_variable_types(self, source_until_cursor: str) -> dict[str, str]:
        """
        Inferencia simple de tipos por asignacion:
            left = Motor(...)
            bot = DriveBase(...)
        y aliases de import:
            from ... import Motor as M
            left = M(...)
        """
        var_types: dict[str, str] = {}
        alias_to_type: dict[str, str] = {}
        known_types = set(_CONTEXT_HINTS.keys())

        for t in known_types:
            alias_to_type[t] = t

        for raw_line in source_until_cursor.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            m_imp = re.match(r"from\s+[\w\.]+\s+import\s+(.+)$", line)
            if m_imp:
                chunk = m_imp.group(1)
                for token in chunk.split(","):
                    token = token.strip()
                    if not token:
                        continue
                    m_as = re.match(
                        r"([A-Za-z_][A-Za-z0-9_]*)(?:\s+as\s+([A-Za-z_][A-Za-z0-9_]*))?$",
                        token,
                    )
                    if not m_as:
                        continue
                    name = m_as.group(1)
                    alias = m_as.group(2) or name
                    if name in known_types:
                        alias_to_type[alias] = name
                continue

            m_asg = re.match(
                r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(",
                line,
            )
            if not m_asg:
                continue
            var_name = m_asg.group(1)
            ctor_name = m_asg.group(2)
            resolved = alias_to_type.get(ctor_name)
            if resolved in known_types:
                var_types[var_name] = resolved

        return var_types

    def _current_completion_context(self) -> tuple[Optional[str], str]:
        """
        Detecta autocompletado contextual para expresiones tipo:
        Port.S  -> ("Port", "S")
        Port.   -> ("Port", "")
        """
        try:
            current_line = self._text.get("insert linestart", "insert")
            source = self._text.get("1.0", "insert")
        except Exception:  # noqa: BLE001
            return None, ""
        if "\n" in current_line:
            current_line = current_line.splitlines()[-1]
        match = re.search(
            r"([A-Za-z_][A-Za-z0-9_\.]*)\.([A-Za-z_][A-Za-z0-9_]*)?$",
            current_line,
        )
        if not match:
            return None, ""
        obj = match.group(1).strip()
        pref = match.group(2) or ""

        # Caso directo (Port., Motor., etc.)
        if obj in _CONTEXT_HINTS:
            return obj, pref

        parts = obj.split(".")
        var_types = self._infer_variable_types(source)
        base_type = var_types.get(parts[0])
        if base_type is None:
            return None, pref

        # Variable directa (left. -> Motor)
        current_type: str | None = base_type
        for attr in parts[1:]:
            if current_type is None:
                return None, pref
            current_type = _ATTR_TYPE_HINTS.get((current_type, attr))
            if current_type is None:
                return None, pref

        if current_type not in _CONTEXT_HINTS:
            return None, pref
        return current_type, pref

    def _on_key_release(self, event) -> None:
        self._highlight()
        self._update_linenos()
        if event.keysym in {
            "Up",
            "Down",
            "Left",
            "Right",
            "Escape",
            "Return",
            "Tab",
            "Shift_L",
            "Shift_R",
            "Control_L",
            "Control_R",
            "Alt_L",
            "Alt_R",
        }:
            return
        context_name, ctx_prefix = self._current_completion_context()
        if context_name is not None:
            self._show_autocomplete(ctx_prefix, context_name=context_name, force=True)
            return

        prefix = self._current_word_prefix()
        if len(prefix) >= 1:
            self._show_autocomplete(prefix)
            return
        self._hide_autocomplete()

    def _on_text_vertical_scroll(self, first: float, last: float) -> None:
        """Sincroniza scrollbar y gutter cuando el editor se desplaza."""
        self._scroll.set(first, last)
        try:
            self._linenos.yview_moveto(first)
        except Exception:  # noqa: BLE001
            pass

    def _on_vertical_scroll(self, *args) -> None:
        """Desplaza editor y numeracion desde la barra vertical."""
        self._text.yview(*args)
        try:
            self._linenos.yview(*args)
        except Exception:  # noqa: BLE001
            pass

    def _on_linenos_mousewheel(self, event):
        """Reenvia rueda del raton del gutter al editor principal."""
        delta = getattr(event, "delta", 0)
        if delta == 0:
            return "break"
        steps = -1 * int(delta / 120)
        if steps == 0:
            steps = -1 if delta > 0 else 1
        self._text.yview_scroll(steps, "units")
        return "break"

    def _on_linenos_mousewheel_linux_up(self, _event):
        self._text.yview_scroll(-1, "units")
        return "break"

    def _on_linenos_mousewheel_linux_down(self, _event):
        self._text.yview_scroll(1, "units")
        return "break"

    def _on_linenos_click(self, event):
        try:
            idx = self._linenos.index(f"@0,{event.y}")
            line_no = int(str(idx).split(".")[0])
        except Exception:  # noqa: BLE001
            return "break"
        if line_no <= 0:
            return "break"
        if line_no in self._breakpoints:
            self._breakpoints.remove(line_no)
        else:
            self._breakpoints.add(line_no)
        if self._on_breakpoints_changed:
            try:
                self._on_breakpoints_changed(set(self._breakpoints))
            except Exception:  # noqa: BLE001
                pass
        self._update_linenos()
        return "break"

    def _on_key_press(self, event):
        # Auto-cierre de paréntesis/comillas
        ch = event.char or ""
        if ch in self._pair_map:
            # Evitar doble autocomilla si ya hay comilla cerrando
            if ch in ("'", '"') and self._char_at_cursor() == ch:
                self._text.mark_set("insert", "insert+1c")
                return "break"
            close = self._pair_map[ch]
            self._text.insert("insert", ch + close)
            self._text.mark_set("insert", "insert-1c")
            return "break"

        # Si el usuario escribe un cierre y ya existe el mismo en cursor:
        # mover cursor en vez de duplicar.
        if ch in self._closing_chars and self._char_at_cursor() == ch:
            self._text.mark_set("insert", "insert+1c")
            return "break"
        return None

    def _on_ctrl_space(self, _event):
        context_name, ctx_prefix = self._current_completion_context()
        if context_name is not None:
            self._show_autocomplete(ctx_prefix, context_name=context_name, force=True)
            return "break"
        prefix = self._current_word_prefix()
        self._show_autocomplete(prefix, force=True)
        return "break"

    def _on_tab_pressed(self, _event):
        if self._is_autocomplete_visible():
            self._apply_autocomplete_selection()
            return "break"
        self._text.insert("insert", "    ")
        return "break"

    def _on_return_pressed(self, _event):
        if self._is_autocomplete_visible():
            self._apply_autocomplete_selection()
            return "break"
        self._insert_newline_with_indent()
        return "break"

    def _on_escape_pressed(self, _event):
        if self._is_autocomplete_visible():
            self._hide_autocomplete()
            return "break"
        return None

    def _on_up_pressed(self, _event):
        if self._is_autocomplete_visible():
            self._move_autocomplete_selection(-1)
            return "break"
        return None

    def _on_down_pressed(self, _event):
        if self._is_autocomplete_visible():
            self._move_autocomplete_selection(1)
            return "break"
        return None

    def _is_autocomplete_visible(self) -> bool:
        return self._ac_popup is not None and self._ac_listbox is not None

    def _current_word_prefix(self) -> str:
        try:
            current = self._text.get("insert linestart", "insert")
        except Exception:  # noqa: BLE001
            return ""
        match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)$", current)
        return match.group(1) if match else ""

    def _char_at_cursor(self) -> str:
        try:
            return self._text.get("insert", "insert+1c")
        except Exception:  # noqa: BLE001
            return ""

    def _show_autocomplete(
        self,
        prefix: str,
        context_name: Optional[str] = None,
        force: bool = False,
    ) -> None:
        items = self._autocomplete_candidates(prefix, context_name=context_name)
        if not force:
            items = [w for w in items if w != prefix]
        if not items:
            self._hide_autocomplete()
            return
        self._ac_items = items

        if self._ac_popup is None or self._ac_listbox is None:
            self._ac_popup = tk.Toplevel(self)
            self._ac_popup.overrideredirect(True)
            try:
                self._ac_popup.wm_attributes("-topmost", True)
            except Exception:  # noqa: BLE001
                pass
            self._ac_listbox = tk.Listbox(
                self._ac_popup,
                height=8,
                activestyle="none",
                bg="#0B1220",
                fg="#E6EDF3",
                selectbackground="#1E3A5F",
                selectforeground="#FFFFFF",
            )
            self._ac_listbox.pack(fill=tk.BOTH, expand=True)
            self._ac_listbox.bind("<Double-Button-1>", lambda _e: self._apply_autocomplete_selection())
            self._ac_listbox.bind("<Return>", lambda _e: self._apply_autocomplete_selection())

        self._ac_listbox.delete(0, tk.END)
        for item in items:
            self._ac_listbox.insert(tk.END, item)
        self._ac_listbox.selection_clear(0, tk.END)
        self._ac_listbox.selection_set(0)
        self._ac_listbox.activate(0)

        x, y = self._autocomplete_popup_coords()
        self._ac_popup.geometry(f"+{x}+{y}")
        self._ac_popup.deiconify()

    def _autocomplete_popup_coords(self) -> tuple[int, int]:
        # Posicionar popup justo bajo el cursor de inserción.
        try:
            bbox = self._text.bbox("insert")
            if bbox:
                x, y, _w, h = bbox
                root_x = int(getattr(self._text, "winfo_rootx", lambda: 0)())
                root_y = int(getattr(self._text, "winfo_rooty", lambda: 0)())
                return root_x + x, root_y + y + h + 2
        except Exception:  # noqa: BLE001
            pass
        return 60, 60

    def _hide_autocomplete(self) -> None:
        if self._ac_popup is not None:
            try:
                self._ac_popup.destroy()
            except Exception:  # noqa: BLE001
                pass
        self._ac_popup = None
        self._ac_listbox = None
        self._ac_items = []

    def _move_autocomplete_selection(self, step: int) -> None:
        if self._ac_listbox is None or not self._ac_items:
            return
        cur = self._ac_listbox.curselection()
        idx = int(cur[0]) if cur else 0
        nxt = max(0, min(len(self._ac_items) - 1, idx + step))
        self._ac_listbox.selection_clear(0, tk.END)
        self._ac_listbox.selection_set(nxt)
        self._ac_listbox.activate(nxt)

    def _apply_autocomplete_selection(self):
        if self._ac_listbox is None or not self._ac_items:
            return None
        cur = self._ac_listbox.curselection()
        idx = int(cur[0]) if cur else 0
        value = self._ac_items[idx]
        prefix = self._current_word_prefix()
        if prefix:
            self._text.delete(f"insert-{len(prefix)}c", "insert")
        self._text.insert("insert", value)
        self._hide_autocomplete()
        self._highlight()
        self._update_linenos()
        return "break"

    def _insert_newline_with_indent(self) -> None:
        line = self._text.get("insert linestart", "insert lineend")
        m = re.match(r"^(\s*)", line)
        indent = m.group(1) if m else ""
        extra = "    " if line.rstrip().endswith(":") else ""
        self._text.insert("insert", "\n" + indent + extra)
        self._hide_autocomplete()
        self._highlight()
        self._update_linenos()

    # ------------------------------------------------------------------
    # Comandos de toolbar
    # ------------------------------------------------------------------

    def _cmd_run(self) -> None:
        code = self.get_code()
        self.set_status("Ejecutando…", color="#1565C0")
        if self._on_run:
            self._on_run(code)

    def _cmd_stop(self) -> None:
        self.set_status("Deteniendo…", color="#B71C1C")
        if self._on_stop:
            self._on_stop()

    def _cmd_debug(self) -> None:
        code = self.get_code()
        self.clear_debug_line()
        self.set_status("Depurando…", color="#EF6C00")
        if self._on_debug:
            self._on_debug(code)
        elif self._on_run:
            self._on_run(code)

    def _cmd_debug_step(self) -> None:
        self.set_status("Depuracion paso", color="#8E24AA")
        if self._on_debug_step:
            self._on_debug_step()

    def _cmd_debug_continue(self) -> None:
        self.set_status("Depuracion continuar", color="#00897B")
        if self._on_debug_continue:
            self._on_debug_continue()

    def _cmd_open(self) -> None:
        path = filedialog.askopenfilename(
            title="Abrir script Python",
            filetypes=[("Python", "*.py"), ("Todos", "*.*")],
        )
        if path:
            try:
                self.load_file(path)
                self.set_status(f"Cargado: {os.path.basename(path)}")
            except OSError as exc:
                messagebox.showerror("Error al abrir", str(exc))

    def _cmd_save(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Guardar script",
            defaultextension=".py",
            filetypes=[("Python", "*.py"), ("Todos", "*.*")],
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.get_code())
                self.set_status(f"Guardado: {os.path.basename(path)}")
            except OSError as exc:
                messagebox.showerror("Error al guardar", str(exc))

    # ------------------------------------------------------------------
    # Resaltado de sintaxis (básico, sin librería externa)
    # ------------------------------------------------------------------

    def _highlight(self) -> None:
        code = self._text.get("1.0", tk.END)
        # Limpiar tags previos
        for tag in ("kw", "builtin", "comment", "string", "number"):
            self._text.tag_remove(tag, "1.0", tk.END)

        lines = code.split("\n")
        for ln_idx, line in enumerate(lines):
            row = ln_idx + 1

            # Comentario de línea completa
            stripped = line.lstrip()
            if stripped.startswith("#"):
                start = f"{row}.0"
                end = f"{row}.{len(line)}"
                self._text.tag_add("comment", start, end)
                continue

            # Tokenizar palabra por palabra
            i = 0
            while i < len(line):
                ch = line[i]

                # String entre comillas simples o dobles
                if ch in ('"', "'"):
                    quote = ch
                    j = i + 1
                    while j < len(line) and line[j] != quote:
                        j += 1
                    end_col = j + 1
                    self._text.tag_add("string", f"{row}.{i}", f"{row}.{end_col}")
                    i = end_col
                    continue

                # Comentario inline
                if ch == "#":
                    self._text.tag_add("comment", f"{row}.{i}", f"{row}.{len(line)}")
                    break

                # Palabra
                if ch.isalpha() or ch == "_":
                    j = i
                    while j < len(line) and (line[j].isalnum() or line[j] == "_"):
                        j += 1
                    word = line[i:j]
                    if word in _KEYWORDS["kw"]:
                        self._text.tag_add("kw", f"{row}.{i}", f"{row}.{j}")
                    elif word in _KEYWORDS["builtin"]:
                        self._text.tag_add("builtin", f"{row}.{i}", f"{row}.{j}")
                    i = j
                    continue

                # Números
                if ch.isdigit():
                    j = i
                    while j < len(line) and (line[j].isdigit() or line[j] in "._"):
                        j += 1
                    self._text.tag_add("number", f"{row}.{i}", f"{row}.{j}")
                    i = j
                    continue

                i += 1

    def _update_linenos(self) -> None:
        first = 0.0
        try:
            yview = self._text.yview()
            if isinstance(yview, (tuple, list)) and yview:
                first = float(yview[0])
        except Exception:  # noqa: BLE001
            first = 0.0
        num_lines = int(self._text.index(tk.END).split(".")[0]) - 1
        self._linenos.configure(state=tk.NORMAL)
        self._linenos.delete("1.0", tk.END)
        gutter_lines: list[str] = []
        for i in range(1, num_lines + 1):
            if i in self._breakpoints:
                gutter_lines.append(f"● {i}")
            else:
                gutter_lines.append(f"  {i}")
        self._linenos.insert("1.0", "\n".join(gutter_lines))
        for line_no in sorted(self._breakpoints):
            if 1 <= line_no <= num_lines:
                self._linenos.tag_add(
                    "breakpoint_dot",
                    f"{line_no}.0",
                    f"{line_no}.1",
                )
                self._linenos.tag_add(
                    "breakpoint_line",
                    f"{line_no}.2",
                    f"{line_no}.end",
                )
        if self._debug_line is not None and 1 <= self._debug_line <= num_lines:
            self._linenos.tag_add(
                "debug_current_line",
                f"{self._debug_line}.0",
                f"{self._debug_line}.end",
            )
        self._linenos.configure(state=tk.DISABLED)
        try:
            self._linenos.yview_moveto(first)
        except Exception:  # noqa: BLE001
            pass

    def open_script_dialog(self) -> None:
        """Public helper to open a script from file dialog."""
        self._cmd_open()

    def save_script_dialog(self) -> None:
        """Public helper to save script with file dialog."""
        self._cmd_save()
