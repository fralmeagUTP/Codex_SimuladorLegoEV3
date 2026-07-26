"""
Tests para la Fase 7: Capa de UI (Tkinter).

Estrategia: los módulos UI importan tkinter, que en algunos CI no tiene
display. Usamos unittest.mock para parchear el módulo completo y testear
sólo la lógica no visual (callbacks, métodos de actualización, etc.).
"""

from __future__ import annotations

import sys
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
    tk.LEFT = "left"
    tk.RIGHT = "right"
    tk.TOP = "top"
    tk.BOTTOM = "bottom"
    tk.X = "x"
    tk.Y = "y"
    tk.BOTH = "both"
    tk.W = "w"
    tk.END = "end"
    tk.NORMAL = "normal"
    tk.DISABLED = "disabled"
    tk.SUNKEN = "sunken"
    tk.RAISED = "raised"
    tk.FLAT = "flat"
    tk.SOLID = "solid"
    tk.LAST = "last"
    tk.WORD = "word"
    tk.VERTICAL = "vertical"
    tk.HORIZONTAL = "horizontal"
    tk.NONE = "none"
    tk.NW = "nw"

    # Clases stub que recuerdan llamadas
    class _Widget:
        def __init__(self, *a, **kw):
            pass

        def pack(self, **kw):
            return self

        def grid(self, **kw):
            return self

        def grid_columnconfigure(self, *a, **kw):
            return None

        def configure(self, **kw):
            return self

        def config(self, **kw):
            return self

        def bind(self, *a, **kw):
            return None

        def unbind(self, *a, **kw):
            return None

        def pack_configure(self, **kw):
            return self

        def cget(self, key):
            return ""

        def after(self, ms, fn=None, *args):
            return "after_id"

        def after_idle(self, fn, *args):
            return fn(*args) if args else fn()

        def after_cancel(self, aid):
            pass

        def destroy(self):
            pass

        def winfo_width(self):
            return 400

        def winfo_height(self):
            return 400

        def winfo_children(self):
            return []

        def delete(self, *a):
            pass

        def create_oval(self, *a, **kw):
            return 1

        def create_rectangle(self, *a, **kw):
            return 1

        def create_line(self, *a, **kw):
            return 1

        def create_polygon(self, *a, **kw):
            return 1

        def create_text(self, *a, **kw):
            return 1

        def create_image(self, *a, **kw):
            return 1

        def create_window(self, *a, **kw):
            return 1

        def bbox(self, *a, **kw):
            return (0, 0, 400, 400)

        def itemconfigure(self, *a, **kw):
            return None

        def insert(self, *a, **kw):
            return None

        def get(self, *a, **kw):
            return ""

        def index(self, *a, **kw):
            return "1.0"

        def tag_add(self, *a, **kw):
            return None

        def tag_remove(self, *a, **kw):
            return None

        def tag_configure(self, *a, **kw):
            return None

        def protocol(self, *a, **kw):
            return None

        def yview(self, *a, **kw):
            return None

        def xview(self, *a, **kw):
            return None

        def yview_moveto(self, *a, **kw):
            return None

        def xview_moveto(self, *a, **kw):
            return None

        def canvasy(self, y):
            return y

        def canvasx(self, x):
            return x

        def find_overlapping(self, *a, **kw):
            return []

        def see(self, *a):
            return None

    class _StringVar:
        def __init__(self, value=""):
            self._val = value

        def set(self, val):
            self._val = val

        def get(self):
            return self._val

    class _BooleanVar:
        def __init__(self, value=False):
            self._val = bool(value)

        def set(self, val):
            self._val = bool(val)

        def get(self):
            return bool(self._val)

    class Tk(_Widget):
        def title(self, t):
            pass

        def geometry(self, g):
            pass

        def minsize(self, w, h):
            pass

        def configure(self, **kw):
            pass

        def mainloop(self):
            pass

    class Toplevel(_Widget):
        def title(self, t):
            pass

        def geometry(self, g):
            pass

        def minsize(self, w, h):
            pass

        def configure(self, **kw):
            pass

    class Frame(_Widget):
        pass

    class LabelFrame(_Widget):
        pass

    class Canvas(_Widget):
        pass

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

    class Text(_Widget):
        pass

    class Entry(_Widget):
        pass

    class Label(_Widget):
        pass

    class Button(_Widget):
        pass

    class Menubutton(_Widget):
        pass

    class Checkbutton(_Widget):
        pass

    class Scrollbar(_Widget):
        def set(self, *a):
            pass

    class PanedWindow(_Widget):
        def add(self, widget, **kw):
            pass

    class Menu(_Widget):
        def add_command(self, **kw):
            pass

        def add_separator(self):
            pass

        def add_cascade(self, **kw):
            pass

        def entryconfigure(self, *a, **kw):
            pass

    tk.Widget = _Widget
    tk.Tk = Tk
    tk.Toplevel = Toplevel
    tk.Frame = Frame
    tk.LabelFrame = LabelFrame
    tk.Canvas = Canvas
    tk.PhotoImage = PhotoImage
    tk.Text = Text
    tk.Entry = Entry
    tk.Label = Label
    tk.Button = Button
    tk.Menubutton = Menubutton
    tk.Checkbutton = Checkbutton
    tk.Scrollbar = Scrollbar
    tk.PanedWindow = PanedWindow
    tk.Menu = Menu
    tk.StringVar = _StringVar
    tk.BooleanVar = _BooleanVar

    # filedialog / messagebox stubs
    filedialog = types.ModuleType("tkinter.filedialog")
    filedialog.askopenfilename = lambda **kw: ""
    filedialog.asksaveasfilename = lambda **kw: ""
    messagebox = types.ModuleType("tkinter.messagebox")
    messagebox.showerror = lambda *a, **kw: None
    messagebox.showinfo = lambda *a, **kw: None
    messagebox.askyesno = lambda *a, **kw: True
    scrolledtext = types.ModuleType("tkinter.scrolledtext")
    scrolledtext.ScrolledText = Text

    tk.filedialog = filedialog
    tk.messagebox = messagebox
    tk.scrolledtext = scrolledtext

    return tk, filedialog, messagebox, scrolledtext


