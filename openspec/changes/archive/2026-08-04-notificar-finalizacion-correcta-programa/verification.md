# Evidencia de verificación

Fecha: 2026-07-28. Entorno: Windows, Python 3.12.5.

- Suite completa: `755 passed, 4 skipped`.
- E2E Web Playwright: `30 passed`.
- Ruff: aprobado para `simulador_ev3` y `tests`.
- Mypy: aprobado para 106 archivos fuente.
- OpenSpec: `openspec validate notificar-finalizacion-correcta-programa --strict` aprobado.

Las pruebas E2E verifican un toast único después de que estado, telemetría y LCD alcanzan el snapshot `finished`; verifican ausencia del aviso ante error y detención manual; y verifican viewport 390×844 en los temas claro y oscuro. La regresión Tkinter valida que `messagebox.showinfo` se emite una sola vez exclusivamente para la ejecución exitosa activa.
