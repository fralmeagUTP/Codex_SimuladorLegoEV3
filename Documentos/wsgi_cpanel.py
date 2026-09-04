"""WSGI para cPanel (Setup Python App / Passenger).

Copiar este contenido a `wsgi.py` en el *Application root* de cPanel.

En cPanel debes tener:
- Startup file: wsgi.py
- Entry point: app
"""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path


def _bootstrap_log_path() -> Path:
    home = Path(os.path.expanduser("~"))
    return home / "logs" / "simuladorlego_bootstrap.log"


def _write_log(message: str) -> None:
    try:
        log_path = _bootstrap_log_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(message.rstrip() + "\n")
    except Exception:
        # Nunca bloquear el arranque por errores de logging.
        pass


def _candidate_roots(base_dir: Path) -> list[Path]:
    home = Path(os.path.expanduser("~"))
    return [
        base_dir,
        home / "public_html" / "simuladorlego",
        home / "simuladorlego",
    ]


def _select_project_root() -> Path:
    base_dir = Path(__file__).resolve().parent
    for candidate in _candidate_roots(base_dir):
        if (candidate / "simulador_ev3").is_dir():
            return candidate
    checked = " | ".join(str(path) for path in _candidate_roots(base_dir))
    raise RuntimeError(
        "No se encontro la carpeta 'simulador_ev3' en ninguna ruta candidata: "
        f"{checked}"
    )


def _bootstrap_app():
    project_root = _select_project_root()
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    _write_log(f"[BOOT] project_root={root_str}")

    from simulador_ev3.web.app import create_app

    return create_app()


try:
    app = _bootstrap_app()
except Exception as exc:  # pragma: no cover - ruta de diagnostico en produccion
    tb = traceback.format_exc()
    _write_log("[BOOT][ERROR] " + repr(exc))
    _write_log(tb)

    def app(environ, start_response):
        body = (
            "Error al iniciar la app EV3 en cPanel.\\n"
            "Contacte al administrador del servicio para revisar los registros.\\n"
        ).encode("utf-8")
        status = "500 Internal Server Error"
        headers = [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ]
        start_response(status, headers)
        return [body]
