"""E2E del modo de actualizacion Web por polling sin SSE."""

from __future__ import annotations

import socket
import threading
from contextlib import closing

import pytest
from werkzeug.serving import make_server

from simulador_ev3.web.app import create_app


def _free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class _FailSseStream:
    """WSGI de prueba que simula una caída de la conexión EventSource."""

    def __init__(self, application):
        self._application = application
        self.snapshot_requests = 0

    def __call__(self, environ, start_response):
        path = str(environ.get("PATH_INFO", ""))
        if path.endswith("/stream"):
            start_response("503 Service Unavailable", [("Content-Type", "text/plain")])
            return [b"SSE unavailable"]
        if path.endswith("/snapshot"):
            self.snapshot_requests += 1
        return self._application(environ, start_response)


@pytest.fixture(scope="module")
def playwright_api():
    return pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def browser(playwright_api):
    with playwright_api.sync_playwright() as runtime:
        try:
            browser = runtime.chromium.launch(headless=True)
        except playwright_api.Error as exc:
            pytest.skip(f"Playwright Chromium no esta instalado: {exc}")
        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture()
def page(browser):
    context = browser.new_context(viewport={"width": 1366, "height": 768})
    page = context.new_page()
    try:
        yield page
    finally:
        page.close()
        context.close()


@pytest.fixture()
def expect(playwright_api):
    return playwright_api.expect


@pytest.fixture()
def polling_web_app(tmp_path):
    worlds_dir = tmp_path / "worlds"
    examples_dir = tmp_path / "examples"
    worlds_dir.mkdir()
    examples_dir.mkdir()
    app = create_app(
        {
            "TESTING": True,
            "WORLDS_DIR": worlds_dir,
            "EXAMPLES_DIR": examples_dir,
            "WEB_SSE_ENABLED": False,
            "WEB_POLLING_INTERVAL_MS": 250,
            "SCRIPT_MAX_RUNTIME_S": 2.0,
            "ENABLE_SESSION_CLEANUP_THREAD": False,
        }
    )
    port = _free_port()
    server = make_server("127.0.0.1", port, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=2)


@pytest.fixture()
def sse_failure_web_app(tmp_path):
    worlds_dir = tmp_path / "worlds"
    examples_dir = tmp_path / "examples"
    worlds_dir.mkdir()
    examples_dir.mkdir()
    app = create_app(
        {
            "TESTING": True,
            "WORLDS_DIR": worlds_dir,
            "EXAMPLES_DIR": examples_dir,
            "WEB_SSE_ENABLED": True,
            "WEB_POLLING_INTERVAL_MS": 250,
            "SCRIPT_MAX_RUNTIME_S": 2.0,
            "ENABLE_SESSION_CLEANUP_THREAD": False,
        }
    )
    wrapped_app = _FailSseStream(app)
    port = _free_port()
    server = make_server("127.0.0.1", port, wrapped_app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}", wrapped_app
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_web_executes_and_updates_telemetry_with_polling_when_sse_is_disabled(
    page, polling_web_app, expect
):
    """Sin SSE la interfaz debe seguir actualizando el snapshot por polling."""

    page.goto(f"{polling_web_app}/")
    expect(page.locator("#sessionStatus")).to_have_text("created")
    page.locator("#codeEditor").fill("from pybricks.tools import wait\nwait(100)\n")
    page.locator("#runBtn").click()

    expect(page.locator("#sessionStatus")).to_have_text("finished", timeout=7000)
    expect(page.locator("#telemetryStatus")).to_have_text("finished", timeout=7000)


def test_web_falls_back_to_polling_when_the_sse_connection_fails(
    page, sse_failure_web_app, expect
):
    """Una caída de SSE no puede impedir la sincronización terminal de la UI."""

    base_url, stream_failure = sse_failure_web_app
    page.goto(f"{base_url}/")
    expect(page.locator("#sessionStatus")).to_have_text("created")
    page.locator("#codeEditor").fill("from pybricks.tools import wait\nwait(100)\n")
    page.locator("#runBtn").click()

    expect(page.locator("#sessionStatus")).to_have_text("finished", timeout=7000)
    expect(page.locator("#telemetryStatus")).to_have_text("finished", timeout=7000)
    assert stream_failure.snapshot_requests >= 2
