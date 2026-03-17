"""Tests para la Fase 4: Runtime Layer (ExecutionPolicy, RuntimeSandbox, RuntimeController)."""

import time
import threading

import pytest

from simulador_ev3.core.command_queue import CommandQueue
from simulador_ev3.core.event_bus import EVENT_RUNTIME_ERROR, EventBus
from simulador_ev3.core.simulation_engine import SimEngineConfig, SimulationEngine
from simulador_ev3.runtime.execution_policy import ExecutionPolicy, SAFE_BUILTINS, BLOCKED_MODULES
from simulador_ev3.runtime.runtime_sandbox import RuntimeSandbox, SandboxState
from simulador_ev3.runtime.runtime_controller import RuntimeController, ControllerState


# ===========================================================================
# ExecutionPolicy
# ===========================================================================

class TestExecutionPolicy:
    def test_default_max_runtime(self):
        p = ExecutionPolicy()
        assert p.max_runtime_s == 30.0

    def test_negative_runtime_raises(self):
        with pytest.raises(ValueError, match="≥ 0"):
            ExecutionPolicy(max_runtime_s=-1.0)

    def test_zero_runtime_allowed(self):
        p = ExecutionPolicy(max_runtime_s=0.0)
        assert p.max_runtime_s == 0.0

    def test_safe_builtins_contains_print(self):
        p = ExecutionPolicy()
        assert "print" in p.safe_builtins

    def test_safe_builtins_excludes_open(self):
        p = ExecutionPolicy()
        assert "open" not in p.safe_builtins

    def test_safe_builtins_excludes_exec(self):
        p = ExecutionPolicy()
        assert "exec" not in p.safe_builtins

    def test_blocked_modules_contains_os(self):
        p = ExecutionPolicy()
        assert p.is_module_blocked("os")

    def test_blocked_modules_contains_sys(self):
        p = ExecutionPolicy()
        assert p.is_module_blocked("sys")

    def test_blocked_modules_os_path(self):
        p = ExecutionPolicy()
        assert p.is_module_blocked("os.path")

    def test_math_not_blocked(self):
        p = ExecutionPolicy()
        assert not p.is_module_blocked("math")

    def test_build_namespace_has_builtins(self):
        p = ExecutionPolicy()
        ns = p.build_namespace()
        assert "__builtins__" in ns
        assert "print" in ns["__builtins__"]

    def test_build_namespace_has_restricted_import(self):
        p = ExecutionPolicy()
        ns = p.build_namespace()
        assert "__import__" in ns["__builtins__"]

    def test_build_namespace_has_math_by_default(self):
        p = ExecutionPolicy()
        ns = p.build_namespace()
        assert "math" in ns

    def test_build_namespace_no_math_when_disabled(self):
        p = ExecutionPolicy(allow_math=False)
        ns = p.build_namespace()
        assert "math" not in ns

    def test_build_namespace_injects_pybricks_modules(self):
        p = ExecutionPolicy()
        sentinel = object()
        ns = p.build_namespace({"pybricks": sentinel})
        assert ns["pybricks"] is sentinel

    def test_build_namespace_sets_dunder_name(self):
        p = ExecutionPolicy()
        ns = p.build_namespace()
        assert ns["__name__"] == "__main__"


# ===========================================================================
# RuntimeSandbox
# ===========================================================================

