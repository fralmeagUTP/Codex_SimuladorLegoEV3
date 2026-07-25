"""Worker IPC aislado, activable gradualmente sin sustituir aún el runtime actual."""

from __future__ import annotations

import builtins
import ctypes
import io
import multiprocessing as mp
import os
import queue
import socket
import sys
import tempfile
import time
import tracemalloc
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

IPC_PROTOCOL_VERSION = 1


class WorkerNetworkDisabled(OSError):
    """Señala un intento de red desde el proceso de scripts aislado."""


@dataclass(frozen=True)
class WorkerResourcePolicy:
    max_runtime_s: float
    max_memory_mb: int
    max_cpu_s: float

    @classmethod
    def from_payload(cls, payload: object) -> "WorkerResourcePolicy":
        if not isinstance(payload, dict):
            raise ValueError("execution_policy debe ser un objeto")
        policy = cls(
            max_runtime_s=float(payload.get("max_runtime_s", 0)),
            max_memory_mb=int(payload.get("max_memory_mb", 0)),
            max_cpu_s=float(payload.get("max_cpu_s", 0)),
        )
        if policy.max_runtime_s <= 0 or policy.max_memory_mb <= 0 or policy.max_cpu_s <= 0:
            raise ValueError("Los límites del worker deben ser positivos")
        return policy


def _disable_network() -> None:
    def denied_socket(*_args, **_kwargs):
        raise WorkerNetworkDisabled("La red está deshabilitada en el worker aislado")

    setattr(socket, "socket", denied_socket)  # noqa: B010 - frontera deliberada del sandbox


