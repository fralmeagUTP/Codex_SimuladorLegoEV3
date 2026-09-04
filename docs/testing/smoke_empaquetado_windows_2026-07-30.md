# Smoke del empaquetado Windows — 2026-07-30

Se validó el artefacto generado por el empaquetado oficial:

`dist/SimuladorEV3/SimuladorEV3.exe`

El proceso se inició oculto, permaneció activo durante cinco segundos y se
cerró de forma controlada exclusivamente usando el identificador del proceso
de prueba.

| Indicador | Resultado |
|---|---|
| Proceso iniciado | Sí (PID 10412) |
| Activo tras 5 s | Sí |
| Código de salida antes de cierre | No aplicable: seguía en ejecución |

Esto confirma que el artefacto inicia en el equipo de construcción. No
reemplaza el smoke en una instalación Windows limpia ni una prueba E2E de la
ventana visible.
