# Estado actual del proyecto

> Vigencia: 2026-08-05. Versión: `1.5.0`. Rama evaluada:
> `codex/desbloquear-menus-al-finalizar-ejecucion`.

## Dictamen

**Apta con observaciones.** No hay defectos críticos o altos abiertos en el
alcance evaluado. Web y Tkinter alcanzaron la paridad funcional definida por
OpenSpec. El PR #4 contiene el cierre publicado y sus comprobaciones remotas
aprobaron.

## Línea base técnica

| Área | Estado vigente |
|---|---|
| Python | 3.11 y 3.12 soportados |
| Web | Flask/Waitress, sesiones independientes, SSE/polling |
| Escritorio | Tkinter en Windows, worker aislado predeterminado |
| Simulación | Tick nominal de 20 ms (50 Hz) |
| Persistencia | Mundos JSON; backends de sesión configurables |
| Observabilidad | `/healthz`, métricas JSON/Prometheus y OpenTelemetry |
| Calidad | Pytest, Playwright, Pywinauto, Ruff, Mypy, Bandit, Pip-Audit |
| Despliegue | Windows local/paquete y Linux en contenedor sin privilegios |

## Evidencia de cierre

- Suite global: **829 aprobadas, 6 omitidas** en 111,87 s.
- E2E Tkinter explícito: **6/6 aprobadas** en 34,84 s; cubre las seis omisiones
  condicionadas por `EV3_RUN_DESKTOP_E2E`.
- E2E Web: **55/55 aprobadas**.
- Catálogos reales: Web 23 ejemplos, 12 mundos, 4 escenarios y 3 misiones;
  Tkinter 23 ejemplos y 12 mundos.
- Ruff y Mypy global: aprobados; Mypy cubre 109 archivos fuente.
- GitHub Actions: Windows 3.11/3.12, Linux 3.11/3.12, E2E Web, evidencia
  Tkinter, contenedor, empaquetado, cobertura, carga y resiliencia aprobados.
- OpenSpec: 15 especificaciones base válidas en modo estricto.

Fuente detallada:
`Documentos/INFORME_PRELIBERACION_PARIDAD_2026-08-04.md` (actualizado como
informe final el 2026-08-05) y `Documentos/LINEA_BASE_PARIDAD_2026-08-04.md`.

## Observaciones no bloqueantes

- Los menús owner-drawn de Tkinter no son enumerables de forma totalmente
  estable por Win32. El E2E usa un oráculo de estado aplicado y ejecuta un
  comando real del menú.
- La compatibilidad Pybricks es deliberadamente parcial y educativa; consultar
  `Documentos/DIFERENCIAS_SIMULADOR_ROBOT.md`.
- Las cifras de QA siempre son evidencia del commit y entorno indicados; deben
  repetirse antes de una nueva liberación.

## Fuentes canónicas

- Versión: `simulador_ev3/_version.py`.
- Dependencias y herramientas: `pyproject.toml`.
- Arquitectura: `Documentos/ARQUITECTURA_C4.md` y `openspec/specs/`.
- Operación: `Documentos/GUIA_OPERACION_WINDOWS.md` y
  `Documentos/GUIA_DESPLIEGUE_LINUX.md`.
- Configuración: `simulador_ev3/web/config.py` y
  `Documentos/REFERENCIA_CONFIGURACION.md`.
- QA: workflows de `.github/workflows/` y `docs/testing/`.