def _sanitize_worker_environment() -> tuple[str, ...]:
    """Elimina secretos heredados antes de aceptar codigo de usuario.

    El proceso conserva las variables necesarias del sistema y del interprete,
    pero no credenciales comunes que el proceso anfitrion pudiera tener.
    """

    removed: list[str] = []
    sensitive_fragments = ("TOKEN", "SECRET", "PASSWORD", "API_KEY", "ACCESS_KEY", "PRIVATE_KEY")
    protected_names = {"SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "PATH", "PYTHONHOME", "PYTHONPATH"}
    for name in tuple(os.environ):
        normalized = name.upper()
        if name in protected_names:
            continue
        if any(fragment in normalized for fragment in sensitive_fragments):
            os.environ.pop(name, None)
            removed.append(name)
    return tuple(sorted(removed))


def _process_is_elevated() -> bool:
    """Indica si el worker conserva privilegios administrativos del anfitrion."""

    if sys.platform.startswith("win"):
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except (AttributeError, OSError):
            return True
    return hasattr(os, "geteuid") and os.geteuid() == 0


def _restrict_open_to_workdir(workdir: str) -> None:
    original_open = builtins.open
    original_io_open = io.open
    original_os_open = os.open
    original_remove = os.remove
    original_replace = os.replace
    original_rename = os.rename
    root = os.path.realpath(workdir)

    def is_permitted(path) -> bool:
        try:
            candidate = os.path.realpath(os.fspath(path))
            return os.path.commonpath((root, candidate)) == root
        except (TypeError, ValueError):
            return False

    def guarded_open(file, *args, **kwargs):
        if not is_permitted(file):
            raise PermissionError("El filesystem del worker está restringido al directorio temporal")
        return original_open(file, *args, **kwargs)

    def guarded_io_open(file, *args, **kwargs):
        if not is_permitted(file):
            raise PermissionError("El filesystem del worker está restringido al directorio temporal")
        return original_io_open(file, *args, **kwargs)

    def guarded_os_open(file, *args, **kwargs):
        if not is_permitted(file):
            raise PermissionError("Filesystem access outside worker directory is denied")
        return original_os_open(file, *args, **kwargs)

    def guarded_remove(path, *args, **kwargs):
        if not is_permitted(path):
            raise PermissionError("Filesystem access outside worker directory is denied")
        return original_remove(path, *args, **kwargs)

    def guarded_replace(source, destination, *args, **kwargs):
        if not all(is_permitted(path) for path in (source, destination)):
            raise PermissionError("Filesystem access outside worker directory is denied")
        return original_replace(source, destination, *args, **kwargs)

    def guarded_rename(source, destination, *args, **kwargs):
        if not all(is_permitted(path) for path in (source, destination)):
            raise PermissionError("Filesystem access outside worker directory is denied")
        return original_rename(source, destination, *args, **kwargs)

    builtins.open = guarded_open
    io.open = guarded_io_open
    setattr(os, "open", guarded_os_open)  # noqa: B010 - frontera deliberada del sandbox
    os.remove = guarded_remove
    os.unlink = guarded_remove
    setattr(os, "replace", guarded_replace)  # noqa: B010 - frontera deliberada del sandbox
    setattr(os, "rename", guarded_rename)  # noqa: B010 - frontera deliberada del sandbox


def _apply_os_resource_limits(policy: WorkerResourcePolicy) -> dict[str, bool]:
    """Aplica los límites disponibles del SO sin afirmar soporte inexistente."""

    capabilities = {"runtime": True, "cpu": False, "memory": False, "privileges": False}
    if sys.platform.startswith("win"):
        capabilities.update(_apply_windows_job_limits(policy))
        return capabilities
    try:
        import resource

        resource.setrlimit(resource.RLIMIT_CPU, (max(1, int(policy.max_cpu_s)), max(1, int(policy.max_cpu_s))))
        resource.setrlimit(resource.RLIMIT_AS, (policy.max_memory_mb * 1024 * 1024, policy.max_memory_mb * 1024 * 1024))
        capabilities.update(cpu=True, memory=True)
    except (ImportError, OSError, ValueError):
        pass
    return capabilities


def _apply_windows_job_limits(policy: WorkerResourcePolicy) -> dict[str, bool]:
    """Asigna el worker a un Job Object con cuotas de CPU y memoria en Windows."""

    if not sys.platform.startswith("win"):
        return {"cpu": False, "memory": False}
    try:
        from ctypes import wintypes

        class IO_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("ReadOperationCount", ctypes.c_ulonglong),
                ("WriteOperationCount", ctypes.c_ulonglong),
                ("OtherOperationCount", ctypes.c_ulonglong),
                ("ReadTransferCount", ctypes.c_ulonglong),
                ("WriteTransferCount", ctypes.c_ulonglong),
                ("OtherTransferCount", ctypes.c_ulonglong),
            ]

        class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", ctypes.c_longlong),
                ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD),
            ]

        class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
                ("IoInfo", IO_COUNTERS),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t),
            ]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        kernel32.SetInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD)
        kernel32.SetInformationJobObject.restype = wintypes.BOOL
        kernel32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
        kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)

        job = kernel32.CreateJobObjectW(None, None)
        if not job:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        limits.BasicLimitInformation.PerProcessUserTimeLimit = max(1, int(policy.max_cpu_s * 10_000_000))
        limits.BasicLimitInformation.LimitFlags = 0x00000002 | 0x00000100
        limits.ProcessMemoryLimit = policy.max_memory_mb * 1024 * 1024
        configured = kernel32.SetInformationJobObject(job, 9, ctypes.byref(limits), ctypes.sizeof(limits))
        assigned = configured and kernel32.AssignProcessToJobObject(job, kernel32.GetCurrentProcess())
        if not assigned:
            kernel32.CloseHandle(job)
            raise ctypes.WinError(ctypes.get_last_error())
        return {"cpu": True, "memory": True}
    except (AttributeError, OSError):
        return {"cpu": False, "memory": False}


def worker_isolation_enabled() -> bool:
    explicit = os.environ.get("EV3_WORKER_ISOLATION_ENABLED")
    if explicit is not None:
        return explicit.strip().lower() in {"1", "true", "yes", "on"}
    local_compatibility = os.environ.get("EV3_LOCAL_RUNTIME_ENABLED", "false")
    return local_compatibility.strip().lower() not in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class WorkerMessage:
    session_id: str
    sequence: int
    kind: str
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    command_id: str | None = None
    protocol_version: int = IPC_PROTOCOL_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol_version": self.protocol_version,
            "session_id": self.session_id,
            "sequence": self.sequence,
            "kind": self.kind,
            "type": self.type,
            "payload": self.payload,
            "command_id": self.command_id,
        }


