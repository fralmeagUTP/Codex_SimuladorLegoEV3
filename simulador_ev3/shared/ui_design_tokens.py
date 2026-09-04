"""Tokens visuales compartidos; la Web es la fuente de verdad semántica."""

from __future__ import annotations

from dataclasses import dataclass

WEB_REFERENCE_WIDTH_PX = 1280
WEB_REFERENCE_HEIGHT_PX = 800
WEB_MIN_WIDTH_PX = 900
WEB_MIN_HEIGHT_PX = 600
VISUAL_COMPARISON_TOLERANCE_PX = 4

# Métricas de composición compartidas. Los toolkits son distintos, pero estas
# medidas mantienen la misma densidad y los mismos mínimos funcionales.
APP_OUTER_PADDING_PX = 12
COMPACT_GAP_PX = 6
PANEL_GAP_PX = 10
PANEL_RADIUS_PX = 4
CANVAS_MIN_HEIGHT_PX = 300
TELEMETRY_MIN_WIDTH_PX = 300
# El Brick contiene una franja de estado, LCD y tabla Robot/Estado. Menos de
# 340 px recorta LED/Altavoz en la composición inferior de 1280 px; este
# mínimo mantiene las dos celdas de estado legibles sin sacrificar telemetría.
BRICK_MIN_WIDTH_PX = 340
EDITOR_MIN_WIDTH_PX = 430
SIMULATION_MIN_WIDTH_PX = 700
STATUS_STRIP_HEIGHT_PX = 30


def scaled_px(value: int, dpi_scale: float = 1.0) -> int:
    """Escala medidas Web de referencia con un límite seguro para DPI."""

    return max(1, round(int(value) * max(0.75, min(float(dpi_scale), 2.0))))


@dataclass(frozen=True)
class ThemeTokens:
    background: str
    surface: str
    surface_muted: str
    text: str
    text_muted: str
    primary: str
    primary_active: str
    danger: str
    success: str
    warning: str
    focus: str
    border: str
    toolbar: str
    toolbar_text: str


LIGHT_TOKENS = ThemeTokens(
    background="#F4F6F8", surface="#FFFFFF", surface_muted="#F8FAFC",
    text="#18212F", text_muted="#314861", primary="#294C7C",
    primary_active="#213858", danger="#B71C1C", success="#2E7D32",
    warning="#F57F17", focus="#0D47A1", border="#C5D2E2",
    # La barra de menús clara replica `.menu-bar` de la Web.
    toolbar="#F8FAFC", toolbar_text="#0F172A",
)
DARK_TOKENS = ThemeTokens(
    background="#0F1724", surface="#152238", surface_muted="#17253A",
    text="#DBE5F5", text_muted="#B8C8DA", primary="#2E5EA3",
    primary_active="#3B67A5", danger="#C62828", success="#81C784",
    warning="#FFCC80", focus="#90CAF9", border="#2B4A66",
    # La variante oscura replica `html[data-theme="dark"] .menu-bar`.
    toolbar="#111C2D", toolbar_text="#E2E8F0",
)


def tokens_for_theme(theme: str) -> ThemeTokens:
    return DARK_TOKENS if str(theme).strip().lower() == "dark" else LIGHT_TOKENS