@pytest.fixture(scope="module", autouse=True)
def patch_tkinter():
    """Instala mocks de tkinter en sys.modules antes de importar módulos UI."""
    tk, fd, mb, st = _make_tk_mock()
    sys.modules["tkinter"] = tk
    sys.modules["tkinter.filedialog"] = fd
    sys.modules["tkinter.messagebox"] = mb
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
    eng = SimulationEngine(
        config=SimEngineConfig(
            robot_x0_mm=500,
            robot_y0_mm=500,
            world_width_mm=2000,
            world_height_mm=2000,
        )
    )
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

    def test_theme_uses_web_canvas_palette(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        wc.set_theme("dark")
        assert wc._canvas_background == "#0F1724"
        assert wc._grid_color == "#213149"
        wc.set_theme("light")
        assert wc._canvas_background == "#FFFFFF"

    def test_update_from_dto_no_crash(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        dto = _snap()
        wc.update_from_dto(dto)  # no debe lanzar

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

    def test_robot_sprite_is_scaled_to_real_ev3_brick_size(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        assert wc._robot_sprite is not None
        assert wc._robot_sprite.width() == 35
        assert wc._robot_sprite.height() == 22

    def test_update_from_dto_recenters_view(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        wc.xview_moveto = mock.Mock()
        wc.yview_moveto = mock.Mock()
        wc.update_from_dto(_snap())
        assert wc.xview_moveto.called
        assert wc.yview_moveto.called

    def test_zoom_in_and_out_change_scale(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        base_scale = wc._px_per_mm
        wc.zoom_in()
        assert wc._px_per_mm > base_scale
        wc.zoom_out()
        assert wc._px_per_mm == pytest.approx(base_scale)

    def test_reset_zoom_restores_base_scale(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        base_scale = wc._px_per_mm
        wc.zoom_in()
        wc.zoom_in()
        assert wc._px_per_mm > base_scale
        wc.reset_zoom()
        assert wc._px_per_mm == pytest.approx(base_scale)

    def test_robot_sprite_rotation_is_requested_with_theta(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        wc._robot_sprite = object()
        wc._get_rotated_robot_sprite = mock.Mock(return_value=wc._robot_sprite)
        wc._draw_robot_sprite(500.0, 500.0, 42.0, False)
        wc._get_rotated_robot_sprite.assert_called_once_with(42.0)

    def test_placement_click_calls_callback_with_theta(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        received = []
        wc.enable_placement_mode(callback=lambda x_mm, y_mm, theta_deg: received.append((x_mm, y_mm, theta_deg)))
        expected_x, expected_y = wc._event_to_world(types.SimpleNamespace(x=100, y=50))

        wc._on_placement_click(types.SimpleNamespace(x=100, y=50))

        assert wc._placement_pos == pytest.approx((expected_x, expected_y))
        assert received[-1] == pytest.approx((expected_x, expected_y, 0.0))

    def test_placement_drag_updates_theta(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        received = []
        wc.enable_placement_mode(callback=lambda x_mm, y_mm, theta_deg: received.append((x_mm, y_mm, theta_deg)))
        expected_x, expected_y = wc._event_to_world(types.SimpleNamespace(x=100, y=100))

        wc._on_placement_click(types.SimpleNamespace(x=100, y=100))
        wc._on_placement_drag(types.SimpleNamespace(x=100, y=200))

        assert wc._placement_theta_deg == pytest.approx(90.0)
        assert received[-1] == pytest.approx((expected_x, expected_y, 90.0))

    def test_placement_wheel_updates_theta(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        received = []
        wc.enable_placement_mode(callback=lambda x_mm, y_mm, theta_deg: received.append((x_mm, y_mm, theta_deg)))
        wc.draw_placement_marker(400.0, 400.0, 10.0)

        wc._on_placement_wheel(types.SimpleNamespace(delta=120))

        assert wc._placement_theta_deg == pytest.approx(15.0)
        assert received[-1] == pytest.approx((400.0, 400.0, 15.0))

    def test_disabling_placement_removes_initial_marker(self):
        wc = self.WorldCanvas(mock.MagicMock(), world_w_mm=2000, world_h_mm=2000)
        wc.delete = mock.Mock()

        wc.disable_placement_mode()

        wc.delete.assert_any_call("placement_ghost")
        wc.delete.assert_any_call("placement_marker")


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

    def test_on_debug_callback_called(self):
        received = []
        ep = self.EditorPanel(mock.MagicMock(), on_debug=lambda c: received.append(c))
        ep._cmd_debug()
        assert len(received) == 1

    def test_on_debug_step_callback_called(self):
        received = []
        ep = self.EditorPanel(mock.MagicMock(), on_debug_step=lambda: received.append("step"))
        ep._cmd_debug_step()
        assert received == ["step"]

    def test_on_debug_continue_callback_called(self):
        received = []
        ep = self.EditorPanel(mock.MagicMock(), on_debug_continue=lambda: received.append("continue"))
        ep._cmd_debug_continue()
        assert received == ["continue"]

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

    def test_set_code_refreshes_linenos(self):
        ep = self.EditorPanel(mock.MagicMock())
        ep._update_linenos = mock.Mock()
        ep.set_code("a = 1\nb = 2\n")
        assert ep._update_linenos.call_count >= 1

    def test_linenos_click_toggles_breakpoint_and_notifies(self):
        received = []
        ep = self.EditorPanel(
            mock.MagicMock(),
            on_breakpoints_changed=lambda bps: received.append(sorted(bps)),
        )
        ep._linenos.index = mock.Mock(return_value="3.0")
        ep._update_linenos = mock.Mock()

        ep._on_linenos_click(types.SimpleNamespace(y=20))

        assert 3 in ep.get_breakpoints()
        assert received[-1] == [3]

    def test_breakpoints_entry_stays_synchronized_with_editor_gutter(self):
        received = []
        ep = self.EditorPanel(
            mock.MagicMock(),
            on_breakpoints_changed=lambda bps: received.append(sorted(bps)),
        )
        ep._update_linenos = mock.Mock()
        ep._breakpoints_var.set("5, 2, invalido, 0")

        ep._on_breakpoints_changed_event()

        assert ep.get_breakpoints() == {2, 5}
        assert ep._breakpoints_var.get() == "2, 5"
        assert received == [[2, 5]]

    def test_watches_are_normalized_and_notified(self):
        received = []
        ep = self.EditorPanel(
            mock.MagicMock(),
            on_watches_changed=lambda watches: received.append(watches),
        )
        ep._watches_var.set("x + 1, , velocidad * 2")

        ep._on_watches_changed_event()

        assert ep.get_watches() == ["x + 1", "velocidad * 2"]
        assert received == [["x + 1", "velocidad * 2"]]

    def test_watches_display_value_and_error(self):
        ep = self.EditorPanel(mock.MagicMock())

        ep.show_watch_results(
            [
                {"expr": "x + 1", "value": 2, "error": None},
                {"expr": "missing", "value": None, "error": "NameError"},
            ]
        )

        assert "x + 1 = 2" in ep._watch_results_var.get()
        assert "missing = error: NameError" in ep._watch_results_var.get()

    def test_autocomplete_candidates_include_pybricks_symbols(self):
        ep = self.EditorPanel(mock.MagicMock())
        items = ep._autocomplete_candidates("Dri")
        assert "DriveBase" in items

    def test_autocomplete_candidates_include_python_keywords(self):
        ep = self.EditorPanel(mock.MagicMock())
        items = ep._autocomplete_candidates("wh")
        assert "while" in items

    def test_autocomplete_candidates_include_port_context(self):
        ep = self.EditorPanel(mock.MagicMock())
        items = ep._autocomplete_candidates("S", context_name="Port")
        assert "S1" in items
        assert "S4" in items

    def test_current_completion_context_detects_dot_notation(self):
        ep = self.EditorPanel(mock.MagicMock())
        ep._text.get = mock.Mock(return_value="from pybricks.parameters import Port\nPort.S")
        obj, pref = ep._current_completion_context()
        assert obj == "Port"
        assert pref == "S"

    def test_current_completion_context_resolves_variable_type(self):
        ep = self.EditorPanel(mock.MagicMock())
        src = (
            "from pybricks.ev3devices import Motor\n"
            "from pybricks.parameters import Port\n"
            "left_motor = Motor(Port.B)\n"
            "left_motor."
        )
        ep._text.get = mock.Mock(return_value=src)
        obj, pref = ep._current_completion_context()
        assert obj == "Motor"
        assert pref == ""

    def test_current_completion_context_resolves_import_alias(self):
        ep = self.EditorPanel(mock.MagicMock())
        src = (
            "from pybricks.ev3devices import Motor as M\n"
            "from pybricks.parameters import Port\n"
            "left_motor = M(Port.B)\n"
            "left_motor.r"
        )
        ep._text.get = mock.Mock(return_value=src)
        obj, pref = ep._current_completion_context()
        assert obj == "Motor"
        assert pref == "r"

    def test_current_completion_context_resolves_chained_attribute_type(self):
        ep = self.EditorPanel(mock.MagicMock())
        src = "from pybricks.hubs import EV3Brick\nev3 = EV3Brick()\nev3.screen."
        ep._text.get = mock.Mock(return_value=src)
        obj, pref = ep._current_completion_context()
        assert obj == "Screen"
        assert pref == ""


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
        bp._update_led("GREEN")  # no debe lanzar excepción
        bp._update_led(None)  # estado apagado tampoco debe lanzar

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

    def test_dynamic_telemetry_supports_dark_then_light_theme(self):
        tp = self.TelemetryPanel(mock.MagicMock())

        tp.set_theme("dark")
        assert tp._theme == "dark"
        tp.set_theme("light")

        assert tp._theme == "light"

    def test_robot_position_reflected_in_vars(self):
        tp = self.TelemetryPanel(mock.MagicMock())
        dto = _snap()
        tp.update_from_dto(dto)
        assert tp._var_x.get() == f"{dto.robot['x_mm'] / 10.0:.1f}"
        assert tp._var_y.get() == f"{dto.robot['y_mm'] / 10.0:.1f}"

    def test_tick_var_updated(self):
        tp = self.TelemetryPanel(mock.MagicMock())
        dto = _snap()
        tp.update_from_dto(dto)
        assert tp._var_tick.get() == str(dto.tick)

    def test_sensors_are_mapped_by_port(self):
        tp = self.TelemetryPanel(mock.MagicMock())
        tp._update_sensors([{"port": "S3", "type": "ColorSensorModel", "value": 61.2}])
        assert tp._sensor_vars["S3"]["type"].get() == "ColorSensorModel"
        assert "61.2" in tp._sensor_vars["S3"]["value"].get()
        assert tp._sensor_vars["S1"]["type"].get() == "Sin conectar"

    def test_motors_are_mapped_by_port(self):
        tp = self.TelemetryPanel(mock.MagicMock())
        tp._update_motors([{"port": "B", "speed": 250.0, "angle": 42.5, "state": "RUNNING"}])
        assert tp._motor_vars["B"]["state"].get() == "RUNNING"
        assert tp._motor_vars["A"]["state"].get() == "Sin conectar"


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

    def test_exposes_simulate_saved_action_disabled_until_a_valid_save(self):
        tb = self._new_toolbar()
        assert tb._simulate_saved_button is not None
        tb.set_simulate_saved_enabled(True)


class TestMainWindow:
    @pytest.fixture(autouse=True)
    def imp(self):
        from simulador_ev3.ui.main_window import EV3SimulatorApp

        self.EV3SimulatorApp = EV3SimulatorApp

    def test_instantiation_no_crash(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()
        assert app is not None
        app._on_close()

    def test_cmd_run_calls_service(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.runtime.runtime_controller import ControllerState

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()
        app._cmd_run("x = 1\n")
        assert app._service.controller_state in (
            ControllerState.RUNNING,
            ControllerState.STOPPED,
        )
        app._on_close()

    def test_cmd_stop_stops_service(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()
        app._cmd_run("x = 1\n")
        app._cmd_stop()
        assert not app._service.is_running
        app._on_close()

    def test_simulation_control_states_follow_execution_state(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()
        app._sim_control_buttons = {key: mock.Mock() for key in ("run", "pause", "resume", "stop")}

        app._sync_sim_control_states("started")

        assert app._sim_control_buttons["run"].configure.call_args.kwargs["state"] == "disabled"
        assert app._sim_control_buttons["pause"].configure.call_args.kwargs["state"] == "normal"
        assert app._sim_control_buttons["resume"].configure.call_args.kwargs["state"] == "disabled"
        assert app._sim_control_buttons["stop"].configure.call_args.kwargs["state"] == "normal"

        app._sync_sim_control_states("paused")
        assert app._sim_control_buttons["pause"].configure.call_args.kwargs["state"] == "disabled"
        assert app._sim_control_buttons["resume"].configure.call_args.kwargs["state"] == "normal"
        app._on_close()

    def test_simulation_control_palette_uses_shared_theme_tokens(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.shared.ui_design_tokens import DARK_TOKENS

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()
        app._sim_control_buttons = {key: mock.Mock() for key in ("run", "pause", "resume", "stop")}
        app._pose_control_button = mock.Mock()
        app._theta_label = mock.Mock()

        app._apply_sim_control_palette(DARK_TOKENS)

        assert app._sim_control_buttons["run"].configure.call_args.kwargs["bg"] == DARK_TOKENS.primary
        assert app._sim_control_buttons["pause"].configure.call_args.kwargs["bg"] == DARK_TOKENS.surface
        assert app._sim_control_buttons["stop"].configure.call_args.kwargs["bg"] == DARK_TOKENS.surface
        assert app._pose_control_button.configure.call_args.kwargs["fg"] == DARK_TOKENS.text
        assert app._theta_label.configure.call_args.kwargs["bg"] == DARK_TOKENS.surface
        app._on_close()

    def test_escape_closes_the_active_auxiliary_dialog(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()
        about = mock.Mock()
        about.winfo_exists.return_value = True
        app._about_window = about
        app._manual_window = mock.Mock()

        assert app._evt_escape() == "break"
        about.destroy.assert_called_once()
        assert app._about_window is None
        assert app._manual_window is not None
        app._on_close()

    def test_close_cancels_pending_resize_callback(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()
        app.after_cancel = mock.Mock()
        app._tick_id = None
        app._resize_after_id = "pending-resize"

        app._on_close()

        app.after_cancel.assert_called_once_with("pending-resize")
        assert app._resize_after_id is None

    def test_ephemeral_window_does_not_restore_or_persist_user_session(self):
        from simulador_ev3.ui import main_window as mw

        with mock.patch.object(mw, "load_desktop_session") as load_session:
            app = self.EV3SimulatorApp(restore_session=False, persist_session=False)

        load_session.assert_not_called()
        with mock.patch.object(mw, "save_desktop_session") as save_session:
            app._on_close()

        save_session.assert_not_called()

    def test_menu_buttons_follow_execution_lock_state(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()
        menu_button = mock.Mock()
        app._lockable_menu_buttons = [menu_button]

        app._set_execution_menu_locked(True)
        menu_button.configure.assert_called_with(state="disabled")
        app._set_execution_menu_locked(False)
        menu_button.configure.assert_called_with(state="normal")
        app._on_close()

    def test_sensor_beams_button_uses_the_web_on_off_labels(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()
        app._sensor_beams_button = mock.Mock()
        app._canvas.set_sensor_beams_enabled = mock.Mock()

        app._on_toggle_sensor_beams()

        assert app._sensor_beams_var.get() is False
        app._sensor_beams_button.configure.assert_called_once_with(text="Haces OFF")
        app._canvas.set_sensor_beams_enabled.assert_called_once_with(False)
        app._on_close()

    def test_cmd_open_script_delegates_to_editor(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        app._editor.open_script_dialog = mock.Mock()
        app._cmd_open_script()

        app._editor.open_script_dialog.assert_called_once()
        app._on_close()

    def test_cmd_save_script_delegates_to_editor(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        app._editor.save_script_dialog = mock.Mock()
        app._cmd_save_script()

        app._editor.save_script_dialog.assert_called_once()
        app._on_close()

    def test_apply_scenario_loads_world_and_example(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.ui import main_window as mw

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        with (
            mock.patch.object(mw.Path, "exists", return_value=True),
            mock.patch.object(app._service, "load_world_file") as load_world,
            mock.patch.object(app._editor, "load_file") as load_file,
        ):
            app._apply_scenario("01_linea_negra.json", "11_siguelineas_basico.py")

        load_world.assert_called_once()
        load_file.assert_called_once()
        app._on_close()

    def test_apply_scenario_shows_error_when_world_missing(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.ui import main_window as mw

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        with (
            mock.patch.object(mw.Path, "exists", side_effect=[False, True]),
            mock.patch.object(mw.messagebox, "showerror") as showerror,
        ):
            app._apply_scenario("01_linea_negra.json", "11_siguelineas_basico.py")

        showerror.assert_called_once()
        app._on_close()

    def test_on_canvas_placement_persists_theta(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        with mock.patch.object(app._service, "set_robot_start") as set_robot_start:
            app._on_canvas_placement(320.0, 480.0, 35.0)

        set_robot_start.assert_called_once_with(320.0, 480.0, 35.0)
        assert app._pending_robot_pose == (320.0, 480.0, 35.0)
        app._on_close()

    def test_read_manual_text_returns_string(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        text = app._read_manual_text()

        assert isinstance(text, str)
        assert len(text) > 0
        app._on_close()

    def test_manual_includes_the_shared_web_tutorials(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        text = app._tutorials_as_text()

        assert "Crear tu primer mundo" in text
        assert "Ejecutar un script" in text
        assert "Depurar por pasos" in text
        app._on_close()

    def test_format_runtime_error_includes_script_line(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        payload = {
            "error": "'DriveBase' object has no attribute 'screen'",
            "traceback": (
                "Traceback (most recent call last):\n"
                '  File "<script>", line 12, in <module>\n'
                "AttributeError: 'DriveBase' object has no attribute 'screen'\n"
            ),
        }
        msg = app._format_runtime_error(payload)

        assert "Linea 12" in msg
        assert "DriveBase" in msg
        app._on_close()

    def test_format_runtime_error_includes_debug_last_lines(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        payload = {
            "error": "division by zero",
            "traceback": "",
            "debug_last_lines": [4, 5, 6, 7],
        }
        msg = app._format_runtime_error(payload)

        assert "Ultimas lineas ejecutadas" in msg
        assert "4, 5, 6, 7" in msg
        app._on_close()

    def test_on_error_shows_line_in_dialog_when_traceback_has_script_line(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.ui import main_window as mw

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        payload = {
            "error": "fallo",
            "traceback": 'File "<script>", line 7, in <module>\n',
        }
        with mock.patch.object(mw.messagebox, "showerror") as showerror:
            app._on_error(payload)

        showerror.assert_called_once()
        _, shown_msg = showerror.call_args[0]
        assert "Linea 7" in shown_msg
        app._on_close()

    def test_cmd_debug_calls_service_start_with_debug_true(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        with mock.patch.object(app._service, "start") as start:
            app._cmd_debug("x = 1\n")

        start.assert_called_once_with(debug=True, step_mode=False)
        app._on_close()

    def test_cmd_debug_step_starts_step_mode_when_stopped(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        with mock.patch.object(app._service, "start") as start:
            app._cmd_debug_step()

        start.assert_called_once_with(debug=True, step_mode=True)
        app._on_close()

    def test_cmd_debug_step_calls_service_step_when_running(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        with (
            mock.patch.object(type(app._service), "is_running", new_callable=mock.PropertyMock, return_value=True),
            mock.patch.object(app._service, "debug_step") as debug_step,
        ):
            app._cmd_debug_step()

        debug_step.assert_called_once()
        app._on_close()

    def test_cmd_debug_continue_calls_service_when_running(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        with (
            mock.patch.object(type(app._service), "is_running", new_callable=mock.PropertyMock, return_value=True),
            mock.patch.object(app._service, "debug_continue") as debug_continue,
        ):
            app._cmd_debug_continue()

        debug_continue.assert_called_once()
        app._on_close()

    def test_menu_lock_state_follows_execution_status(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        assert app._execution_menu_locked is False

        app._on_status("started")
        assert app._execution_menu_locked is True

        app._on_status("stopped")
        assert app._execution_menu_locked is True

        app._on_status("finished")
        assert app._execution_menu_locked is True

        app._on_status("timed_out")
        assert app._execution_menu_locked is True

        app._on_status("reset")
        assert app._execution_menu_locked is False
        app._on_close()

    def test_finished_status_preserves_final_robot_instead_of_reactivating_placement(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        with (
            mock.patch.object(app, "_activate_placement_mode") as activate,
            mock.patch.object(app, "_preserve_final_robot_visual") as preserve,
        ):
            app._on_status("finished")

        preserve.assert_called_once_with("finished")
        activate.assert_not_called()
        app._on_close()

    def test_stop_and_reset_applies_initial_snapshot_to_all_tkinter_views(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()
        initial = _snap()

        with (
            mock.patch.object(app._service, "reset") as reset,
            mock.patch.object(app._service, "current_snapshot", return_value=initial),
            mock.patch.object(app, "_apply_snapshot") as apply_snapshot,
        ):
            app._cmd_stop_and_reset()

        reset.assert_called_once()
        apply_snapshot.assert_called_once_with(initial)
        app._on_close()

    def test_guard_menu_locked_shows_message_when_blocked(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory
        from simulador_ev3.ui import main_window as mw

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        app._set_execution_menu_locked(True)
        with mock.patch.object(mw.messagebox, "showinfo") as showinfo:
            assert app._guard_menu_locked() is True

        showinfo.assert_called_once()
        app._on_close()

    def test_cmd_new_is_blocked_while_menu_locked(self):
        from simulador_ev3.pybricks_api._context import PybricksContext
        from simulador_ev3.pybricks_api.factory import PybricksFactory

        PybricksFactory.cleanup()
        PybricksContext.clear()
        app = self.EV3SimulatorApp()

        app._set_execution_menu_locked(True)
        app._editor.set_code = mock.Mock()
        app._cmd_new()

        app._editor.set_code.assert_not_called()
        app._on_close()
