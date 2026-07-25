"""Waitress runner for the EV3 Flask web application."""

from __future__ import annotations

import os
import sys

from simulador_ev3.web.wsgi import app


def main() -> None:
    try:
        from waitress import serve
    except ImportError as error:
        print(
            "Falta instalar Waitress. Ejecuta: .\\.venv\\Scripts\\python.exe -m pip install -e .[web-prod]",
            file=sys.stderr,
        )
        raise SystemExit(1) from error

    host = os.environ.get("EV3_WEB_HOST", "127.0.0.1")
    port = int(os.environ.get("EV3_WEB_PORT", "5050"))
    threads = int(os.environ.get("EV3_WEB_THREADS", "8"))
    serve(app, host=host, port=port, threads=threads)


if __name__ == "__main__":
    main()
