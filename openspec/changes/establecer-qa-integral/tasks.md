# Tareas: establecer QA integral y compuerta de calidad

## Fase 1 — Gobierno, inventario y riesgo

- [ ] 1.1 Consolidar requisitos documentados e inferidos en un inventario funcional versionado.
- [ ] 1.2 Clasificar cada funcionalidad por criticidad, riesgo, capa, interfaz y cobertura actual.
- [ ] 1.3 Crear matriz de trazabilidad requisito → riesgo → caso → automatización → evidencia.
- [ ] 1.4 Registrar catálogo de defectos confirmados y convertirlos en regresiones priorizadas.

## Fase 2 — Fundaciones automatizadas

- [ ] 2.1 Normalizar marcadores pytest: `unit`, `integration`, `contract`, `ui`, `e2e`, `security`, `performance`, `release`.
- [ ] 2.2 Crear fixtures, fábricas y mundos temporales aislados; prohibir escritura sobre recursos de usuario.
- [ ] 2.3 Medir cobertura real por paquete productivo y establecer umbrales graduales por capa.
- [ ] 2.4 Añadir pruebas de mutación o escenarios equivalentes para motor, runtime y transiciones de sesión críticas.
- [ ] 2.5 Ejecutar Ruff, Mypy, Bandit y Pip-Audit con resultados reproducibles en local y CI.

## Fase 3 — Funcionalidad y contratos

- [ ] 3.1 Cubrir CRUD y validaciones de mundos, persistencia, cancelación y recuperación de errores.
- [ ] 3.2 Cubrir catálogo Pybricks soportado: motores A–D, DriveBase, LCD, sensores, temporizadores, errores y límites.
- [ ] 3.3 Cubrir sesión terminal: `finished`, `error`, `timed_out`, `stopped`, `reset` y eventos tardíos.
- [ ] 3.4 Añadir regresión para que un error de script deje editor, barra, canvas, LCD y telemetría en `ERROR`, no `EJECUTANDO`.
- [ ] 3.5 Validar paridad de casos de uso Web/Tkinter y documentar diferencias justificadas.

## Fase 4 — UI real, E2E y accesibilidad

- [ ] 4.1 Automatizar Web con Playwright visible: menús, diálogos, editor, mundos, misiones, controles y navegación.
- [ ] 4.2 Automatizar Tkinter con escritorio Windows visible: introducción, menús, diálogos nativos, editor, canvas y cierre.
- [ ] 4.3 Ejecutar el catálogo crítico en claro/oscuro y resoluciones requeridas; incluir móvil 390×844 para Web.
- [ ] 4.4 Verificar teclado, foco, Escape, contraste, texto truncado, lectores de estado `aria-live` y orden de tabulación.
- [ ] 4.5 Guardar capturas antes/después, consola, red y logs de cada fallo real.

## Fase 5 — Seguridad, rendimiento y resiliencia

- [ ] 5.1 Probar entradas maliciosas o inválidas de scripts, mundos, API y rutas sin exponer datos reales.
- [ ] 5.2 Medir latencia, ticks, memoria, cola y sesiones bajo carga sintética controlada.
- [ ] 5.3 Ejercitar caída/recuperación de worker, cancelación, recarga y eventos retrasados.
- [ ] 5.4 Validar límites configurables, bucles no terminantes y capacidad de detención manual.
- [ ] 5.5 Ejecutar smoke de Docker/Linux y empaquetado Windows, con instalación limpia y configuración por entorno.

## Fase 6 — Reporte y compuerta de liberación

- [ ] 6.1 Publicar diagnóstico, estrategia, casos, matriz de trazabilidad y reporte de ejecución bajo `docs/testing/`.
- [ ] 6.2 Añadir comandos de ejecución por tipo, cobertura y solución de problemas a README/guía de contribución.
- [ ] 6.3 Configurar CI para publicar resultados, cobertura y evidencia de fallos.
- [ ] 6.4 Emitir dictamen de liberación: apta, apta con observaciones o no apta, con riesgos aceptados explícitos.
