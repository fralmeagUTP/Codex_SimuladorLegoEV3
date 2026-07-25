import pytest

from simulador_ev3.application.simulation_service import SimulationService
from simulador_ev3.core.simulation_profile import resolve_profile


def test_ideal_profile_preserves_zero_sensor_noise() -> None:
    profile = resolve_profile("ideal")

    assert profile.ultrasonic_noise_mm == 0.0
    assert profile.color_reflection_noise == 0.0


def test_realistic_profile_has_deterministic_sensor_noise() -> None:
    profile = resolve_profile("realistic")

    assert profile.ultrasonic_noise_mm > 0
    assert profile.color_reflection_noise > 0
    assert profile.traction_scale < 1.0


def test_calibrated_profile_accepts_explicit_overrides() -> None:
    profile = resolve_profile(
        "calibrated", {"traction_scale": 0.9, "ultrasonic_noise_mm": 3.5, "color_reflection_noise": 1.25}
    )

    assert profile.ultrasonic_noise_mm == 3.5
    assert profile.color_reflection_noise == 1.25
    assert profile.traction_scale == 0.9


def test_unknown_profile_is_rejected() -> None:
    with pytest.raises(ValueError, match="simulation_profile"):
        resolve_profile("unknown")


def test_service_rebuilds_with_selected_calibrated_profile() -> None:
    service = SimulationService()

    service.set_simulation_profile("calibrated", {"traction_scale": 0.9})

    assert service.engine_config.simulation_profile == "calibrated"
    assert service.engine.drivebase_profile.straight_speed == pytest.approx(180.0)
