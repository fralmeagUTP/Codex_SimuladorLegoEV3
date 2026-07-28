# Evidencia de verificación

Fecha: `2026-07-25`  
Entorno: Windows, Python 3.12.5, Simulador EV3 1.4.0

## Tareas completadas

| Tarea | Evidencia |
| --- | --- |
| 1.1–1.3 | Mapa de destinos en `design.md`, matriz de paridad y manual actualizados. |
| 2.1–2.4 | `shared/help_tutorials.py`, ayuda Tkinter contextual y acción `Simular mundo guardado`. |
| 3.1 | Playwright cubre tutoriales y navegación Ayuda → Mundos → Simulación. |
| 3.2 | `tests/e2e/test_desktop_pywinauto.py` controla menús nativos con ratón en Windows. |
| 3.3 | Pruebas de contrato para tutoriales y de transición de mundo guardado. |
| 3.4 | La suite, Ruff y Mypy se ejecutaron; el informe está en `docs/testing/reporte_ejecucion.md`. |

## Comandos ejecutados

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check simulador_ev3 tests
.\.venv\Scripts\python.exe -m mypy
$env:EV3_RUN_DESKTOP_E2E='1'; .\.venv\Scripts\python.exe -m pytest tests/e2e/test_desktop_pywinauto.py -q
```

## Resultado

- Suite completa: `695 passed, 1 skipped`.
- Ruff: correcto.
- Mypy: `Success: no issues found in 100 source files`.
- El recorrido Web E2E está ejecutado.
- La prueba `desktop_e2e` fue omitida de forma intencional porque la sesión de
  automatización no expone una ventana Windows visible. En una sesión local
  visible, se habilita con `EV3_RUN_DESKTOP_E2E=1` y no se omite.

## Controles de seguridad

- Bandit con la configuración oficial del repositorio finaliza sin hallazgos.
  La configuración documenta como mecanismos deliberados del sandbox el
  `exec` de scripts Pybricks y el `eval` de watches.
- Las herramientas del entorno de desarrollo se actualizaron y Pip-Audit
  concluyó `No known vulnerabilities found`. El paquete local
  `simulador-ev3` se omite de la consulta porque no existe publicado en PyPI;
  no es una vulnerabilidad.
