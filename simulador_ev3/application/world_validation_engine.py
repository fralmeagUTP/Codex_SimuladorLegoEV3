"""
world_validation_engine.py
==========================
Validation engine for the formal EV3 world editor model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from simulador_ev3.domain.editor.world_editor_model import (
    Direction,
    EditorWorldModel,
    MAX_WORLD_PIXELS,
    Placement,
    SUPPORTED_ROTATIONS,
    get_asset_spec,
)

_DIRECTION_DELTAS: dict[Direction, tuple[int, int]] = {
    "N": (0, -2),
    "S": (0, 2),
    "E": (2, 0),
    "W": (-2, 0),
}

_OPPOSITE: dict[Direction, Direction] = {
    "N": "S",
    "S": "N",
    "E": "W",
    "W": "E",
}

_ROTATE_CLOCKWISE: dict[Direction, Direction] = {
    "N": "E",
    "E": "S",
    "S": "W",
    "W": "N",
}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = "error"
    placement_id: Optional[str] = None
    cell: Optional[tuple[int, int]] = None


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity != "error"]

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def messages(self) -> list[str]:
        return [issue.message for issue in self.issues]


class ValidationEngine:
    """Validates editor worlds using deterministic discrete rules."""

    def validate(self, world: EditorWorldModel) -> ValidationReport:
        report = ValidationReport()
        report.issues.extend(self._validate_structural(world))
        report.issues.extend(self._validate_overlap(world))
        report.issues.extend(self._validate_line_connectivity(world))
        return _deduplicate_issues(report)

    def _validate_structural(self, world: EditorWorldModel) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        robot_placements = 0
        if world.grid_size_px <= 0:
            issues.append(
                ValidationIssue(
                    code="INVALID_GRID",
                    message="grid_size_px debe ser mayor que 0.",
                )
            )
            return issues
        if world.world_width_cells <= 0 or world.world_height_cells <= 0:
            issues.append(
                ValidationIssue(
                    code="INVALID_WORLD_SIZE",
                    message="world_width_cells y world_height_cells deben ser mayores que 0.",
                )
            )
            return issues
        world_width_px = world.world_width_cells * world.grid_size_px
        world_height_px = world.world_height_cells * world.grid_size_px
        if world_width_px > MAX_WORLD_PIXELS or world_height_px > MAX_WORLD_PIXELS:
            issues.append(
                ValidationIssue(
                    code="WORLD_SIZE_EXCEEDS_MAX",
                    message=(
                        f"El mundo excede el maximo permitido de {MAX_WORLD_PIXELS} px por eje "
                        f"(actual: {world_width_px}x{world_height_px}px)."
                    ),
                )
            )
            return issues

        seen_ids: set[str] = set()
        for placement in world.placements:
            pid = str(placement.id)
            if not pid:
                issues.append(
                    ValidationIssue(
                        code="EMPTY_ID",
                        message="Cada placement debe tener un id no vacio.",
                    )
                )
            elif pid in seen_ids:
                issues.append(
                    ValidationIssue(
                        code="DUPLICATE_ID",
                        message=f"Id duplicado: {pid}",
                        placement_id=pid,
                    )
                )
            seen_ids.add(pid)

            spec = get_asset_spec(placement.asset_key)
            if spec is None:
                issues.append(
                    ValidationIssue(
                        code="UNKNOWN_ASSET",
                        message=f"Asset no reconocido: {placement.asset_key}",
                        placement_id=pid,
                    )
                )
                continue

            if spec.asset_type == "robot":
                robot_placements += 1

            if placement.rotation % 360 not in SUPPORTED_ROTATIONS:
                issues.append(
                    ValidationIssue(
                        code="INVALID_ROTATION",
                        message=(
                            f"Rotacion invalida en {pid}: {placement.rotation}. "
                            f"Permitidas: {SUPPORTED_ROTATIONS}"
                        ),
                        placement_id=pid,
                    )
                )

            if placement.x_px % world.grid_size_px != 0 or placement.y_px % world.grid_size_px != 0:
                issues.append(
                    ValidationIssue(
                        code="MISALIGNED_PLACEMENT",
                        message=(
                            f"Placement {pid} fuera de alineacion de grid "
                            f"({world.grid_size_px}px)."
                        ),
                        placement_id=pid,
                    )
                )

            width_cells, height_cells = placement_size_cells(placement)
            x_cell = placement.x_px // world.grid_size_px
            y_cell = placement.y_px // world.grid_size_px
            if x_cell < 0 or y_cell < 0:
                issues.append(
                    ValidationIssue(
                        code="OUT_OF_BOUNDS",
                        message=f"Placement {pid} tiene coordenadas negativas.",
                        placement_id=pid,
                    )
                )
                continue

            if x_cell + width_cells > world.world_width_cells or y_cell + height_cells > world.world_height_cells:
                issues.append(
                    ValidationIssue(
                        code="OUT_OF_BOUNDS",
                        message=f"Placement {pid} excede limites del mundo.",
                        placement_id=pid,
                    )
                )

        if robot_placements > 1:
            issues.append(
                ValidationIssue(
                    code="MULTIPLE_ROBOTS",
                    message="Solo se permite un robot en el mapa.",
                )
            )

        return issues

    def _validate_overlap(self, world: EditorWorldModel) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        cell_types: dict[tuple[int, int], list[tuple[str, str]]] = {}

        for placement in world.placements:
            spec = get_asset_spec(placement.asset_key)
            if spec is None:
                continue
            for cell in iter_occupied_cells(world, placement):
                bucket = cell_types.setdefault(cell, [])
                bucket.append((spec.asset_type, placement.id))

        for cell, entries in cell_types.items():
            type_counts: dict[str, int] = {}
            for asset_type, _pid in entries:
                type_counts[asset_type] = type_counts.get(asset_type, 0) + 1

            zone_count = type_counts.get("zone", 0)
            line_count = type_counts.get("line", 0)
            wall_count = type_counts.get("wall", 0)
            robot_count = type_counts.get("robot", 0)

            if zone_count > 1:
                issues.append(
                    ValidationIssue(
                        code="ZONE_OVERLAP",
                        message=f"Hay mas de una zona en la celda {cell}.",
                        cell=cell,
                    )
                )
            if line_count > 1:
                issues.append(
                    ValidationIssue(
                        code="LINE_OVERLAP",
                        message=f"Hay mas de una linea en la celda {cell}.",
                        cell=cell,
                    )
                )
            if wall_count > 1:
                issues.append(
                    ValidationIssue(
                        code="WALL_OVERLAP",
                        message=f"Hay mas de un muro en la celda {cell}.",
                        cell=cell,
                    )
                )
            if robot_count > 1:
                issues.append(
                    ValidationIssue(
                        code="ROBOT_OVERLAP",
                        message=f"Hay mas de un robot en la celda {cell}.",
                        cell=cell,
                    )
                )

            if wall_count >= 1 and (zone_count >= 1 or line_count >= 1 or robot_count >= 1):
                issues.append(
                    ValidationIssue(
                        code="WALL_INCOMPATIBLE_OVERLAP",
                        message=f"Un muro no puede solaparse con zona/linea/robot en celda {cell}.",
                        cell=cell,
                    )
                )

        return issues

    def _validate_line_connectivity(self, world: EditorWorldModel) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        line_nodes: dict[tuple[int, int], tuple[str, set[Direction]]] = {}

        for placement in world.placements:
            spec = get_asset_spec(placement.asset_key)
            if spec is None or spec.asset_type != "line":
                continue
            connectors = rotated_connectors(spec.connectors, placement.rotation)
            x_cell = placement.x_px // world.grid_size_px
            y_cell = placement.y_px // world.grid_size_px
            line_nodes[(x_cell, y_cell)] = (placement.id, set(connectors))

        if not line_nodes:
            return issues

        for node, (placement_id, connectors) in line_nodes.items():
            for direction in connectors:
                dx, dy = _DIRECTION_DELTAS[direction]
                neighbor = (node[0] + dx, node[1] + dy)
                if neighbor not in line_nodes:
                    issues.append(
                        ValidationIssue(
                            code="LINE_OPEN_END",
                            message=f"Linea {placement_id} tiene extremo abierto hacia {direction}.",
                            severity="warning",
                            placement_id=placement_id,
                            cell=node,
                        )
                    )
                    continue

                _nid, neighbor_connectors = line_nodes[neighbor]
                expected = _OPPOSITE[direction]
                if expected not in neighbor_connectors:
                    issues.append(
                        ValidationIssue(
                            code="LINE_BROKEN_LINK",
                            message=(
                                f"Conexion inconsistente entre {placement_id} y "
                                f"{line_nodes[neighbor][0]}."
                            ),
                            severity="warning",
                            placement_id=placement_id,
                            cell=node,
                        )
                    )

        # Connected component check (single component).
        components = connected_components(line_nodes)
        if len(components) > 1:
            issues.append(
                ValidationIssue(
                    code="LINE_DISCONNECTED_COMPONENTS",
                    message=f"Las lineas forman {len(components)} componentes desconectados.",
                    severity="warning",
                )
            )
        return issues


def placement_size_cells(placement: Placement) -> tuple[int, int]:
    spec = get_asset_spec(placement.asset_key)
    if spec is None:
        return 0, 0
    if placement.rotation % 180 == 90:
        return spec.height_cells, spec.width_cells
    return spec.width_cells, spec.height_cells


def iter_occupied_cells(world: EditorWorldModel, placement: Placement) -> list[tuple[int, int]]:
    width_cells, height_cells = placement_size_cells(placement)
    if width_cells <= 0 or height_cells <= 0:
        return []
    x0 = placement.x_px // world.grid_size_px
    y0 = placement.y_px // world.grid_size_px
    cells = []
    for cx in range(x0, x0 + width_cells):
        for cy in range(y0, y0 + height_cells):
            cells.append((cx, cy))
    return cells


def rotated_connectors(connectors: set[Direction] | frozenset[Direction], rotation_deg: int) -> set[Direction]:
    turns = (int(rotation_deg) % 360) // 90
    out = set(connectors)
    for _ in range(turns):
        out = {_ROTATE_CLOCKWISE[d] for d in out}
    return out


def connected_components(
    line_nodes: dict[tuple[int, int], tuple[str, set[Direction]]]
) -> list[set[tuple[int, int]]]:
    remaining = set(line_nodes.keys())
    components: list[set[tuple[int, int]]] = []
    while remaining:
        root = next(iter(remaining))
        stack = [root]
        component: set[tuple[int, int]] = set()
        while stack:
            node = stack.pop()
            if node in component:
                continue
            component.add(node)
            _, connectors = line_nodes[node]
            for direction in connectors:
                dx, dy = _DIRECTION_DELTAS[direction]
                neighbor = (node[0] + dx, node[1] + dy)
                if neighbor not in line_nodes:
                    continue
                neighbor_connectors = line_nodes[neighbor][1]
                if _OPPOSITE[direction] in neighbor_connectors:
                    stack.append(neighbor)
        remaining -= component
        components.append(component)
    return components


def _deduplicate_issues(report: ValidationReport) -> ValidationReport:
    seen: set[tuple[str, str, str, Optional[tuple[int, int]]]] = set()
    out: list[ValidationIssue] = []
    for issue in report.issues:
        key = (issue.code, issue.message, str(issue.placement_id), issue.cell)
        if key in seen:
            continue
        seen.add(key)
        out.append(issue)
    return ValidationReport(issues=out)
