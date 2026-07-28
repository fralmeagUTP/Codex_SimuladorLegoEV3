# Diagnóstico QA

Fecha: 2026-07-24. Alcance: simulador EV3, Web Flask, Tkinter, runtime aislado y frontend.

## Arquitectura detectada

- Python 3.11+; Flask para Web, Tkinter para escritorio y JavaScript sin framework para la UI Web.
- Capas: `domain`, `core`, `application`, `runtime`, `web`, `ui`, `persistence` y `pybricks_api`.
- Ejecución de scripts mediante worker aislado; sesiones Web en memoria/archivo y Redis opcional.
- Sin base de datos relacional ni autenticación de usuarios. La autorización Web se basa en token de propietario de sesión.

## Hallazgos con evidencia

| ID | Severidad | Evidencia | Riesgo | Recomendación |
|---|---|---|---|---|
| QA-01 | Media | `README.md` informa validaciones antiguas (565), mientras la suite actual reúne 672 pruebas. | Diagnóstico de CI incorrecto. | Actualizar resultados y comandos. |
| QA-02 | Media | `ui/main_window.py` contiene múltiples `except Exception: pass`. | Fallos visuales/configuración pueden ocultarse. | Registrar o acotar excepciones en siguiente iteración. |
| QA-03 | Media | `simulation_app.js` conserva orquestación residual pese a controladores extraídos. | Riesgo de regresión frontend. | Seguir extrayendo lógica de editor y SSE/polling en cambios pequeños. |

No se confirmó defecto funcional durante esta auditoría: la evidencia ejecutable terminó sin fallos.
