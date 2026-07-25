# Reporte de ejecución

> Evidencia actual: 2026-07-24, Windows, Python 3.12.5, version `1.4.0`.
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
