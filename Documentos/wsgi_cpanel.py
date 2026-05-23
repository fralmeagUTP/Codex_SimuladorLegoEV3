"""WSGI para cPanel (Setup Python App / Passenger).

Copiar este contenido a:
/home/ur5cxigur1qs/simuladorlego/wsgi.py

En cPanel debes tener:
- Startup file: wsgi.py
- Entry point: app
"""

import os
import sys

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from simulador_ev3.web.app import create_app

app = create_app()