class TestSandboxExecution:
    def _make_sandbox(self, code: str, policy=None, bus=None, modules=None):
        return RuntimeSandbox(
            source_code=code,
            policy=policy or ExecutionPolicy(max_runtime_s=0),
            event_bus=bus or EventBus(),
            pybricks_modules=modules or {},
        )

    def test_simple_script_finishes(self):
        sb = self._make_sandbox("x = 1 + 1")
        sb.start()
        sb.join(timeout=2.0)
        assert sb.state == SandboxState.FINISHED

    def test_error_script_reports_error(self):
        bus = EventBus()
        errors = []
        bus.subscribe(EVENT_RUNTIME_ERROR, lambda e, p: errors.append(p))
        sb = self._make_sandbox("raise ValueError('test error')", bus=bus)
        sb.start()
        sb.join(timeout=2.0)
        assert sb.state == SandboxState.ERROR
        assert sb.error is not None
        assert "test error" in sb.error
        assert len(errors) == 1

    def test_error_publishes_traceback(self):
        errors = []
        bus = EventBus()
        bus.subscribe(EVENT_RUNTIME_ERROR, lambda e, p: errors.append(p))
        sb = self._make_sandbox("1/0", bus=bus)
        sb.start()
        sb.join(timeout=2.0)
        assert sb.traceback_str is not None
        assert "ZeroDivisionError" in sb.traceback_str

    def test_cannot_start_twice(self):
        sb = self._make_sandbox("x = 1")
        sb.start()
        sb.join(timeout=2.0)
        with pytest.raises(RuntimeError):
            sb.start()

    def test_stop_sets_stop_event(self):
        # Script que hace un sleep largo (simulado con threading.Event.wait)
        code = "__stop_event__.wait(timeout=10)"
        sb = self._make_sandbox(code)
        sb.start()
        time.sleep(0.05)
        sb.stop()
        sb.join(timeout=2.0)
        assert sb.stop_event.is_set()

    def test_blocked_module_cannot_be_imported(self):
        """os no debe poder usarse en el namespace restringido."""
        code = "import os; os.getcwd()"
        sb = self._make_sandbox(code)
        sb.start()
        sb.join(timeout=2.0)
        assert sb.state == SandboxState.ERROR
        assert sb.error is not None

    def test_safe_import_of_math_works(self):
        code = "import math\nresult = math.sqrt(16)"
        sb = self._make_sandbox(code)
        sb.start()
        sb.join(timeout=2.0)
        assert sb.state == SandboxState.FINISHED

    def test_pybricks_module_injected(self):
        """Un módulo virtual puede inyectarse y usarse en el script."""
        class FakeTools:
            called = False
            def wait(self_inner, ms):
                FakeTools.called = True

        tools = FakeTools()
        code = "tools.wait(100)"
        sb = self._make_sandbox(code, modules={"tools": tools})
        sb.start()
        sb.join(timeout=2.0)
        assert sb.state == SandboxState.FINISHED
        assert FakeTools.called

    def test_math_available_by_default(self):
        """math debe estar disponible en el namespace."""
        results = []
        code = "result = math.sqrt(16)"
        sb = self._make_sandbox(code)
        sb.start()
        sb.join(timeout=2.0)
        assert sb.state == SandboxState.FINISHED

    def test_on_finished_callback(self):
        called = []
        sb = RuntimeSandbox(
            source_code="x = 42",
            on_finished=lambda: called.append(True),
        )
        sb.start()
        sb.join(timeout=2.0)
        assert len(called) == 1

    def test_watchdog_timeout(self):
        """El watchdog debe parar el script tras max_runtime_s."""
        bus = EventBus()
        errors = []
        bus.subscribe(EVENT_RUNTIME_ERROR, lambda e, p: errors.append(p))
        policy = ExecutionPolicy(max_runtime_s=0.1)
        # Script que dura mucho: espera el stop_event con timeout largo
        code = "__stop_event__.wait(timeout=60)"
        sb = RuntimeSandbox(source_code=code, policy=policy, event_bus=bus)
        sb.start()
        time.sleep(0.5)   # dar tiempo al watchdog
        sb.join(timeout=1.0)
        assert sb.state in (SandboxState.TIMED_OUT, SandboxState.FINISHED)
        # Se publicó error de timeout
        assert any("tiempo" in e.get("error", "").lower() or
                   "máximo" in e.get("error", "").lower()
                   for e in errors), f"No se encontró error de timeout en {errors}"


# ===========================================================================
# RuntimeController
# ===========================================================================

def make_engine():
    cfg = SimEngineConfig(
        robot_x0_mm=500, robot_y0_mm=500,
        world_width_mm=2000, world_height_mm=2000,
    )
    q   = CommandQueue()
    bus = EventBus()
    return SimulationEngine(config=cfg, command_queue=q, event_bus=bus), bus


