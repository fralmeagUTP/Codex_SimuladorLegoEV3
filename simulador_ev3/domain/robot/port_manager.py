"""
port_manager.py
===============
Registro y validación de puertos del brick EV3.

El brick EV3 expone:
    Puertos de salida (motores):  A, B, C, D
    Puertos de entrada (sensores): S1, S2, S3, S4

Responsabilidades:
    - Registrar qué dispositivo está conectado en cada puerto.
    - Validar que el tipo de dispositivo es coherente con el puerto.
    - Proveer acceso al dispositivo por nombre de puerto.
    - Detectar conflictos (dos dispositivos en el mismo puerto).
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Any, Dict


class PortType(Enum):
    """Categoría de puerto según el tipo de señal que soporta."""

    OUTPUT = auto()  # puertos de motores: A, B, C, D
    INPUT = auto()  # puertos de sensores: S1, S2, S3, S4


# Definición estática de todos los puertos del brick EV3
_PORT_CATALOG: Dict[str, PortType] = {
    "A": PortType.OUTPUT,
    "B": PortType.OUTPUT,
    "C": PortType.OUTPUT,
    "D": PortType.OUTPUT,
    "S1": PortType.INPUT,
    "S2": PortType.INPUT,
    "S3": PortType.INPUT,
    "S4": PortType.INPUT,
}


# Tipos de dispositivo reconocidos para validación semántica
class DeviceCategory(Enum):
    MOTOR = auto()
    SENSOR = auto()


# Categoría esperada por tipo de puerto
_EXPECTED_CATEGORY: Dict[PortType, DeviceCategory] = {
    PortType.OUTPUT: DeviceCategory.MOTOR,
    PortType.INPUT: DeviceCategory.SENSOR,
}


class PortError(Exception):
    """Error relacionado con la gestión de puertos."""


class PortManager:
    """
    Gestiona el registro de dispositivos en los puertos del brick EV3.

    Ejemplo de uso:
        pm = PortManager()
        motor = MotorModel("B")
        pm.register("B", motor, DeviceCategory.MOTOR)
        device = pm.get_device("B")
    """

    def __init__(self) -> None:
        # Mapeo puerto → (dispositivo, categoría)
        self._registry: Dict[str, tuple[Any, DeviceCategory]] = {}

    # ------------------------------------------------------------------ #
    # Registro
    # ------------------------------------------------------------------ #

    def register(
        self,
        port_name: str,
        device: Any,
        category: DeviceCategory,
    ) -> None:
        """
        Registra un dispositivo en un puerto.

        Args:
            port_name: Nombre del puerto (p.ej. 'B', 'S1').
            device:    Instancia del modelo de dispositivo.
            category:  Categoría del dispositivo (MOTOR o SENSOR).

        Raises:
            PortError: Si el puerto no existe, el tipo no coincide,
                       o ya hay un dispositivo registrado.
        """
        port_name = port_name.upper()

        if port_name not in _PORT_CATALOG:
            raise PortError(
                f"Puerto '{port_name}' no existe en el brick EV3. Puertos válidos: {list(_PORT_CATALOG.keys())}"
            )

        port_type = _PORT_CATALOG[port_name]
        expected = _EXPECTED_CATEGORY[port_type]

        if category != expected:
            raise PortError(
                f"Puerto '{port_name}' es de tipo {port_type.name} "
                f"y acepta {expected.name}, pero se intentó registrar {category.name}."
            )

        if port_name in self._registry:
            existing, _ = self._registry[port_name]
            raise PortError(f"Puerto '{port_name}' ya tiene registrado: {existing!r}. Llama a unregister() primero.")

        self._registry[port_name] = (device, category)

    def unregister(self, port_name: str) -> None:
        """
        Elimina el dispositivo registrado en un puerto.

        Raises:
            PortError: Si el puerto no tiene dispositivo registrado.
        """
        port_name = port_name.upper()
        if port_name not in self._registry:
            raise PortError(f"Puerto '{port_name}' no tiene dispositivo registrado.")
        del self._registry[port_name]

    # ------------------------------------------------------------------ #
    # Acceso
    # ------------------------------------------------------------------ #

    def get_device(self, port_name: str) -> Any:
        """
        Retorna el dispositivo registrado en un puerto.

        Raises:
            PortError: Si el puerto no tiene dispositivo registrado.
        """
        port_name = port_name.upper()
        if port_name not in self._registry:
            raise PortError(f"No hay dispositivo registrado en puerto '{port_name}'.")
        device, _ = self._registry[port_name]
        return device

    def get_category(self, port_name: str) -> DeviceCategory:
        """Retorna la categoría del dispositivo en un puerto."""
        port_name = port_name.upper()
        if port_name not in self._registry:
            raise PortError(f"No hay dispositivo registrado en puerto '{port_name}'.")
        _, category = self._registry[port_name]
        return category

    def is_registered(self, port_name: str) -> bool:
        """Indica si hay algún dispositivo en el puerto."""
        return port_name.upper() in self._registry

    # ------------------------------------------------------------------ #
    # Consultas globales
    # ------------------------------------------------------------------ #

    def all_motors(self) -> Dict[str, Any]:
        """Retorna todos los dispositivos de categoría MOTOR por puerto."""
        return {port: device for port, (device, cat) in self._registry.items() if cat == DeviceCategory.MOTOR}

    def all_sensors(self) -> Dict[str, Any]:
        """Retorna todos los dispositivos de categoría SENSOR por puerto."""
        return {port: device for port, (device, cat) in self._registry.items() if cat == DeviceCategory.SENSOR}

    @staticmethod
    def available_ports() -> Dict[str, PortType]:
        """Retorna el catálogo completo de puertos del brick EV3."""
        return dict(_PORT_CATALOG)

    def __repr__(self) -> str:  # pragma: no cover
        registered = {p: type(d).__name__ for p, (d, _) in self._registry.items()}
        return f"PortManager(registered={registered})"
