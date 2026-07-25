# Reporte de ejecución

> Evidencia actual: 2026-07-25, Windows, Python 3.12.5, version `1.5.0`.
> Ejecucion realizada desde el entorno limpio `C:\temp\ev3-doc-verify-20260724`.

| Comando | Objetivo | Resultado |
|---|---|---|
| `py -3.12 -m pytest -q` | Suite completa | 689 aprobadas |
| `py -3.12 -m pytest --cov=simulador_ev3 --cov-report=term-missing -q` | Suite y cobertura | 689 aprobadas; 71.50% |
| `py -3.12 -m pytest tests/e2e/test_web_playwright.py -q` | E2E real Chromium | 20 aprobadas |
| `py -3.12 -m ruff check simulador_ev3 tests` | Lint | salida 0 |
| `py -3.12 -m mypy` | Tipado | 99 módulos, salida 0 |

Cobertura real registrada: 71.50% global; el umbral configurado es 70%.
Ruff, Mypy (99 modulos), Bandit y Pip-Audit finalizaron con codigo 0. Pip-Audit
emitio advertencias de deserializacion de cache y concluyo `No known vulnerabilities found`.

## Verificación de navegación Web–Tkinter — 2026-07-25

| Comando | Objetivo | Resultado |
|---|---|---|
| `.\.venv\Scripts\python.exe -m pytest -q` | Regresión completa, incluyendo navegación | 695 aprobadas, 1 omitida por escritorio no visible. |
| `.\.venv\Scripts\python.exe -m ruff check simulador_ev3 tests` | Estilo y errores estáticos | salida 0. |
| `.\.venv\Scripts\python.exe -m mypy` | Tipado global | 100 módulos, salida 0. |
| `$env:EV3_RUN_DESKTOP_E2E='1'; ... pytest tests/e2e/test_desktop_pywinauto.py -q` | Recorrido nativo Windows con ratón | Omitida: esta sesión automatizada no expone una ventana Windows visible. |

La prueba `desktop_e2e` inicia Tkinter y navega por **Ayuda → Manual de uso**
y **Mundos → Editor de mundos** mediante controles nativos cuando hay una
sesión gráfica local. No se ejecuta en CI ni en sesiones aisladas sin escritorio.

Bandit finaliza sin hallazgos usando la configuración oficial del repositorio,
que documenta el `exec` de scripts Pybricks y el `eval` de watches como
mecanismos deliberados del runtime sandbox. Tras actualizar las herramientas
del entorno, Pip-Audit finalizó con `No known vulnerabilities found`; omite
únicamente el paquete local `simulador-ev3`, que no está publicado en PyPI.
