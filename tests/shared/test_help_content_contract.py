from simulador_ev3.shared.help_content_contract import (
    HELP_CONTENT_CONTRACT_VERSION,
    HELP_PROGRESS_STORAGE_KEY,
    PRIVACY_POLICY,
    GuideProgress,
    LearningLevel,
    VerifiableStep,
)


def test_help_content_contract_is_versioned_and_uses_stable_learning_levels() -> None:
    assert HELP_CONTENT_CONTRACT_VERSION == 1
    assert HELP_PROGRESS_STORAGE_KEY.endswith("-v1")
    assert LearningLevel.INITIAL == "inicial"
    assert VerifiableStep("open", "Abre Simulación", "El canvas está visible").verification


def test_local_progress_keeps_only_known_steps_and_never_contains_sensitive_payloads() -> None:
    progress = GuideProgress("first-simulation", ("open", "invalid", "run"), completed=True)

    cleaned = progress.sanitized(("open", "run"))

    assert cleaned.completed_step_ids == ("open", "run")
    assert cleaned.completed is True
    assert "sesión" in PRIVACY_POLICY
    assert "código" in PRIVACY_POLICY
