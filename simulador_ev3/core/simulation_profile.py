"""Perfiles reproducibles de fidelidad para física y sensores."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SimulationProfile(StrEnum):
    IDEAL = "ideal"
    REALISTIC = "realistic"
    CALIBRATED = "calibrated"


@dataclass(frozen=True)
class ProfileParameters:
    traction_scale: float = 1.0
    ultrasonic_noise_mm: float = 0.0
    color_reflection_noise: float = 0.0


def resolve_profile(name: str, calibration: dict[str, float] | None = None) -> ProfileParameters:
    """Resuelve valores deterministas; calibrado permite sobrescribirlos."""
    try:
        profile = SimulationProfile(str(name).lower())
    except ValueError as exc:
        raise ValueError("simulation_profile debe ser ideal, realistic o calibrated") from exc
    defaults = {
        SimulationProfile.IDEAL: ProfileParameters(),
        SimulationProfile.REALISTIC: ProfileParameters(
            traction_scale=0.96, ultrasonic_noise_mm=8.0, color_reflection_noise=2.0
        ),
        SimulationProfile.CALIBRATED: ProfileParameters(),
    }[profile]
    values = dict(calibration or {}) if profile is SimulationProfile.CALIBRATED else {}
    return ProfileParameters(
        traction_scale=float(values.get("traction_scale", defaults.traction_scale)),
        ultrasonic_noise_mm=float(values.get("ultrasonic_noise_mm", defaults.ultrasonic_noise_mm)),
        color_reflection_noise=float(values.get("color_reflection_noise", defaults.color_reflection_noise)),
    )
