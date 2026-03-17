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
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from typing import Callable, Optional

# Palabras clave a resaltar (coloreado muy básico, sin librería externa)
_KEYWORDS = {
    "kw":      ("from", "import", "def", "class", "return", "if", "else",
                 "elif", "for", "while", "in", "not", "and", "or", "True",
                 "False", "None", "try", "except", "finally", "raise",
                 "with", "as", "pass", "break", "continue", "lambda"),
    "builtin": ("print", "len", "range", "str", "int", "float", "list",
                 "dict", "set", "tuple", "type"),
    "comment": ("#",),
}

_COLORS = {
    "kw":      "#79C0FF",
    "builtin": "#D2A8FF",
    "comment": "#7EE787",
    "string":  "#FFA657",
    "number":  "#A5D6FF",
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
        on_run:  Optional[Callable[[str], None]] = None,
        on_stop: Optional[Callable[[], None]]    = None,
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_run  = on_run
        self._on_stop = on_stop

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
        self._highlight()

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
        bar = tk.Frame(self, bg="#1E2530", padx=4, pady=4)
        bar.pack(side=tk.TOP, fill=tk.X)

        btn_style = {"relief": tk.FLAT, "padx": 10, "pady": 3, "cursor": "hand2"}

        btn_run = tk.Button(
            bar, text="▶  Ejecutar",
            bg="#4CAF50", fg="white",
            command=self._cmd_run,
            **btn_style,
        )
        btn_run.pack(side=tk.LEFT, padx=2)

        btn_stop = tk.Button(
            bar, text="■  Detener",
            bg="#F44336", fg="white",
            command=self._cmd_stop,
            **btn_style,
        )
        btn_stop.pack(side=tk.LEFT, padx=2)

        tk.Frame(bar, width=20, bg="#1E2530").pack(side=tk.LEFT)

        btn_open = tk.Button(
            bar, text="📂 Abrir…",
            bg="#2196F3", fg="white",
            command=self._cmd_open,
            **btn_style,
        )
        btn_open.pack(side=tk.LEFT, padx=2)

        btn_save = tk.Button(
            bar, text="💾 Guardar…",
            bg="#607D8B", fg="white",
            command=self._cmd_save,
            **btn_style,
        )
        btn_save.pack(side=tk.LEFT, padx=2)

        # Barra de estado
        self._status_var = tk.StringVar(value="Listo")
        self._status_lbl = tk.Label(
            bar, textvariable=self._status_var,
            bg="#1E2530", fg="#C9D1D9", anchor=tk.W,
        )
        self._status_lbl.pack(side=tk.RIGHT, padx=8)

    def _build_editor(self) -> None:
        frame = tk.Frame(self, bg="#0D1117")
        frame.pack(fill=tk.BOTH, expand=True)

        # Numeración de líneas
        self._linenos = tk.Text(
            frame, width=4, padx=4, takefocus=0,
            border=0, state=tk.DISABLED,
            bg="#0D1117", fg="#6E7681",
            font=("Courier New", 11),
        )
        self._linenos.pack(side=tk.LEFT, fill=tk.Y)

        # Scrollbar compartida
        scroll = tk.Scrollbar(frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Editor principal
        self._text = tk.Text(
            frame, undo=True, wrap=tk.NONE,
            font=("Courier New", 11),
            bg="#0D1117", fg="#E6EDF3",
            insertbackground="#58A6FF",
            selectbackground="#264F78",
            yscrollcommand=scroll.set,
        )
        self._text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.configure(command=self._text.yview)

        # Tags de sintaxis
        self._text.tag_configure("kw",      foreground=_COLORS["kw"])
        self._text.tag_configure("builtin", foreground=_COLORS["builtin"])
        self._text.tag_configure("comment", foreground=_COLORS["comment"])
        self._text.tag_configure("string",  foreground=_COLORS["string"])
        self._text.tag_configure("number",  foreground=_COLORS["number"])

        # Contenido inicial
        self._text.insert("1.0", _PLACEHOLDER)
        self._highlight()
        self._update_linenos()

        # Eventos
        self._text.bind("<KeyRelease>", lambda e: (self._highlight(), self._update_linenos()))

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
            col = 0

            # Comentario de línea completa
            stripped = line.lstrip()
            if stripped.startswith("#"):
                start = f"{row}.0"
                end   = f"{row}.{len(line)}"
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
                        self._text.tag_add("kw",      f"{row}.{i}", f"{row}.{j}")
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
        num_lines = int(self._text.index(tk.END).split(".")[0]) - 1
        self._linenos.configure(state=tk.NORMAL)
        self._linenos.delete("1.0", tk.END)
        self._linenos.insert(
            "1.0",
            "\n".join(str(i) for i in range(1, num_lines + 1))
        )
        self._linenos.configure(state=tk.DISABLED)
