"""Datos sintéticos reutilizables para campañas de calidad.

No usa los directorios `worlds/` ni `examples/` del repositorio; por ello los
casos que persisten datos pueden ejecutarse en paralelo o desde UI sin afectar
recursos educativos ni archivos de usuario.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from simulador_ev3.domain.editor.world_editor_model import EditorWorldModel, Placement


@dataclass(frozen=True)
class TestWorkspace:
    """Raíces temporales requeridas por una sesión o editor de prueba."""

    root: Path
    worlds: Path
    examples: Path
    session_store: Path

    def web_config(self) -> dict[str, Path]:
        return {
            "WORLDS_DIR": self.worlds,
            "EXAMPLES_DIR": self.examples,
            "FILE_MIRROR_DIR": self.session_store,
        }


def make_workspace(root: Path) -> TestWorkspace:
    """Crea las rutas temporales de una campaña sin copiar recursos reales."""

    worlds = root / "worlds"
    examples = root / "examples"
    session_store = root / "sessions"
    for path in (worlds, examples, session_store):
        path.mkdir(parents=True, exist_ok=True)
    return TestWorkspace(root=root, worlds=worlds, examples=examples, session_store=session_store)


def make_editor_world(
    *,
    width_cells: int = 20,
    height_cells: int = 20,
    include_robot: bool = True,
) -> EditorWorldModel:
    """Construye un mundo mínimo válido y explícitamente sintético."""

    placements = (
        [Placement(id="qa-robot", asset_key="robot_ev3_32x32", x_px=0, y_px=0, rotation=0)]
        if include_robot
        else []
    )
    return EditorWorldModel(
        grid_size_px=32,
        world_width_cells=width_cells,
        world_height_cells=height_cells,
        placements=placements,
    )
