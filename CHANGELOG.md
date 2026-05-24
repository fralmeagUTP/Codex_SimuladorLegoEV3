# Changelog

## v1.3.2 - 2026-05-24

- Corregidos flujos de ejecucion web para evitar estados colgados y mejorar respuesta al finalizar script.
- Unificados controles de parada en `Detener y reiniciar` para reducir ambiguedad operacional.
- Agregado reinicio automatico de simulacion al terminar ejecucion para dejar la sesion en estado limpio.
- Mejorada la experiencia de depuracion con resaltado de linea actual y estabilidad de controles.
- Ajustadas pruebas E2E y de release a la nueva paleta del editor de mundos y al catalogo educativo de ejemplos renombrados.
- Consolidado testeo integral: `565 passed`.

## v1.3.1 - 2026-05-22

- Mejorada la ayuda web con enfoque didactico, tutoriales guiados y recursos visuales integrados.
- Adaptada la ayuda para despliegue en `http://nyquist.app/simuladorlego` con navegacion por menu sin rutas manuales.
- Ajustado el editor de mundos: eliminada opcion `Guardar` y flujo centrado en `Guardar como` con selector nativo del sistema.
- Reemplazado el campo editable de nombre de mundo por una etiqueta informativa al abrir/importar mundos.
- Agregada documentacion de despliegue en cPanel, archivo `requirements.txt`, plantilla `wsgi` y checklist post-deploy.

## v1.3.0 - 2026-05-20

- Publicada version web Flask con simulacion, editor de mundos, sesiones independientes y evidencia visual.
- Alineado el mapa web con Tkinter: escala `32 px = 100 mm`, canvas de mundo del mismo tamano y scroll cuando no cabe en el panel.
- Corregida la colocacion y arrastre de assets web para coincidir con el editor Tkinter.
- Corregido estado de ejecucion web para que scripts finalizados pasen a `stopped` y no aparenten quedar colgados.
- Agregadas pruebas unitarias web, E2E Playwright y pruebas de release.
- Agregados scripts Windows para iniciar, detener, reiniciar, validar smoke y capturar evidencia web.
- Agregada documentacion de uso, migracion web, QA y guia de operacion Flask/Windows.

## v0.2.0 - 2026-05-19

- Agregada version web Flask con sesiones independientes.
- Separadas las pantallas `/` para simulacion y `/worlds` para editor de mundos.
- Agregado streaming SSE con fallback por polling.
- Agregados controles web de debug: breakpoints, step y continue.
- Reorganizada la UI web para acercarla a la distribucion de la app Tkinter.
- Agregado cleanup periodico de sesiones expiradas.
- Agregada CI de tests en Windows con GitHub Actions.
- Agregada checklist QA de release.
- Agregadas pruebas E2E Playwright con Chromium para simulacion, editor de mundos, ayuda y aislamiento entre perfiles de navegador.
- Agregada evidencia QA de release 2026-05-20 con resultados automatizados por bloque.
- Verificado build Windows con PyInstaller y recursos de ejemplos/mundos incluidos.
- Agregado script de evidencia visual web para capturar viewports y perfiles independientes.
- Ajustado layout web para mantener simulacion/editor visibles en 1366x768.
- Corregida la miniatura de `floor_tile_256_c` para usar el asset `.jpg` real.
- Ampliadas pruebas unitarias web para helpers, contratos de error, assets, sesiones y uploads.

## v0.1.0

- Version inicial del simulador educativo EV3 con dominio, runtime, API Pybricks virtual, UI Tkinter, mundos JSON y pruebas base.
