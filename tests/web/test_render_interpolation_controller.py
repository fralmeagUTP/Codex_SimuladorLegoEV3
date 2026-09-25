"""Pruebas del controlador visual ejecutadas con el motor JavaScript real."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_render_interpolation_controller_smooths_pose_without_terminal_motion() -> None:
    source = Path("simulador_ev3/web/static/js/render_interpolation_controller.js")
    program = f"""
const fs = require("fs");
const vm = require("vm");
let clock = 0;
const frames = [];
const rendered = [];
const context = {{
  window: {{}},
  performance: {{ now: () => clock }},
  requestAnimationFrame: (callback) => frames.push(callback),
}};
vm.runInNewContext(fs.readFileSync({source.as_posix()!r}, "utf8"), context);
const controller = context.window.EV3RenderInterpolationController.create({{
  onRender: (snapshot) => rendered.push(snapshot),
  now: () => clock,
  raf: (callback) => frames.push(callback),
}});
controller.apply({{ snapshot_generation: 1, tick: 1, status: "running", colliding: false,
  robot: {{ x_mm: 0, y_mm: 0, theta_deg: 350 }} }});
controller.apply({{ snapshot_generation: 1, tick: 2, status: "running", colliding: false,
  robot: {{ x_mm: 100, y_mm: 50, theta_deg: 10 }} }});
clock = 16;
frames.shift()();
const middle = rendered.at(-1);
controller.apply({{ snapshot_generation: 1, tick: 3, status: "finished", colliding: false,
  robot: {{ x_mm: 120, y_mm: 60, theta_deg: 15 }} }});
const terminal = rendered.at(-1);
const diagnostics = controller.diagnostics();
console.log(JSON.stringify({{
  middle: {{
    x: middle.robot.x_mm, y: middle.robot.y_mm,
    theta: middle.robot.theta_deg, interpolated: middle.visual_interpolated,
  }},
  terminal: {{ x: terminal.robot.x_mm, status: terminal.status, interpolated: terminal.visual_interpolated }},
  diagnostics,
}}));
"""

    completed = subprocess.run(
        ["node", "-e", program],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    result = json.loads(completed.stdout)

    assert result["middle"]["interpolated"] is True
    # A 50 Hz, un frame de 16 ms ya recorre aproximadamente 80 % de un tick;
    # si se fuerza el mínimo anterior de 33 ms, el resultado sería < 50 %.
    assert 50 < result["middle"]["x"] < 100
    assert 25 < result["middle"]["y"] < 50
    # El giro 350° -> 10° sigue la ruta corta pasando por 0°, no por 180°.
    assert result["middle"]["theta"] > 350
    assert result["terminal"] == {"x": 120, "status": "finished"}
    assert result["diagnostics"]["receivedSnapshots"] == 3
    assert result["diagnostics"]["renderedFrames"] >= 1
