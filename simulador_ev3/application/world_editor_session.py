"""Contrato de sesión compartido para el Editor de Mundos."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from simulador_ev3.application.world_editor_service import WorldEditorService
from simulador_ev3.domain.editor.asset_presentation import presentation_for_asset
from simulador_ev3.domain.editor.world_editor_model import Placement

WORLD_EDITOR_SESSION_VERSION = 1


@dataclass(frozen=True)
class WorldEditorSessionSnapshot:
    """Estado serializable que ambos adaptadores pueden proyectar."""

    world: dict[str, Any]
    selected_placement_id: str | None
    layers: tuple[dict[str, Any], ...]
    validation: tuple[str, ...]
    actions: dict[str, bool]
    dirty: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": WORLD_EDITOR_SESSION_VERSION,
            "world": self.world,
            "selected_placement_id": self.selected_placement_id,
            "layers": list(self.layers),
            "validation": list(self.validation),
            "actions": dict(self.actions),
            "dirty": self.dirty,
        }


class WorldEditorSession:
    """Orquesta comandos de autoría y expone snapshots equivalentes de UI."""

    def __init__(self, service: WorldEditorService | None = None) -> None:
        self._service = service or WorldEditorService()
        self._selected_placement_id: str | None = None
        self._dirty = False

    @property
    def service(self) -> WorldEditorService:
        """Compatibilidad temporal para adaptadores aún basados en el servicio."""

        return self._service

    def snapshot(self) -> WorldEditorSessionSnapshot:
        world = self._service.current_formal_world()
        selected = self._service.get_placement(self._selected_placement_id) if self._selected_placement_id else None
        if selected is None:
            self._selected_placement_id = None
        layers = tuple(self._layer_item(placement) for placement in world.placements)
        return WorldEditorSessionSnapshot(
            world=world.to_dict(),
            selected_placement_id=self._selected_placement_id,
            layers=layers,
            validation=tuple(self._service.validate_current_world()),
            actions={
                "select": True,
                "place": True,
                "delete": selected is not None,
                "rotate": selected is not None,
                "duplicate": selected is not None,
                "update": selected is not None,
                "validate": True,
                "apply_to_simulation": True,
                "save": True,
            },
            dirty=self._dirty,
        )

    def new(self, width_cells: int | None = None, height_cells: int | None = None) -> WorldEditorSessionSnapshot:
        self._service.reset_formal_world(width_cells, height_cells)
        self._selected_placement_id = None
        self._dirty = False
        return self.snapshot()

    def select(self, placement_id: str | None) -> WorldEditorSessionSnapshot:
        if placement_id is not None and self._service.get_placement(placement_id) is None:
            raise ValueError(f"No existe asset_id: {placement_id}")
        self._selected_placement_id = placement_id
        return self.snapshot()

    def place(self, asset_key: str, x_px: int, y_px: int, rotation: int = 0) -> WorldEditorSessionSnapshot:
        placement = self._service.place_asset_current(asset_key, x_px, y_px, rotation)
        self._selected_placement_id = placement.id
        self._dirty = True
        return self.snapshot()

    def move(self, placement_id: str, x_px: int, y_px: int) -> WorldEditorSessionSnapshot:
        if not self._service.move_asset_current(placement_id, x_px, y_px):
            raise ValueError(f"No se pudo mover asset_id: {placement_id}")
        self._selected_placement_id = placement_id
        self._dirty = True
        return self.snapshot()

    def rotate(self, placement_id: str, delta_deg: int = 90) -> WorldEditorSessionSnapshot:
        if not self._service.rotate_asset_current(placement_id, delta_deg):
            raise ValueError(f"No se pudo rotar asset_id: {placement_id}")
        self._selected_placement_id = placement_id
        self._dirty = True
        return self.snapshot()

    def duplicate(self, placement_id: str) -> WorldEditorSessionSnapshot:
        placement = self._service.duplicate_asset_current(placement_id)
        if placement is None:
            raise ValueError(f"No se pudo duplicar asset_id: {placement_id}")
        self._selected_placement_id = placement.id
        self._dirty = True
        return self.snapshot()

    def delete(self, placement_id: str) -> WorldEditorSessionSnapshot:
        if not self._service.remove_asset_current(placement_id):
            raise ValueError(f"No se pudo eliminar asset_id: {placement_id}")
        if self._selected_placement_id == placement_id:
            self._selected_placement_id = None
        self._dirty = True
        return self.snapshot()

    def mark_saved(self) -> WorldEditorSessionSnapshot:
        self._dirty = False
        return self.snapshot()

    @staticmethod
    def _layer_item(placement: Placement) -> dict[str, Any]:
        presentation = presentation_for_asset(placement.asset_key)
        return {
            "id": placement.id,
            "asset_key": placement.asset_key,
            "label": presentation.name,
            "category": presentation.category,
            "x_px": placement.x_px,
            "y_px": placement.y_px,
            "rotation": placement.rotation,
        }
