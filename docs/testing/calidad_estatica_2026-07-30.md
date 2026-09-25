# Calidad estática — 2026-07-30

| Comando | Resultado |
|---|---|
| `.\\.venv\\Scripts\\python.exe -m ruff check simulador_ev3 tests` | Sin incidencias. |
| `.\\.venv\\Scripts\\python.exe -m mypy` | Sin incidencias en 109 archivos fuente. |
| `.\\.venv\\Scripts\\python.exe -m bandit -q -c pyproject.toml -r simulador_ev3` | Salida 0 con la política de exclusiones documentada para el sandbox. |
| `.\\.venv\\Scripts\\python.exe -m pip_audit` | Sin vulnerabilidades conocidas. `simulador-ev3 (1.4.0)` se omite porque es un paquete local no publicado en PyPI. |
