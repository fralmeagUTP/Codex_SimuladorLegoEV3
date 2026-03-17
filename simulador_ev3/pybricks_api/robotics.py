"""
robotics.py — DriveBase Pybricks (pybricks.robotics).

DriveBase encapsula el movimiento diferencial del robot.
Los métodos straight() y turn() bloquean el ScriptThread hasta que
el SimulationEngine señala la finalización vía threading.Event.
"""
from __future__ import annotations

from simulador_ev3.core.command_queue import SimulationCommand
from simulador_ev3.pybricks_api._context import PybricksContext
from simulador_ev3.pybricks_api.parameters import Stop, STOP_TO_STOPMODE
# Motor se importa tardíamente para evitar importación circular
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from simulador_ev3.pybricks_api.ev3devices import Motor


class DriveBase:
    """
    DriveBase diferencial EV3 (pybricks.robotics.DriveBase).

    Args:
        left_motor:       Motor izquierdo.
        right_motor:      Motor derecho.
        wheel_diameter:   Diámetro de rueda en mm.
        axle_track:       Distancia entre centros de rueda en mm.
    """

    def __init__(
        self,
        left_motor: "Motor",
        right_motor: "Motor",
        wheel_diameter: float,
        axle_track: float,
    ) -> None:
        ctx = PybricksContext.get_current()
        self._queue = ctx.command_queue

        # Actualiza los parámetros geométricos del DriveBaseModel del engine
        # (los valores se conservan del SimEngineConfig si no se llama settings)
        db = ctx.engine._drivebase
        db.wheel_diameter_mm = float(wheel_diameter)
        db.axle_track_mm     = float(axle_track)

    # ------------------------------------------------------------------
    # Comandos no bloqueantes
    # ------------------------------------------------------------------

    def drive(self, speed: float, turn_rate: float) -> None:
        """
        Conducción continua.

        Args:
            speed:     Velocidad lineal en mm/s (positivo = adelante).
            turn_rate: Tasa de giro en deg/s (positivo = izquierda).
        """
        self._queue.put(SimulationCommand.db_drive(speed, turn_rate))

    def stop(self) -> None:
        """Detiene el DriveBase (coast)."""
        self._queue.put(SimulationCommand.db_stop())

    # ------------------------------------------------------------------
    # Comandos bloqueantes
    # ------------------------------------------------------------------

    def straight(
        self,
        distance: float,
        then: Stop = Stop.HOLD,
        wait: bool = True,
    ) -> None:
        """
        Avanza/retrocede `distance` mm en línea recta y para.

        Args:
            distance: Distancia en mm (positivo = adelante).
            then:     Modo de parada al finalizar.
            wait:     Si True, bloquea hasta completar.
        """
        cmd = SimulationCommand.db_straight(distance)
        if wait:
            # timeout: tiempo estimado + 5 s
            ctx = PybricksContext.get_current()
            speed = ctx.engine._drivebase.profile.straight_speed
            est_s = abs(distance) / max(abs(speed), 1) + 5.0
            self._queue.put_and_wait(cmd, timeout=est_s)
        else:
            self._queue.put(cmd)

    def turn(
        self,
        angle: float,
        then: Stop = Stop.HOLD,
        wait: bool = True,
    ) -> None:
        """
        Gira `angle` grados sobre sí mismo y para.

        Args:
            angle: Giro en grados (positivo = izquierda/antihorario).
            then:  Modo de parada al finalizar.
            wait:  Si True, bloquea hasta completar.
        """
        cmd = SimulationCommand.db_turn(angle)
        if wait:
            ctx   = PybricksContext.get_current()
            rate  = ctx.engine._drivebase.profile.turn_rate
            est_s = abs(angle) / max(abs(rate), 1) + 5.0
            self._queue.put_and_wait(cmd, timeout=est_s)
        else:
            self._queue.put(cmd)

    # ------------------------------------------------------------------
    # Configuración
    # ------------------------------------------------------------------

    def settings(
        self,
        straight_speed: float     = 200.0,
        straight_acceleration: float = 200.0,
        turn_rate: float          = 90.0,
        turn_acceleration: float  = 90.0,
    ) -> None:
        """Ajusta los parámetros de velocidad/aceleración del DriveBase."""
        self._queue.put(
            SimulationCommand.db_settings(
                straight_speed, straight_acceleration,
                turn_rate, turn_acceleration,
            )
        )

    # ------------------------------------------------------------------
    # Lecturas de odometría
    # ------------------------------------------------------------------

    def distance(self) -> float:
        """
        Distancia total recorrida en mm desde el último reset_distance().
        Aproximación: posición euclidiana absoluta del robot.
        """
        ctx  = PybricksContext.get_current()
        pose = ctx.engine.robot.pose
        return (pose.x ** 2 + pose.y ** 2) ** 0.5

    def angle(self) -> float:
        """Ángulo total girado en grados desde el último reset_angle()."""
        import math
        ctx = PybricksContext.get_current()
        return math.degrees(ctx.engine.robot.pose.theta)

    def reset(self) -> None:
        """Resetea la odometría (no implementado en la simulación básica)."""
        pass  # Futuro: resetear pose del robot
