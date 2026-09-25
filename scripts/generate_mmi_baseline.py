"""Genera una linea base MMI reproducible para adjuntarla a una evidencia CI."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from simulador_ev3.shared.maturity_manifest import MMI_DIMENSIONS, MATURITY_MANIFEST_VERSION, validate_maturity_manifest


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, encoding="utf-8").strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--browser", default="pending-manual-validation")
    parser.add_argument("--resolutions", default="1920x1080,1280x800,1024x768,390x844")
    args = parser.parse_args()
    validate_maturity_manifest()
    payload = {
        "mmi_version": MATURITY_MANIFEST_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "commit": _git_commit(),
        "system": platform.platform(),
        "python": sys.version.split()[0],
        "browser": args.browser,
        "resolutions": [item.strip() for item in args.resolutions.split(",") if item.strip()],
        "themes": ["light", "dark"],
        "dimensions": [item.identifier for item in MMI_DIMENSIONS],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
