"""
ev3devices.py — Dispositivos EV3 Pybricks (pybricks.ev3devices).

Implementa Motor y todos los sensores del EV3.  Cada clase:
  1. Recibe el puerto en el constructor.
  2. Crea y adjunta el modelo de dominio correspondiente al engine.
  3. Envía comandos al CommandQueue.
  4. Lee valores directamente del modelo de dominio.

Los sensores quedan adjuntos al engine para ser actualizados en cada tick.
"""

from __future__ import annotations

from typing import Optional

from simulador_ev3.core.command_queue import SimulationCommand
from simulador_ev3.domain.robot.motor_model import MotorState
from simulador_ev3.domain.sensors.color_sensor_model import ColorSensorModel
from simulador_ev3.domain.sensors.gyro_sensor_model import GyroSensorModel
from simulador_ev3.domain.sensors.infrared_sensor_model import InfraredSensorModel
from simulador_ev3.domain.sensors.touch_sensor_model import TouchSensorModel
from simulador_ev3.domain.sensors.ultrasonic_sensor_model import UltrasonicSensorModel
from simulador_ev3.pybricks_api._context import PybricksContext
from simulador_ev3.pybricks_api.parameters import (
    STOP_TO_STOPMODE,
    SURFACE_TO_PYBRICKS,
    Color,
    Direction,
    Port,
    Stop,
)

# ---------------------------------------------------------------------------
# Motor
# ---------------------------------------------------------------------------


