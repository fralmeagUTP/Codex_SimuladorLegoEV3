"""Shared filesystem paths for desktop and web adapters.

This module defines canonical, lowercase resource folders at repository root:
- examples
- worlds
- docs

It keeps backward compatibility with legacy folders under Documentos.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CANONICAL_DOCS_DIR = PROJECT_ROOT / "docs"
LEGACY_DOCS_DIR = PROJECT_ROOT / "Documentos"

CANONICAL_EXAMPLES_DIR = PROJECT_ROOT / "examples"
LEGACY_EXAMPLES_DIR = LEGACY_DOCS_DIR / "Ejemplos"

CANONICAL_WORLDS_DIR = PROJECT_ROOT / "worlds"
LEGACY_WORLDS_DIR = LEGACY_DOCS_DIR / "Mundos"

CANONICAL_IMAGE_ASSETS_DIR = PROJECT_ROOT / "simulador_ev3" / "assets"
LEGACY_IMAGE_ASSETS_DIRS = (
    PROJECT_ROOT / "simulador_ev3" / "assets" / "images",
    PROJECT_ROOT / "simulador_ev3" / "images",
)


def resolve_docs_dir() -> Path:
    if CANONICAL_DOCS_DIR.exists():
        return CANONICAL_DOCS_DIR
    if LEGACY_DOCS_DIR.exists():
        return LEGACY_DOCS_DIR
    return CANONICAL_DOCS_DIR


def resolve_examples_dir() -> Path:
    if CANONICAL_EXAMPLES_DIR.exists():
        return CANONICAL_EXAMPLES_DIR
    if LEGACY_EXAMPLES_DIR.exists():
        return LEGACY_EXAMPLES_DIR
    return CANONICAL_EXAMPLES_DIR


def resolve_worlds_dir() -> Path:
    if CANONICAL_WORLDS_DIR.exists():
        return CANONICAL_WORLDS_DIR
    if LEGACY_WORLDS_DIR.exists():
        return LEGACY_WORLDS_DIR
    return CANONICAL_WORLDS_DIR


def resolve_image_assets_dir() -> Path:
    if CANONICAL_IMAGE_ASSETS_DIR.exists():
        return CANONICAL_IMAGE_ASSETS_DIR
    for legacy_dir in LEGACY_IMAGE_ASSETS_DIRS:
        if legacy_dir.exists():
            return legacy_dir
    return CANONICAL_IMAGE_ASSETS_DIR


def resolve_manual_path() -> Path:
    docs_dir = resolve_docs_dir()
    manual_path = docs_dir / "MANUAL_DE_USO.md"
    if manual_path.exists():
        return manual_path
    return LEGACY_DOCS_DIR / "MANUAL_DE_USO.md"
