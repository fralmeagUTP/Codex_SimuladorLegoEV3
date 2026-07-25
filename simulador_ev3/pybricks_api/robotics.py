"""
robotics.py — DriveBase Pybricks (pybricks.robotics).

DriveBase encapsula el movimiento diferencial del robot.
Los métodos straight() y turn() bloquean el ScriptThread hasta que
el SimulationEngine señala la finalización vía threading.Event.
"""

from __future__ import annotations

import math
import threading
import time

# Motor se importa tardíamente para evitar importación circular
from typing import TYPE_CHECKING

from simulador_ev3.core.command_queue import SimulationCommand
from simulador_ev3.pybricks_api._context import PybricksContext
from simulador_ev3.pybricks_api.parameters import Stop

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
        db.axle_track_mm = float(axle_track)

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
        self._queue.put(SimulationCommand.db_stop("COAST"))

    def brake(self) -> None:
        """Frena el DriveBase activamente."""
        self._queue.put(SimulationCommand.db_stop("BRAKE"))

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
        cmd = SimulationCommand.db_straight(distance, stop_mode=then.name)
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
        cmd = SimulationCommand.db_turn(angle, stop_mode=then.name)
        if wait:
            ctx = PybricksContext.get_current()
            rate = ctx.engine._drivebase.profile.turn_rate
            est_s = abs(angle) / max(abs(rate), 1) + 5.0
            self._queue.put_and_wait(cmd, timeout=est_s)
        else:
            self._queue.put(cmd)

    def curve(
        self,
        radius: float,
        angle: float,
        then: Stop = Stop.HOLD,
        wait: bool = True,
    ) -> None:
        """
        Recorre un arco de radio `radius` y angulo `angle`.

        Implementacion aproximada sobre `drive(speed, turn_rate)` con
        duracion estimada.
        """
        if abs(angle) <= 1e-9:
            return
        if abs(radius) <= 1e-9:
            self.turn(angle, then=then, wait=wait)
            return

        ctx = PybricksContext.get_current()
        base_speed = max(1.0, abs(ctx.engine._drivebase.profile.straight_speed))
        arc_mm = math.radians(float(angle)) * float(radius)
        speed = math.copysign(base_speed, arc_mm)
        turn_rate = math.degrees(speed / float(radius))
        duration_s = abs(float(angle)) / max(abs(turn_rate), 1e-6)

        self._queue.put(SimulationCommand.db_drive(speed, turn_rate))
        if wait:
            from simulador_ev3.pybricks_api.tools import wait as py_wait

            py_wait(duration_s * 1000.0)
            self._apply_stop_mode(then)
            return

        def _deferred_stop() -> None:
            time.sleep(duration_s)
            self._apply_stop_mode(then)

        threading.Thread(target=_deferred_stop, daemon=True).start()

    # ------------------------------------------------------------------
    # Configuración
    # ------------------------------------------------------------------

    def settings(
        self,
        straight_speed: float = 200.0,
        straight_acceleration: float = 200.0,
        turn_rate: float = 90.0,
        turn_acceleration: float = 90.0,
    ) -> None:
        """Ajusta los parámetros de velocidad/aceleración del DriveBase."""
        self._queue.put(
            SimulationCommand.db_settings(
                straight_speed,
                straight_acceleration,
                turn_rate,
                turn_acceleration,
            )
        )

    def done(self) -> bool:
        """True si no hay maniobra acotada en progreso."""
        from simulador_ev3.domain.robot.drivebase_model import DriveState

        ctx = PybricksContext.get_current()
        return ctx.engine._drivebase.state in (DriveState.IDLE, DriveState.BRAKE, DriveState.HOLD)

    def stalled(self) -> bool:
        """Deteccion aproximada de estancamiento del drivebase."""
        from simulador_ev3.domain.robot.drivebase_model import DriveState

        ctx = PybricksContext.get_current()
        db = ctx.engine._drivebase
        if db.state == DriveState.IDLE:
            return False
        if getattr(ctx.engine, "_colliding", False):
            return True
        return abs(db.linear_speed) < 1e-3 and abs(db.angular_speed_deg) < 1e-3

    def state(self) -> tuple[int, int, int, int]:
        """
        Estado cinemático aproximado:
        (distance_mm, speed_mm_s, angle_deg, turn_rate_deg_s).
        """
        ctx = PybricksContext.get_current()
        db = ctx.engine._drivebase
        return (
            int(round(self.distance())),
            int(round(db.linear_speed)),
            int(round(self.angle())),
            int(round(db.angular_speed_deg)),
        )

    def use_gyro(self, enabled: bool = True) -> None:
        """
        Compatibilidad API.
        La simulacion actual no aplica correccion con gyro en DriveBase.
        """
        _ = enabled

    def _apply_stop_mode(self, then: Stop) -> None:
        """Aplica modo de parada al terminar maniobras sinteticas."""
        self._queue.put(SimulationCommand.db_stop(then.name))

    # ------------------------------------------------------------------
    # Lecturas de odometría
    # ------------------------------------------------------------------

    def distance(self) -> float:
        """
        Distancia total recorrida en mm desde el último reset_distance().
        Aproximación: posición euclidiana absoluta del robot.
        """
        ctx = PybricksContext.get_current()
        pose = ctx.engine.robot.pose
        return (pose.x**2 + pose.y**2) ** 0.5

    def angle(self) -> float:
        """Ángulo total girado en grados desde el último reset_angle()."""
        import math

        ctx = PybricksContext.get_current()
        return math.degrees(ctx.engine.robot.pose.theta)

    def reset(self) -> None:
        """Resetea la odometría (no implementado en la simulación básica)."""
        pass  # Futuro: resetear pose del robot
