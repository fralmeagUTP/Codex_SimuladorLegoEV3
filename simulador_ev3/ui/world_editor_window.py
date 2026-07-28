"""
world_editor_window.py
======================
Standalone Tk window for creating and editing simulator worlds.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any, Callable, Optional

from simulador_ev3.application.world_editor_service import WorldEditorService
from simulador_ev3.domain.editor.world_editor_model import (
    CELL_SIZE_MM,
    GRID_SIZE_PX,
    MAX_WORLD_CELLS,
    MAX_WORLD_PIXELS,
)
from simulador_ev3.shared.paths import resolve_worlds_dir
from simulador_ev3.ui.object_properties_panel import ObjectPropertiesPanel
from simulador_ev3.ui.world_canvas_editor import WorldCanvasEditor
from simulador_ev3.ui.world_toolbar import WorldToolbar

_WORLDS_DIR = resolve_worlds_dir()
_BUILTIN_WORLD_FILENAMES = frozenset(
    {
        "01_linea_negra_basica.json",
        "02_linea_negra_v1.json",
        "03_linea_negra_v2.json",
        "04_linea_negra_v3.json",
        "05_obstaculos_baliza_ir.json",
        "06_pasillo_gyro_rumbo.json",
        "07_laberinto_v1.json",
        "08_laberinto_v2.json",
        "09_laberinto_v3.json",
        "10_laberinto_v4.json",
        "11_laberinto_v5.json",
        "12_radar_ultrasonido_360.json",
    }
)


class WorldEditorWindow(tk.Toplevel):
    """World editor window."""

    def __init__(
        self,
        parent: Any,
        on_world_saved: Optional[Callable[[str], None]] = None,
        on_simulate_saved: Optional[Callable[[str], None]] = None,
    ) -> None:
        super().__init__(parent)
        self.title("Editor de Mundos EV3")
        self.geometry("1320x860")
        self.minsize(980, 620)
        self.configure(bg="#ECEFF1")

        self._on_world_saved = on_world_saved
        self._on_simulate_saved = on_simulate_saved
        self._service = WorldEditorService()
        self._selected_id: Optional[str] = None
        self._current_path: Optional[Path] = None

        self._build()
        self._sync_world_size_inputs()
        self._refresh_canvas()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        self._toolbar = WorldToolbar(
            self,
            on_tool_change=self._on_tool_change,
            on_new=self._cmd_new,
            on_open=self._cmd_open,
            on_save=self._cmd_save,
            on_save_as=self._cmd_save_as,
            on_delete_world_file=self._cmd_delete_world_file,
            on_delete=self._cmd_delete_selected,
            on_duplicate=self._cmd_duplicate_selected,
            on_rotate=self._cmd_rotate_selected,
            on_apply_props=self._cmd_apply_properties,
            on_simulate_saved=self._cmd_simulate_saved,
        )
        self._toolbar.pack(fill=tk.X, side=tk.TOP)

        world_cfg = tk.Frame(self, bg="#ECEFF1", padx=8, pady=4)
        world_cfg.pack(fill=tk.X, side=tk.TOP)
        tk.Label(world_cfg, text="World W (cells):", bg="#ECEFF1").pack(side=tk.LEFT)
        self._world_w_entry = tk.Entry(world_cfg, width=8)
        self._world_w_entry.pack(side=tk.LEFT, padx=(4, 10))
        tk.Label(world_cfg, text="World H (cells):", bg="#ECEFF1").pack(side=tk.LEFT)
        self._world_h_entry = tk.Entry(world_cfg, width=8)
        self._world_h_entry.pack(side=tk.LEFT, padx=(4, 10))
        tk.Button(world_cfg, text="Aplicar tamano", command=self._cmd_apply_world_size).pack(side=tk.LEFT)
        tk.Frame(world_cfg, width=12, bg="#ECEFF1").pack(side=tk.LEFT)
        tk.Button(world_cfg, text="+", width=3, command=self._cmd_zoom_in).pack(side=tk.LEFT, padx=2)
        tk.Button(world_cfg, text="-", width=3, command=self._cmd_zoom_out).pack(side=tk.LEFT, padx=2)
        tk.Button(world_cfg, text="[]", width=3, command=self._cmd_zoom_reset).pack(side=tk.LEFT, padx=2)

        content = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=6, bg="#B0BEC5")
        content.pack(fill=tk.BOTH, expand=True, padx=6, pady=(2, 6))

        canvas_container = tk.Frame(content, bg="#ECEFF1")
        content.add(canvas_container, minsize=760, stretch="always")

        self._canvas = WorldCanvasEditor(
            canvas_container,
            on_place_asset=self._on_place_asset,
            on_select=self._on_select,
            on_move=self._on_move,
            on_delete=self._on_delete,
            on_status=self._set_cursor_status,
        )
        y_scroll = tk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self._canvas.yview)
        x_scroll = tk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self._canvas.xview)
        self._canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._props = ObjectPropertiesPanel(content)
        content.add(self._props, minsize=300, stretch="never")

        status_bar = tk.Frame(self, bg="#CFD8DC", padx=8, pady=3)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self._status_var = tk.StringVar(value="Listo")
        self._validation_var = tk.StringVar(value="Validación: OK")
        tk.Label(status_bar, textvariable=self._status_var, bg="#CFD8DC", anchor="w").pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        self._validation_label = tk.Label(
            status_bar,
            textvariable=self._validation_var,
            bg="#CFD8DC",
            anchor="e",
            fg="#1B5E20",
        )
        self._validation_label.pack(side=tk.RIGHT)

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def _cmd_new(self) -> None:
        if not messagebox.askyesno("Editor de mundos", "Crear un mundo nuevo? Se perderan cambios no guardados."):
            return
        self._service.reset_formal_world()
        self._selected_id = None
        self._current_path = None
        self._toolbar.set_delete_world_file_enabled(False)
        self._toolbar.set_simulate_saved_enabled(False)
        self._props.set_object(None)
        self._sync_world_size_inputs()
        self._refresh_canvas()
        self._set_status("Mundo nuevo creado")

    def _cmd_open(self) -> None:
        path = filedialog.askopenfilename(
            title="Abrir mundo",
            initialdir=str(_WORLDS_DIR),
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
        )
        if not path:
            return
        try:
            loaded_path, note = self._service.load_json(path)
            self._current_path = loaded_path
            self._toolbar.set_delete_world_file_enabled(not self._is_builtin_world_path(loaded_path))
            self._toolbar.set_simulate_saved_enabled(True)
            self._selected_id = None
            self._props.set_object(None)
            self._sync_world_size_inputs()
            self._refresh_canvas()
            if note:
                self._set_status(note)
            else:
                self._set_status(f"Mundo cargado: {loaded_path.name}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Editor de mundos", f"No se pudo abrir el archivo:\n{exc}")

    def _cmd_save(self) -> None:
        if self._current_path is None:
            self._cmd_save_as()
            return
        self._save_to_path(self._current_path)

    def _cmd_save_as(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Guardar mundo como",
            initialdir=str(_WORLDS_DIR),
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
        )
        if not path:
            return
        self._save_to_path(Path(path))

    def _save_to_path(self, path: Path) -> None:
        try:
            issues = self._service.validate_current_world()
            if issues:
                self._refresh_validation_status()
                messagebox.showerror("Editor de mundos", f"No se puede guardar un mundo inválido:\n{issues[0]}")
                return
            saved = self._service.save_json(path)
            self._current_path = saved
            self._set_status(f"Mundo guardado: {saved.name}")
            self._toolbar.set_simulate_saved_enabled(True)
            self._toolbar.set_delete_world_file_enabled(not self._is_builtin_world_path(saved))
            # Compatibilidad con integraciones anteriores que reaccionaban al
            # guardado; la ventana principal usa la acción explícita de simular.
            if self._on_world_saved is not None:
                self._on_world_saved(str(saved))
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Editor de mundos", f"No se pudo guardar el archivo:\n{exc}")

    def _cmd_delete_world_file(self) -> None:
        """Elimina exclusivamente el archivo abierto, nunca un mundo incluido."""
        path = self._current_path
        if path is None:
            self._set_status("Abre o guarda un mundo editable antes de eliminarlo")
            return
        if self._is_builtin_world_path(path):
            messagebox.showwarning("Editor de mundos", "Los mundos preestablecidos no se pueden eliminar.")
            return
        try:
            resolved = path.resolve(strict=True)
        except FileNotFoundError:
            self._set_status("El archivo de mundo ya no existe")
            self._current_path = None
            self._toolbar.set_delete_world_file_enabled(False)
            return
        if not resolved.is_file() or resolved.suffix.lower() != ".json":
            messagebox.showerror("Editor de mundos", "El archivo abierto no es un mundo JSON válido.")
            return
        if not messagebox.askyesno(
            "Eliminar archivo de mundo",
            f"Se eliminará permanentemente este mundo:\n{resolved.name}\n\n¿Deseas continuar?",
            icon="warning",
        ):
            return
        try:
            resolved.unlink()
        except OSError as exc:
            messagebox.showerror("Editor de mundos", f"No se pudo eliminar el archivo:\n{exc}")
            return

        self._service.reset_formal_world()
        self._selected_id = None
        self._current_path = None
        self._props.set_object(None)
        self._sync_world_size_inputs()
        self._refresh_canvas()
        self._toolbar.set_delete_world_file_enabled(False)
        self._toolbar.set_simulate_saved_enabled(False)
        self._set_status(f"Mundo eliminado: {resolved.name}. Se creó un mundo nuevo.")

    @staticmethod
    def _is_builtin_world_path(path: Path) -> bool:
        """Identifica solo los mundos distribuidos por el proyecto."""
        try:
            return path.resolve().parent == _WORLDS_DIR.resolve() and path.name in _BUILTIN_WORLD_FILENAMES
        except OSError:
            return False

    def _cmd_simulate_saved(self) -> None:
        """Aplica explícitamente el último mundo válido guardado a simulación."""

        if self._current_path is None:
            self._set_status("Guarda un mundo válido antes de simularlo")
            return
        if self._service.validate_current_world():
            self._refresh_validation_status()
            self._set_status("Corrige las validaciones antes de simular el mundo")
            return
        if self._on_simulate_saved is None:
            self._set_status("No hay simulación disponible para aplicar el mundo")
            return
        try:
            self._on_simulate_saved(str(self._current_path))
            self._set_status(f"Mundo aplicado a simulación: {self._current_path.name}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Editor de mundos", f"No se pudo aplicar el mundo a simulación:\n{exc}")

    def _cmd_delete_selected(self) -> None:
        if not self._selected_id:
            return
        if self._service.remove_asset_current(self._selected_id):
            self._selected_id = None
            self._props.set_object(None)
            self._refresh_canvas()

    def _cmd_duplicate_selected(self) -> None:
        if not self._selected_id:
            return
        duplicated = self._service.duplicate_asset_current(self._selected_id, dx_px=GRID_SIZE_PX, dy_px=GRID_SIZE_PX)
        if duplicated is None:
            self._set_status("No fue posible duplicar: validación fallida")
            return
        self._selected_id = duplicated.id
        self._props.set_object(duplicated.to_dict())
        self._refresh_canvas()

    def _cmd_rotate_selected(self) -> None:
        if not self._selected_id:
            return
        if not self._service.rotate_asset_current(self._selected_id, 90):
            self._set_status("No fue posible rotar: validación fallida")
            return
        self._refresh_canvas()
        selected = self._service.get_placement(self._selected_id)
        self._props.set_object(selected.to_dict() if selected else None)

    def _cmd_apply_properties(self) -> None:
        if not self._selected_id:
            return
        updates = self._props.collect_updates()
        if updates is None:
            return
        ok = self._service.update_asset_current(
            self._selected_id,
            x_px=updates.get("x_px"),
            y_px=updates.get("y_px"),
            rotation=updates.get("rotation"),
            asset_key=updates.get("asset_key"),
        )
        if not ok:
            self._set_status("Propiedades no aplicadas: validación fallida")
            return
        self._refresh_canvas()
        selected = self._service.get_placement(self._selected_id)
        self._props.set_object(selected.to_dict() if selected else None)

    def _cmd_apply_world_size(self) -> None:
        try:
            width_cells = int(self._world_w_entry.get())
            height_cells = int(self._world_h_entry.get())
        except ValueError:
            messagebox.showerror("Editor de mundos", "Width/Height deben ser enteros (cells).")
            return
        if width_cells > MAX_WORLD_CELLS or height_cells > MAX_WORLD_CELLS:
            messagebox.showerror(
                "Editor de mundos",
                f"Tamano maximo: {MAX_WORLD_CELLS} celdas por eje ({MAX_WORLD_PIXELS} px).",
            )
            return
        if not self._service.resize_formal_world(width_cells, height_cells):
            messagebox.showerror(
                "Editor de mundos",
                (
                    "No se pudo cambiar el tamano: hay placements fuera de limites, "
                    f"datos invalidos o se supera {MAX_WORLD_PIXELS} px por eje."
                ),
            )
            return
        self._refresh_canvas()

    def _cmd_zoom_in(self) -> None:
        self._canvas.zoom_in()

    def _cmd_zoom_out(self) -> None:
        self._canvas.zoom_out()

    def _cmd_zoom_reset(self) -> None:
        self._canvas.fit_to_view()

    # ------------------------------------------------------------------
    # Canvas callbacks
    # ------------------------------------------------------------------

    def _on_tool_change(self, tool_id: str) -> None:
        self._canvas.set_tool(tool_id)
        self._set_status(f"Herramienta: {tool_id}")

    def _on_place_asset(self, asset_key: str, x_px: int, y_px: int) -> None:
        try:
            placement = self._service.place_asset_current(asset_key, x_px, y_px, rotation=0)
        except ValueError as exc:
            self._set_status(f"No se pudo colocar: {exc}")
            self._refresh_validation_status()
            return
        self._selected_id = placement.id
        self._props.set_object(placement.to_dict())
        self._refresh_canvas()

    def _on_select(self, object_id: Optional[str]) -> None:
        self._selected_id = object_id
        placement = self._service.get_placement(object_id) if object_id else None
        self._props.set_object(placement.to_dict() if placement else None)
        self._canvas.set_selected_id(object_id)

    def _on_move(self, object_id: str, x_px: int, y_px: int) -> None:
        if self._service.move_asset_current(object_id, x_px, y_px):
            self._refresh_canvas()
            if self._selected_id == object_id:
                placement = self._service.get_placement(object_id)
                self._props.set_object(placement.to_dict() if placement else None)

    def _on_delete(self, object_id: str) -> None:
        if self._service.remove_asset_current(object_id):
            if self._selected_id == object_id:
                self._selected_id = None
                self._props.set_object(None)
            self._refresh_canvas()

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def _sync_world_size_inputs(self) -> None:
        world = self._service.current_formal_world()
        self._world_w_entry.delete(0, tk.END)
        self._world_h_entry.delete(0, tk.END)
        self._world_w_entry.insert(0, str(world.world_width_cells))
        self._world_h_entry.insert(0, str(world.world_height_cells))

    def _refresh_canvas(self) -> None:
        world = self._service.current_formal_world()
        self._canvas.set_world_size(
            world.world_width_cells * CELL_SIZE_MM,
            world.world_height_cells * CELL_SIZE_MM,
        )
        self._canvas.set_placements([placement.to_dict() for placement in world.placements])
        self._canvas.set_selected_id(self._selected_id)
        self._refresh_validation_status()

    def _refresh_validation_status(self) -> None:
        issues = self._service.validate_current_world()
        if issues:
            self._validation_var.set(f"Validación: {len(issues)} issue(s) | {issues[0]}")
            self._validation_label.configure(fg="#B71C1C")
        else:
            self._validation_var.set("Validación: OK")
            self._validation_label.configure(fg="#1B5E20")

    def _set_cursor_status(self, text: str) -> None:
        self._status_var.set(text)

    def _set_status(self, text: str) -> None:
        self._status_var.set(text)
