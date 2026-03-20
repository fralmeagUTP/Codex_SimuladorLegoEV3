"""
Tests para la Fase 7: Capa de UI (Tkinter).

Estrategia: los módulos UI importan tkinter, que en algunos CI no tiene
display. Usamos unittest.mock para parchear el módulo completo y testear
sólo la lógica no visual (callbacks, métodos de actualización, etc.).
"""
from __future__ import annotations

import importlib
import sys
import threading
import types
import unittest.mock as mock

import pytest

from simulador_ev3.application.snapshot_dto import SnapshotDTO
from simulador_ev3.core.simulation_engine import SimEngineConfig, SimulationEngine


# ===========================================================================
# Fixture: mock de tkinter global
# ===========================================================================

def _make_tk_mock():
    """Crea un módulo tkinter falso suficiente para que los módulos UI importen."""
    tk = types.ModuleType("tkinter")
    # Constantes comunes
    tk.LEFT  = "left"
    tk.RIGHT = "right"
    tk.TOP   = "top"
    tk.BOTTOM  = "bottom"
    tk.X     = "x"
    tk.Y     = "y"
    tk.BOTH  = "both"
    tk.W     = "w"
    tk.END   = "end"
    tk.NORMAL   = "normal"
    tk.DISABLED = "disabled"
    tk.SUNKEN   = "sunken"
    tk.RAISED   = "raised"
    tk.FLAT     = "flat"
    tk.LAST     = "last"
    tk.VERTICAL   = "vertical"
    tk.HORIZONTAL = "horizontal"
    tk.NONE = "none"
    tk.NW = "nw"

    # Clases stub que recuerdan llamadas
    class _Widget:
        def __init__(self, *a, **kw): pass
        def pack(self, **kw):   return self
        def grid(self, **kw):   return self
        def configure(self, **kw): return self
        def config(self, **kw):    return self
        def bind(self, *a, **kw):  return None
        def unbind(self, *a, **kw): return None
        def pack_configure(self, **kw): return self
        def cget(self, key): return ""
        def after(self, ms, fn=None, *args):
            return "after_id"
        def after_idle(self, fn, *args):
            return fn(*args) if args else fn()
        def after_cancel(self, aid): pass
        def destroy(self): pass
        def winfo_width(self):  return 400
        def winfo_height(self): return 400
        def winfo_children(self): return []
        def delete(self, *a): pass
        def create_oval(self, *a, **kw): return 1
        def create_rectangle(self, *a, **kw): return 1
        def create_line(self, *a, **kw): return 1
        def create_polygon(self, *a, **kw): return 1
        def create_text(self, *a, **kw): return 1
        def create_image(self, *a, **kw): return 1
        def create_window(self, *a, **kw): return 1
        def bbox(self, *a, **kw): return (0, 0, 400, 400)
        def itemconfigure(self, *a, **kw): return None
        def insert(self, *a, **kw): return None
        def get(self, *a, **kw): return ""
        def index(self, *a, **kw): return "1.0"
        def tag_add(self, *a, **kw): return None
        def tag_remove(self, *a, **kw): return None
        def tag_configure(self, *a, **kw): return None
        def protocol(self, *a, **kw): return None
        def yview(self, *a, **kw): return None
        def xview(self, *a, **kw): return None
        def yview_moveto(self, *a, **kw): return None
        def xview_moveto(self, *a, **kw): return None
        def canvasy(self, y): return y
        def canvasx(self, x): return x
        def find_overlapping(self, *a, **kw): return []
        def see(self, *a): return None

    class _StringVar:
        def __init__(self, value=""):
            self._val = value
        def set(self, val): self._val = val
        def get(self):      return self._val

    class Tk(_Widget):
        def title(self, t): pass
        def geometry(self, g): pass
        def minsize(self, w, h): pass
        def configure(self, **kw): pass
        def mainloop(self): pass

    class Frame(_Widget): pass
    class LabelFrame(_Widget): pass
    class Canvas(_Widget): pass
    class PhotoImage:
        def __init__(self, *a, **kw):
            self._w = 32
            self._h = 32
        def width(self):
            return self._w
        def height(self):
            return self._h
        def zoom(self, zx=1, zy=1):
            out = PhotoImage()
            out._w = max(1, int(self._w * zx))
            out._h = max(1, int(self._h * zy))
            return out
        def subsample(self, sx=1, sy=1):
            out = PhotoImage()
            out._w = max(1, int(self._w / max(1, sx)))
            out._h = max(1, int(self._h / max(1, sy)))
            return out
    class Text(_Widget): pass
    class Label(_Widget): pass
    class Button(_Widget): pass
    class Scrollbar(_Widget):
        def set(self, *a): pass
    class PanedWindow(_Widget):
        def add(self, widget, **kw): pass
    class Menu(_Widget):
        def add_command(self, **kw): pass
        def add_separator(self): pass
        def add_cascade(self, **kw): pass

    tk.Widget     = _Widget
    tk.Tk         = Tk
    tk.Frame      = Frame
    tk.LabelFrame = LabelFrame
    tk.Canvas     = Canvas
    tk.PhotoImage = PhotoImage
    tk.Text       = Text
    tk.Label      = Label
    tk.Button     = Button
    tk.Scrollbar  = Scrollbar
    tk.PanedWindow = PanedWindow
    tk.Menu       = Menu
    tk.StringVar  = _StringVar

    # filedialog / messagebox stubs
    filedialog = types.ModuleType("tkinter.filedialog")
    filedialog.askopenfilename  = lambda **kw: ""
    filedialog.asksaveasfilename = lambda **kw: ""
    messagebox = types.ModuleType("tkinter.messagebox")
    messagebox.showerror = lambda *a, **kw: None
    messagebox.showinfo  = lambda *a, **kw: None
    messagebox.askyesno  = lambda *a, **kw: True
    scrolledtext = types.ModuleType("tkinter.scrolledtext")
    scrolledtext.ScrolledText = Text

    tk.filedialog   = filedialog
    tk.messagebox   = messagebox
    tk.scrolledtext = scrolledtext

    return tk, filedialog, messagebox, scrolledtext


