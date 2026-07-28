"""Regresión visual de la geometría estable de telemetría.

Se ejecuta en los entornos con una sesión gráfica de Tkinter. En CI sin
display se omite de forma explícita: las pruebas de lógica siguen viviendo en
``test_ui.py``.
"""

from __future__ import annotations

import tkinter as tk

import pytest

from simulador_ev3.ui.telemetry_panel import TelemetryPanel


def _root_or_skip() -> tk.Tk:
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter no tiene una sesión gráfica disponible")
    root.withdraw()
    root.geometry("740x520")
    return root


def _block_sizes(panel: TelemetryPanel) -> tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]:
    motors = tuple((frame.winfo_width(), frame.winfo_height()) for frame in panel._motor_frames.values())
    sensors = tuple((frame.winfo_width(), frame.winfo_height()) for frame in panel._sensor_frames.values())
    return motors, sensors


def test_long_sensor_readings_do_not_reflow_telemetry_tables() -> None:
    """Una lectura larga no puede cambiar el ancho ni la altura de las tablas."""
    root = _root_or_skip()
    try:
        panel = TelemetryPanel(root)
        panel.pack(fill=tk.BOTH, expand=True)
        root.deiconify()
        root.update()
        before = _block_sizes(panel)
        assert len(panel._motor_frames) == 4  # noqa: SLF001 - estructura visible del tablero.
        assert all(width > 0 and height > 0 for width, height in before[0])

        panel._update_sensors(  # noqa: SLF001 - se prueba el punto que recibe el DTO.
            [
                {"port": "S1", "type": "TouchSensorModel", "value": {"pressed": False, "port": "S1"}},
                {
                    "port": "S4",
                    "type": "UltrasonicSensorModel",
                    "value": {"distance_mm": 748, "presence": False, "port": "S4"},
                },
            ]
        )
        panel._update_motors(  # noqa: SLF001 - se prueba el punto que recibe el DTO.
            [
                {"port": "A", "speed": 0, "angle": 0, "state": "IDLE"},
                {"port": "C", "speed": 337, "angle": 344, "state": "RUN"},
            ]
        )
        root.update()

        assert _block_sizes(panel) == before
    finally:
        root.destroy()
