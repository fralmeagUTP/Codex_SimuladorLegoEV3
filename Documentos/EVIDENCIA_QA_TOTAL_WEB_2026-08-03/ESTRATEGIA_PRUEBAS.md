# Estrategia de pruebas — QA total Web

## Objetivo

Verificar el Simulador EV3 Pybricks Web en una instancia real, separando con
claridad evidencia manual visible, pruebas E2E aisladas y pruebas de API.

## Pirámide y criterio de aprobación

| Nivel | Alcance | Herramienta | Criterio |
|---|---|---|---|
| Manual UI | Menús, canvas, editor, mundos, temas, diálogos y controles | Navegador gráfico | PASS solo tras acción visible y resultado observado. |
| E2E | Sesiones, ayuda, responsive, ejecución y paridad de flujo | Playwright/Pytest | Aprobación de todas las aserciones. |
| Integración/API | Contratos, token, límites, editor y errores | Pytest/Flask test client | Código HTTP y payload esperados. |
| Calidad | Lint, tipos, seguridad, dependencias, cobertura y build | Ruff, Mypy, Bandit, Pip-Audit, pytest, Docker | Registrar código de salida y hallazgos. |

Un resultado E2E o API no convierte un caso manual no ejercitado en PASS. Todo
caso sin control de la interfaz requerida se marca BLOCKED.

## Prioridad

1. Crítica: ejecución, pausa, detención, reinicio, sincronía de snapshot,
   cancelación, sesiones y aislamiento del runtime.
2. Alta: depuración, catálogos, CRUD de mundos, recuperación y móvil.
3. Media: accesibilidad, navegación, tema y ayudas.

## Ambientes y datos

- Manual oficial: `.venv`, Waitress, `http://127.0.0.1:5052/`.
- E2E: servidor efímero aislado que inicia la suite.
- Datos: scripts sintéticos, mundos temporales y catálogos incluidos. No se
  usan cuentas, secretos ni datos de producción.

## Salida de la campaña

No apta para liberar si permanece un defecto crítico reproducible, un error
500 en un control principal o desincronización entre estado global y snapshot.
