from __future__ import annotations

import pytest

from simulador_ev3.shared.ui_settings import (
    DEFAULT_UI_THEME,
    load_desktop_session,
    load_ui_theme,
    save_desktop_session,
    save_ui_theme,
)


def test_ui_theme_defaults_when_no_preferences_file(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("EV3_UI_SETTINGS_PATH", str(tmp_path / "missing.json"))

    assert load_ui_theme() == DEFAULT_UI_THEME


def test_ui_theme_is_saved_and_reloaded(monkeypatch, tmp_path) -> None:
    settings_file = tmp_path / "settings" / "ui.json"
    monkeypatch.setenv("EV3_UI_SETTINGS_PATH", str(settings_file))

    assert save_ui_theme("dark") == "dark"
    assert load_ui_theme() == "dark"


def test_ui_theme_rejects_unknown_value(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("EV3_UI_SETTINGS_PATH", str(tmp_path / "ui.json"))

    with pytest.raises(ValueError, match="Tema no soportado"):
        save_ui_theme("solarized")


def test_desktop_session_is_saved_alongside_theme(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("EV3_UI_SETTINGS_PATH", str(tmp_path / "ui.json"))
    save_ui_theme("dark")
    save_desktop_session({"source": "x = 1", "breakpoints": [2]})

    assert load_ui_theme() == "dark"
    assert load_desktop_session() == {"source": "x = 1", "breakpoints": [2]}


def test_settings_are_written_without_leaving_a_temporary_file(monkeypatch, tmp_path) -> None:
    settings_file = tmp_path / "settings" / "ui.json"
    monkeypatch.setenv("EV3_UI_SETTINGS_PATH", str(settings_file))

    save_ui_theme("dark")

    assert settings_file.exists()
    assert not list(settings_file.parent.glob("*.tmp"))
