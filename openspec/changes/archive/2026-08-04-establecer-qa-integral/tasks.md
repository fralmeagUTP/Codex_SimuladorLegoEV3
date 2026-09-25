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
- [x] 4.2 Automatizar Tkinter con escritorio Windows visible: introducción, menús, diálogos nativos, editor, canvas y cierre. *(La campaña `interactive_desktop_qa.py` y las capturas de `Documentos/EVIDENCIA_TESTEO_INTEGRAL_TKINTER_2026-07-28/` ejercitan una ventana Tkinter visible. La variante Pywinauto queda registrada separadamente en 7.1 por su restricción de sesión.)*
- [x] 4.3 Ejecutar el catálogo crítico en claro/oscuro y resoluciones requeridas; incluir móvil 390×844 para Web.
- [x] 4.4 Verificar teclado, foco, Escape, contraste, texto truncado, lectores de estado `aria-live` y orden de tabulación. *(Web automatiza teclado, foco, `aria-live` y contraste. Tkinter se revalidó con F10, Tab, Shift+Tab, Enter y Escape mediante `keyboard-navigation`; la evidencia `teclado_foco_escape_real.png` confirma que vuelve sin modal ni foco bloqueado.)*
- [x] 4.5 Guardar capturas antes/después, consola, red y logs de cada fallo real. *(E2E Web conserva automáticamente captura, consola, red y HAR; la campaña Tkinter conserva capturas reales por caso, incluidos error sintáctico, pausa y reinicio. No se observó un fallo nuevo durante la revalidación.)*

## Fase 5 — Seguridad, rendimiento y resiliencia

- [x] 5.1 Probar entradas maliciosas o inválidas de scripts, mundos, API y rutas sin exponer datos reales.
- [x] 5.2 Medir latencia, ticks, memoria, cola y sesiones bajo carga sintética controlada. *(Incluye smoke concurrente, workers aislados y carga sostenida de 12 operaciones con latencia individual <2 s y duración total <5 s en entorno de prueba; no sustituye un SLA de producción.)*
- [x] 5.3 Ejercitar caída/recuperación de worker, cancelación, recarga y eventos retrasados. *(QA-REG-006, QA-REG-007 y QA-REG-009 fueron corregidas y cubiertas; QA-REG-010 fue revalidada en el escenario Web.)*
- [x] 5.4 Validar límites configurables, bucles no terminantes y capacidad de detención manual.
- [x] 5.5 Ejecutar smoke de Docker/Linux y empaquetado Windows, con instalación limpia y configuración por entorno. *(El 2026-07-30 el smoke local construyó `simulador-ev3:qa-local-20260730` y `/healthz` respondió HTTP 200. Tras publicar `9530e15`, los jobs remotos `contenedor Linux` y `empaquetado Windows limpio` del workflow `calidad` también finalizaron correctamente.)*

## Fase 6 — Reporte y compuerta de liberación

- [x] 6.1 Publicar diagnóstico, estrategia, casos, matriz de trazabilidad y reporte de ejecución bajo `docs/testing/`.
- [x] 6.2 Añadir comandos de ejecución por tipo, cobertura y solución de problemas a README/guía de contribución.
- [x] 6.3 Configurar CI para publicar resultados, cobertura y evidencia de fallos.
- [x] 6.4 Emitir dictamen de liberación: apta, apta con observaciones o no apta, con riesgos aceptados explícitos.
