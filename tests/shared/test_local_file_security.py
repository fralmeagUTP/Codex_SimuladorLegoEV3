from __future__ import annotations

import os

import pytest

from simulador_ev3.shared.local_file_security import (
    LocalFileSecurityError,
    read_text_limited,
    safe_desktop_error,
    validate_open_file,
    write_text_atomically,
)


def test_read_text_limited_accepts_valid_utf8_script(tmp_path) -> None:
    script = tmp_path / "mission.py"
    script.write_text("print('ok')\n", encoding="utf-8")

    path, source = read_text_limited(script, allowed_suffixes=(".py",), max_bytes=1024)

    assert path == script.resolve()
    assert source == "print('ok')\n"


def test_open_file_rejects_unexpected_extension_and_oversized_content(tmp_path) -> None:
    text_file = tmp_path / "not-script.txt"
    text_file.write_text("x", encoding="utf-8")
    too_large = tmp_path / "large.py"
    too_large.write_bytes(b"x" * 16)

    with pytest.raises(LocalFileSecurityError, match="tipo"):
        validate_open_file(text_file, allowed_suffixes=(".py",), max_bytes=1024)
    with pytest.raises(LocalFileSecurityError, match="tamano"):
        validate_open_file(too_large, allowed_suffixes=(".py",), max_bytes=8)


def test_atomic_writer_replaces_content_and_leaves_no_temporary_file(tmp_path) -> None:
    destination = tmp_path / "world.json"
    destination.write_text("old", encoding="utf-8")

    saved = write_text_atomically(destination, '{"version": 1}', allowed_suffixes=(".json",), max_bytes=1024)

    assert saved == destination.resolve()
    assert destination.read_text(encoding="utf-8") == '{"version": 1}'
    assert not list(tmp_path.glob(".ev3-save-*"))


def test_atomic_writer_rejects_invalid_destination_suffix(tmp_path) -> None:
    with pytest.raises(LocalFileSecurityError, match="tipo"):
        write_text_atomically(tmp_path / "world.txt", "{}", allowed_suffixes=(".json",))


def test_atomic_writer_removes_temp_file_when_replace_fails(tmp_path, monkeypatch) -> None:
    destination = tmp_path / "world.json"

    def fail_replace(*_args) -> None:
        raise OSError("simulated")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(LocalFileSecurityError):
        write_text_atomically(destination, "{}", allowed_suffixes=(".json",))

    assert not list(tmp_path.glob(".ev3-save-*"))


def test_safe_desktop_error_redacts_paths_tracebacks_and_tokens() -> None:
    assert safe_desktop_error(ValueError(r"C:\\private\\world.json"), "safe") == "safe"
    assert safe_desktop_error(ValueError("Traceback with secret token"), "safe") == "safe"
    assert safe_desktop_error(ValueError("Formato JSON invalido"), "safe") == "Formato JSON invalido"
