# Estrategia de pruebas

> Estado: actual al 2026-07-25. Version aplicable: `1.5.0`. Los datos de prueba
> son mundos y scripts sinteticos del repositorio; nunca datos de produccion ni secretos.

| Tipo | Herramienta | Prioridad | Criterio de aprobación |
|---|---|---|---|
| Unidad/dominio | pytest | Crítica | motor, Pybricks y validaciones pasan |
| Integración/API | pytest + Flask test client | Crítica | sesiones, errores y mundos preservan contrato |
| Worker/resiliencia | pytest | Crítica | aislamiento, cancelación y recuperación pasan |
| E2E Web | Playwright Chromium | Alta | flujos de usuario críticos pasan |
| UI Tkinter | pytest | Alta | contrato, componentes, teclado y estados verificables pasan |
| Paridad de interfaz | pytest + catalogo compartido | Alta | Web y Tkinter producen estados equivalentes |
| Regresion visual | capturadores Web/Tkinter | Media | evidencia reproducible; comparacion automatica planificada |
| Estático | Ruff, Mypy, Bandit, Pip-Audit | Alta | salida 0 |
| Carga | pytest tests/load | Media | sesiones sin error en escenario smoke |

## Ejecucion local

```powershell
py -3.12 -m pytest -q
py -3.12 -m pytest --cov=simulador_ev3 --cov-report=term-missing -q
py -3.12 -m pytest tests/e2e/test_web_playwright.py -q
py -3.12 -m ruff check simulador_ev3 tests
py -3.12 -m mypy
py -3.12 -m bandit -q -c pyproject.toml -r simulador_ev3 --severity-level medium
py -3.12 -m pip_audit -r requirements-audit.txt
```

Playwright exige Chromium instalado: `py -3.12 -m playwright install chromium`.
El umbral global de cobertura configurado es 70%; core y domain tienen un gate
dedicado de 90% en CI. La salida esperada para cada comando es codigo 0.
