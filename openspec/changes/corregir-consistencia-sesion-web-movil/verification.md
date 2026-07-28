# Evidencia de verificación

## Automatizada

- `ruff check`: aprobado.
- `pytest tests/web/test_web_app.py tests/e2e/test_web_playwright.py tests/runtime/test_isolated_worker.py -q`: 135 aprobadas.
- Regresión focalizada posterior: 2 pruebas de contrato Web y 6 E2E aprobadas.

## Revalidación gráfica visible

- URL: `http://127.0.0.1:5050/`.
- WEB-F-001: script con LCD finalizó con `finished` tanto en estado global como
  telemetría; tiempo `0.14 s` y tick `7` visibles.
- WEB-F-002: un bucle cancelado terminó en `created`, telemetría `created`,
  tick `1` y tiempo `0.02 s`.
- WEB-F-003: a 390×844 el canvas terminó en x=356 y el botón Haces en x=261,
  dentro del viewport de 390, sin overflow horizontal, en claro y oscuro.
- Navegador gráfico: Microsoft Edge WebView `149.0.4022.98`.
- La consola no registró errores ni advertencias en los flujos ejecutados.
- Las E2E registraron respuestas HTTP exitosas para creación de sesión,
  carga de script, inicio, snapshot y reset. La sesión gráfica disponible no
  expone un panel de red DevTools, por lo que este registro no sustituye una
  exportación HAR de navegador.

Capturas: `WEB-F-001-corregido-terminal.png`,
`WEB-F-002-corregido-reset.png`, `WEB-F-003-corregido-movil-claro.png` y
`WEB-F-003-corregido-movil-oscuro.png` en la carpeta de evidencia de QA Web.