def _worker_main(commands, events, session_id: str) -> None:
    sequence = 0
    status = "created"
    service = None

    def emit(event_type: str, payload: dict[str, Any], command_id: str | None = None) -> None:
        nonlocal sequence
        sequence += 1
        events.put(WorkerMessage(session_id, sequence, "event", event_type, payload, command_id).to_dict())

    original_cwd = os.getcwd()
    with tempfile.TemporaryDirectory(prefix="ev3-worker-") as workdir:
        os.chdir(workdir)
        removed_environment_variables = _sanitize_worker_environment()
        os.environ["TMP"] = workdir
        os.environ["TEMP"] = workdir
        tempfile.tempdir = workdir
        _disable_network()
        _restrict_open_to_workdir(workdir)
        tracemalloc.start()
        started_cpu_s = time.process_time()
        emit(
            "ready",
            {
                "worker_pid": os.getpid(),
                "workdir": workdir,
                "network_enabled": False,
                "environment_sanitized": True,
                "removed_environment_variables": len(removed_environment_variables),
            },
        )
        while True:
            raw = commands.get()
            if not isinstance(raw, dict) or raw.get("protocol_version") != IPC_PROTOCOL_VERSION:
                emit("error", {"code": "IPC_PROTOCOL_ERROR"})
                continue
            command_type = str(raw.get("type", ""))
            command_id = raw.get("command_id")
            if command_type == "shutdown":
                emit("terminated", {"reason": "shutdown"}, command_id)
                os.chdir(original_cwd)
                return
            if command_type == "probe_environment":
                payload = raw.get("payload", {})
                name = str(payload.get("name", ""))
                emit(
                    "sandbox",
                    {"environment_sanitized": True, "value_present": bool(os.environ.get(name))},
                    command_id,
                )
                continue
            if command_type == "initialize":
                try:
                    policy = WorkerResourcePolicy.from_payload(raw.get("payload", {}).get("execution_policy"))
                except (TypeError, ValueError) as exc:
                    emit("error", {"code": "IPC_POLICY_INVALID", "message": str(exc)}, command_id)
                    continue
                if _process_is_elevated():
                    emit(
                        "error",
                        {
                            "code": "IPC_PRIVILEGE_POLICY",
                            "message": "El worker aislado no puede ejecutar scripts con privilegios elevados.",
                        },
                        command_id,
                    )
                    continue
                from simulador_ev3.application.simulation_service import SimulationService
                from simulador_ev3.core.simulation_engine import SimEngineConfig
                from simulador_ev3.runtime.execution_policy import ExecutionPolicy

                engine_config_payload = raw.get("payload", {}).get("engine_config", {})
                if not isinstance(engine_config_payload, dict):
                    emit("error", {"code": "IPC_ENGINE_CONFIG_INVALID"}, command_id)
                    continue
                try:
                    engine_config = SimEngineConfig(**engine_config_payload)
                except TypeError as exc:
                    emit("error", {"code": "IPC_ENGINE_CONFIG_INVALID", "message": str(exc)}, command_id)
                    continue
                service = SimulationService(
                    config=engine_config, policy=ExecutionPolicy(max_runtime_s=policy.max_runtime_s)
                )
                service.set_snapshot_callback(lambda snapshot: emit("snapshot", snapshot.to_dict()))
                service.set_error_callback(lambda error: emit("error", {"code": "SCRIPT_ERROR", **error}))
                service.set_status_callback(
                    lambda service_status: emit(
                        "status",
                        {"status": {"started": "running", "stopped": "stopped"}.get(service_status, service_status)},
                    )
                )
                service.set_debug_callback(lambda debug: emit("debug", debug))
                capabilities = _apply_os_resource_limits(policy)
                capabilities["privileges"] = True
                status = "ready"
                emit(
                    "status",
                    {
                        "status": status,
                        "execution_policy": policy.__dict__,
                        "engine_config": engine_config_payload,
                        "resource_limits": capabilities,
                    },
                    command_id,
                )
                continue
            if command_type == "load_script":
                if service is not None:
                    service.load_script(str(raw.get("payload", {}).get("source", "")))
                status = "ready"
                emit("loaded", {"status": status}, command_id)
                continue
            if command_type == "set_simulation_profile":
                payload = raw.get("payload", {})
                profile = payload.get("profile")
                calibration = payload.get("calibration")
                if not isinstance(profile, str) or (calibration is not None and not isinstance(calibration, dict)):
                    emit("error", {"code": "IPC_PROFILE_INVALID"}, command_id)
                    continue
                try:
                    if service is not None:
                        service.set_simulation_profile(profile, calibration)
                    emit("profile_configured", {"profile": profile, "calibration": calibration or {}}, command_id)
                except (RuntimeError, ValueError) as exc:
                    emit("error", {"code": "IPC_PROFILE_INVALID", "message": str(exc)}, command_id)
                continue
            if command_type == "start":
                if service is not None:
                    payload = raw.get("payload", {})
                    service.start(
                        debug=bool(payload.get("debug", False)), step_mode=bool(payload.get("step_mode", False))
                    )
                status = "running"
                emit("status", {"status": status}, command_id)
                continue
            if command_type == "pause":
                if service is not None:
                    service.pause()
                status = "paused"
                emit("status", {"status": status}, command_id)
                continue
            if command_type == "resume":
                if service is not None:
                    service.resume()
                status = "running"
                emit("status", {"status": status}, command_id)
                continue
            if command_type == "stop":
                if service is not None:
                    service.stop()
                status = "stopped"
                emit("status", {"status": status}, command_id)
                continue
            if command_type == "reset":
                status = "created"
                emit("status", {"status": status}, command_id)
                continue
            if command_type == "set_robot_start":
                payload = raw.get("payload", {})
                try:
                    x_mm = float(payload["x_mm"])
                    y_mm = float(payload["y_mm"])
                    theta_deg = payload.get("theta_deg")
                    theta_deg = float(theta_deg) if theta_deg is not None else None
                except (KeyError, TypeError, ValueError):
                    emit("error", {"code": "IPC_ROBOT_START_INVALID"}, command_id)
                    continue
                if service is not None:
                    service.set_robot_start(x_mm, y_mm, theta_deg)
                emit("robot_start_configured", {"x_mm": x_mm, "y_mm": y_mm, "theta_deg": theta_deg}, command_id)
                continue
            if command_type == "load_world":
                source = raw.get("payload", {}).get("source")
                if not isinstance(source, str):
                    emit("error", {"code": "IPC_WORLD_INVALID", "message": "source debe ser JSON textual"}, command_id)
                    continue
                try:
                    world_path = Path(workdir) / f"world-{uuid.uuid4().hex}.json"
                    world_path.write_text(source, encoding="utf-8")
                    if service is not None:
                        service.load_world_file(world_path)
                    service_snapshot = service.get_snapshot() if service is not None else None
                    snapshot = service_snapshot.to_dict() if service_snapshot is not None else None
                    emit("world_loaded", {"status": status, "snapshot": snapshot}, command_id)
                except (OSError, ValueError, TypeError) as exc:
                    emit("error", {"code": "IPC_WORLD_INVALID", "message": str(exc)}, command_id)
                finally:
                    if "world_path" in locals():
                        world_path.unlink(missing_ok=True)
                continue
            if command_type == "load_blank_world":
                payload = raw.get("payload", {})
                try:
                    width_mm = float(payload["width_mm"])
                    height_mm = float(payload["height_mm"])
                    if service is not None:
                        service.load_blank_world(width_mm=width_mm, height_mm=height_mm)
                except (KeyError, TypeError, ValueError) as exc:
                    emit("error", {"code": "IPC_WORLD_INVALID", "message": str(exc)}, command_id)
                    continue
                emit("world_loaded", {"status": status, "blank": True}, command_id)
                continue
            if command_type == "set_debug":
                payload = raw.get("payload", {})
                raw_breakpoints = payload.get("breakpoints", [])
                raw_watches = payload.get("watches", [])
                if not isinstance(raw_breakpoints, list) or not isinstance(raw_watches, list):
                    emit(
                        "error",
                        {"code": "IPC_DEBUG_CONFIG_INVALID", "message": "breakpoints y watches deben ser listas"},
                        command_id,
                    )
                    continue
                try:
                    breakpoints = {int(line) for line in raw_breakpoints if int(line) > 0}
                except (TypeError, ValueError):
                    emit(
                        "error",
                        {"code": "IPC_DEBUG_CONFIG_INVALID", "message": "Los breakpoints deben ser lineas positivas"},
                        command_id,
                    )
                    continue
                watches = [str(expression).strip() for expression in raw_watches if str(expression).strip()]
                if service is not None:
                    service.set_debug_breakpoints(breakpoints)
                    service.set_debug_watches(watches)
                emit(
                    "debug_configured",
                    {"status": status, "breakpoints": sorted(breakpoints), "watches": watches},
                    command_id,
                )
                continue
            if command_type == "debug_continue":
                if service is not None:
                    service.debug_continue()
                emit("debug_command", {"status": status, "action": "continue"}, command_id)
                continue
            if command_type == "debug_step":
                if service is not None:
                    service.debug_step()
                emit("debug_command", {"status": status, "action": "step"}, command_id)
                continue
            if command_type == "probe_network":
                try:
                    socket.socket()
                except WorkerNetworkDisabled:
                    emit("sandbox", {"network_enabled": False}, command_id)
                else:
                    emit("error", {"code": "NETWORK_SANDBOX_BYPASSED"}, command_id)
                continue
            if command_type == "probe_filesystem":
                try:
                    with open(os.path.join(workdir, "probe.txt"), "w", encoding="utf-8") as probe:
                        probe.write("ok")
                    Path(__file__).open(encoding="utf-8")
                    os.open(__file__, os.O_RDONLY)
                except PermissionError:
                    emit("sandbox", {"filesystem_restricted": True}, command_id)
                else:
                    emit("error", {"code": "FILESYSTEM_SANDBOX_BYPASSED"}, command_id)
                continue
            if command_type == "heartbeat":
                current_memory, peak_memory = tracemalloc.get_traced_memory()
                emit(
                    "heartbeat",
                    {
                        "status": status,
                        "cpu_s": round(time.process_time() - started_cpu_s, 6),
                        "memory_bytes": current_memory,
                        "peak_memory_bytes": peak_memory,
                        "event_queue_depth": 0,
                    },
                    command_id,
                )
                continue
            emit("error", {"code": "IPC_COMMAND_UNSUPPORTED", "type": command_type}, command_id)