class Motor:
    """
    Motor EV3 individual (pybricks.ev3devices.Motor).

    Args:
        port:               Puerto del motor (Port.A … Port.D).
        positive_direction: Dirección positiva (Direction.CLOCKWISE por defecto).
    """

    def __init__(
        self,
        port: Port,
        positive_direction: Direction = Direction.CLOCKWISE,
    ) -> None:
        ctx = PybricksContext.get_current()
        self._queue = ctx.command_queue
        self._port = str(port)
        self._dir = positive_direction
        # Acceso directo al MotorModel del engine
        self._model = ctx.engine._motors.get(self._port)
        # Aproximacion para convertir duty cycle (%) a deg/s.
        self._max_speed_dps = 1050.0

    # ------------------------------------------------------------------
    # Comandos (no bloqueantes)
    # ------------------------------------------------------------------

    def run(self, speed: float) -> None:
        """Gira continuamente a `speed` deg/s."""
        s = speed if self._dir == Direction.CLOCKWISE else -speed
        self._queue.put(SimulationCommand.motor_run(self._port, s))

    def dc(self, duty: float) -> None:
        """
        Gira usando ciclo de trabajo (%), aproximado a velocidad angular.
        """
        duty_clamped = max(-100.0, min(100.0, float(duty)))
        speed = (duty_clamped / 100.0) * self._max_speed_dps
        self.run(speed)

    def stop(self) -> None:
        """Detiene el motor (coast)."""
        self._queue.put(SimulationCommand.motor_stop(self._port))

    def brake(self) -> None:
        """Frena activamente."""
        self._queue.put(SimulationCommand.motor_brake(self._port))

    def hold(self) -> None:
        """Mantiene la posición actual."""
        self._queue.put(SimulationCommand.motor_hold(self._port))

    # ------------------------------------------------------------------
    # Comandos bloqueantes
    # ------------------------------------------------------------------

    def run_time(
        self,
        speed: float,
        time: float,
        then: Stop = Stop.BRAKE,
        wait: bool = True,
    ) -> None:
        """
        Gira a `speed` deg/s durante `time` ms.
        Si `wait=True`, bloquea hasta completar.
        """
        s = speed if self._dir == Direction.CLOCKWISE else -speed
        cmd = SimulationCommand.motor_run_time(
            self._port,
            s,
            time,
            stop_mode=STOP_TO_STOPMODE.get(then, "BRAKE"),
        )
        if wait:
            self._queue.put_and_wait(cmd, timeout=time / 1000.0 + 5.0)
        else:
            self._queue.put(cmd)

    def run_angle(
        self,
        speed: float,
        rotation_angle: float,
        then: Stop = Stop.HOLD,
        wait: bool = True,
    ) -> None:
        """
        Gira `rotation_angle` grados a `speed` deg/s.
        Si `wait=True`, bloquea hasta completar.
        """
        s = speed if self._dir == Direction.CLOCKWISE else -speed
        ra = rotation_angle if self._dir == Direction.CLOCKWISE else -rotation_angle
        cmd = SimulationCommand.motor_run_angle(
            self._port,
            s,
            ra,
            stop_mode=STOP_TO_STOPMODE.get(then, "HOLD"),
        )
        if wait:
            # timeout generoso: tiempo estimado + 5 s
            est_s = abs(ra) / max(abs(s), 1) + 5.0
            self._queue.put_and_wait(cmd, timeout=est_s)
        else:
            self._queue.put(cmd)

    def run_target(
        self,
        speed: float,
        target_angle: float,
        then: Stop = Stop.HOLD,
        wait: bool = True,
    ) -> None:
        """
        Gira hasta alcanzar un angulo absoluto objetivo.
        Implementado como delta sobre `run_angle`.
        """
        delta = float(target_angle) - float(self.angle())
        self.run_angle(speed=speed, rotation_angle=delta, then=then, wait=wait)

    def track_target(self, target_angle: float) -> None:
        """
        Sigue un objetivo angular de forma continua.
        Aproximacion: run_target con alta velocidad y wait=False.
        """
        self.run_target(
            speed=900.0,
            target_angle=target_angle,
            then=Stop.HOLD,
            wait=False,
        )

    def run_until_stalled(
        self,
        speed: float,
        then: Stop = Stop.COAST,
        duty_limit: Optional[float] = None,
    ) -> float:
        """
        Corre el motor hasta detectar estancamiento y retorna avance angular.

        Nota:
        El simulador no modela torque/corriente real, por lo que la deteccion
        de estancamiento es aproximada (angulo sin cambio por ventana corta).
        """
        _ = duty_limit  # compatibilidad de firma

        from simulador_ev3.pybricks_api.tools import StopWatch, wait

        start_angle = float(self.angle())
        self.run(speed)

        watch = StopWatch()
        last_angle = start_angle
        still_ms = 0
        timeout_ms = 2000
        sample_ms = 20

        while watch.time() < timeout_ms:
            wait(sample_ms)
            current = float(self.angle())
            if abs(current - last_angle) < 0.5:
                still_ms += sample_ms
                if still_ms >= 120:
                    break
            else:
                still_ms = 0
            last_angle = current

        if then == Stop.HOLD:
            self.hold()
        elif then == Stop.BRAKE:
            self.brake()
        else:
            self.stop()

        return float(self.angle()) - start_angle

    # ------------------------------------------------------------------
    # Lecturas del sensor integrado del motor
    # ------------------------------------------------------------------

    def angle(self) -> float:
        """Posición acumulada en grados desde el último reset."""
        if self._model:
            return self._model.angle
        return 0.0

    def speed(self) -> float:
        """Velocidad angular actual en deg/s."""
        if self._model:
            return self._model.speed
        return 0.0

    def reset_angle(self, angle: float = 0.0) -> None:
        """Resetea el encoder a `angle` (funcionalidad mínima — pone en 0)."""
        if self._model:
            self._model._angle = float(angle)  # acceso interno al dominio

    def done(self) -> bool:
        """True si no hay maniobra pendiente del motor."""
        if self._model is None:
            return True
        return self._model.state in (
            MotorState.IDLE,
            MotorState.BRAKE,
            MotorState.HOLD,
        )

    def stalled(self) -> bool:
        """
        Deteccion aproximada de estancamiento.
        Se considera estancado si hay estado de movimiento con velocidad ~0.
        """
        if self._model is None:
            return False
        moving = self._model.state in (
            MotorState.RUN,
            MotorState.RUN_TIME,
            MotorState.RUN_ANGLE,
        )
        return moving and abs(self._model.speed) < 1e-3

    def load(self) -> float:
        """Carga estimada del motor (%), aproximada por potencia interna."""
        if self._model is None:
            return 0.0
        return float(self._model.power)

    def settings(self, *args, **kwargs) -> tuple:
        """
        Compatibilidad de API.
        El control avanzado no esta modelado; se conserva firma.
        """
        _ = kwargs
        return tuple(args)

    def close(self) -> None:
        """Finaliza el recurso del motor (compatibilidad), equivalente a stop()."""
        self.stop()


# ---------------------------------------------------------------------------
# TouchSensor
# ---------------------------------------------------------------------------


class TouchSensor:
    """Sensor de contacto EV3 (pybricks.ev3devices.TouchSensor)."""

    def __init__(self, port: Port) -> None:
        ctx = PybricksContext.get_current()
        self._model = TouchSensorModel()
        ctx.engine.attach_sensor(str(port), self._model)

    def pressed(self) -> bool:
        """True si el sensor está siendo presionado."""
        return self._model.pressed()


