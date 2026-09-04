from simulador_ev3.shared.session_status import SessionStatus, can_transition, is_terminal


def test_running_session_can_finish_without_resetting() -> None:
    assert can_transition(SessionStatus.RUNNING, SessionStatus.FINISHED)
    assert is_terminal(SessionStatus.FINISHED)


def test_timeout_is_terminal_and_can_be_reset() -> None:
    assert can_transition(SessionStatus.RUNNING, SessionStatus.TIMED_OUT)
    assert is_terminal(SessionStatus.TIMED_OUT)
    assert can_transition(SessionStatus.TIMED_OUT, SessionStatus.RESETTING)


def test_error_is_terminal_and_recovers_only_through_a_new_lifecycle() -> None:
    assert can_transition(SessionStatus.RUNNING, SessionStatus.ERROR)
    assert is_terminal(SessionStatus.ERROR)
    assert can_transition(SessionStatus.ERROR, SessionStatus.RESETTING)


def test_expired_session_cannot_resume() -> None:
    assert not can_transition(SessionStatus.EXPIRED, SessionStatus.RUNNING)