class IsolatedRuntimeWorker:
    """Cliente del worker aislado v1; la migración de sesiones se hace en 3.4."""

    def __init__(self, session_id: str | None = None) -> None:
        self.session_id = session_id or str(uuid.uuid4())
        self._context = mp.get_context("spawn")
        self._commands = self._context.Queue()
        self._events = self._context.Queue()
        self._process: Any = None
        self._sequence = 0

    def start(self) -> None:
        if self._process and self._process.is_alive():
            return
        self._process = self._context.Process(
            target=_worker_main, args=(self._commands, self._events, self.session_id), daemon=True
        )
        self._process.start()

    def send(self, command_type: str, payload: dict[str, Any] | None = None, command_id: str | None = None) -> str:
        if not self._process or not self._process.is_alive():
            raise RuntimeError("Worker aislado no iniciado")
        self._sequence += 1
        identifier = command_id or str(uuid.uuid4())
        self._commands.put(
            WorkerMessage(self.session_id, self._sequence, "command", command_type, payload or {}, identifier).to_dict()
        )
        return identifier

    def send_raw_for_diagnostics(self, message: dict[str, Any]) -> None:
        """Envía un mensaje crudo sólo para pruebas del contrato IPC."""
        if not self._process or not self._process.is_alive():
            raise RuntimeError("Worker aislado no iniciado")
        self._commands.put(message)

    def receive(self, timeout_s: float = 1.0) -> dict[str, Any]:
        try:
            return self._events.get(timeout=timeout_s)
        except queue.Empty as exc:
            raise TimeoutError("Worker no emitió evento dentro del tiempo esperado") from exc

    def drain_events(self, limit: int = 100) -> list[dict[str, Any]]:
        """Obtiene eventos disponibles sin bloquear, preservando su orden IPC."""
        drained: list[dict[str, Any]] = []
        for _ in range(max(0, int(limit))):
            try:
                drained.append(self._events.get_nowait())
            except queue.Empty:
                break
        return drained

    def close(self) -> None:
        if self._process and self._process.is_alive():
            try:
                self.send("shutdown")
                self.receive(1.0)
            except (RuntimeError, TimeoutError):
                self._process.terminate()
            self._process.join(timeout=1.0)

    def restart(self) -> None:
        """Recrea el proceso aislado después de una caída o cancelación forzada."""
        if self._process and self._process.is_alive():
            self._process.terminate()
            self._process.join(timeout=1.0)
        self._process = None
        self.start()
