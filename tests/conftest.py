"""Configuracion comun: las pruebas unitarias usan compatibilidad local explicita."""

import os

os.environ.setdefault("EV3_LOCAL_RUNTIME_ENABLED", "true")
