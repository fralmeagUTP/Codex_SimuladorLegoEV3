"""WSGI entrypoint for production-capable servers."""

from __future__ import annotations

from simulador_ev3.web.app import create_app


app = create_app()