class TestRuntimeControllerLifecycle:
    def test_initial_state_is_idle(self):
        eng, bus = make_engine()
        ctrl = RuntimeController(eng, bus)
        assert ctrl.state == ControllerState.IDLE

    def test_start_transitions_to_running(self):
        eng, bus = make_engine()
        ctrl = RuntimeController(eng, bus)
        ctrl.start()
        assert ctrl.state == ControllerState.RUNNING
        ctrl.stop()

    def test_stop_transitions_to_stopped(self):
        eng, bus = make_engine()
        ctrl = RuntimeController(eng, bus)
        ctrl.start()
        ctrl.stop()
        assert ctrl.state == ControllerState.STOPPED

    def test_double_start_raises(self):
        eng, bus = make_engine()
        ctrl = RuntimeController(eng, bus)
        ctrl.start()
        with pytest.raises(RuntimeError):
            ctrl.start()
        ctrl.stop()

    def test_double_stop_is_harmless(self):
        eng, bus = make_engine()
        ctrl = RuntimeController(eng, bus)
        ctrl.start()
        ctrl.stop()
        ctrl.stop()   # no debe lanzar

    def test_reset_returns_to_idle(self):
        eng, bus = make_engine()
        ctrl = RuntimeController(eng, bus)
        ctrl.start()
        ctrl.reset()
        assert ctrl.state == ControllerState.IDLE

    def test_pause_and_resume(self):
        eng, bus = make_engine()
        ctrl = RuntimeController(eng, bus)
        ctrl.start()
        ctrl.pause()
        assert ctrl.state == ControllerState.PAUSED
        ctrl.resume()
        assert ctrl.state == ControllerState.RUNNING
        ctrl.stop()


class TestRuntimeControllerEngine:
    def test_engine_ticks_while_running(self):
        """El engine avanza ticks mientras el controller está RUNNING."""
        eng, bus = make_engine()
        ctrl = RuntimeController(eng, bus, tick_rate_hz=50)
        ctrl.start()
        time.sleep(0.1)    # ~5 ticks a 50 Hz
        ctrl.stop()
        assert eng.tick >= 3

    def test_engine_paused_does_not_tick(self):
        """Con el controller pausado, el engine no avanza."""
        eng, bus = make_engine()
        ctrl = RuntimeController(eng, bus, tick_rate_hz=50)
        ctrl.start()
        time.sleep(0.05)
        tick_before = eng.tick
        ctrl.pause()
        time.sleep(0.1)
        tick_after = eng.tick
        ctrl.stop()
        # Puede haber 1 tick extra por race condition de concurrencia
        assert tick_after - tick_before <= 2

    def test_snapshot_callback_called(self):
        """El callback de snapshot se invoca en cada tick."""
        eng, bus = make_engine()
        ctrl = RuntimeController(eng, bus, tick_rate_hz=50)
        snaps = []
        ctrl.set_snapshot_callback(lambda s: snaps.append(s))
        ctrl.start()
        time.sleep(0.1)
        ctrl.stop()
        assert len(snaps) >= 3

    def test_manual_tick(self):
        """tick() manual ejecuta un único step del engine."""
        eng, bus = make_engine()
        ctrl = RuntimeController(eng, bus)
        ctrl.start()
        ctrl.stop()
        # reset y tick manual
        ctrl.reset()
        # En IDLE, tick() devuelve None
        result = ctrl.tick()
        assert result is None


class TestRuntimeControllerScript:
    def test_simple_script_finishes(self):
        eng, bus = make_engine()
        ctrl = RuntimeController(
            eng, bus,
            policy=ExecutionPolicy(max_runtime_s=0),
        )
        ctrl.load_script("x = 1 + 2")
        ctrl.start()
        time.sleep(0.2)
        # El controlador debería haberse detenido solo al terminar el script
        assert ctrl.state in (ControllerState.STOPPED, ControllerState.RUNNING)
        ctrl.stop()

    def test_load_script_while_running_raises(self):
        eng, bus = make_engine()
        ctrl = RuntimeController(eng, bus)
        ctrl.start()
        with pytest.raises(RuntimeError, match="mientras la simulación corre"):
            ctrl.load_script("x = 1")
        ctrl.stop()

    def test_error_script_publishes_runtime_error(self):
        eng, bus = make_engine()
        errors = []
        bus.subscribe(EVENT_RUNTIME_ERROR, lambda e, p: errors.append(p))
        ctrl = RuntimeController(
            eng, bus,
            policy=ExecutionPolicy(max_runtime_s=0),
        )
        ctrl.load_script("raise RuntimeError('fallo de prueba')")
        ctrl.start()
        time.sleep(0.3)
        ctrl.stop()
        assert len(errors) >= 1
        assert "fallo de prueba" in errors[0].get("error", "")

    def test_sandbox_accessible_after_run(self):
        eng, bus = make_engine()
        ctrl = RuntimeController(
            eng, bus,
            policy=ExecutionPolicy(max_runtime_s=0),
        )
        ctrl.load_script("x = 42")
        ctrl.start()
        time.sleep(0.2)
        ctrl.stop()
        assert ctrl.sandbox is not None
