import inspect
import simulador_ev3.web.app as app_mod
from simulador_ev3.web.app import create_app

print("app_module:", app_mod.__file__)
src = inspect.getsource(app_mod)
print("has_file_store_import:", "from simulador_ev3.web.file_session_store import FileSessionStore" in src)
print("has_create_metadata_store:", "def _create_metadata_store" in src)

app = create_app({"TESTING": True})
mgr = app.extensions["session_manager"]
diag = mgr.diagnostics()
print("metadata_mirror:", diag.get("metadata_mirror"))