# ---------------------------------------------------------------------------
# UltrasonicSensor
# ---------------------------------------------------------------------------


class UltrasonicSensor:
    """Sensor ultrasónico EV3 (pybricks.ev3devices.UltrasonicSensor)."""

    def __init__(self, port: Port) -> None:
        ctx = PybricksContext.get_current()
        self._model = UltrasonicSensorModel()
        ctx.engine.attach_sensor(str(port), self._model)

    def distance(self) -> int:
        """Distancia al objeto más cercano en mm."""
        return self._model.distance()

    def presence(self) -> bool:
        """True si detecta otro sensor ultrasónico activo (siempre False en sim)."""
        return self._model.presence()


# ---------------------------------------------------------------------------
# ColorSensor
# ---------------------------------------------------------------------------


class ColorSensor:
    """Sensor de color EV3 (pybricks.ev3devices.ColorSensor)."""

    def __init__(self, port: Port) -> None:
        ctx = PybricksContext.get_current()
        self._model = ColorSensorModel()
        ctx.engine.attach_sensor(str(port), self._model)
        self._detectable_colors: Optional[set[Color]] = None

    def color(self) -> Optional[Color]:
        """Color detectado como enum Color, o None."""
        surface_color = self._model.color()
        name = surface_color.name  # e.g. "BLACK", "WHITE"
        detected = SURFACE_TO_PYBRICKS.get(name, Color.NONE)
        if self._detectable_colors is None:
            return detected
        return detected if detected in self._detectable_colors else Color.NONE

    def reflection(self) -> int:
        """Luz reflejada: 0 (negro) … 100 (blanco)."""
        return self._model.reflection()

    def ambient(self) -> int:
        """Luz ambiente: siempre 0 en el simulador."""
        return self._model.ambient()

    def hsv(self, surface: bool = True) -> Color:
        """
        Compatibilidad API.
        Devuelve una aproximacion usando el color discreto detectado.
        """
        _ = surface
        return self.color() or Color.NONE

    def detectable_colors(self, colors: Optional[list[Color]] = None):
        """
        Obtiene o fija el conjunto de colores detectables.
        """
        if colors is None:
            if self._detectable_colors is None:
                return []
            return list(self._detectable_colors)
        self._detectable_colors = set(colors)
        return list(self._detectable_colors)


# ---------------------------------------------------------------------------
# GyroSensor
# ---------------------------------------------------------------------------


class GyroSensor:
    """Sensor giroscópico EV3 (pybricks.ev3devices.GyroSensor)."""

    def __init__(self, port: Port) -> None:
        ctx = PybricksContext.get_current()
        self._model = GyroSensorModel()
        ctx.engine.attach_sensor(str(port), self._model)

    def angle(self) -> int:
        """Ángulo acumulado en grados (0 al inicio, ±)."""
        return self._model.angle()

    def speed(self) -> int:
        """Velocidad angular en deg/s."""
        return self._model.speed()

    def reset_angle(self, angle: int = 0) -> None:
        """Resetea el ángulo al valor dado."""
        self._model.reset_angle(angle)


# ---------------------------------------------------------------------------
# InfraredSensor
# ---------------------------------------------------------------------------


class InfraredSensor:
    """Sensor infrarrojo EV3 (pybricks.ev3devices.InfraredSensor)."""

    def __init__(self, port: Port) -> None:
        ctx = PybricksContext.get_current()
        self._model = InfraredSensorModel()
        ctx.engine.attach_sensor(str(port), self._model)

    def distance(self) -> int:
        """Proximidad en 0-100 (100=muy cerca, 0=lejos o nada)."""
        return self._model.distance()

    def reflection(self) -> int:
        """
        Compatibilidad API de otras familias Pybricks.
        Se aproxima usando la misma lectura de proximidad IR.
        """
        return self._model.distance()

    def count(self) -> int:
        """Conteo de objetos (no modelado en EV3 actual)."""
        return 0

    def beacon(self, channel: int = 1):
        """
        Lectura del beacon IR.
        Devuelve (distance: int 0-100, heading: int -25..25).
        """
        ctx = PybricksContext.get_current()
        rx = ctx.engine.robot.pose.x
        ry = ctx.engine.robot.pose.y
        th = ctx.engine.robot.pose.theta
        return self._model.beacon(channel, ctx.engine.world, rx, ry, th)
