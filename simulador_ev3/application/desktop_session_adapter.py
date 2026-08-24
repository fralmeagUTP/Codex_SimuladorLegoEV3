"""Adaptador de casos de uso de simulación para la interfaz Tkinter."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from simulador_ev3.application.interface_ports import (
    LearningPort,
    LearningState,
    ObservabilityPort,
    ObservabilitySnapshot,
    PresentationPort,
    PresentationState,
)
from simulador_ev3.application.session_contract import SessionEvent
from simulador_ev3.application.simulation_service import SimulationService
from simulador_ev3.application.simulation_session_port import SimulationSessionPort
from simulador_ev3.application.snapshot_dto import SnapshotDTO
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.runtime.execution_policy import ExecutionPolicy
from simulador_ev3.runtime.isolated_worker import IsolatedRuntimeWorker, worker_isolation_enabled
from simulador_ev3.shared.interface_catalog import (
    controls_for_status,
    is_supported_runtime_limit,
    message_for_status,
)
from simulador_ev3.shared.learning_catalog import initial_learning_route


class DesktopSessionAdapter(SimulationSessionPort, PresentationPort, LearningPort, ObservabilityPort):
    """Fachada de UI local equivalente a una sesión de simulación web.

    Encapsula el servicio de aplicación para que la interfaz de escritorio no
    conozca la construcción ni el ciclo interno del runtime.
    """

    def __init__(self, config: SimEngineConfig) -> None:
        self.session_id = "desktop-local"
        self._service = SimulationService(config=config, policy=ExecutionPolicy())
        self._worker: IsolatedRuntimeWorker | None = None
        self._worker_status = "created"
        self._last_command_id: str | None = None
        self._status_callback = None
        self._error_callback = None
        self._active_mission = None
        self._latest_learning_result: dict | None = None
        # La interfaz registra su callback en el adaptador. Mantener este
        # intermediario permite que el contrato PresentationPort se actualice
        # tambien en modo local, sin depender de que exista un worker.
        self._service.set_status_callback(self._on_service_status)
        self._service.set_error_callback(self._on_service_error)
        if worker_isolation_enabled():
            self._start_worker()

    def _on_service_status(self, status: str) -> None:
        normalized = {
            "started": "running",
            "resumed": "running",
            "reset": "created",
            "world_loaded": "created",
        }.get(status, status)
        self._worker_status = normalized
        if self._status_callback is not None:
            self._status_callback(status)

    def set_status_callback(self, callback) -> None:
        """Registra un callback de UI sin perder el estado del adaptador."""

        self._status_callback = callback

    def _on_service_error(self, error: dict) -> None:
        """Normaliza errores locales como estado terminal de sesión.

        El worker aislado ya produce eventos IPC de error. En modo local, el
        servicio invoca este callback: ambos caminos deben dejar de presentar
        ``running`` antes de notificar a la interfaz.
        """

        message = str(error.get("error", error.get("message", ""))).lower()
        self._worker_status = "timed_out" if "tiempo maximo" in message else "error"
        if self._error_callback is not None:
            self._error_callback(error)

    def set_error_callback(self, callback) -> None:
        """Registra el receptor de errores conservando el contrato de sesión."""

        self._error_callback = callback

    def _start_worker(self) -> None:
        """Crea y configura el worker de escritorio, incluso tras una caída."""
        self._worker = IsolatedRuntimeWorker("desktop-shadow")
        self._worker.start()
        self._worker.receive()
        self._worker.send(
            "initialize",
            {
                "execution_policy": {
                    "max_runtime_s": self._service.max_runtime_s,
                    "max_memory_mb": 256,
                    "max_cpu_s": 300,
                },
                "engine_config": asdict(self._service.engine_config),
            },
        )
        self._worker.receive()

    @property
    def engine(self):
        return self._service.engine

    @property
    def is_running(self) -> bool:
        return self._worker_status == "running" if self._worker is not None else self._service.is_running

    @property
    def is_paused(self) -> bool:
        return self._worker_status == "paused" if self._worker is not None else self._service.is_paused

    @property
    def worker_enabled(self) -> bool:
        return self._worker is not None

    def __getattr__(self, name: str):
        """Delega los casos de uso publicados por SimulationService durante la migración."""
        return getattr(self._service, name)

    def debug_configuration(self) -> dict[str, object]:
        """Expone la configuración de depuración como contrato de UI local."""
        return self._service.debug_configuration

    @property
    def engine_config(self) -> SimEngineConfig:
        return self._service.engine_config

    def world_visual_data(self) -> dict:
        return self._service.world_visual_data()

    def _mirror(self, command: str, payload: dict | None = None) -> str | None:
        if self._worker is not None:
            try:
                self._last_command_id = self._worker.send(command, payload)
                return self._last_command_id
            except RuntimeError as exc:
                if "no iniciado" not in str(exc):
                    raise
                self._start_worker()
                self._last_command_id = self._worker.send(command, payload)
                return self._last_command_id
        return None

    def load_script(self, source: str) -> None:
        self._service.load_script(source)
        self._worker_status = "ready"
        self._mirror("load_script", {"source": source})

    def start(self, *, debug: bool = False, step_mode: bool = False) -> None:
        self._worker_status = "running"
        if self._worker is None:
            self._service.start(debug=debug, step_mode=step_mode)
        self._mirror("start", {"debug": debug, "step_mode": step_mode})

    def pause(self) -> None:
        self._worker_status = "paused"
        if self._worker is None:
            self._service.pause()
        self._mirror("pause")

    def resume(self) -> None:
        self._worker_status = "running"
        if self._worker is None:
            self._service.resume()
        self._mirror("resume")

    def stop(self, reason: str = "manual_stop") -> None:
        self._worker_status = "stopped"
        if self._worker is None:
            self._service.stop(reason=reason)
        self._mirror("stop")

    def reset(self) -> str | None:
        self._service.reset()
        self._worker_status = "created"
        return self._mirror("reset")

    def current_snapshot(self) -> SnapshotDTO | None:
        """Estado local de referencia para sincronizar la UI tras un reinicio."""
        return self._service.current_snapshot()

    def presentation_state(self) -> PresentationState:
        status = "paused" if self.is_paused else "running" if self.is_running else self._worker_status
        return PresentationState(
            session_id=self.session_id,
            status=status,
            controls=controls_for_status(status),
            message=message_for_status(status),
        )

    def learning_state(self) -> LearningState:
        route = initial_learning_route()
        mission = self._active_mission
        result = self._latest_learning_result
        completed = bool(result and result.get("result", {}).get("passed")) or (
            mission is None and self.presentation_state().status == "finished"
        )
        return LearningState(
            session_id=self.session_id,
            activity_id=getattr(mission, "identifier", route.identifier),
            objective=getattr(mission, "title", route.objective),
            next_step=route.practice,
            result="Actividad completada." if completed else None,
            progress_current=1 if completed else 0,
            progress_total=1,
        )

    def activate_mission(self, mission) -> None:
        """Conserva el contexto pedagógico al activar una misión local."""

        self._active_mission = mission
        self._latest_learning_result = None
        self._service.activate_mission(mission)

    def complete_active_mission(self, outcome: str) -> dict | None:
        """Actualiza el resultado pedagógico sin exponer el servicio interno."""

        result = self._service.complete_active_mission(outcome)
        if result is not None:
            self._latest_learning_result = result
        return result

    def observability_snapshot(self) -> ObservabilitySnapshot:
        snapshot = self.current_snapshot()
        return ObservabilitySnapshot(
            session_id=self.session_id,
            command_id=self._last_command_id,
            worker_id="desktop-shadow" if self._worker is not None else None,
            status=self.presentation_state().status,
            tick=snapshot.tick if snapshot is not None else None,
            simulation_time_s=snapshot.sim_time_s if snapshot is not None else None,
        )

    def set_robot_start(self, x_mm: float, y_mm: float, theta_deg: float | None = None) -> None:
        self._service.set_robot_start(x_mm, y_mm, theta_deg)
        self._mirror("set_robot_start", {"x_mm": x_mm, "y_mm": y_mm, "theta_deg": theta_deg})

    def set_max_runtime_s(self, max_runtime_s: float) -> None:
        if not is_supported_runtime_limit(max_runtime_s):
            raise ValueError("El tiempo maximo debe ser 30, 60, 120, 300 o 0 (sin limite).")
        self._service.set_max_runtime_s(max_runtime_s)
        self._mirror("set_max_runtime", {"max_runtime_s": float(max_runtime_s)})

    @property
    def max_runtime_s(self) -> float:
        return self._service.max_runtime_s

    def load_world_file(self, path: str | Path) -> None:
        source = Path(path).read_text(encoding="utf-8")
        self._service.load_world_file(path)
        self._mirror("load_world", {"source": source})

    def load_blank_world(self, width_mm: float | None = None, height_mm: float | None = None) -> None:
        self._service.load_blank_world(width_mm=width_mm, height_mm=height_mm)
        self._mirror(
            "load_blank_world",
            {
                "width_mm": width_mm if width_mm is not None else 3000.0,
                "height_mm": height_mm if height_mm is not None else 3000.0,
            },
        )

    def set_simulation_profile(self, profile: str, calibration: dict[str, float] | None = None) -> None:
        self._service.set_simulation_profile(profile, calibration)
        self._mirror("set_simulation_profile", {"profile": profile, "calibration": calibration or {}})

    def set_debug_breakpoints(self, breakpoints: set[int]) -> None:
        self._service.set_debug_breakpoints(breakpoints)
        self._mirror(
            "set_debug", {"breakpoints": sorted(breakpoints), "watches": self._service.debug_configuration["watches"]}
        )

    def set_debug_watches(self, watches: list[str]) -> None:
        self._service.set_debug_watches(watches)
        self._mirror(
            "set_debug",
            {"breakpoints": self._service.debug_configuration["breakpoints"], "watches": list(watches)},
        )

    def debug_continue(self) -> None:
        if self._worker is None:
            self._service.debug_continue()
        self._mirror("debug_continue")

    def debug_step(self) -> None:
        if self._worker is None:
            self._service.debug_step()
        self._mirror("debug_step")

    def close(self) -> None:
        if self._worker is not None:
            self._worker.close()
        self._service.stop()

    def drain_worker_events(self) -> list[dict]:
        raw_events = self._worker.drain_events() if self._worker is not None else []
        events = [SessionEvent.from_dict(event).to_dict() for event in raw_events]
        terminal_status: str | None = None
        for event in events:
            if event.get("type") == "snapshot" and isinstance(event.get("payload"), dict):
                self._service.record_external_snapshot(SnapshotDTO(event["payload"]))
            if event.get("type") == "status" and isinstance(event.get("payload"), dict):
                candidate = event["payload"].get("status")
                if isinstance(candidate, str):
                    self._worker_status = candidate
            if event.get("type") == "error" and isinstance(event.get("payload"), dict):
                message = str(event["payload"].get("error", event["payload"].get("message", ""))).lower()
                # Un lote IPC puede traer primero ``running`` y luego el error
                # terminal del mismo comando. El terminal siempre prevalece;
                # de otro modo la UI queda como Ejecutando aunque el programa
                # ya falló en el worker.
                terminal_status = "timed_out" if "tiempo maximo" in message else "error"
        if terminal_status is not None:
            self._worker_status = terminal_status
        return events
