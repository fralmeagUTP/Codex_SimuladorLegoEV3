# Tareas: establecer QA integral y compuerta de calidad

## Fase 1 — Gobierno, inventario y riesgo

- [x] 1.1 Consolidar requisitos documentados e inferidos en un inventario funcional versionado.
- [x] 1.2 Clasificar cada funcionalidad por criticidad, riesgo, capa, interfaz y cobertura actual.
- [x] 1.3 Crear matriz de trazabilidad requisito → riesgo → caso → automatización → evidencia.
- [x] 1.4 Registrar catálogo de defectos confirmados y convertirlos en regresiones priorizadas.

## Fase 2 — Fundaciones automatizadas

- [x] 2.1 Normalizar marcadores pytest: `unit`, `integration`, `contract`, `ui`, `e2e`, `security`, `performance`, `release`.
- [x] 2.2 Crear fixtures, fábricas y mundos temporales aislados; prohibir escritura sobre recursos de usuario.
- [x] 2.3 Medir cobertura real por paquete productivo y establecer umbrales graduales por capa.
- [x] 2.4 Añadir pruebas de mutación o escenarios equivalentes para motor, runtime y transiciones de sesión críticas.
- [x] 2.5 Ejecutar Ruff, Mypy, Bandit y Pip-Audit con resultados reproducibles en local y CI.

## Fase 3 — Funcionalidad y contratos

- [x] 3.1 Cubrir CRUD y validaciones de mundos, persistencia, cancelación y recuperación de errores.
- [x] 3.2 Cubrir catálogo Pybricks soportado: motores A–D, DriveBase, LCD, sensores, temporizadores, errores y límites.
- [x] 3.3 Cubrir sesión terminal: `finished`, `error`, `timed_out`, `stopped`, `reset` y eventos tardíos.
- [x] 3.4 Añadir regresión para que un error de script deje editor, barra, canvas, LCD y telemetría en `ERROR`, no `EJECUTANDO`.
- [x] 3.5 Validar paridad de casos de uso Web/Tkinter y documentar diferencias justificadas.

## Fase 4 — UI real, E2E y accesibilidad

- [x] 4.1 Automatizar Web con Playwright visible: menús, diálogos, editor, mundos, misiones, controles y navegación.
- [ ] 4.2 Automatizar Tkinter con escritorio Windows visible: introducción, menús, diálogos nativos, editor, canvas y cierre.
- [x] 4.3 Ejecutar el catálogo crítico en claro/oscuro y resoluciones requeridas; incluir móvil 390×844 para Web.
- [ ] 4.4 Verificar teclado, foco, Escape, contraste, texto truncado, lectores de estado `aria-live` y orden de tabulación. *(Parcial: se automatizó Flecha abajo/Escape/foco, Tab/Shift+Tab/Enter, las 10 entradas de la barra de menú Web, el bloqueo/restauración de menús durante ejecución y los controles secundarios Web de Ayuda/Acerca de/haces/ubicación del robot; los 10 pares críticos de contraste Web ya pasan. Falta revisión equivalente de Tkinter en un escritorio visible.)*
- [ ] 4.5 Guardar capturas antes/después, consola, red y logs de cada fallo real. *(Parcial: E2E Web conserva automáticamente captura, consola, eventos de red erróneos y un HAR por cada fallo; faltan reconstruir evidencia de fallos manuales y la campaña Tkinter visible.)*

## Fase 5 — Seguridad, rendimiento y resiliencia

- [x] 5.1 Probar entradas maliciosas o inválidas de scripts, mundos, API y rutas sin exponer datos reales.
- [x] 5.2 Medir latencia, ticks, memoria, cola y sesiones bajo carga sintética controlada. *(Incluye smoke concurrente, workers aislados y carga sostenida de 12 operaciones con latencia individual <2 s y duración total <5 s en entorno de prueba; no sustituye un SLA de producción.)*
- [x] 5.3 Ejercitar caída/recuperación de worker, cancelación, recarga y eventos retrasados. *(QA-REG-006, QA-REG-007 y QA-REG-009 fueron corregidas y cubiertas; QA-REG-010 fue revalidada en el escenario Web.)*
- [x] 5.4 Validar límites configurables, bucles no terminantes y capacidad de detención manual.
- [ ] 5.5 Ejecutar smoke de Docker/Linux y empaquetado Windows, con instalación limpia y configuración por entorno. *(Parcial: el empaquetado Windows oficial generó `dist/SimuladorEV3/SimuladorEV3.exe` de 6,686,829 bytes con Ejemplos y Mundos el 2026-07-30; el ejecutable permaneció activo cinco segundos en un smoke local y se cerró de forma controlada. El 2026-07-30 se instaló Docker Desktop/WSL2, se construyó `simulador-ev3:qa-local-20260730` y `/healthz` respondió HTTP 200. Se corrigieron el host del contenedor (`EV3_WEB_HOST=0.0.0.0`) y las variables seguras del job Docker. Falta ejecutar los jobs remotos `docker-smoke` y `windows-release-smoke`.)*

## Fase 6 — Reporte y compuerta de liberación

- [x] 6.1 Publicar diagnóstico, estrategia, casos, matriz de trazabilidad y reporte de ejecución bajo `docs/testing/`.
- [x] 6.2 Añadir comandos de ejecución por tipo, cobertura y solución de problemas a README/guía de contribución.
- [x] 6.3 Configurar CI para publicar resultados, cobertura y evidencia de fallos.
- [x] 6.4 Emitir dictamen de liberación: apta, apta con observaciones o no apta, con riesgos aceptados explícitos.
