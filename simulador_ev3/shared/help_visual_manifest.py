"""Manifiesto versionado de capturas reales utilizadas por el Centro de ayuda."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from simulador_ev3.shared.help_content_contract import GuideVisualReference
from simulador_ev3.shared.help_tutorials import HELP_GUIDES

HELP_VISUAL_MANIFEST_VERSION = 1
HELP_VISUAL_CAPTURE_DATE = "2026-08-24"


@dataclass(frozen=True)
class HelpVisual:
    """Entrada concreta del manifiesto, con procedencia auditable."""

    guide_id: str
    platform: str
    filename: str
    theme: str
    source: str
    alt: str
    transcript: str
    ui_version: str

    def reference(self) -> GuideVisualReference:
        """Expone el DTO público sin revelar la procedencia interna de captura."""

        return GuideVisualReference(
            guide_id=self.guide_id,
            platform=self.platform,
            filename=self.filename,
            alt=self.alt,
            transcript=self.transcript,
            theme=self.theme,
            ui_version=self.ui_version,
        )


HELP_VISUALS: tuple[HelpVisual, ...] = (
    HelpVisual(
        "first-simulation",
        "web",
        "web/primera_simulacion.png",
        "light",
        "capture_web_evidence",
        "Simulación Web con canvas, editor, telemetría y Brick visibles.",
        "Identifica Ejecutar, el mundo activo, el canvas, el editor y la telemetría.",
        "1.5.0",
    ),
    HelpVisual(
        "create-world",
        "web",
        "web/crear_mundo.png",
        "light",
        "capture_web_evidence",
        "Editor Web de mundos con biblioteca, lienzo e inspector.",
        "Selecciona un asset en Biblioteca, colócalo en el lienzo y revisa sus propiedades.",
        "1.5.0",
    ),
    HelpVisual(
        "run-simulation",
        "web",
        "web/ejecutar_pausar_reiniciar.png",
        "dark",
        "capture_web_evidence",
        "Controles de ejecución Web en tema oscuro.",
        "Los controles Ejecutar, Pausar, Reanudar y Detener y reiniciar aparecen sobre el canvas.",
        "1.5.0",
    ),
    HelpVisual(
        "use-sensors",
        "web",
        "web/motores_sensores.png",
        "light",
        "capture_web_evidence",
        "Panel Brick y telemetría del simulador Web.",
        "La telemetría muestra motores y sensores; el Brick contiene LED, altavoz y LCD.",
        "1.5.0",
    ),
    HelpVisual(
        "debug-script",
        "web",
        "web/depurar_programa.png",
        "light",
        "capture_web_evidence",
        "Editor Web con sintaxis y controles de depuración.",
        "El editor contiene puntos de interrupción, Paso, Continuar y Watches.",
        "1.5.0",
    ),
    HelpVisual(
        "recover-script-error",
        "tkinter",
        "tkinter/error_programa.png",
        "light",
        "interactive_desktop_qa",
        "Diálogo real de error de programa en Tkinter.",
        "El error se presenta sin ocultar el editor; la recuperación empieza desde el mensaje mostrado.",
        "1.5.0",
    ),
    HelpVisual(
        "recover-world-validation",
        "web",
        "web/validar_mundo.png",
        "light",
        "capture_web_evidence",
        "Inspector de propiedades del Editor Web de mundos.",
        "La validación se revisa después de seleccionar un elemento y completar sus propiedades.",
        "1.5.0",
    ),
    HelpVisual(
        "recover-script-error",
        "web",
        "web/error_programa.png",
        "light",
        "capture_web_evidence",
        "Error de programa mostrado en la aplicación Web.",
        "El error se presenta junto al editor y se corrige antes de reiniciar la simulación.",
        "1.5.0",
    ),
    HelpVisual(
        "missions",
        "web",
        "web/misiones.png",
        "light",
        "capture_web_evidence",
        "Simulación con escenario, robot y paneles de resultado.",
        "La misión se selecciona desde el menú y se comprueba después de finalizar.",
        "1.5.0",
    ),
    HelpVisual(
        "traces",
        "web",
        "web/trazas.png",
        "dark",
        "capture_web_evidence",
        "Canvas de simulación con controles para observar un recorrido.",
        "Las trazas sirven para comparar recorridos y se limpian al reiniciar.",
        "1.5.0",
    ),
    HelpVisual(
        "runtime-limit",
        "web",
        "web/tiempo_maximo.png",
        "light",
        "capture_web_evidence",
        "Interfaz Web con controles y menú de configuración.",
        "El menú Tiempo máximo establece el límite de ejecución de los scripts.",
        "1.5.0",
    ),
    HelpVisual(
        "session-diagnostics",
        "web",
        "web/diagnostico_sesion.png",
        "light",
        "capture_web_evidence",
        "Aplicación Web con editor y estado de ejecución visibles.",
        "El diagnóstico de sesión se abre desde Ayuda y no expone el código del usuario.",
        "1.5.0",
    ),
)


# Huellas de los recursos Web publicados. Si cambia una captura de forma
# intencional, se debe regenerar y revisar su metadata antes de actualizar este
# mapa; no se aceptan cambios silenciosos de assets didácticos.
HELP_VISUAL_SHA256: dict[str, str] = {
    "web/primera_simulacion.png": "a5f49d94d2c00be74c1409444a47bf34a7257dc61f0214cc0b3b128a55533cb5",
    "web/crear_mundo.png": "d0720f4129f24f0dc200129cac389336c382a86f995657111b5c09c0736732a4",
    "web/ejecutar_pausar_reiniciar.png": "07eeab69f8f2f4c06da78ddcdb69ed4219a1203153a775a20f6b086ec4f32f76",
    "web/motores_sensores.png": "ade5b9e9c708fbeadc1466707fe700af9d404c7c314c858d7efd01962023607b",
    "web/depurar_programa.png": "7512242ee7dd1e8c4914eac66dbc1d5fa31fb7f0140148c2d1d23a8458f3c408",
    "web/error_programa.png": "b02365ee92a544d890dd8439625b35962bf21e8d7aac89073cddcd5d308f87eb",
    "web/validar_mundo.png": "5f8cc11de93af8a3e63e31e354783a6b1611587490912140fc314a3f8cbda012",
    "web/misiones.png": "bd7b6dd76e9f40d6d66eac344b0ccbf59667a962ec8854fb3aaf276c09ebdb7a",
    "web/trazas.png": "9deafecb80ee8c190b92dd15bda4572d4ae48d68db0a1754adb3d3fca7e0c988",
    "web/tiempo_maximo.png": "584912abe443b33d8a8998954be491e79ce28c46c84944e95d60ea6f39e74660",
    "web/diagnostico_sesion.png": "fcb38bffcbf730caffd59bca1c7c9182158480e4cf8f67945a34509420fadea7",
}
_FORBIDDEN_CAPTURE_MARKERS = (b"authorization:", b"api_key", b"password=", b"bearer ")


def validate_visual_manifest(static_help_directory: Path) -> tuple[str, ...]:
    """Devuelve errores de cobertura y de archivos faltantes del manifiesto."""

    errors: list[str] = []
    guide_ids = {guide.identifier for guide in HELP_GUIDES}
    web_visuals = {visual.guide_id: visual for visual in HELP_VISUALS if visual.platform == "web"}
    for guide in HELP_GUIDES:
        visual = web_visuals.get(guide.identifier)
        if visual is None:
            errors.append(f"La guía {guide.identifier} no tiene captura Web.")
            continue
        if visual.filename != guide.image_name:
            errors.append(f"La guía {guide.identifier} no referencia su captura canónica.")
        asset_path = static_help_directory / visual.filename
        if not asset_path.is_file():
            errors.append(f"No existe el asset de ayuda {visual.filename}.")
            continue
        asset = asset_path.read_bytes()
        if not asset.startswith(b"\x89PNG\r\n\x1a\n"):
            errors.append(f"El asset {visual.filename} no es un PNG válido.")
        if not 10_000 <= len(asset) <= 2_000_000:
            errors.append(f"El tamaño de {visual.filename} está fuera del rango permitido.")
        expected_hash = HELP_VISUAL_SHA256.get(visual.filename)
        if expected_hash is None:
            errors.append(f"No existe huella de integridad para {visual.filename}.")
        elif sha256(asset).hexdigest() != expected_hash:
            errors.append(f"La huella de {visual.filename} no coincide con el manifiesto.")
        if any(marker in asset.lower() for marker in _FORBIDDEN_CAPTURE_MARKERS):
            errors.append(f"El asset {visual.filename} contiene un marcador sensible prohibido.")
        if not visual.alt or not visual.transcript:
            errors.append(f"La captura {visual.filename} no tiene texto alternativo y transcripción.")
    for visual in HELP_VISUALS:
        if visual.guide_id not in guide_ids:
            errors.append(f"El manifiesto contiene una guía desconocida: {visual.guide_id}.")
    return tuple(errors)


def visual_for(guide_id: str, platform: str = "web") -> HelpVisual:
    for visual in HELP_VISUALS:
        if visual.guide_id == guide_id and visual.platform == platform:
            return visual
    raise KeyError(f"No existe visual para guía={guide_id!r}, plataforma={platform!r}")
