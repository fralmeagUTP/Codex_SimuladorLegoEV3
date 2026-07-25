"""
simulation_engine.py — Motor de simulación EV3 (50 Hz).

Responsabilidades (SAD §8):
  1. Consumir comandos de CommandQueue y aplicarlos a los modelos de dominio.
  2. Actualizar todos los modelos (motores, DriveBase, robot, sensores)
     en cada tick dt = 0.02 s.
  3. Detectar colisiones y señalarlas.
  4. Publicar eventos en EventBus (sensor_updated cada tick).
  5. Proveer StateSnapshot inmutable para la UI y la telemetría.

Uso:
    engine = SimulationEngine(config=SimEngineConfig())
    engine.start()      # arranca el loop de ticks vía tkinter.after() o thread
    engine.update(dt)   # también puede llamarse manualmente en tests

El Engine NO gestiona su propio thread; eso corresponde a RuntimeController
(Fase 4).  Aquí sólo se define la lógica pura update(dt).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from simulador_ev3.core.command_queue import CommandQueue, CommandType, SimulationCommand
from simulador_ev3.core.event_bus import (
    EVENT_SENSOR_UPDATED,
    EVENT_SIMULATION_STARTED,
    EVENT_SIMULATION_STOPPED,
    EventBus,
)
from simulador_ev3.core.simulation_profile import resolve_profile
from simulador_ev3.domain.brick.ev3brick_model import EV3BrickModel
from simulador_ev3.domain.brick.led_model import LedColor
from simulador_ev3.domain.robot.drivebase_model import AccelerationProfile, DriveBaseModel
from simulador_ev3.domain.robot.motor_model import MotorModel, MotorState, StopMode
from simulador_ev3.domain.robot.port_manager import DeviceCategory, PortManager
from simulador_ev3.domain.robot.robot_model import Pose, RobotModel
from simulador_ev3.domain.sensors.color_sensor_model import ColorSensorModel
from simulador_ev3.domain.sensors.gyro_sensor_model import GyroSensorModel
from simulador_ev3.domain.sensors.infrared_sensor_model import InfraredSensorModel
from simulador_ev3.domain.sensors.touch_sensor_model import TouchSensorModel
from simulador_ev3.domain.sensors.ultrasonic_sensor_model import UltrasonicSensorModel
from simulador_ev3.domain.world.world_model import WorldModel
from simulador_ev3.infrastructure.audio_output import create_audio_output

# ---------------------------------------------------------------------------
# Snapshot inmutable de estado completo
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RobotSnapshot:
    x_mm: float
    y_mm: float
    theta_deg: float


@dataclass(frozen=True)
class MotorSnapshot:
    port: str
    angle_deg: float
    speed_dps: float
    state: str


@dataclass(frozen=True)
class SensorSnapshot:
    port: str
    sensor_type: str
    data: dict  # valores específicos del sensor


@dataclass(frozen=True)
class StateSnapshot:
    """
    Foto inmutable del estado completo del simulador en un instante dado.
    La UI y la telemetría leen únicamente este objeto.
    """

    tick: int
    sim_time_s: float
    robot: RobotSnapshot
    motors: tuple[MotorSnapshot, ...]
    sensors: tuple[SensorSnapshot, ...]
    brick: dict  # to_dict() de EV3BrickModel
    colliding: bool


# ---------------------------------------------------------------------------
# Configuración del Engine
# ---------------------------------------------------------------------------


@dataclass
class SimEngineConfig:
    """Parámetros iniciales del simulador."""

    # Geometría del mundo (mm)
    world_width_mm: float = 2000.0
    world_height_mm: float = 2000.0

    # Posición inicial del robot
    robot_x0_mm: float = 200.0
    robot_y0_mm: float = 200.0
    robot_theta0_deg: float = 0.0

    # DriveBase — valores por defecto compatibles con Pybricks
    wheel_diameter_mm: float = 56.0
    axle_track_mm: float = 114.0
    straight_speed: float = 200.0  # mm/s
    straight_accel: float = 200.0  # mm/s²
    turn_rate: float = 90.0  # deg/s
    turn_accel: float = 90.0  # deg/s²

    # Radio del robot para detección de colisiones (mm)
    robot_radius_mm: float = 75.0
    simulation_profile: str = "ideal"
    calibration: dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Motor de simulación
# ---------------------------------------------------------------------------


class SimulationEngine:
    """
    Motor de simulación EV3.

    El Engine orquesta:
    - PortManager      — registro de dispositivos
    - RobotModel       — pose + DriveBase
    - Motores A-D      — acceso individual
    - EV3BrickModel    — LED, pantalla, altavoz, botones
    - WorldModel       — superficie, obstáculos, beacon
    - Sensores S1-S4   — modelos de dominio de cada sensor

    Internamente sólo expone update(dt) y la API de comandos/snapshot.
    El threading lo maneja RuntimeController (Fase 4).
    """

    TICK_RATE_HZ: float = 50.0
    DT: float = 1.0 / TICK_RATE_HZ  # 0.02 s

    def __init__(
        self,
        config: Optional[SimEngineConfig] = None,
        command_queue: Optional[CommandQueue] = None,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._cfg = config or SimEngineConfig()
        self._profile = resolve_profile(self._cfg.simulation_profile, self._cfg.calibration)
        self._queue = command_queue or CommandQueue()
        self._bus = event_bus or EventBus()

        # Estado interno
        self._tick: int = 0
        self._sim_time: float = 0.0
        self._running: bool = False
        self._colliding: bool = False
        self._drivebase_source: str = "idle"  # idle | command | tank

        # Última colisión bloqueante (para no mover el robot si hay colisión)
        self._collision_blocked: bool = False
        self._audio_output = create_audio_output()

        # --- Modelos de dominio ---
        self._build_models()

        # Tabla de handlers de comandos
        self._handlers: dict[CommandType, object] = {
            CommandType.MOTOR_RUN: self._handle_motor_run,
            CommandType.MOTOR_RUN_TIME: self._handle_motor_run_time,
            CommandType.MOTOR_RUN_ANGLE: self._handle_motor_run_angle,
            CommandType.MOTOR_STOP: self._handle_motor_stop,
            CommandType.MOTOR_BRAKE: self._handle_motor_brake,
            CommandType.MOTOR_HOLD: self._handle_motor_hold,
            CommandType.DB_DRIVE: self._handle_db_drive,
            CommandType.DB_STOP: self._handle_db_stop,
            CommandType.DB_STRAIGHT: self._handle_db_straight,
            CommandType.DB_TURN: self._handle_db_turn,
            CommandType.DB_SETTINGS: self._handle_db_settings,
            CommandType.LED_ON: self._handle_led_on,
            CommandType.LED_OFF: self._handle_led_off,
            CommandType.PLAY_SOUND: self._handle_play_sound,
            CommandType.DISPLAY_TEXT: self._handle_display_text,
            CommandType.SCREEN_CLEAR: self._handle_screen_clear,
            CommandType.SCREEN_PIXEL: self._handle_screen_pixel,
            CommandType.SCREEN_LINE: self._handle_screen_line,
            CommandType.SCREEN_CIRCLE: self._handle_screen_circle,
            CommandType.SCREEN_BOX: self._handle_screen_box,
        }

        # Comandos bloqueantes activos (esperando signal_done)
        self._pending_blocking: list[SimulationCommand] = []

    # ------------------------------------------------------------------
    # Construcción de modelos
    # ------------------------------------------------------------------

    def _build_models(self) -> None:
        cfg = self._cfg

        self._port_manager = PortManager()

        # Motores A-D
        self._motors: dict[str, MotorModel] = {}
        for port in ("A", "B", "C", "D"):
            m = MotorModel(port_name=port)
            self._motors[port] = m
            self._port_manager.register(port, m, DeviceCategory.MOTOR)

        # DriveBase (motores B y C por defecto en EV3 con oruga)
        profile = AccelerationProfile(
            straight_speed=cfg.straight_speed * self._profile.traction_scale,
            straight_acceleration=cfg.straight_accel,
            turn_rate=cfg.turn_rate * self._profile.traction_scale,
            turn_acceleration=cfg.turn_accel,
        )
        self._drivebase = DriveBaseModel(
            wheel_diameter_mm=cfg.wheel_diameter_mm,
            axle_track_mm=cfg.axle_track_mm,
            profile=profile,
        )

        # Robot (pose + DriveBase + PortManager)
        initial_pose = Pose(
            x=cfg.robot_x0_mm,
            y=cfg.robot_y0_mm,
            theta=math.radians(cfg.robot_theta0_deg),
        )
        self._robot = RobotModel(
            drivebase=self._drivebase,
            port_manager=self._port_manager,
            initial_pose=initial_pose,
        )

        # Ladrillo EV3
        self._brick = EV3BrickModel()

        # Mundo
        self._world = WorldModel(
            width_mm=cfg.world_width_mm,
            height_mm=cfg.world_height_mm,
        )

        # Sensores — se exponen como dict por puerto S1-S4
        # Por defecto ningún sensor está conectado (None)
        self._sensors: dict[str, Optional[object]] = {"S1": None, "S2": None, "S3": None, "S4": None}

    # ------------------------------------------------------------------
    # API externa
    # ------------------------------------------------------------------

    @property
    def command_queue(self) -> CommandQueue:
        return self._queue

    @property
    def event_bus(self) -> EventBus:
        return self._bus

    @property
    def world(self) -> WorldModel:
        return self._world

    def set_world(self, world: WorldModel) -> None:
        """Reemplaza el mundo activo de la simulación."""
        self._world = world

    @property
    def robot(self) -> RobotModel:
        return self._robot

    @property
    def tick(self) -> int:
        return self._tick

    @property
    def sim_time_s(self) -> float:
        return self._sim_time

    @property
    def drivebase_profile(self) -> AccelerationProfile:
        """Perfil cinemático efectivo después de aplicar el perfil de simulación."""
        return self._drivebase.profile

    def attach_sensor(
        self,
        port: str,
        sensor: "TouchSensorModel | UltrasonicSensorModel | ColorSensorModel | GyroSensorModel | InfraredSensorModel",
    ) -> None:
        """Conecta un modelo de sensor al puerto S1-S4."""
        if port not in self._sensors:
            raise ValueError(f"Puerto de sensor inválido: '{port}'. Use S1-S4.")
        self._sensors[port] = sensor
        if isinstance(sensor, UltrasonicSensorModel):
            sensor.noise_mm = self._profile.ultrasonic_noise_mm
        elif isinstance(sensor, ColorSensorModel):
            sensor.reflection_noise = self._profile.color_reflection_noise
        self._port_manager.register(port, sensor, DeviceCategory.SENSOR)

    def detach_sensor(self, port: str) -> None:
        """Desconecta el sensor del puerto."""
        if port not in self._sensors:
            raise ValueError(f"Puerto de sensor inválido: '{port}'.")
        self._sensors[port] = None
        # No se elimina del port_manager para no complicar la API pública

    def notify_started(self) -> None:
        """RuntimeController llama aquí al iniciar la simulación."""
        self._running = True
        self._bus.publish(EVENT_SIMULATION_STARTED, {})

    def notify_stopped(self, reason: str = "normal") -> None:
        """RuntimeController llama aquí al detener la simulación."""
        self._running = False
        self._bus.publish(EVENT_SIMULATION_STOPPED, {"reason": reason})
        # Señalar todos los bloqueantes pendientes para no dejar el script colgado
        for cmd in self._pending_blocking:
            cmd.signal_done()
        self._pending_blocking.clear()

    # ------------------------------------------------------------------
    # Tick principal
    # ------------------------------------------------------------------

    def update(self, dt: float = DT) -> StateSnapshot:
        """
        Ejecuta un tick de simulación.

        Orden de operaciones (SAD §11):
          1. Consumir y aplicar comandos de la cola.
          2. Actualizar modelos de movimiento (DriveBase, motores libres).
          3. Integrar pose del robot.
          4. Detectar colisiones; revertir si colisiona.
          5. Actualizar sensores.
          6. Actualizar ladrillo (altavoz).
          7. Señalar comandos bloqueantes completados.
          8. Publicar eventos.
          9. Construir y devolver snapshot.
        """
        # 1. Comandos
        self._process_commands(self._queue.drain())

        # 2. Actualizar motores individuales
        self._update_motors(dt)

        # 3. Sincronización opcional tipo tanque desde motores A/C o B/C
        self._sync_tank_drive_from_motors()
        self._sync_motors_from_drivebase(dt)

        # 4. Movimiento del robot
        prev_x = self._robot.pose.x
        prev_y = self._robot.pose.y
        self._robot.update(dt)

        # 5. Colisión
        rx, ry = self._robot.pose.x, self._robot.pose.y
        self._colliding = self._world.is_colliding(rx, ry, self._cfg.robot_radius_mm)
        if self._colliding:
            # Revertir posición pero mantener ángulo (choque frontal)
            self._robot.pose.x = prev_x
            self._robot.pose.y = prev_y
            # Parar el drivebase para que no siga acumulando delta
            self._drivebase.cmd_stop()
            self._drivebase_source = "idle"

        # 6. Sensores
        self._update_sensors(dt)

        # 7. Ladrillo
        self._brick.update(dt)

        # 8. Señalar bloqueantes completados
        self._check_blocking_completion()

        # 9. Publicar sensor_updated
        self._publish_sensor_events()

        # 10. Snapshot
        self._tick += 1
        self._sim_time += dt
        return self._build_snapshot()

    # ------------------------------------------------------------------
    # Procesado de comandos
    # ------------------------------------------------------------------

    def _process_commands(self, commands: list[SimulationCommand]) -> None:
        for cmd in commands:
            handler = self._handlers.get(cmd.cmd_type)
            if handler:
                handler(cmd)  # type: ignore[operator]
                if cmd.blocking:
                    self._pending_blocking.append(cmd)

    # Motor individual --------------------------------------------------

    def _handle_motor_run(self, cmd: SimulationCommand) -> None:
        motor = self._get_motor(cmd.port)
        if motor:
            motor.cmd_run(cmd.params["speed"])

    def _handle_motor_run_time(self, cmd: SimulationCommand) -> None:
        motor = self._get_motor(cmd.port)
        if motor:
            stop_mode = self._parse_stop_mode(cmd.params.get("stop_mode", "BRAKE"))
            motor.cmd_run_time(
                speed=cmd.params["speed"],
                time_ms=cmd.params["time_ms"],
                then=stop_mode,
            )

    def _handle_motor_run_angle(self, cmd: SimulationCommand) -> None:
        motor = self._get_motor(cmd.port)
        if motor:
            stop_mode = self._parse_stop_mode(cmd.params.get("stop_mode", "BRAKE"))
            motor.cmd_run_angle(
                speed=cmd.params["speed"],
                rotation_angle=cmd.params["angle_deg"],
                then=stop_mode,
            )

    def _handle_motor_stop(self, cmd: SimulationCommand) -> None:
        motor = self._get_motor(cmd.port)
        if motor:
            motor.cmd_stop()

    def _handle_motor_brake(self, cmd: SimulationCommand) -> None:
        motor = self._get_motor(cmd.port)
        if motor:
            motor.cmd_brake()

    def _handle_motor_hold(self, cmd: SimulationCommand) -> None:
        motor = self._get_motor(cmd.port)
        if motor:
            motor.cmd_hold()

    # DriveBase ---------------------------------------------------------

    def _handle_db_drive(self, cmd: SimulationCommand) -> None:
        self._drivebase.cmd_drive(
            speed_mm_s=cmd.params["speed"],
            turn_rate_deg_s=cmd.params["turn_rate"],
        )
        self._drivebase_source = "command"

    def _handle_db_stop(self, cmd: SimulationCommand) -> None:
        stop_mode = self._parse_stop_mode(cmd.params.get("stop_mode", "COAST"))
        if stop_mode == StopMode.HOLD:
            self._drivebase.cmd_hold()
        elif stop_mode == StopMode.BRAKE:
            self._drivebase.cmd_brake()
        else:
            self._drivebase.cmd_stop()
        self._drivebase_source = "idle"

    def _handle_db_straight(self, cmd: SimulationCommand) -> None:
        self._drivebase.cmd_straight(
            cmd.params["distance_mm"], self._parse_stop_mode(cmd.params.get("stop_mode", "HOLD"))
        )
        self._drivebase_source = "command"

    def _handle_db_turn(self, cmd: SimulationCommand) -> None:
        self._drivebase.cmd_turn(cmd.params["angle_deg"], self._parse_stop_mode(cmd.params.get("stop_mode", "HOLD")))
        self._drivebase_source = "command"

    def _handle_db_settings(self, cmd: SimulationCommand) -> None:
        self._drivebase.cmd_settings(
            straight_speed=cmd.params["straight_speed"],
            straight_acceleration=cmd.params["straight_acceleration"],
            turn_rate=cmd.params["turn_rate"],
            turn_acceleration=cmd.params["turn_acceleration"],
        )

    # LED ---------------------------------------------------------------

    def _handle_led_on(self, cmd: SimulationCommand) -> None:
        color_map = {
            "RED": LedColor.RED,
            "GREEN": LedColor.GREEN,
            "ORANGE": LedColor.ORANGE,
            "YELLOW": LedColor.YELLOW,
        }
        color = color_map.get(cmd.params.get("color", "GREEN"), LedColor.GREEN)
        self._brick.light.cmd_on(color)

    def _handle_led_off(self, cmd: SimulationCommand) -> None:
        self._brick.light.cmd_off()

    # Altavoz -----------------------------------------------------------

    def _handle_play_sound(self, cmd: SimulationCommand) -> None:
        frequency = int(cmd.params.get("frequency", 440))
        duration_ms = int(cmd.params.get("duration_ms", 100))
        volume = int(cmd.params.get("volume", 50))

        self._brick.speaker.cmd_beep(
            frequency=frequency,
            duration_ms=duration_ms,
            volume=volume,
        )
        try:
            self._audio_output.play_beep(frequency, duration_ms, volume)
        except Exception:
            pass

    # Pantalla ----------------------------------------------------------

    def _handle_display_text(self, cmd: SimulationCommand) -> None:
        text = str(cmd.params.get("text", ""))
        self._brick.screen.cmd_print(text)

    def _handle_screen_clear(self, cmd: SimulationCommand) -> None:
        self._brick.screen.cmd_clear()

    def _handle_screen_pixel(self, cmd: SimulationCommand) -> None:
        self._brick.screen.cmd_draw_pixel(
            x=int(cmd.params.get("x", 0)),
            y=int(cmd.params.get("y", 0)),
            color=int(cmd.params.get("color", 1)),
        )

    def _handle_screen_line(self, cmd: SimulationCommand) -> None:
        self._brick.screen.cmd_draw_line(
            x1=int(cmd.params.get("x1", 0)),
            y1=int(cmd.params.get("y1", 0)),
            x2=int(cmd.params.get("x2", 0)),
            y2=int(cmd.params.get("y2", 0)),
            color=int(cmd.params.get("color", 1)),
        )

    def _handle_screen_circle(self, cmd: SimulationCommand) -> None:
        self._brick.screen.cmd_draw_circle(
            x=int(cmd.params.get("x", 0)),
            y=int(cmd.params.get("y", 0)),
            r=int(cmd.params.get("r", 0)),
            color=int(cmd.params.get("color", 1)),
            fill=bool(cmd.params.get("fill", False)),
        )

    def _handle_screen_box(self, cmd: SimulationCommand) -> None:
        self._brick.screen.cmd_draw_box(
            x=int(cmd.params.get("x", 0)),
            y=int(cmd.params.get("y", 0)),
            w=int(cmd.params.get("w", 0)),
            h=int(cmd.params.get("h", 0)),
            color=int(cmd.params.get("color", 1)),
            fill=bool(cmd.params.get("fill", False)),
        )

    # ------------------------------------------------------------------
    # Sensores
    # ------------------------------------------------------------------

    def _update_sensors(self, dt: float) -> None:
        rx = self._robot.pose.x
        ry = self._robot.pose.y
        theta = self._robot.pose.theta  # radianes

        for _port, sensor in self._sensors.items():
            if sensor is None:
                continue
            if isinstance(sensor, TouchSensorModel):
                sensor.update(rx, ry, theta, self._world)
            elif isinstance(sensor, UltrasonicSensorModel):
                sensor.update(rx, ry, theta, self._world)
            elif isinstance(sensor, ColorSensorModel):
                sensor.update(rx, ry, theta, self._world)
            elif isinstance(sensor, GyroSensorModel):
                sensor.update(self._robot.pose.theta, dt)
            elif isinstance(sensor, InfraredSensorModel):
                sensor.update(rx, ry, theta, self._world)

    def _publish_sensor_events(self) -> None:
        for port, sensor in self._sensors.items():
            if sensor is None:
                continue
            sensor_type = type(sensor).__name__
            if hasattr(sensor, "to_dict"):
                data = sensor.to_dict()
            else:
                data = {}
            self._bus.publish(
                EVENT_SENSOR_UPDATED,
                {"port": port, "sensor_type": sensor_type, "data": data},
            )

    def _update_motors(self, dt: float) -> None:
        """Avanza el estado temporal de todos los motores A-D."""
        for motor in self._motors.values():
            motor.update(dt)

    def _sync_tank_drive_from_motors(self) -> None:
        """
        Emula conducción diferencial usando motores individuales.

        Compatibilidad para scripts de ejemplo basados en:
            left = Motor(Port.A); right = Motor(Port.C)
            left.run(...); right.run(...)

        También soporta el par B/C.
        """
        if self._drivebase_source == "command":
            return

        pair = self._select_active_tank_pair()
        if pair is None:
            if self._drivebase_source == "tank":
                self._drivebase.cmd_stop()
                self._drivebase_source = "idle"
            return

        left_motor, right_motor = pair

        mm_per_deg = math.pi * self._drivebase.wheel_diameter_mm / 360.0
        vl_mm_s = left_motor.speed * mm_per_deg
        vr_mm_s = right_motor.speed * mm_per_deg

        linear_mm_s = (vl_mm_s + vr_mm_s) / 2.0
        omega_rad_s = (vr_mm_s - vl_mm_s) / self._drivebase.axle_track_mm
        turn_rate_deg_s = math.degrees(omega_rad_s)

        if abs(linear_mm_s) < 1e-9 and abs(turn_rate_deg_s) < 1e-9:
            if self._drivebase_source == "tank":
                self._drivebase.cmd_stop()
                self._drivebase_source = "idle"
            return

        self._drivebase.cmd_drive(linear_mm_s, turn_rate_deg_s)
        self._drivebase_source = "tank"

    def _sync_motors_from_drivebase(self, dt: float) -> None:
        """
        Sincroniza la telemetria de motores cuando el movimiento viene de
        comandos de DriveBase (drive/straight/turn).
        """
        if self._drivebase_source != "command":
            return

        left = self._motors.get("B")
        right = self._motors.get("C")
        if left is None or right is None:
            return

        if self._drivebase.state.name == "IDLE":
            left._speed = 0.0
            right._speed = 0.0
            left.state = MotorState.IDLE
            right.state = MotorState.IDLE
            return

        left_dps, right_dps = self._drivebase.wheel_speeds_deg_s()
        left._speed = float(left_dps)
        right._speed = float(right_dps)
        left._angle += left._speed * dt
        right._angle += right._speed * dt
        left.state = MotorState.RUN
        right.state = MotorState.RUN

    def _select_active_tank_pair(self) -> Optional[tuple[MotorModel, MotorModel]]:
        """Retorna el primer par activo de motores para conducción tipo tanque."""
        for left_port, right_port in (("A", "C"), ("B", "C")):
            left = self._motors.get(left_port)
            right = self._motors.get(right_port)
            if left is None or right is None:
                continue

            left_active = left.state not in (MotorState.IDLE, MotorState.HOLD, MotorState.BRAKE)
            right_active = right.state not in (MotorState.IDLE, MotorState.HOLD, MotorState.BRAKE)
            if left_active or right_active:
                return left, right

        return None

    # ------------------------------------------------------------------
    # Comandos bloqueantes completados
    # ------------------------------------------------------------------

    def _check_blocking_completion(self) -> None:
        """
        Señala el done_event de los comandos bloqueantes cuyo movimiento
        asociado haya completado.

        Criterios:
        - DB_STRAIGHT / DB_TURN: DriveBase en estado IDLE
        - MOTOR_RUN_TIME / MOTOR_RUN_ANGLE: Motor en estado IDLE/BRAKE/HOLD
        """
        still_pending: list[SimulationCommand] = []
        for cmd in self._pending_blocking:
            completed = self._is_cmd_complete(cmd)
            if completed:
                cmd.signal_done()
            else:
                still_pending.append(cmd)
        self._pending_blocking = still_pending

    def _is_cmd_complete(self, cmd: SimulationCommand) -> bool:
        from simulador_ev3.domain.robot.drivebase_model import DriveState
        from simulador_ev3.domain.robot.motor_model import MotorState

        if cmd.cmd_type in (CommandType.DB_STRAIGHT, CommandType.DB_TURN):
            return self._drivebase.state in (DriveState.IDLE, DriveState.BRAKE, DriveState.HOLD)

        if cmd.cmd_type in (CommandType.MOTOR_RUN_TIME, CommandType.MOTOR_RUN_ANGLE):
            motor = self._get_motor(cmd.port)
            if motor is None:
                return True
            return motor.state in (MotorState.IDLE, MotorState.BRAKE, MotorState.HOLD)

        return True  # comandos no bloqueantes nunca deberían llegar aquí

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def _build_snapshot(self) -> StateSnapshot:
        pose = self._robot.pose
        theta_deg = math.degrees(pose.theta)

        motor_snaps = tuple(
            MotorSnapshot(
                port=port,
                angle_deg=motor.angle,
                speed_dps=motor.speed,
                state=motor.state.name,
            )
            for port, motor in self._motors.items()
        )

        sensor_snaps: list[SensorSnapshot] = []
        for port, sensor in self._sensors.items():
            if sensor is None:
                continue
            data = sensor.to_dict() if hasattr(sensor, "to_dict") else {}
            sensor_snaps.append(
                SensorSnapshot(
                    port=port,
                    sensor_type=type(sensor).__name__,
                    data=data,
                )
            )

        return StateSnapshot(
            tick=self._tick,
            sim_time_s=self._sim_time,
            robot=RobotSnapshot(
                x_mm=pose.x,
                y_mm=pose.y,
                theta_deg=theta_deg,
            ),
            motors=motor_snaps,
            sensors=tuple(sensor_snaps),
            brick=self._brick.to_dict(),
            colliding=self._colliding,
        )

    def snapshot(self) -> StateSnapshot:
        """Devuelve el estado actual sin avanzar el reloj de simulación."""
        return self._build_snapshot()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_motor(self, port: Optional[str]) -> Optional[MotorModel]:
        if port is None:
            return None
        return self._motors.get(port.upper())

    @staticmethod
    def _parse_stop_mode(name: str) -> StopMode:
        mapping = {
            "COAST": StopMode.COAST,
            "BRAKE": StopMode.BRAKE,
            "HOLD": StopMode.HOLD,
        }
        return mapping.get(name.upper(), StopMode.BRAKE)

    def reset(self) -> None:
        """
        Reinicia el motor al estado inicial (misma config).
        Preserva los suscriptores del EventBus.
        """
        self._queue.clear()
        for cmd in self._pending_blocking:
            cmd.signal_done()
        self._pending_blocking.clear()
        self._tick = 0
        self._sim_time = 0.0
        self._colliding = False
        self._build_models()
