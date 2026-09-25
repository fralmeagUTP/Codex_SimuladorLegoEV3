from pathlib import Path


def test_simulation_page_loads_extracted_control_modules() -> None:
    root = Path(__file__).parents[2]
    template = (root / "simulador_ev3" / "web" / "templates" / "index.html").read_text(encoding="utf-8")
    app = (root / "simulador_ev3" / "web" / "static" / "js" / "simulation_app.js").read_text(encoding="utf-8")

    for module in ("api.js", "theme_manager.js", "menu_controller.js", "canvas_world.js"):
        assert module in template
    assert "window.EV3_ASSET_MANIFEST" in template
    assert "window.EV3_STATUS_LABELS" in template
    assert "trace_controls.js" in template
    assert "profile_controls.js" in template
    assert "session_controller.js" in template
    assert "stream_health_controller.js" in template
    assert "snapshot_controller.js" in template
    assert "telemetry_controller.js" in template
    assert "world_view_controller.js" in template
    assert "editor_interaction_controller.js" in template
    assert "page_lifecycle_controller.js" in template
    assert "file_input_controller.js" in template
    assert "live_update_controller.js" in template
    assert "speaker_audio.js" in template
    assert "about_dialog.js" in template
    assert "function playSpeakerTone" not in app
    assert "EV3SpeakerAudio.handleSpeaker" in app
    assert "EV3AboutDialog.create" in app
    assert "EV3SessionController.create" in app
    assert "EV3StreamHealthController.create" in app
    assert "EV3SnapshotController.create" in app
    assert "EV3TelemetryController.create" in app
    assert "EV3WorldViewController.create" in app
    assert "EV3EditorInteractionController.bind" in app
    assert "EV3PageLifecycleController.bind" in app
    assert "EV3FileInputController.bind" in app
    assert "EV3LiveUpdateController.create" in app


def test_trace_tick_confirmation_requires_an_observable_increment() -> None:
    root = Path(__file__).parents[2]
    trace_controls = (root / "simulador_ev3" / "web" / "static" / "js" / "trace_controls.js").read_text(
        encoding="utf-8"
    )

    assert "const before" in trace_controls
    assert "const after" in trace_controls
    assert "after > before" in trace_controls
    assert "No se avanzo el tick de simulacion." in trace_controls


def test_simulation_page_uses_an_optional_learning_guide_instead_of_a_fixed_panel() -> None:
    root = Path(__file__).parents[2]
    template = (root / "simulador_ev3" / "web" / "templates" / "index.html").read_text(encoding="utf-8")
    app = (root / "simulador_ev3" / "web" / "static" / "js" / "simulation_app.js").read_text(encoding="utf-8")

    assert 'id="learningPanel"' not in template
    assert 'id="activityGuideLink"' in template
    assert '#guide-first-simulation' in template
    assert "function renderLearningState" not in app
    assert "api.learningState()" not in app


def test_world_transition_clears_web_trail_before_loading_a_new_world() -> None:
    root = Path(__file__).parents[2]
    app = (root / "simulador_ev3" / "web" / "static" / "js" / "simulation_app.js").read_text(encoding="utf-8")

    assert app.count("window.EV3Canvas.resetTrail();") >= 3


def test_simulation_composition_keeps_brick_state_below_lcd() -> None:
    root = Path(__file__).parents[2]
    template = (root / "simulador_ev3" / "web" / "templates" / "index.html").read_text(encoding="utf-8")

    assert 'class="sim-main-area"' in template
    assert 'class="sim-bottom-panels"' in template
    assert template.index('class="brick-screen"') < template.index('class="brick-robot-state"')
    assert template.index('class="sim-left-column"') < template.index('sim-panel sim-code-pane')


def test_web_canvas_repaints_after_loading_canonical_assets() -> None:
    root = Path(__file__).parents[2]
    canvas = (root / "simulador_ev3" / "web" / "static" / "js" / "canvas_world.js").read_text(
        encoding="utf-8"
    )
    app = (root / "simulador_ev3" / "web" / "static" / "js" / "simulation_app.js").read_text(
        encoding="utf-8"
    )

    assert 'new CustomEvent("ev3-assets-loaded")' in canvas
    assert 'addEventListener("ev3-assets-loaded", redrawCanvas)' in app
    assert "hydrateAssetCatalogFromApi" in canvas
    assert '"/api/editor/assets"' in canvas
