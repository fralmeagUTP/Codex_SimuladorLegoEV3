# Tareas: ejecutar QA total de la aplicación Web

## Fase 1 — Preparación e inventario

- [x] 1.1 Registrar SO, Python, rama, commit, URL, servidor y versión del navegador.
- [x] 1.2 Iniciar una instancia Web oficial aislada y comprobar salud, consola y red.
- [x] 1.3 Descubrir y congelar el inventario de todos los menús, comandos,
  ejemplos, mundos, escenarios, misiones, ayudas y controles visibles.
- [x] 1.4 Crear datos sintéticos temporales y plan de limpieza segura.
- [x] 1.5 Crear matriz requisito → funcionalidad → riesgo → caso → evidencia.

## Fase 2 — Navegación y operaciones manuales reales

- [x] 2.1 Recorrer todos los menús y cada comando, incluidas aperturas
  repetidas, aceptar, cancelar, cerrar y Escape de diálogos (ejecutado; las
  operaciones que requieren archivo local/exportación quedan BLOCKED por el
  navegador integrado y las de mundos por WEB-WE-002).
- [x] 2.2 Probar barra de simulación, pose, haces, zoom, paneo, trazas,
  fidelidad y tiempo máximo en navegador real.
- [x] 2.3 Cargar y ejecutar cada ejemplo disponible; registrar estado final,
  canvas, LCD, telemetría, editor, consola y mensaje de resultado.
- [x] 2.4 Cargar, ejecutar y reiniciar cada mundo, escenario y misión;
  verificar limpieza de entidades, robot único y snapshot coherente.
- [x] 2.5 Ejecutar el catálogo Pybricks y todos los flujos negativos/terminales
  (FAIL: WEB-RT-011 reproducido para error de ejecución).
- [x] 2.6 Probar depuración: breakpoints, paso, continuar, watches, error,
  cancelación y recuperación (FAIL: WEB-DBG-016 y WEB-DBG-018 bloquean los
  casos posteriores).

- [x] 2.7 Medir en navegador tiempo de pared frente a `sim_time_s` y ticks para
  waits, movimientos, giros y radar; registrar desviación y fluidez visual.
- [x] 2.8 Confirmar que interpolación no adelanta LCD, telemetría, estado ni fin
  de ejecución respecto al snapshot autoritativo.

## Fase 3 — Autoría y persistencia de mundos

- [x] 3.1 Intentar crear mundos mínimo, con inicio personalizado, obstáculos, meta y sensores
  (BLOCKED por WEB-WE-002 al colocar assets/guardar).
- [x] 3.2 Validar entradas vacías, duplicadas, fuera de rango, no numéricas e inválidas
  (BLOCKED parcialmente por WEB-WE-002; validación básica de mundo vacío PASS).
- [x] 3.3 Guardar, recargar navegador, cargar, editar, cancelar, duplicar si
  existe, eliminar y confirmar que no quedan datos visuales heredados
  (BLOCKED por WEB-WE-002; no se alteraron datos persistentes).
- [x] 3.4 Verificar que el mundo activo sincroniza mapa, pose, sensores y telemetría
  (PASS para los 12 mundos predefinidos; autoría manual BLOCKED por WEB-WE-002).

## Fase 4 — Sesiones, API y concurrencia

- [x] 4.1 Ejercitar creación, reutilización, expiración, cierre y recuperación de sesión.
- [x] 4.2 Ejecutar dos o más usuarios/contextos en paralelo con mundos y scripts distintos.
- [x] 4.3 Verificar aislamiento de token, código, eventos SSE, snapshot, mundo,
  telemetría, errores y cancelación entre usuarios.
- [x] 4.4 Forzar fallback SSE/polling, recarga durante ejecución y eventos tardíos.
- [x] 4.5 Cubrir API de sesión, script, mundo, editor, stream y errores con contratos.

## Fase 5 — Calidad no funcional

- [x] 5.1 Ejecutar Ruff, Mypy, Bandit, Pip-Audit, cobertura y pruebas de mutación/escenarios críticos.
- [x] 5.2 Ejecutar accesibilidad, teclado, foco, contraste y `aria-live` en ambos temas.
- [x] 5.3 Probar responsividad en las cuatro resoluciones, sin recortes ni scroll horizontal indebido.
- [x] 5.4 Medir latencia de sesión/snapshot, FPS de canvas, memoria, CPU y carga concurrente controlada.
- [x] 5.5 Probar seguridad: límites, rutas, payloads inválidos, autorización,
  aislamiento de runtime y manejo de errores sin secretos.
- [x] 5.6 Validar recuperación ante worker caído, timeout, red/SSE interrumpida y servidor reiniciado.

## Fase 6 — Regresión, evidencia y dictamen

- [x] 6.1 Convertir cada defecto confirmado en prueba de regresión o caso manual documentado.
- [x] 6.2 Guardar capturas, vídeo si está disponible, consola, red/HAR y logs por FAIL/BLOCKED.
- [x] 6.3 Publicar inventario, estrategia, casos, matriz, reporte de ejecución y defectos priorizados.
- [x] 6.4 Ejecutar la batería final en navegador real y emitir dictamen de liberación.

## Fase 7 — Aviso de finalización de simulación

- [x] 7.1 Verificar en Web y Tkinter que, tras el estado terminal exitoso
  `finished` y después de aplicar el snapshot final, se muestra una única
  notificación: `El programa se ejecutó correctamente.`
- [x] 7.2 Verificar que el aviso no se muestra para `error`, `timed_out`,
  `stopped`, cancelación manual ni `reset`, y que eventos tardíos de una
  ejecución anterior no pueden producirlo.
- [x] 7.3 Registrar evidencia manual y automatizada: Web en claro/oscuro y
  móvil 390×844; Tkinter sin diálogos duplicados ni bloqueo de interfaz.
