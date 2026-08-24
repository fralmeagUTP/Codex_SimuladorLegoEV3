# Controles de calidad

> Revisado: 2026-08-05. Versión aplicable: `1.5.0`.

La integracion continua ejecuta pruebas, Ruff, Mypy, Bandit y Pip-Audit en cada cambio.
La auditoria resuelve las dependencias directas declaradas en `requirements-audit.txt`,
por lo que no mezcla vulnerabilidades de herramientas instaladas globalmente en el equipo.

Mypy se aplica a todos los paquetes productivos declarados en `pyproject.toml`,
incluidos Web y Tkinter. La campaña vigente validó 109 archivos fuente sin
ocultar errores de contratos estabilizados.

Bandit omite las reglas `B102` y `B307` exclusivamente porque el simulador necesita
ejecutar programas Pybricks y expresiones de inspeccion de depuracion. Ambas operaciones
se realizan dentro de `RuntimeSandbox` y, en modo aislado, dentro del worker con limites
de tiempo, memoria, red y sistema de archivos. Tambien se omiten `B110` y `B112` para
callbacks opcionales de interfaz: esos callbacks no pueden interrumpir la simulacion.
No se omiten reglas de severidad alta ni se ignoran hallazgos de credenciales.

## Mínimos obligatorios por capa

| Capa | Evidencia mínima para liberar | Compuerta |
|---|---|---|
| Dominio y motor | Unidad, validaciones y escenarios críticos | pytest; cobertura de `core` y `domain` ≥ 90 %. |
| Aplicación y contratos | Integración, DTOs y recuperación | pytest de `tests/application` y `tests/runtime`. |
| Web | API, sesión, accesibilidad y E2E | pytest Web y Playwright con Chromium. |
| Tkinter | Componentes, teclado, tema y E2E visible | pytest UI; Pywinauto marcado PASS o BLOCKED con causa de entorno. |
| Seguridad y dependencias | Código estático y dependencias declaradas | Ruff, Mypy, Bandit y Pip-Audit, salida 0. |
| Rendimiento y resiliencia | Carga concurrente, cancelación y worker | `tests/load`, workers aislados y métricas verificables. |
| Empaquetado y despliegue | Arranque local y artefacto verificable | smoke Windows, contenedor Linux y `healthz`. |

Una compuerta bloqueada por falta de escritorio gráfico o infraestructura debe
figurar como **BLOCKED** con evidencia. Nunca se convierte en PASS por omitirla.

La campaña de mutación usa Mutmut sobre `web/services/simulation_session.py` y
se ejecuta en Linux/WSL: Mutmut no soporta ejecución nativa en Windows. En un
equipo Windows la comprobación queda BLOCKED localmente, pero no se elimina de
la compuerta de CI Linux.
