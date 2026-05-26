"""
snapshot_dto.py — DTO para transportar StateSnapshot a la capa de UI.

Convierte el StateSnapshot (dataclass frozen del engine) a un dict
JSON-serializable que la UI puede consumir directamente sin depender
de los tipos del dominio.

Estructura del dict de salida:
{
    "tick":       int,          # número de tick del engine
    "sim_time_s": float,        # tiempo simulado acumulado
    "colliding":  bool,

    "robot": {
        "x_mm":      float,
        "y_mm":      float,
        "theta_deg": float
    },

    "motors": [              # lista de 4 entradas (A, B, C, D)
        {"port": "A", "speed": float, "angle": float, "state": str},
        ...
    ],

    "sensors": [             # lista de hasta 4 entradas (S1..S4)
        {"port": "S1", "type": str, "value": float|bool|str|None},
        ...
    ],

    "brick": {
        "led":     str | None,   # "RED", "GREEN", "ORANGE", None
        "screen":  dict,         # metadata + lineas de pantalla
        "speaker": dict | None,  # {"freq": int, "duration_ms": int}
        "buttons": list          # botones presionados (normalmente [])
    }
}

Nota: el DTO no importa nada del dominio; sólo depende de StateSnapshot
para mantener la capa de aplicación desacoplada.
"""
from __future__ import annotations

from typing import Any


class SnapshotDTO:
    """
    Convierte un StateSnapshot a un dict JSON-serializable.

    Uso:
        dto = SnapshotDTO.from_snapshot(snapshot)
        data = dto.to_dict()   # safe para json.dumps
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    # ------------------------------------------------------------------
    # Fábrica
    # ------------------------------------------------------------------

    @classmethod
    def from_snapshot(cls, snapshot) -> "SnapshotDTO":
        """
        Construye un SnapshotDTO a partir de un StateSnapshot del engine.

        Args:
            snapshot: simulador_ev3.core.simulation_engine.StateSnapshot
        """
        data: dict[str, Any] = {
            "tick":       snapshot.tick,
            "sim_time_s": round(snapshot.sim_time_s, 4),
            "colliding":  snapshot.colliding,
            "robot": _robot_dict(snapshot.robot),
            "motors":  [_motor_dict(m) for m in snapshot.motors],
            "sensors": [_sensor_dict(s) for s in snapshot.sensors],
            "brick":   _brick_dict(snapshot.brick),
        }
        return cls(data)

    # ------------------------------------------------------------------
    # Acceso
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Devuelve el dict serializable (copia superficial)."""
        return dict(self._data)

    # Accesores directos de conveniencia
    @property
    def tick(self) -> int:
        return self._data["tick"]

    @property
    def sim_time_s(self) -> float:
        return self._data["sim_time_s"]

    @property
    def colliding(self) -> bool:
        return self._data["colliding"]

    @property
    def robot(self) -> dict[str, float]:
        return self._data["robot"]

    @property
    def motors(self) -> list[dict]:
        return self._data["motors"]

    @property
    def sensors(self) -> list[dict]:
        return self._data["sensors"]

    @property
    def brick(self) -> dict:
        return self._data["brick"]

    def __repr__(self) -> str:
        return (
            f"SnapshotDTO(tick={self.tick}, "
            f"t={self.sim_time_s:.3f}s, "
            f"colliding={self.colliding})"
        )


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

def _robot_dict(robot_snap) -> dict[str, float]:
    return {
        "x_mm":      round(robot_snap.x_mm, 2),
        "y_mm":      round(robot_snap.y_mm, 2),
        "theta_deg": round(robot_snap.theta_deg, 3),
    }


def _motor_dict(motor_snap) -> dict[str, Any]:
    return {
        "port":  motor_snap.port,
        "speed": round(motor_snap.speed_dps, 2),
        "angle": round(motor_snap.angle_deg, 2),
        "state": motor_snap.state,
    }


def _sensor_dict(sensor_snap) -> dict[str, Any]:
    # sensor_snap.data es un dict con valores específicos del sensor
    data = sensor_snap.data or {}
    # "value" = primer valor del dict (o todo el dict si hay varios)
    if len(data) == 1:
        raw = next(iter(data.values()))
    else:
        raw = data
    if isinstance(raw, float):
        raw = round(raw, 3)
    return {
        "port":  sensor_snap.port,
        "type":  sensor_snap.sensor_type,
        "value": raw,
        "data":  {k: (round(v, 3) if isinstance(v, float) else v)
                  for k, v in data.items()},
    }


def _brick_dict(brick_dict: dict) -> dict[str, Any]:
    """
    Convierte el dict interno del EV3BrickModel al formato DTO.

    Estructura del dict que recibe (EV3BrickModel.to_dict()):
      "led":     {"is_on": bool, "color": str}
      "speaker": {"state": str, "frequency_hz": int,
                  "remaining_ms": int, "volume": int}
      "screen":  {"lines": list[str], "width_px": int, ...}
      "buttons": (dict específico de ButtonsModel)
    """
    # LED ─────────────────────────────────────────────────────────────
    led_raw = brick_dict.get("led")
    if isinstance(led_raw, dict):
        led_str: str | None = led_raw["color"] if led_raw.get("is_on") else None
    elif hasattr(led_raw, "name"):          # enum LedColor
        led_str = led_raw.name
    else:
        led_str = str(led_raw) if led_raw else None

    # Pantalla ────────────────────────────────────────────────────────
    screen_raw = brick_dict.get("screen")
    screen_out = {
        "lines": [],
        "draw_ops": [],
        "width_px": 178,
        "height_px": 128,
        "width_mm": 36.0,
        "height_mm": 24.0,
        "diagonal_mm": 47.0,
        "backlight_leds": 4,
        "monochrome": True,
    }
    if isinstance(screen_raw, dict):
        screen_out["lines"] = [str(ln) for ln in screen_raw.get("lines", [])]
        screen_out["draw_ops"] = [
            dict(op) for op in screen_raw.get("draw_ops", []) if isinstance(op, dict)
        ]
        for key in (
            "width_px",
            "height_px",
            "width_mm",
            "height_mm",
            "diagonal_mm",
            "backlight_leds",
            "monochrome",
        ):
            if key in screen_raw:
                screen_out[key] = screen_raw[key]
    elif isinstance(screen_raw, list):
        screen_out["lines"] = [str(ln) for ln in screen_raw]
    elif screen_raw:
        text = str(screen_raw)
        screen_out["lines"] = text.splitlines() or [text]

    # Altavoz ─────────────────────────────────────────────────────────
    speaker_raw = brick_dict.get("speaker")
    speaker_out: dict | None = None
    if isinstance(speaker_raw, dict):
        state = speaker_raw.get("state", "IDLE")
        if state != "IDLE":
            speaker_out = {
                "freq":        speaker_raw.get("frequency_hz", 0),
                "duration_ms": speaker_raw.get("remaining_ms", 0),
                "volume":      speaker_raw.get("volume", 50),
            }

    # Botones ─────────────────────────────────────────────────────────
    buttons_raw = brick_dict.get("buttons")
    if isinstance(buttons_raw, dict):
        # ButtonsModel.to_dict() devuelve {"pressed": [list]}
        buttons_out = list(buttons_raw.get("pressed", []))
    elif buttons_raw:
        buttons_out = list(buttons_raw)
    else:
        buttons_out = []

    return {
        "led":     led_str,
        "screen":  screen_out,
        "speaker": speaker_out,
        "buttons": buttons_out,
    }