@pytest.fixture(scope="module", autouse=True)
def patch_tkinter():
    """Instala mocks de tkinter en sys.modules antes de importar módulos UI."""
    tk, fd, mb, st = _make_tk_mock()
    sys.modules["tkinter"]              = tk
    sys.modules["tkinter.filedialog"]   = fd
    sys.modules["tkinter.messagebox"]   = mb
    sys.modules["tkinter.scrolledtext"] = st

    # Re-importar módulos UI para que usen el mock
    for mod_name in list(sys.modules):
        if "simulador_ev3.ui" in mod_name:
            del sys.modules[mod_name]
    yield
    # Limpiar al terminar
    for mod_name in list(sys.modules):
        if "simulador_ev3.ui" in mod_name:
            del sys.modules[mod_name]


def _snap():
    """Crea un SnapshotDTO de prueba usando un engine real."""
    eng = SimulationEngine(config=SimEngineConfig(
        robot_x0_mm=500, robot_y0_mm=500,
        world_width_mm=2000, world_height_mm=2000,
    ))
    snap = eng.update()
    return SnapshotDTO.from_snapshot(snap)


# ===========================================================================
# WorldCanvas
# ===========================================================================

class TestWorldCanvas:
    @pytest.fixture(autouse=True)
    def imp(self):
        from simulador_ev3.ui.world_canvas import WorldCanvas
        self.WorldCanvas = WorldCanvas

    def test_instantiation(self):
        parent = mock.MagicMock()
        wc = self.WorldCanvas(parent, world_w_mm=2000, world_h_mm=2000)
        assert wc is not None

    def test_update_from_dto_no_crash(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        dto = _snap()
        wc.update_from_dto(dto)   # no debe lanzar

    def test_clear_trail(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        wc._trail = [(10, 10), (20, 20)]
        wc.clear_trail()
        assert wc._trail == []

    def test_reset_clears_trail(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        wc._trail = [(5, 5)]
        wc.reset()
        assert wc._trail == []

    def test_set_obstacles_stores_list(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        obs = [{"x_mm": 100, "y_mm": 100, "width_mm": 200, "height_mm": 200}]
        wc.set_obstacles(obs)
        assert wc._obstacles == obs

    def test_robot_sprite_is_scaled_to_32x23(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        assert wc._robot_sprite is not None
        assert wc._robot_sprite.width() == 32
        assert wc._robot_sprite.height() == 23

    def test_update_from_dto_recenters_view(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        wc.xview_moveto = mock.Mock()
        wc.yview_moveto = mock.Mock()
        wc.update_from_dto(_snap())
        assert wc.xview_moveto.called
        assert wc.yview_moveto.called

    def test_robot_sprite_rotation_is_requested_with_theta(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        wc._robot_sprite = object()
        wc._get_rotated_robot_sprite = mock.Mock(return_value=wc._robot_sprite)
        wc._draw_robot_sprite(500.0, 500.0, 42.0, False)
        wc._get_rotated_robot_sprite.assert_called_once_with(42.0)

    def test_placement_click_calls_callback_with_theta(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        received = []
        wc.enable_placement_mode(
            callback=lambda x_mm, y_mm, theta_deg: received.append((x_mm, y_mm, theta_deg))
        )
        expected_x, expected_y = wc._event_to_world(types.SimpleNamespace(x=100, y=50))

        wc._on_placement_click(types.SimpleNamespace(x=100, y=50))

        assert wc._placement_pos == pytest.approx((expected_x, expected_y))
        assert received[-1] == pytest.approx((expected_x, expected_y, 0.0))

    def test_placement_drag_updates_theta(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        received = []
        wc.enable_placement_mode(
            callback=lambda x_mm, y_mm, theta_deg: received.append((x_mm, y_mm, theta_deg))
        )
        expected_x, expected_y = wc._event_to_world(types.SimpleNamespace(x=100, y=100))

        wc._on_placement_click(types.SimpleNamespace(x=100, y=100))
        wc._on_placement_drag(types.SimpleNamespace(x=100, y=200))

        assert wc._placement_theta_deg == pytest.approx(90.0)
        assert received[-1] == pytest.approx((expected_x, expected_y, 90.0))

    def test_placement_wheel_updates_theta(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        received = []
        wc.enable_placement_mode(
            callback=lambda x_mm, y_mm, theta_deg: received.append((x_mm, y_mm, theta_deg))
        )
        wc.draw_placement_marker(400.0, 400.0, 10.0)

        wc._on_placement_wheel(types.SimpleNamespace(delta=120))

        assert wc._placement_theta_deg == pytest.approx(15.0)
        assert received[-1] == pytest.approx((400.0, 400.0, 15.0))


# ===========================================================================
# EditorPanel
# ===========================================================================

class TestEditorPanel:
    @pytest.fixture(autouse=True)
    def imp(self):
        from simulador_ev3.ui.editor_panel import EditorPanel
        self.EditorPanel = EditorPanel

    def test_instantiation(self):
        ep = self.EditorPanel(mock.MagicMock())
        assert ep is not None

    def test_on_run_callback_called(self):
        received = []
        ep = self.EditorPanel(mock.MagicMock(), on_run=lambda c: received.append(c))
        ep._cmd_run()
        assert len(received) == 1

    def test_on_stop_callback_called(self):
        received = []
        ep = self.EditorPanel(mock.MagicMock(), on_stop=lambda: received.append(True))
        ep._cmd_stop()
        assert received == [True]

    def test_set_status_updates_var(self):
        ep = self.EditorPanel(mock.MagicMock())
        ep.set_status("Prueba", "red")
        assert ep._status_var.get() == "Prueba"

    def test_set_and_get_code(self):
        ep = self.EditorPanel(mock.MagicMock())
        # El mock de Text.get() devuelve "" por defecto →
        # sólo verificamos que no lanza
        ep.set_code("x = 1\n")
        result = ep.get_code()
        assert isinstance(result, str)


# ===========================================================================
# BrickPanel
# ===========================================================================

class TestBrickPanel:
    @pytest.fixture(autouse=True)
    def imp(self):
        from simulador_ev3.ui.brick_panel import BrickPanel
        self.BrickPanel = BrickPanel

    def test_instantiation(self):
        bp = self.BrickPanel(mock.MagicMock())
        assert bp is not None

    def test_update_from_dto_no_crash(self):
        bp = self.BrickPanel(mock.MagicMock())
        bp.update_from_dto(_snap())

    def test_reset_no_crash(self):
        bp = self.BrickPanel(mock.MagicMock())
        bp.reset()

    def test_update_led_sets_label(self):
        bp = self.BrickPanel(mock.MagicMock())
        bp._update_led("GREEN")   # no debe lanzar excepción
        bp._update_led(None)      # estado apagado tampoco debe lanzar

    def test_update_screen_no_crash(self):
        bp = self.BrickPanel(mock.MagicMock())
        bp._update_screen("Hola mundo")
        bp._update_screen({"lines": ["Linea 1", "Linea 2"], "width_px": 178, "height_px": 128})

    def test_update_speaker_no_crash(self):
        bp = self.BrickPanel(mock.MagicMock())
        bp._update_speaker({"freq": 440, "duration_ms": 100, "volume": 50})


# ===========================================================================
# TelemetryPanel
# ===========================================================================

class TestTelemetryPanel:
    @pytest.fixture(autouse=True)
    def imp(self):
        from simulador_ev3.ui.telemetry_panel import TelemetryPanel
        self.TelemetryPanel = TelemetryPanel

    def test_instantiation(self):
        tp = self.TelemetryPanel(mock.MagicMock())
        assert tp is not None

    def test_update_from_dto_no_crash(self):
        tp = self.TelemetryPanel(mock.MagicMock())
        tp.update_from_dto(_snap())

    def test_reset_no_crash(self):
        tp = self.TelemetryPanel(mock.MagicMock())
        tp.reset()

    def test_robot_position_reflected_in_vars(self):
        tp = self.TelemetryPanel(mock.MagicMock())
        dto = _snap()
        tp.update_from_dto(dto)
        assert tp._var_x.get() == f"{dto.robot['x_mm']:.1f}"
        assert tp._var_y.get() == f"{dto.robot['y_mm']:.1f}"

    def test_tick_var_updated(self):
        tp = self.TelemetryPanel(mock.MagicMock())
        dto = _snap()
        tp.update_from_dto(dto)
        assert tp._var_tick.get() == str(dto.tick)

    def test_sensors_are_mapped_by_port(self):
        tp = self.TelemetryPanel(mock.MagicMock())
        tp._update_sensors([
            {"port": "S3", "type": "ColorSensorModel", "value": 61.2}
        ])
        assert tp._sensor_vars["S3"]["type"].get() == "ColorSensorModel"
        assert "61.2" in tp._sensor_vars["S3"]["value"].get()
        assert tp._sensor_vars["S1"]["type"].get() == "-"

    def test_motors_are_mapped_by_port(self):
        tp = self.TelemetryPanel(mock.MagicMock())
        tp._update_motors([
            {"port": "B", "speed": 250.0, "angle": 42.5, "state": "RUNNING"}
        ])
        assert tp._motor_vars["B"]["state"].get() == "RUNNING"
        assert tp._motor_vars["A"]["state"].get() == "-"


# ===========================================================================
# MainWindow (smoke test de importación y construcción)
# ===========================================================================

class TestWorldToolbar:
    @pytest.fixture(autouse=True)
    def imp(self):
        from simulador_ev3.ui.world_toolbar import WorldToolbar
        self.WorldToolbar = WorldToolbar

    def _new_toolbar(self):
        return self.WorldToolbar(
            mock.MagicMock(),
            on_tool_change=lambda _tool: None,
            on_new=lambda: None,
            on_open=lambda: None,
            on_save=lambda: None,
            on_save_as=lambda: None,
            on_delete=lambda: None,
            on_duplicate=lambda: None,
            on_rotate=lambda: None,
            on_apply_props=lambda: None,
        )

    def test_tool_icons_scaled_to_32x32(self):
        tb = self._new_toolbar()
        icon = tb._get_tool_icon("wall_64x64_a")
        assert icon is not None
        assert icon.width() == 32
        assert icon.height() == 32

    def test_icon_loader_uses_fallback_when_first_candidate_fails(self):
        from simulador_ev3.ui import world_toolbar as wt

        tb = self._new_toolbar()
        tb._image_lookup = {
            "floor_tile_256_c.jpg": "floor_tile_256_c.jpg",
            "floor_tile_256_b.png": "floor_tile_256_b.png",
        }

        class _OkPhoto:
            def __init__(self, *a, **kw):
                self._w = 64
                self._h = 64

            def width(self):
                return self._w

            def height(self):
                return self._h

            def zoom(self, zx=1, zy=1):
                out = _OkPhoto()
                out._w = max(1, int(self._w * zx))
                out._h = max(1, int(self._h * zy))
                return out

            def subsample(self, sx=1, sy=1):
                out = _OkPhoto()
                out._w = max(1, int(self._w / max(1, sx)))
                out._h = max(1, int(self._h / max(1, sy)))
                return out

        def _photoimage_side_effect(*a, **kw):
            file_path = str(kw.get("file", ""))
            if file_path.endswith(".jpg"):
                raise RuntimeError("unsupported format")
            return _OkPhoto()

        with mock.patch.object(wt.tk, "PhotoImage", side_effect=_photoimage_side_effect):
            icon = tb._get_tool_icon("floor_tile_256_c")

        assert icon is not None
        assert icon.width() == 32
        assert icon.height() == 32


class TestMainWindow:
    @pytest.fixture(autouse=True)
    def imp(self):
        from simulador_ev3.ui.main_window import EV3SimulatorApp
        self.EV3SimulatorApp = EV3SimulatorApp

    def test_instantiation_no_crash(self):
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.pybricks_api._context import PybricksContext
        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()
        assert app is not None
        app._on_close()

    def test_cmd_run_calls_service(self):
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.pybricks_api._context import PybricksContext
        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()
        app._cmd_run("x = 1\n")
        assert app._service.is_running
        app._on_close()

    def test_cmd_stop_stops_service(self):
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.pybricks_api._context import PybricksContext
        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()
        app._cmd_run("x = 1\n")
        app._cmd_stop()
        assert not app._service.is_running
        app._on_close()

    def test_cmd_open_script_delegates_to_editor(self):
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.pybricks_api._context import PybricksContext
        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        app._editor.open_script_dialog = mock.Mock()
        app._cmd_open_script()

        app._editor.open_script_dialog.assert_called_once()
        app._on_close()

    def test_cmd_save_script_delegates_to_editor(self):
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.pybricks_api._context import PybricksContext
        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        app._editor.save_script_dialog = mock.Mock()
        app._cmd_save_script()

        app._editor.save_script_dialog.assert_called_once()
        app._on_close()

    def test_apply_scenario_loads_world_and_example(self):
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.ui import main_window as mw
        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        with mock.patch.object(mw.os.path, "exists", return_value=True), \
             mock.patch.object(app._service, "load_world_file") as load_world, \
             mock.patch.object(app._editor, "load_file") as load_file:
            app._apply_scenario("01_linea_negra.json", "06_siguelineas_basico.py")

        load_world.assert_called_once()
        load_file.assert_called_once()
        app._on_close()

    def test_apply_scenario_shows_error_when_world_missing(self):
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.ui import main_window as mw
        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        def _exists(path: str) -> bool:
            return not path.endswith("01_linea_negra.json")

        with mock.patch.object(mw.os.path, "exists", side_effect=_exists), \
             mock.patch.object(mw.messagebox, "showerror") as showerror:
            app._apply_scenario("01_linea_negra.json", "06_siguelineas_basico.py")

        showerror.assert_called_once()
        app._on_close()

    def test_on_canvas_placement_persists_theta(self):
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.pybricks_api._context import PybricksContext
        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        with mock.patch.object(app._service, "set_robot_start") as set_robot_start:
            app._on_canvas_placement(320.0, 480.0, 35.0)

        set_robot_start.assert_called_once_with(320.0, 480.0, 35.0)
        assert app._pending_robot_pose == (320.0, 480.0, 35.0)
        app._on_close()
