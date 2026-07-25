"""Catálogo de scripts de ejemplo del simulador EV3."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExampleInfo:
    name: str
    path: Path


class ExampleCatalog:
    """Descubre y carga ejemplos Python desde un directorio."""

    def __init__(self, examples_dir: str | Path) -> None:
        self._dir = Path(examples_dir)

    @property
    def base_dir(self) -> Path:
        return self._dir

    def list_examples(self) -> list[ExampleInfo]:
        if not self._dir.exists():
            return []
        return [ExampleInfo(name=path.name, path=path) for path in sorted(self._dir.glob("*.py"))]

    def read_example(self, name_or_path: str) -> str:
        path = Path(name_or_path)
        if not path.is_absolute():
            path = self._dir / name_or_path
        return path.read_text(encoding="utf-8")

    def exists(self, name_or_path: str) -> bool:
        path = Path(name_or_path)
        if not path.is_absolute():
            path = self._dir / name_or_path
        return path.exists()
