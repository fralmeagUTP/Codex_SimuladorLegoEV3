"""Adaptador de casos de uso de simulación para la interfaz Tkinter."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from simulador_ev3.application.session_contract import SessionEvent
from simulador_ev3.application.simulation_service import SimulationService
from simulador_ev3.application.simulation_session_port import SimulationSessionPort
from simulador_ev3.application.snapshot_dto import SnapshotDTO
from simulador_ev3.core.simulation_engine import SimEngineConfig
from simulador_ev3.runtime.execution_policy import ExecutionPolicy
from simulador_ev3.runtime.isolated_worker import IsolatedRuntimeWorker, worker_isolation_enabled


class DesktopSessionAdapter(SimulationSessionPort):
    """Fachada de UI local equivalente a una sesión de simulación web.

    Encapsula el servicio de aplicación para que la interfaz de escritorio no
    conozca la construcción ni el ciclo interno del runtime.
    """

    def __init__(self, config: SimEngineConfig) -> None:
        self._service = SimulationService(config=config, policy=ExecutionPolicy())
        self._worker: IsolatedRuntimeWorker | None = None
        self._worker_status = "created"
        if worker_isolation_enabled():
            self._start_worker()

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
                return self._worker.send(command, payload)
            except RuntimeError as exc:
                if "no iniciado" not in str(exc):
                    raise
                self._start_worker()
                return self._worker.send(command, payload)
        return None

    def load_script(self, source: str) -> None:
        self._service.load_script(source)
        self._mirror("load_script", {"source": source})

    def start(self, *, debug: bool = False, step_mode: bool = False) -> None:
        if self._worker is None:
            self._service.start(debug=debug, step_mode=step_mode)
        else:
            self._worker_status = "running"
        self._mirror("start", {"debug": debug, "step_mode": step_mode})

    def pause(self) -> None:
        if self._worker is None:
            self._service.pause()
        else:
            self._worker_status = "paused"
        self._mirror("pause")

    def resume(self) -> None:
        if self._worker is None:
            self._service.resume()
        else:
            self._worker_status = "running"
        self._mirror("resume")

    def stop(self, reason: str = "manual_stop") -> None:
        if self._worker is None:
            self._service.stop(reason=reason)
        else:
            self._worker_status = "stopped"
        self._mirror("stop")

    def reset(self) -> str | None:
        self._service.reset()
        return self._mirror("reset")

    def current_snapshot(self) -> SnapshotDTO | None:
        """Estado local de referencia para sincronizar la UI tras un reinicio."""
        return self._service.current_snapshot()

    def set_robot_start(self, x_mm: float, y_mm: float, theta_deg: float | None = None) -> None:
        self._service.set_robot_start(x_mm, y_mm, theta_deg)
        self._mirror("set_robot_start", {"x_mm": x_mm, "y_mm": y_mm, "theta_deg": theta_deg})

    def set_max_runtime_s(self, max_runtime_s: float) -> None:
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
        for event in events:
            if event.get("type") == "snapshot" and isinstance(event.get("payload"), dict):
                self._service.record_external_snapshot(SnapshotDTO(event["payload"]))
            if event.get("type") == "status" and isinstance(event.get("payload"), dict):
                candidate = event["payload"].get("status")
                if isinstance(candidate, str):
                    self._worker_status = candidate
            if event.get("type") == "error" and isinstance(event.get("payload"), dict):
                message = str(event["payload"].get("error", event["payload"].get("message", ""))).lower()
                self._worker_status = "timed_out" if "tiempo maximo" in message else "error"
        return events
