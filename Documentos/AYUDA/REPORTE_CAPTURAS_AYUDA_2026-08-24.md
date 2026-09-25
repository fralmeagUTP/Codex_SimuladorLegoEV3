# Reporte de capturas para el Centro de ayuda

Fecha: 2026-08-24  
Versión de interfaz: 1.5.0  
Datos: sintéticos y locales; no se usaron credenciales ni sesiones de usuarios.

## Web

Generado por `scripts/capture_web_evidence.py` en una instancia local temporal,
usando Chromium automatizado y una resolución de 1280×800 para composición,
además de flujos específicos a 1366×768.

- Tema claro y oscuro de simulación y Editor de mundos.
- Menú de ejemplos, editor con autocompletado, Brick/LCD y telemetría.
- Previsualización y propiedades del Editor de mundos.
- Dos sesiones independientes para confirmar aislamiento visual básico.

Los resultados están en `Documentos/EVIDENCIA_AYUDA_2026-08-24/web/`. Las
capturas usadas directamente por la ayuda se copiaron a
`simulador_ev3/web/static/images/help/web/` y están vinculadas desde el
manifiesto canónico.

## Tkinter

Generado por `scripts/capture_desktop_evidence.py` en sesión gráfica de
Windows, con comprobación de distribución (`--verify-layout`).

- Simulación en temas claro y oscuro a 1280×800.
- Editor de mundos con los controles y assets vigentes.
- Comprobación: telemetría, Brick y LCD tuvieron geometría visible y
  alcanzable durante la captura.

Los resultados están en `Documentos/EVIDENCIA_AYUDA_2026-08-24/tkinter/` y
las referencias reutilizables en `simulador_ev3/web/static/images/help/tkinter/`.

## Incidencia corregida en el capturador

El flujo de mundos esperaba el texto obsoleto `Tool:`. La interfaz actual usa
`Herramienta:`; el script se actualizó para que las capturas fallen solo ante
una regresión real de la interfaz y no por la traducción ya implementada.

## Verificación de calidad automatizada

Ejecutada el 2026-08-24 sobre los recursos publicados de ayuda:

- 16 pruebas unitarias y de integración: contrato versionado, privacidad del
  progreso local, manifiesto y hashes de capturas, ejemplos seguros, ruta
  docente, reinicio del progreso, portapapeles y cierre seguro de Tkinter.
- 3 pruebas end-to-end Playwright: búsqueda y categorías, marcado y
  persistencia del recorrido, modo docente, teclado, tema oscuro, móvil
  390×844 y preferencia de reducción de movimiento.
- Análisis estático Ruff de los módulos y pruebas del cambio: sin hallazgos.

Resultado: todas las pruebas automatizadas indicadas finalizaron correctamente.
La validación manual con estudiantes y docente permanece pendiente y no está
representada como evidencia automatizada.

## Renovación de capturas por guía

Las imágenes publicadas de ayuda se regeneraron desde una instancia local real
de la aplicación Web. Cada guía dispone ahora de una escena propia, en lugar de
reutilizar una captura genérica: ejecución, motores y sensores, depuración,
error de programa, validación de mundo, misiones, trazas, tiempo máximo y
diagnóstico de sesión. El capturador publica los PNG canónicos y el manifiesto
verifica sus hashes, tamaño, formato, cobertura y ausencia de marcadores
sensibles.
