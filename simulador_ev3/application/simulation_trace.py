"""Registro y exportación reproducible de snapshots de simulación."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SimulationTrace:
    snapshots: list[dict[str, Any]] = field(default_factory=list)
    max_snapshots: int = 5_000
    dropped_snapshots: int = 0

    def record(self, snapshot: dict[str, Any]) -> None:
        limit = max(1, int(self.max_snapshots))
        if len(self.snapshots) >= limit:
            self.snapshots.pop(0)
            self.dropped_snapshots += 1
        self.snapshots.append(dict(snapshot))

    def clear(self) -> None:
        self.snapshots.clear()
        self.dropped_snapshots = 0

    def to_json(self) -> str:
        return json.dumps(
            {
                "trace_version": 2,
                "snapshots": self.snapshots,
                "truncated": self.dropped_snapshots > 0,
                "dropped_snapshots": self.dropped_snapshots,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )

    def to_csv(self) -> str:
        output = io.StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=("tick", "sim_time_s", "x_mm", "y_mm", "theta_deg", "colliding"))
        writer.writeheader()
        for snapshot in self.snapshots:
            robot: dict[str, Any] = {}
            raw_robot = snapshot.get("robot")
            if isinstance(raw_robot, dict):
                robot.update(raw_robot)
            writer.writerow(
                {
                    "tick": snapshot.get("tick"),
                    "sim_time_s": snapshot.get("sim_time_s"),
                    "x_mm": robot.get("x_mm"),
                    "y_mm": robot.get("y_mm"),
                    "theta_deg": robot.get("theta_deg"),
                    "colliding": snapshot.get("colliding"),
                }
            )
        return output.getvalue()

    @classmethod
    def from_json(cls, payload: str) -> "SimulationTrace":
        data = json.loads(payload)
        snapshots = data.get("snapshots") if isinstance(data, dict) else None
        if not isinstance(snapshots, list) or not all(isinstance(item, dict) for item in snapshots):
            raise ValueError("La traza no contiene snapshots validos.")
        try:
            dropped_count = max(0, int(data.get("dropped_snapshots", 0)))
        except (TypeError, ValueError):
            dropped_count = 0
        return cls(snapshots=[dict(item) for item in snapshots], dropped_snapshots=dropped_count)
