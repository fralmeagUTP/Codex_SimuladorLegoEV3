# Inventario funcional

> Fuente: requisitos inferidos de OpenSpec, README, módulos productivos y
> campañas reales Web/Tkinter. Estado actualizado: 2026-08-05. Versión 1.5.0.

| ID | Funcionalidad | Entrada / salida | Componentes principales | Reglas y validaciones | Riesgo | Cobertura actual |
|---|---|---|---|---|---|---|
| F-01 | Ciclo de sesión | comandos de ejecutar, pausar, reanudar, detener y reset → snapshot/versionado | `application`, `runtime`, `core`, Web y Tkinter | generación vigente, cancelación, idempotencia y estado terminal | Crítico | unitario, contrato, Web/Tkinter E2E |
| F-02 | Ejecución Pybricks | script Python → estado, LCD, motores, sensores, error o timeout | `runtime`, `pybricks_api`, `domain` | imports permitidos, límite, cancelación y errores legibles | Crítico | unitario, runtime, Web/Tkinter E2E |
| F-03 | Worker aislado | comando/snapshot IPC → recuperación | `runtime/isolated_worker.py` | aislamiento de proceso, cola, fallo recuperable y eventos tardíos | Crítico | runtime, carga |
| F-04 | Mundo físico | JSON o edición gráfica → mundo validado | `domain/world`, `application/world_editor_service`, `persistence` | nombre, límites, obstáculos, meta, inicio y sensores | Alto | dominio, servicio, API, CRUD/E2E y catálogos reales |
| F-05 | Simulación | mundo + tick → posición, colisión, trazas y sensores | `core`, `domain/robot`, `domain/sensors` | paso fijo, límites, unidades y colisiones | Crítico | dominio, core, regresión |
| F-06 | Hardware virtual EV3 | API Pybricks → estado Brick/LCD/motores/sensores | `pybricks_api`, `domain/brick` | puertos A-D/S1-S4 y subconjunto de conformidad documentado | Alto | API, contrato, UI y E2E |
| F-07 | Sesión y API Web | HTTP/SSE → snapshot y persistencia de sesión | `web`, `web/session_manager.py` | token propietario, expiración, errores HTTP y recuperación | Crítico | API, integración, E2E |
| F-08 | Interfaz Web | acciones de usuario → canvas, editor, telemetría, LCD y diálogos | Flask, JS, CSS, controladores | paridad de estado, responsive, temas y accesibilidad | Alto | Playwright 55/55 y recorrido real |
| F-09 | Interfaz Tkinter | acciones nativas → canvas, editor, telemetría, LCD y diálogos | `ui`, presentadores, `tkinter` | callbacks seguros, temas, menús y foco | Alto | componentes, visual y Pywinauto 6/6 |
| F-10 | Misiones y escenarios | selección/ejecución → evaluación y resultado | `domain/assessment`, `application`, recursos | criterios de éxito/fallo/cancelación y limpieza entre misiones | Alto | unitario, catálogo y E2E |
| F-11 | Trazas y depuración | breakpoints/watches/perfil → eventos visibles | `runtime`, `web`, `ui` | no bloquear sesión ni filtrar estado de otra sesión | Alto | contrato, paridad y E2E |
| F-12 | Preferencias visuales | tema/fidelidad/tiempo máximo → configuración persistida | `shared`, Web, Tkinter | claro/oscuro, contraste y valor de límite válido | Medio | Web/Tkinter, visual y E2E |
| F-13 | Observabilidad | métricas/trazas → diagnóstico operativo | `web`, `observability` | correlación de sesión/comando/worker y datos no sensibles | Medio | Web, configuración |
| F-14 | Empaquetado y operación | entorno limpio → aplicación operable | Docker, PyInstaller, scripts de inicio | sin secretos, usuario no privilegiado, dependencias completas | Alto | contenedor y paquete Windows aprobados |

## Estados de verificación

- **Documentada:** aparece en OpenSpec, README o guía de usuario.
- **Detectada:** implementada en código o recursos, aunque no exista requisito
  formal separado.
- **Parcial:** hay pruebas de capa o recorrido visible incompleto.
- **No verificable aún:** requiere ambiente, dato sintético o instrumentación
  que no está disponible; se marca `BLOCKED` en el informe de campaña.
