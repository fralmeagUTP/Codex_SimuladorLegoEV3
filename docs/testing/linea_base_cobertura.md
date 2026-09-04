# Línea base de cobertura

Fecha: 2026-07-28.

| Comando | Resultado | Cobertura |
|---|---|---|
| `.\.venv\Scripts\python.exe -m pytest --cov=simulador_ev3 --cov-report=term --cov-report=json:build\qa-coverage.json -q` | 773 aprobadas, 4 omitidas, 1 advertencia | **71.15%** global |

| Paquete | Promedio de archivos | Mínimo identificado | Decisión gradual |
|---|---:|---:|---|
| `core` | 97.8% | 92.0% | Mantener compuerta CI actual de 90% junto con `domain`. |
| `domain` | 98.1% | 88.6% | Mantener compuerta CI actual de 90% junto con `core`. |
| `web` | 82.5% | 0.0% (`waitress_server.py`) | Añadir smoke de arranque del servidor antes de elevar umbral. |
| `runtime` | 71.9% | 22.8% (`isolated_worker.py`) | Prioridad P1: recuperación, IPC y cancelación de worker. |
| `ui` | 58.9% | 21.3% (`world_editor_window.py`) | Prioridad P1: pruebas de interacción visible y componentes editor. |

La compuerta global permanece en 70% mientras se elevan gradualmente `runtime`,
`ui` y Web. Estos porcentajes son mediciones reales, no estimaciones.
