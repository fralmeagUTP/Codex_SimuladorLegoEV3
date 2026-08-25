"""Fuente única de versión distribuible del Simulador EV3."""

APP_VERSION = "1.5.0"
# Se incrementa por cambios de frontend aunque la versión distribuible no cambie.
# Evita que el navegador conserve CSS/JS anterior tras una actualización local.
WEB_ASSET_VERSION = f"v{APP_VERSION}-ui4"
