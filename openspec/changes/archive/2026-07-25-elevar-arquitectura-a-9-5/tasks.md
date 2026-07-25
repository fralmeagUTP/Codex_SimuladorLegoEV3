# Tareas: elevar arquitectura a 9.5

## Fase 1 — Contrato de sesión

- [x] 1.1 Definir DTOs versionados para comando, evento, snapshot, error y depuración.
- [x] 1.2 Extraer fachada `SimulationSession` compartida por Web y Tkinter.
- [x] 1.3 Hacer el worker ruta predeterminada y documentar fallback local explícito.
- [x] 1.4 Cubrir idempotencia, cancelación y recuperación con contratos cruzados.

## Fase 2 — Interfaces modernas y paridad

- [x] 2.1 Dividir frontend en controladores de sesión, editor, streaming, telemetría, mundo y depuración.
- [x] 2.2 Introducir presentadores/adaptadores modernos de Tkinter sobre el contrato común.
- [x] 2.3 Igualar accesibilidad, teclado, tema, perfiles, trazas y depuración.
- [x] 2.4 Bloquear diferencias de catálogo de casos de uso en CI.

## Fase 3 — Calidad interna

- [x] 3.1 Eliminar accesos privados restantes y definir puertos de runtime, mundos y telemetría.
- [x] 3.2 Ampliar Mypy a todos los paquetes productivos.
- [x] 3.3 Establecer cobertura por capa y escenarios críticos de runtime/motor.

## Fase 4 — Operación y despliegue

- [x] 4.1 Exponer métricas Prometheus y trazas OpenTelemetry correlacionadas.
- [x] 4.2 Añadir métricas de latencia, worker, cola, memoria, sesiones y ticks.
- [x] 4.3 Crear contenedor Linux sin privilegios y guía de despliegue aula/servidor.
- [x] 4.4 Añadir carga, resiliencia y recuperación de sesión en CI.

## Fase 5 — Validación y documentación

- [x] 5.1 Ejecutar Playwright completo en CI.
- [x] 5.2 Publicar diagramas C4 y guía de arquitectura/operación.
- [x] 5.3 Actualizar diferencias simulador–robot y criterios docentes.

## Avance

- 2026-07-24: se creó `SessionCommand` y `SessionEvent` como envolturas
  versionadas y validadas para los mensajes de worker consumidos por Web y
  Tkinter. El worker se activa por defecto; `EV3_LOCAL_RUNTIME_ENABLED=true`
  conserva el modo local para desarrollo y pruebas.
- 2026-07-24: `SimulationSessionPort` formaliza los casos de uso compartidos y
  Web/Tkinter lo implementan con una prueba de contrato ejecutable.
- 2026-07-24: CI instala Chromium y ejecuta la batería Playwright en un trabajo
  E2E dedicado de Linux.
- 2026-07-24: `/metrics` expone formato Prometheus con latencia HTTP, sesiones,
  workers, CPU, memoria, cola de eventos y ticks agregados desde heartbeats IPC.
- 2026-07-24: cada petición Web crea un span OpenTelemetry con traza, sesión,
  comando, método, ruta y resultado HTTP; la tarea 4.1 queda completada.
- 2026-07-24: la sesión puede recuperar un worker caído recreándolo, reiniciando
  política/configuración y reproduciendo script y depuración; se cubre con una
  prueba de contrato IPC. Idempotencia y cancelación siguen cubiertas por la
  batería existente, por lo que 1.4 queda completada.
- 2026-07-24: CI ejecuta el trabajo `runtime-resilience` con carga y pruebas de
  worker, cancelación y recuperación. La tarea 4.4 queda completada.
- 2026-07-24: la aplicación expone puertos públicos para configuración de
  depuración, aplicación/lectura de mundos y trazas. Web/Tkinter y rutas API
  dejan de acceder a internals del servicio; la tarea 3.1 queda completada.
- 2026-07-24: se publicaron el diagrama C4 inicial y la guía de despliegue Linux
  sin privilegios para aula/servidor; la tarea 5.2 queda completada.
- 2026-07-24: se documentaron diferencias de tiempo, motores, sensores,
  ultrasonido, interacción y seguridad entre simulador/robot, con criterio de
  entrega docente verificable. La tarea 5.3 queda completada.
- 2026-07-24: se añadió `Dockerfile` que usa el usuario no privilegiado `ev3`
  y guía de despliegue Linux para aula/servidor. La tarea 4.3 queda completada.
- 2026-07-24: cobertura global mínima de 70% y gate de 90% para core/domain;
  las pruebas críticas de motor y runtime se ejecutan en CI. La tarea 3.3 queda
  completada.
- 2026-07-24: Mypy cubre ahora core, domain y los contratos de sesión/perfil/
  trazas; 33 módulos pasan el gate. UI, runtime y Web quedan como siguiente
  incremento para completar 3.2.
- 2026-07-24: Mypy cubre las capas productivas principales (97 módulos),
  incluidas Web y Tkinter, sin exclusiones para errores de UI. La tarea 3.2
  queda completada.
- 2026-07-24: el adaptador de escritorio implementa el contrato de sesión
  compartido y la matriz de paridad confirma tema, teclado, perfiles, trazas y
  depuración en ambas interfaces. El catálogo se valida en CI y las pruebas de
  contrato cubren ciclo de vida, depuración, mundo, perfiles y trazas; se
  completan las tareas 2.2, 2.3 y 2.4.
- 2026-07-24: inició la descomposición del frontend: `session_controller.js`
  contiene los comandos de ejecución y depuración y está verificado como
  dependencia de la página. Falta extraer streaming, telemetría, mundo y editor
  para completar la tarea 2.1.
- 2026-07-24: se añadieron `stream_health_controller.js` y
  `snapshot_controller.js`; este último valida la versión del contrato, descarta
  snapshots obsoletos y delega su renderizado. La separación de la actualización
  en vivo está iniciada, pero aún faltan los controladores completos de streaming,
  telemetría, mundo y editor para cerrar la tarea 2.1.
- 2026-07-24: `telemetry_controller.js` extrae el renderizado de robot, motores
  y sensores del orquestador principal. Persisten como trabajo de 2.1 la
  extracción completa de streaming, mundo/canvas y editor.
- 2026-07-24: el frontend quedó compuesto por controladores de sesión,
  interacción del editor, actualización en vivo, salud del stream, snapshots,
  telemetría, vista de mundo, ciclo de vida y archivos. Playwright con Chromium
  instalado validó los flujos Web reales (20/20), y la batería completa pasó
  (672/672); la tarea 2.1 queda completada.
