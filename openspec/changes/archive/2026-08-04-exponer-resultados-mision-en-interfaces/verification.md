# Evidencia de verificación

Fecha: 2026-07-27. Entorno: Windows, Python 3.12, sesión Web local de prueba
con `EV3_LOCAL_RUNTIME_ENABLED=true`. El producto conserva el worker aislado
como comportamiento predeterminado; este ajuste solo evita la limitación de
`multiprocessing spawn` al ejecutar una campaña desde entrada estándar.

| Misión | Desenlace | Evidencia | Puntuación |
|---|---|---:|---:|
| Sigue líneas básico | `finished` | 723 ticks | 40/40 |
| Evita obstáculos | `finished` | 0 colisiones | 40/40 |
| Radar ultrasónico | `finished` | 288 lecturas | 40/40 |

Se ejecutó la suite completa por módulos para evitar un proceso hijo huérfano
que aparece únicamente al invocar `pytest` de forma agregada en este Windows:
`741 passed, 3 skipped` sobre 744 casos. Las tres pruebas E2E de escritorio se
omiten por la limitación documentada de Pywinauto. Ruff también pasó sobre los
archivos modificados.

## Validación visual de Tkinter

Se cargó y ejecutó manualmente **Sigue líneas básico** desde el menú
`Misiones`. La aplicación mostró `FINALIZADO` en telemetría, el estado del
editor `Misión COMPLETADA: 40 puntos` y el diálogo **Resultado de misión** con
el criterio `tiene-traza` aprobado. Tras aceptar el diálogo, la ventana siguió
operativa y se cerró sin procesos de interfaz residuales.

Evidencia: `Documentos/EVIDENCIA_INTERACCION_TKINTER_2026-07-27/`
`mision_resultado_tkinter.png` y `mision_resultado_tkinter_cerrado.png`.

También se validaron desenlaces no exitosos de la misma misión: un
`RuntimeError` controlado mostró `ERROR` y 0 puntos; la acción **Detener y
reiniciar** mostró `CANCELADA` y 0 puntos. La cancelación también restauró
posición, tick y telemetría del mundo activo. Evidencia:
`mision_fallo_tkinter.png` y `mision_cancelada_tkinter.png`.
