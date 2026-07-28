"""Compara evidencia visual con máscaras y umbrales explícitos.

Uso: python scripts/compare_visual_evidence.py referencia.png actual.png --threshold 0.08
Las máscaras opcionales son imágenes PNG: píxeles blancos se ignoran; negros
se comparan. Esto permite excluir bordes propios de los widgets nativos.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


def difference_ratio(reference: Path, actual: Path, mask: Path | None = None) -> float:
    """Devuelve la fracción normalizada de diferencia RGB fuera de la máscara."""
    expected = Image.open(reference).convert("RGB")
    observed = Image.open(actual).convert("RGB")
    if expected.size != observed.size:
        raise ValueError(f"Las dimensiones difieren: {expected.size} frente a {observed.size}")
    diff = ImageChops.difference(expected, observed)
    if mask is not None:
        ignored = Image.open(mask).convert("L")
        if ignored.size != expected.size:
            raise ValueError("La máscara debe tener el mismo tamaño que las imágenes")
        diff.paste((0, 0, 0), mask=ignored)
    return sum(ImageStat.Stat(diff).mean) / (255 * 3)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara dos capturas de paridad visual.")
    parser.add_argument("reference", type=Path)
    parser.add_argument("actual", type=Path)
    parser.add_argument("--mask", type=Path)
    parser.add_argument("--threshold", type=float, default=0.08)
    args = parser.parse_args()
    ratio = difference_ratio(args.reference, args.actual, args.mask)
    print(f"diferencia={ratio:.4f}; umbral={args.threshold:.4f}")
    return 0 if ratio <= args.threshold else 1


if __name__ == "__main__":
    raise SystemExit(main())
