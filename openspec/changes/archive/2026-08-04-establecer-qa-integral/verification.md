# Verificación: QA integral y compuerta de calidad

## Comandos base

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -m unit -q
.\.venv\Scripts\python.exe -m pytest -m integration -q
.\.venv\Scripts\python.exe -m pytest -m contract -q
.\.venv\Scripts\python.exe -m pytest -m e2e -q
.\.venv\Scripts\ruff check .
.\.venv\Scripts\mypy simulador_ev3
.\.venv\Scripts\bandit -r simulador_ev3
.\.venv\Scripts\pip-audit -r requirements.txt
```

Los comandos se ajustarán únicamente si la configuración real del repositorio
define otros equivalentes. Toda ejecución registrará código de salida, entorno,
duración, advertencias y artefactos.

## Criterios de aceptación verificables

1. Existe una matriz que cubre cada funcionalidad crítica en al menos un caso
   automatizado y un caso UI real cuando tenga interacción visible.
2. Web y Tkinter ejecutan el mismo catálogo de flujos compartidos o justifican
   de forma explícita toda diferencia.
3. Un error, timeout, detención o reset no produce aviso de éxito ni conserva
   estado terminal incoherente.
4. Las pruebas de UI se ejecutan en un navegador/escritorio visibles; los casos
   no ejercitables se registran `BLOCKED` con la causa concreta.
5. No hay defectos críticos o altos abiertos para declarar una versión apta.
6. CI conserva resultados, cobertura y evidencia de fallos para auditoría.
