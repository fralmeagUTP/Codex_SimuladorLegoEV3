# Actualización de QA — 2026-07-30

## Ejecución consolidada

| Comando | Resultado | Evidencia |
|---|---|---|
| `.\\.venv\\Scripts\\python.exe -m pytest tests\\e2e\\test_web_playwright.py -q` | 49 aprobadas en 50.92 s | Navegación, menús, diálogos, editor, ejecución, reinicio, accesibilidad y vista móvil Web. |
| `.\\.venv\\Scripts\\python.exe -m pytest -q` | **800 aprobadas, 4 omitidas en 92.41 s** | Regresión integral de capas productivas, Web, carga y pruebas de liberación. |

## Cobertura nueva

La prueba `test_execution_locks_mutating_menus_and_restores_them_after_reset`
ejercita la interfaz Web real mediante teclado. Verifica que, con un script en
ejecución, los botones y enlaces de los menús que alteran la sesión quedan
deshabilitados y fuera de navegación. Tras **Detener y reiniciar**, valida que
los mismos elementos recuperan su estado habilitado y accesible.

La fixture E2E conserva por cada fallo una captura de página, consola JSON,
eventos de red y un archivo HAR en `artifacts/e2e-web`. Los artefactos de casos
aprobados se descartan para no contaminar el repositorio.

## Recorrido manual asistido en navegador

Se inició el servidor oficial con `scripts/start_web.ps1 -Port 5050` y se
operó una sesión Web real en navegador. Se ejecutó el script inicial y se
observó el aviso único **“El programa se ejecutó correctamente.”** después del
snapshot terminal: telemetría `finished`, tick 27, tiempo 0.54 s, LED verde y
motor A detenido en 180°. A continuación se activó **Detener y reiniciar**:
el estado volvió a `created`, la telemetría quedó en tick 1/tiempo 0.02 s, el
LED se apagó y la pose retornó a X=20 cm, Y=20 cm, theta=0°. La consola del
navegador no registró errores ni advertencias. El servidor de QA se detuvo al
terminar el recorrido.

## Limitaciones de entorno

- Las 4 omisiones corresponden a automatización Tkinter con Pywinauto: esta
  sesión no expone un escritorio Windows interactivo.
- El smoke de Docker/Linux fue aprobado localmente después de instalar Docker
  Desktop y WSL2. La imagen arranca con configuración de producción efímera y
  `/healthz` responde HTTP 200. Falta únicamente su ejecución remota en CI.
- El empaquetado Windows se generó en esta estación, pero sigue pendiente su
  ejecución en una instalación Windows limpia.
